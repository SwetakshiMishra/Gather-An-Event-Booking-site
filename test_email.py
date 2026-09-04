import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

gmail_address = os.getenv("GMAIL_ADDRESS")
gmail_password = os.getenv("GMAIL_APP_PASSWORD")

print("Password loaded:", gmail_password is not None)
print("Length:", len(gmail_password) if gmail_password else 0)
print("Has leading/trailing spaces:",
      gmail_password != gmail_password.strip())

message = EmailMessage()
message["From"] = gmail_address
message["To"] = gmail_address
message["Subject"] = "Test Email"
message.set_content("This is a test.")

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    print("SMTP connection successful")

    server.login(gmail_address, gmail_password)
    print("Gmail login successful")

    server.send_message(message)
    print("Email sent!")