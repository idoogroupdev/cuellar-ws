from users.tasks import send_email_task
from utils.functions.get_email_content import get_email_content


class MailService:
    @staticmethod
    def send_registration_code(email: str, code: str):
        html, text = get_email_content(
            template_name="emails/account_verification_email", context={"code": code}
        )
        send_email_task.delay(
            emails=[email],
            subject="Verication code",
            message=text,
            html_message=html,
        )
