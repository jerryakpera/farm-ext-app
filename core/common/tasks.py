"""
Shared Celery tasks for HiddenWord.
"""

# django_packages
from django.conf import settings

# third_party_packages
import mailtrap as mt

# other_apps_packages
from celery import shared_task


def _get_mailtrap_client() -> mt.MailtrapClient:
    """
    Build and return a configured Mailtrap client.

    Returns
    -------
    mt.MailtrapClient
        Client pointed at sandbox or live depending on settings.
    """

    kwargs: dict = {"token": settings.MAILTRAP_API_KEY}

    if settings.MAILTRAP_USE_SANDBOX and settings.MAILTRAP_INBOX_ID:
        kwargs["sandbox"] = True
        kwargs["inbox_id"] = int(settings.MAILTRAP_INBOX_ID)

    return mt.MailtrapClient(**kwargs)


@shared_task(name="core.tasks.send_email")
def send_email(
    recipient: str,
    subject: str,
    html_message: str,
) -> str:
    """
    Send a transactional email via Mailtrap.

    Parameters
    ----------
    recipient : str
        Destination email address.
    subject : str
        Email subject line.
    html_message : str
        HTML body content.

    Returns
    -------
    str
        The recipient email address, confirming dispatch.
    """

    client = _get_mailtrap_client()

    mail = mt.Mail(
        sender=mt.Address(
            email=settings.DEFAULT_FROM_EMAIL,
            name="HiddenWord",
        ),
        to=[mt.Address(email=recipient)],
        subject=subject,
        html=html_message,
        text="",  # plaintext fallback — populate if needed
    )

    client.send(mail)
    return recipient
