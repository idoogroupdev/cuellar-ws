from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from django.utils.translation import gettext_lazy as _
from graphql_jwt.settings import jwt_settings
from graphql_jwt.shortcuts import create_refresh_token, get_token
from graphql_jwt.utils import jwt_decode

from services.mail_service import MailService
from services.rate_limiter import RateLimiter
from users.models import AccountVerification, User
from utils.exceptions import TooManyAttempts
from utils.validators import validate_email


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

        if user.is_verified:
            raise ValueError(_("User is already verified"))

        if auth_code.value == AuthCodeEnum.REGISTRATION.value:
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
            # TODO: send email
            pass

    @staticmethod
    def verify_auth_code(email: str, code: str, auth_code: AuthCodeEnum):
        validate_email(email)

        if auth_code.value == AuthCodeEnum.REGISTRATION.value:
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

            auth_info = AuthService.create_jwt_and_refresh_info(verification.user)

            return verification.user, auth_info
