import smtplib
import os

def send_email(to_email, message):
    try:
        server = smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT")))
        server.starttls()
        server.login(os.getenv("EMAIL"), os.getenv("PASSWORD"))
        server.sendmail(os.getenv("EMAIL"), to_email, message)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")
