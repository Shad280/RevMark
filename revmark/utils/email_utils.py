from flask_mail import Message
from flask import current_app
from revmark import mail


def send_email(subject, recipients, body, html=None):
    """Send an email using the app's initialized Mail instance.

    Args:
        subject (str): Email subject.
        recipients (list[str]): List of recipient email addresses.
        body (str): Plain-text body.
        html (str|None): Optional HTML body.
    """
    msg = Message(subject, recipients=recipients, body=body, html=html)
    mail.send(msg)
