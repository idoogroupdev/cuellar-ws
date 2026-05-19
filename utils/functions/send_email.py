import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


def send_email(
    emails: list[str],
    subject: str,
    message: str,
    html_message: str = None,
    attachments: list = None,
):
    """Send emails to users"""

    logger.info("Sending email to %s", emails)

    from_email = f"Dulcería Cuellar <{settings.DEFAULT_FROM_EMAIL}>"

    msg = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=from_email,
        to=emails,
    )

    if attachments:
        for attachment in attachments:
            msg.attach(
                filename=attachment["file"].name,
                content=attachment["file"].getvalue(),
                mimetype=attachment["mimetype"],
            )

    if html_message:
        msg.attach_alternative(html_message, "text/html")

    return msg.send(fail_silently=False)
