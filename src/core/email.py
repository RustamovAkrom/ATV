import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config import get_settings

settings = get_settings()


def send_email(to: str, subject: str, body: str) -> None:
    """
    Send email via SMTP (production-safe)
    """

    # =========================
    # VALIDATION
    # =========================
    if not to:
        raise ValueError("Recipient email is empty")

    if "@" not in to:
        raise ValueError(f"Invalid email address: {to}")

    # =========================
    # BUILD MESSAGE
    # =========================
    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    # =========================
    # SEND
    # =========================
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()

            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

            result = server.send_message(msg)

            # 🔥 VERY IMPORTANT
            if result:
                raise Exception(f"SMTP rejected recipients: {result}")

    except smtplib.SMTPRecipientsRefused as e:
        raise Exception(f"Recipients refused: {e.recipients}")

    except smtplib.SMTPAuthenticationError:
        raise Exception("SMTP authentication failed")

    except smtplib.SMTPException as e:
        raise Exception(f"SMTP error: {str(e)}")
