from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.core.database import get_db
from app.core.security import hash_password, verify_password
from app.utils.email import send_verification_email

async def register_user(user: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    send_verification_email(new_user.email)
    return UserOut.from_orm(new_user)

async def authenticate_user(email: str, password: str, db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user