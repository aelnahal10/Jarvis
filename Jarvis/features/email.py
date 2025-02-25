import smtplib
import Jarvis.config as config

def send_email(to, subject, body):
    """Sends an email via Gmail."""
    sender_email = config.email
    sender_password = config.email_password

    msg = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as mail:
            mail.starttls()
            mail.login(sender_email, sender_password)
            mail.sendmail(sender_email, to, msg)
        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {e}"
