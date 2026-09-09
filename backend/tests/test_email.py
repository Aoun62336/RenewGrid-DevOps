import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()

host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
port = int(os.environ.get("SMTP_PORT", 587))
user = os.environ.get("SMTP_USER")
password = os.environ.get("SMTP_PASS")

try:
    print(f"Connecting to {host}:{port} as {user}...")
    with smtplib.SMTP(host, port, timeout=10) as server:
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(user, password)
        print("Login successful!")
        
        msg = MIMEText("This is a test email from the server.")
        msg["Subject"] = "Test Email"
        msg["From"] = user
        msg["To"] = user
        
        server.sendmail(user, user, msg.as_string())
        print("Email sent!")
except Exception as e:
    print(f"Failed: {e}")
