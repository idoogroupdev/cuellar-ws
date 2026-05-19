from config.celery import app
from utils.functions.send_email import send_email


@app.task
def send_email_task(
    emails: list[str],
    subject: str,
    message: str,
    html_message: str = None,
    attachments: list = None,
):
    return send_email(
        emails=emails,
        subject=subject,
        message=message,
        html_message=html_message,
        attachments=attachments,
    )
