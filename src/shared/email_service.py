import aiosmtplib
from email.message import EmailMessage

from src.core.config import Settings


async def send_contact_email(contact, settings: Settings) -> None:
    msg = EmailMessage()
    msg["From"] = settings.email_username
    msg["To"] = settings.email_to
    msg["Subject"] = "Nouveau message de contact"
    msg.set_content(
        f"Nom : {contact.name}\nEmail : {contact.email}\n\nMessage :\n{contact.message}"
    )

    await aiosmtplib.send(
        msg,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=settings.email_username,
        password=settings.email_password,
    )
