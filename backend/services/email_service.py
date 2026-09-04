import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def send_email(to_email: str, subject: str, body: str):
    gmail_address = os.getenv("GMAIL_ADDRESS")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")

    print("Gmail:", gmail_address)
    print("Password loaded:", bool(gmail_password))
    print("Password length:", len(gmail_password) if gmail_password else 0)

    message = EmailMessage()
    message["From"] = gmail_address
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(gmail_address, gmail_password)
        server.send_message(message)

