from django.utils.translation import gettext_lazy as _

from users.tasks import send_email_task
from utils.functions.get_email_content import get_email_content


class MailService:
    @staticmethod
    def send_registration_code(email: str, code: str):
        html, text = get_email_content(
            template_name="emails/account_verification", context={"code": code}
        )
        send_email_task.delay(
            emails=[email],
            subject=_("Verification code"),
            message=text,
            html_message=html,
        )

    @staticmethod
    def send_password_recovery_code(email: str, code: str):
        html, text = get_email_content(
            template_name="emails/password_recovery", context={"code": code}
        )
        send_email_task.delay(
            emails=[email],
            subject=_("Password recovery code"),
            message=text,
            html_message=html,
        )
