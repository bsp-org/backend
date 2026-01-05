"""Email service for sending emails."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urlparse

from pydantic import BaseModel

from src.config import settings

logger = logging.getLogger(__name__)


class SMTPConfig(BaseModel):
    """SMTP configuration parsed from URL."""

    host: str
    port: int
    username: str
    password: str
    use_tls: bool


def parse_smtp_url(smtp_url: str) -> SMTPConfig:
    """Parse SMTP URL into components.

    Args:
        smtp_url: SMTP URL in format smtp://[user:pass@]host[:port] or smtps://[user:pass@]host[:port]

    Returns:
        SMTPConfig: Pydantic model with host, port, username, password, and use_tls fields
    """
    parsed = urlparse(smtp_url)

    # Determine if TLS should be used based on scheme
    use_tls = parsed.scheme == "smtps"

    # Default port based on scheme
    default_port = 465 if use_tls else 587
    port = parsed.port if parsed.port else default_port

    return SMTPConfig(
        host=parsed.hostname or "localhost",
        port=port,
        username=parsed.username or "",
        password=parsed.password or "",
        use_tls=use_tls,
    )


def send_email(to_email: str, subject: str, text_body: str, html_body: str | None = None) -> bool:
    """Send an email with plain text and optional HTML content.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        text_body: Plain text version of the email
        html_body: Optional HTML version of the email

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Parse SMTP configuration
        smtp_config = parse_smtp_url(settings.email_smtp_url)

        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from_email
        msg["To"] = to_email

        # Attach plain text version
        part1 = MIMEText(text_body, "plain")
        msg.attach(part1)

        # Attach HTML version if provided
        if html_body:
            part2 = MIMEText(html_body, "html")
            msg.attach(part2)

        # Send email
        with smtplib.SMTP(smtp_config.host, smtp_config.port) as server:
            if smtp_config.use_tls:
                server.starttls()

            # Only authenticate if credentials are provided
            if smtp_config.username and smtp_config.password:
                server.login(smtp_config.username, smtp_config.password)

            server.sendmail(settings.smtp_from_email, to_email, msg.as_string())

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_login_code_email(email: str, code: str) -> bool:
    """Send login code via email.

    Args:
        email: Recipient email address
        code: Login code to send

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = "Your Bible Search Login Code"

    text_body = f"""
Your login code is: {code}

This code will expire in 5 minutes.

If you didn't request this code, please ignore this email.
"""

    html_body = f"""
<html>
  <body>
    <h2>Your Bible Search Login Code</h2>
    <p>Your login code is: <strong>{code}</strong></p>
    <p>This code will expire in 5 minutes.</p>
    <p><small>If you didn't request this code, please ignore this email.</small></p>
  </body>
</html>
"""

    return send_email(email, subject, text_body, html_body)
