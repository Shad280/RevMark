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
    
    # Logic to save the file and return the URL
    # For example, save to a cloud storage and return the URL
    attachment_url = f"/uploads/{file.filename}"  # Placeholder for actual upload logic
    return attachment_url