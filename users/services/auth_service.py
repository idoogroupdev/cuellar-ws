from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from graphql_jwt.settings import jwt_settings
from graphql_jwt.shortcuts import create_refresh_token, get_token
from graphql_jwt.utils import jwt_decode

from services.mail_service import MailService
from services.rate_limiter import RateLimiter
from users.models import AccountVerification, RecoverPassword, User
from utils.exceptions import TooManyAttempts
from utils.validators import validate_email, validate_password


class AuthCodeEnum(str, Enum):
    REGISTRATION = "REGISTRATION"
    PASSWORD_RECOVERY = "PASSWORD_RECOVERY"  # nosec


@dataclass
class AuthInfo:
    token: str
    refresh_token: str
    payload: dict
    refresh_expires_in: datetime


class AuthService:
    BLOCK_TIME = 60
    SCOPES = {
        "registration_code": "verify_registration_code",
        "passwd_code": "verify_passwd_code",  # nosec
    }

    @staticmethod
    def create_jwt_and_refresh_info(user: User):
        token = get_token(user)
        refresh_token = create_refresh_token(user)
        refresh_expires_in = (
            refresh_token.created + jwt_settings.JWT_REFRESH_EXPIRATION_DELTA
        )

        return AuthInfo(
            token=token,
            refresh_token=refresh_token.token,
            payload=jwt_decode(token),
            refresh_expires_in=refresh_expires_in,
        )

    @staticmethod
    def send_auth_code(email: str, auth_code: AuthCodeEnum):
        validate_email(email)

        user = User.objects.filter(email=email).first()

        if not user:
            raise ValueError(_("You cannot request a auth code for this time"))

        if not user.is_active:
            raise ValueError(_("User is not active"))

        if auth_code.value == AuthCodeEnum.REGISTRATION.value:
            if user.is_verified:
                raise ValueError(_("User is already verified"))

            result = RateLimiter.hit(
                scope="req_auth_code_regis",
                key=email,
                expiration=AuthService.BLOCK_TIME,
            )

            if result.allowed is False:
                raise TooManyAttempts(seconds=result.remaining)

            verification = AccountVerification.objects.get_or_create(user=user)[0]
            verification.generate_code()

            MailService.send_registration_code(email, verification.code)

        if auth_code.value == AuthCodeEnum.PASSWORD_RECOVERY.value:
            result = RateLimiter.hit(
                scope="req_auth_code_passwd_recovery",
                key=email,
                expiration=AuthService.BLOCK_TIME,
            )

            if result.allowed is False:
                raise TooManyAttempts(seconds=result.remaining)

            recover_password = RecoverPassword.objects.get_or_create(user=user)[0]
            recover_password.generate_code()

            MailService.send_password_recovery_code(email, code=recover_password.code)

    @staticmethod
    def verify_auth_code(
        email: str, code: str, auth_code: AuthCodeEnum, request: HttpRequest = None
    ):
        validate_email(email)

        if auth_code.value == AuthCodeEnum.REGISTRATION.value:
            scope = AuthService.SCOPES["registration_code"]
            function = AuthService._verify_registration_code

        elif auth_code.value == AuthCodeEnum.PASSWORD_RECOVERY.value:
            scope = AuthService.SCOPES["passwd_code"]
            function = AuthService._verify_passwd_recovery_code

        else:
            raise ValueError(_("Invalid auth code"))

        result = RateLimiter.check(scope=scope, request=request)

        if result.allowed is False:
            raise TooManyAttempts(seconds=result.remaining)

        try:
            user = function(email, code)
        except ValueError:
            RateLimiter.register_failure(scope=scope, request=request)
            raise

        auth_info = AuthService.create_jwt_and_refresh_info(user)
        RateLimiter.reset(scope=scope, request=request)

        return user, auth_info

    @staticmethod
    def _verify_registration_code(email: str, code: str):
        verification = (
            AccountVerification.objects.select_related("user")
            .filter(user__email=email)
            .first()
        )

        if not verification:
            raise ValueError(_("Invalid auth code"))

        if verification.is_expired():
            raise ValueError(_("Auth code expired"))

        if verification.is_verified():
            raise ValueError(_("User is already verified"))

        if not verification.is_valid_code(code):
            raise ValueError(_("Invalid auth code"))

        verification.mark_as_verified()

        return verification.user

    @staticmethod
    def _verify_passwd_recovery_code(email: str, code: str):
        recover_password = (
            RecoverPassword.objects.select_related("user")
            .filter(user__email=email)
            .first()
        )

        if not recover_password:
            raise ValueError(_("Invalid auth code"))

        if recover_password.is_expired():
            raise ValueError(_("Auth code expired"))

        if not recover_password.is_valid_code(code):
            raise ValueError(_("Invalid auth code"))

        user = recover_password.user
        user.state = User.StateChoices.WAITING_FOR_NEW_PASSWD
        user.save(update_fields=["state"])

        verification = AccountVerification.objects.get_or_create(user=user)[0]
        verification.mark_as_verified()

        recover_password.delete()

        return user

    @staticmethod
    def reset_password_after_recovery(email: str, new_password: str):
        validate_email(email)
        validate_password(new_password)

        user = User.objects.filter(email=email).first()

        if not user:
            raise ValueError(_("Invalid password recovery flow"))

        if user.state != User.StateChoices.WAITING_FOR_NEW_PASSWD:
            raise ValueError(_("User is not allowed to reset password"))

        user.set_password(new_password)
        user.state = User.StateChoices.NONE
        user.save(update_fields=["password", "state"])

        return user
