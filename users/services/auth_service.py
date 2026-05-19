from enum import Enum

from django.utils.translation import gettext_lazy as _

from services.mail_service import MailService
from services.rate_limiter import RateLimiter
from users.models import AccountVerification, User
from utils.exceptions import TooManyAttempts
from utils.validators import validate_email


class AuthCodeEnum(str, Enum):
    REGISTRATION = "REGISTRATION"
    PASSWORD_RECOVERY = "PASSWORD_RECOVERY"  # nosec


class AuthService:
    BLOCK_TIME = 60

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
