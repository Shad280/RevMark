from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.schemas.message import MessageCreate, MessageResponse
from app.models.message import Message
from app.core.database import get_db
from app.services.message import send_message, get_messages

router = APIRouter()

@router.post("/", response_model=MessageResponse)
async def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    return await send_message(message, db)

@router.get("/{user_id}", response_model=list[MessageResponse])
async def read_messages(user_id: int, db: Session = Depends(get_db)):
    messages = await get_messages(user_id, db)
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found")
    return messages

@router.post("/upload/", response_model=MessageResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Logic to handle file upload and create a message with the file URL
    file_url = await handle_file_upload(file)  # Implement this function in your file_upload service
    message = MessageCreate(content="File uploaded", attachment_url=file_url)
    return await send_message(message, db)