from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageOut
from app.core.database import get_db
from app.utils.validators import validate_image_file

async def send_message(db: Session, message_data: MessageCreate, sender_id: int, receiver_id: int) -> MessageOut:
    message = Message(**message_data.dict(), sender_id=sender_id, receiver_id=receiver_id)
    db.add(message)
    db.commit()
    db.refresh(message)
    return MessageOut.from_orm(message)

async def get_messages(db: Session, user_id: int, offset: int = 0, limit: int = 100):
    messages = db.query(Message).filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id)
    ).offset(offset).limit(limit).all()
    return messages

async def upload_attachment(file: UploadFile):
    if not validate_image_file(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")

    import boto3
    import os
    from uuid import uuid4
    from fastapi import Request

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

    file_extension = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"message-attachments/{uuid4().hex}{file_extension}"

    try:
        file.file.seek(0)
        s3_client.upload_fileobj(
            file.file,
            AWS_S3_BUCKET,
            unique_filename,
            ExtraArgs={
                "ACL": "private",
                "ContentType": file.content_type or "application/octet-stream",
                "Metadata": {
                    "original_filename": file.filename
                }
            }
        )
        s3_url = f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"
        return s3_url
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"File upload service unavailable: {str(e)}")