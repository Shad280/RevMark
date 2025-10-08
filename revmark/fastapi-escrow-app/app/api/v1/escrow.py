from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.models.escrow import RequestItem
from app.schemas.escrow import RequestItemCreate, RequestItemResponse
from app.api.deps import get_db, get_current_user
from app.services.escrow import create_request_item, get_request_items
from app.services.file_upload import upload_file_to_storage

router = APIRouter()

@router.post("/", response_model=RequestItemResponse)
async def create_escrow_request(
    request_item: RequestItemCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    return create_request_item(db=db, request_item=request_item, user_id=current_user)

@router.get("/", response_model=list[RequestItemResponse])
async def read_escrow_requests(
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    return get_request_items(db=db, user_id=current_user)

@router.post("/upload", response_model=str)
async def upload_attachment(file: UploadFile = File(...)):
    file_url = await upload_file_to_storage(file)
    if not file_url:
        raise HTTPException(status_code=400, detail="File upload failed")
    return file_url