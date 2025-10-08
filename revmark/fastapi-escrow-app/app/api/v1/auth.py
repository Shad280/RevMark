from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut
from app.services.auth import create_user, authenticate_user
from app.core.database import get_db

router = APIRouter()

@router.post("/signup", response_model=UserOut)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db=db, user=user)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User already exists")
    return db_user

@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    access_token = authenticate_user(db=db, email=user.email, password=user.password)
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": access_token, "token_type": "bearer"}