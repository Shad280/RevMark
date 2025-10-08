from fastapi import UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os

UPLOAD_DIRECTORY = "uploads"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

async def upload_file(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        return JSONResponse(content={"filename": file.filename}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))