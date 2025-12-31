"""Email service for sending emails."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urlparse

from src.config import settings

logger = logging.getLogger(__name__)


def parse_smtp_url(smtp_url: str) -> dict[str, str | int | bool]:
    """Parse SMTP URL into components.

    Args:
        smtp_url: SMTP URL in format smtp://[user:pass@]host[:port] or smtps://[user:pass@]host[:port]

    Returns:
        dict: Dictionary with host, port, username, password, and use_tls keys
    """
    parsed = urlparse(smtp_url)

    # Determine if TLS should be used based on scheme
    use_tls = parsed.scheme == "smtps"

    # Default port based on scheme
    default_port = 465 if use_tls else 587
    port = parsed.port if parsed.port else default_port

    return {
        "host": parsed.hostname or "localhost",
        "port": port,
        "username": parsed.username or "",
        "password": parsed.password or "",
        "use_tls": use_tls,
    }


def send_login_code_email(email: str, code: str) -> bool:
    """Send login code via email.

    Args:
        email: Recipient email address
        code: Login code to send

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Parse SMTP configuration
        smtp_config = parse_smtp_url(settings.email_smtp_url)

        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Your Bible Search Login Code"
        msg["From"] = settings.smtp_from_email
        msg["To"] = email

        # Create plain text and HTML versions
        text = f"""
Your login code is: {code}

This code will expire in 5 minutes.

If you didn't request this code, please ignore this email.
"""

        html = f"""
<html>
  <body>
    <h2>Your Bible Search Login Code</h2>
    <p>Your login code is: <strong>{code}</strong></p>
    <p>This code will expire in 5 minutes.</p>
    <p><small>If you didn't request this code, please ignore this email.</small></p>
  </body>
</html>
"""

        # Attach both plain text and HTML versions
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)

        # Send email
        with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
            if smtp_config["use_tls"]:
                server.starttls()

            # Only authenticate if credentials are provided
            if smtp_config["username"] and smtp_config["password"]:
                server.login(smtp_config["username"], smtp_config["password"])

            server.sendmail(settings.smtp_from_email, email, msg.as_string())

        logger.info(f"Login code email sent successfully to {email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send login code email to {email}: {e}")
        return False
