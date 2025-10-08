from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.file_upload import upload_file_to_storage

router = APIRouter()

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")
    
    try:
        file_url = await upload_file_to_storage(file)
        return JSONResponse(content={"file_url": file_url}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))