import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Support both naming styles:
# - New: SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD
# - Legacy: EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
EMAIL_HOST = os.getenv("SMTP_SERVER") or os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("SMTP_PORT") or os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_ADDRESS") or os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD") or os.getenv("EMAIL_HOST_PASSWORD")


def send_email(to_email: str, subject: str, body: str):
    if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
        raise ValueError("Missing email credentials. Set EMAIL_ADDRESS/EMAIL_PASSWORD in .env")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_HOST_USER
    msg["To"] = to_email

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.send_message(msg)
