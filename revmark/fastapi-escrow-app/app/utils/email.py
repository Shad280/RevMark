from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import os

class EmailUtils:
    conf = ConnectionConfig(
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_FROM=os.getenv("MAIL_FROM"),
        MAIL_PORT=587,
        MAIL_SERVER=os.getenv("MAIL_SERVER"),
        MAIL_FROM_NAME="Escrow App",
        MAIL_TLS=True,
        MAIL_SSL=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )

    @staticmethod
    async def send_email(email: EmailStr, subject: str, message: str, background_tasks: BackgroundTasks):
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=message,
            subtype="html"
        )
        fm = FastMail(EmailUtils.conf)
        background_tasks.add_task(fm.send_message, message)