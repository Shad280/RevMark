# -----------------------
# Common update endpoints with email notifications
# -----------------------
from fastapi import Body

# Update account info (email notification)
@app.post("/account/update")
async def update_account(username: Optional[str] = Form(None), email: Optional[str] = Form(None), db=Depends(get_db), user=Depends(current_user_dep)):
    updated = False
    if username and username != user.username:
        user.username = username
        updated = True
    if email and email != user.email:
        user.email = email
        updated = True
    if updated:
        db.add(user)
        db.commit()
        from app.utils.email import EmailUtils
        from fastapi import BackgroundTasks
        background_tasks = BackgroundTasks()
        subject = "Your RevMark account information was updated"
        body = f"<p>Hello {user.username},</p>\n<p>Your account information was updated. If you did not make this change, please contact support immediately.</p>"
        await EmailUtils.send_email(user.email, subject, body, background_tasks)
        await background_tasks()
        return {"detail": "Account updated and notification sent"}
    return {"detail": "No changes made"}

# Update product/listing info (email notification)
@app.post("/requests/{request_id}/update")
async def update_request(request_id: int, title: Optional[str] = Form(None), description: Optional[str] = Form(None), db=Depends(get_db), user=Depends(current_user_dep)):
    req = db.query(RequestItem).filter(RequestItem.id == request_id).first()
    if not req:
        raise HTTPException(404, "Request not found")
    # Only buyer or seller can update
    if user.id not in [req.buyer_id, req.seller_id]:
        raise HTTPException(403, "Not authorized to update this request")
    updated = False
    if title and title != req.title:
        req.title = title
        updated = True
    if description and description != req.description:
        req.description = description
        updated = True
    if updated:
        db.add(req)
        db.commit()
        # Notify both buyer and seller
        from app.utils.email import EmailUtils
        from fastapi import BackgroundTasks
        background_tasks = BackgroundTasks()
        subject = f"Request #{req.id} information updated"
        body = f"<p>The request '<b>{req.title}</b>' was updated.</p>\n<p>Log in to your account to view the latest details.</p>"
        recipients = []
        if req.buyer_id:
            buyer = db.query(User).filter(User.id == req.buyer_id).first()
            if buyer:
                recipients.append(buyer.email)
        if req.seller_id:
            seller = db.query(User).filter(User.id == req.seller_id).first()
            if seller:
                recipients.append(seller.email)
        for email in recipients:
            await EmailUtils.send_email(email, subject, body, background_tasks)
        await background_tasks()
        return {"detail": "Request updated and notifications sent"}
    return {"detail": "No changes made"}

# Update offer info (email notification)
@app.post("/offers/{offer_id}/update")
async def update_offer(offer_id: int = Body(...), new_status: Optional[str] = Body(None), db=Depends(get_db), user=Depends(current_user_dep)):
    # This is a placeholder; actual offer model/logic may differ
    # Add your Offer model and update logic here
    # For demonstration, just send a notification
    from app.utils.email import EmailUtils
    from fastapi import BackgroundTasks
    background_tasks = BackgroundTasks()
    subject = f"Your offer (ID: {offer_id}) was updated"
    body = f"<p>Your offer (ID: {offer_id}) was updated. Status: {new_status or 'changed'}.</p>\n<p>Log in to your account to view details.</p>"
    # You should look up the offer and its owner to get the email
    # For now, just send to the current user
    await EmailUtils.send_email(user.email, subject, body, background_tasks)
    await background_tasks()
    return {"detail": "Offer updated and notification sent"}
# -----------------------
# Mark product as shipped
# -----------------------
from fastapi import status as http_status

@app.post("/requests/{request_id}/ship", status_code=http_status.HTTP_200_OK)
async def mark_as_shipped(request_id: int, db=Depends(get_db), user=Depends(current_user_dep)):
    req = db.query(RequestItem).filter(RequestItem.id == request_id).first()
    if not req:
        raise HTTPException(404, "Request not found")
    # Only seller can mark as shipped
    if req.seller_id != user.id:
        raise HTTPException(403, "Only the seller can mark as shipped")
    if req.status == "shipped":
        return {"detail": "Already marked as shipped"}
    req.status = "shipped"
    db.add(req)
    db.commit()

    # Notify buyer by email
    buyer = db.query(User).filter(User.id == req.buyer_id).first()
    if buyer:
        from app.utils.email import EmailUtils
        from fastapi import BackgroundTasks
        background_tasks = BackgroundTasks()
        subject = f"Your product has been shipped for Request #{req.id}"
        body = f"<p>Hello {buyer.username},</p>\n<p>Your product for the request '<b>{req.title}</b>' has been shipped by the seller.</p>\n<p>Log in to your account to view details and track your order.</p>"
        await EmailUtils.send_email(buyer.email, subject, body, background_tasks)
        await background_tasks()

    return {"detail": "Marked as shipped and buyer notified"}
import os
import json
import uuid
from decimal import Decimal
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import stripe
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError as JWTError

# -----------------------
# Configuration (env)
# -----------------------
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./escrow.db")
JWT_SECRET = os.getenv("JWT_SECRET", "dev_jwt_secret_change_me")
JWT_ALG = "HS256"
JWT_EXPIRE_MINUTES = 60*24*7

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
PLATFORM_FEE_PERCENT = int(os.getenv("PLATFORM_FEE_PERCENT", "5"))

if not STRIPE_API_KEY:
    print("WARNING: STRIPE_API_KEY not set. Please set it in your .env file")
else:
    stripe.api_key = STRIPE_API_KEY

# -----------------------
# Database (SQLAlchemy)
# -----------------------
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------
# Models
# -----------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    stripe_account_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class RequestItem(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    budget = Column(Integer, nullable=False)  # cents
    buyer_id = Column(Integer, ForeignKey("users.id"))
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    payment_intent_id = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, funded, captured, released, refunded
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=True)
    attachment = Column(String, nullable=True)
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# -----------------------
# Auth utilities (JWT)
# -----------------------
def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_ctx.verify(password, hashed)

def create_token(user_id: int, username: str):
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": username, "uid": user_id, "exp": expire.timestamp()}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def get_current_user(authorization: Optional[str] = None, db = None):
    if authorization is None:
        raise HTTPException(401, "Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid Authorization header format")
    
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError:
        raise HTTPException(401, "Invalid token")
    
    username = payload.get("sub")
    uid = payload.get("uid")
    if not uid or not username:
        raise HTTPException(401, "Invalid token payload")
    
    user = db.query(User).filter(User.id == int(uid)).first()
    if not user:
        raise HTTPException(401, "User not found")
    return user

# FastAPI dependency wrapper
def current_user_dep(authorization: Optional[str] = None, db=Depends(get_db)):
    return get_current_user(authorization, db)

# -----------------------
# App & Static
# -----------------------
app = FastAPI(title="RevMark Escrow + Messaging API", version="1.0.0")

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# -----------------------
# Pydantic Schemas
# -----------------------
class SignupIn(BaseModel):
    username: str
    email: str
    password: str

class LoginIn(BaseModel):
    email: str
    password: str

class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str

class CreateRequestIn(BaseModel):
    title: str
    description: Optional[str] = None
    budget: float  # dollars

class CreateIntentOut(BaseModel):
    client_secret: str
    payment_intent_id: str

class MessageOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: Optional[str]
    attachment: Optional[str]
    is_read: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

# -----------------------
# Auth routes
# -----------------------
@app.post("/auth/signup", response_model=LoginOut)
def signup(payload: SignupIn, db=Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(400, "Username already exists")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(400, "Email already exists")
    
    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_token(user.id, user.username)
    return LoginOut(
        access_token=token,
        user_id=user.id,
        username=user.username
    )

@app.post("/auth/login", response_model=LoginOut)
def login(payload: LoginIn, db=Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    
    token = create_token(user.id, user.username)
    return LoginOut(
        access_token=token,
        user_id=user.id,
        username=user.username
    )

# -----------------------
# Seller onboarding (Stripe Express)
# -----------------------
@app.post("/seller/create-account")
def create_seller_account(db=Depends(get_db), user=Depends(current_user_dep)):
    if user.stripe_account_id:
        raise HTTPException(400, "User already has a Stripe account")
    
    if not STRIPE_API_KEY:
        raise HTTPException(500, "Stripe not configured")
    
    try:
        acct = stripe.Account.create(
            type="express",
            country="US",
            email=user.email
        )
        user.stripe_account_id = acct.id
        db.add(user)
        db.commit()
        return {"account_id": acct.id}
    except stripe.error.StripeError as e:
        raise HTTPException(400, f"Stripe error: {str(e)}")

@app.get("/seller/account-link")
def create_account_link(db=Depends(get_db), user=Depends(current_user_dep)):
    if not user.stripe_account_id:
        raise HTTPException(400, "Seller does not have Stripe account. Call /seller/create-account first.")
    
    if not STRIPE_API_KEY:
        raise HTTPException(500, "Stripe not configured")
    
    try:
        account_link = stripe.AccountLink.create(
            account=user.stripe_account_id,
            refresh_url="http://localhost:8000/seller/reauth",
            return_url="http://localhost:8000/seller/onboarded",
            type="account_onboarding"
        )
        return {"url": account_link.url}
    except stripe.error.StripeError as e:
        raise HTTPException(400, f"Stripe error: {str(e)}")

# -----------------------
# Buyer: create PaymentIntent with capture_method=manual (authorization)
# -----------------------
@app.post("/payments/create-intent", response_model=CreateIntentOut)
def create_payment_intent(request_id: int = Form(...), db=Depends(get_db), user=Depends(current_user_dep)):
    req = db.query(RequestItem).filter(RequestItem.id == request_id).first()
    if not req:
        raise HTTPException(404, "Request not found")
    if req.buyer_id != user.id:
        raise HTTPException(403, "Not the buyer for this request")
    
    if req.payment_intent_id:
        try:
            pi = stripe.PaymentIntent.retrieve(req.payment_intent_id)
            return CreateIntentOut(client_secret=pi.client_secret, payment_intent_id=pi.id)
        except stripe.error.StripeError:
            pass  # Create new one if retrieval fails
    
    if not STRIPE_API_KEY:
        raise HTTPException(500, "Stripe not configured")
    
    try:
        amount = int(req.budget)  # already in cents
        pi = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method_types=["card"],
            capture_method="manual",
            metadata={"request_id": str(req.id)}
        )
        req.payment_intent_id = pi.id
        req.status = "funded"
        db.add(req)
        db.commit()
        return CreateIntentOut(client_secret=pi.client_secret, payment_intent_id=pi.id)
    except stripe.error.StripeError as e:
        raise HTTPException(400, f"Stripe error: {str(e)}")

# -----------------------
# Capture authorized payment and release funds to seller (transfer)
# -----------------------
@app.post("/payments/capture")
def capture_and_release(
    payment_intent_id: str = Form(...),
    seller_user_id: int = Form(...),
    db=Depends(get_db),
    user=Depends(current_user_dep)
):
    req = db.query(RequestItem).filter(RequestItem.payment_intent_id == payment_intent_id).first()
    if not req:
        raise HTTPException(404, "Request not found")
    if req.buyer_id != user.id:
        raise HTTPException(403, "Not authorized (only buyer can capture)")
    
    if not STRIPE_API_KEY:
        raise HTTPException(500, "Stripe not configured")
    
    # Capture payment
    try:
        pi = stripe.PaymentIntent.capture(payment_intent_id)
    except stripe.error.StripeError as e:
        raise HTTPException(400, f"Stripe capture error: {str(e)}")

    req.status = "captured"
    req.seller_id = seller_user_id
    db.add(req)
    db.commit()

    # Find seller
    seller = db.query(User).filter(User.id == seller_user_id).first()
    if not seller or not seller.stripe_account_id:
        raise HTTPException(400, "Seller not onboarded with Stripe")

    total_amount = pi.amount_received
    platform_fee = int(round(total_amount * PLATFORM_FEE_PERCENT / 100.0))
    payout_amount = total_amount - platform_fee
    if payout_amount < 0:
        payout_amount = 0

    # Create transfer
    try:
        transfer = stripe.Transfer.create(
            amount=payout_amount,
            currency=pi.currency,
            destination=seller.stripe_account_id,
            metadata={"request_id": str(req.id), "payment_intent": pi.id}
        )
    except stripe.error.StripeError as e:
        raise HTTPException(400, f"Stripe transfer error: {str(e)}")

    req.status = "released"
    db.add(req)
    db.commit()

    # Send email notification to seller about offer approval/payment release
    from app.utils.email import EmailUtils
    from fastapi import BackgroundTasks
    background_tasks = BackgroundTasks()
    subject = f"Your offer has been approved and payment released for Request #{req.id}"
    body = f"<p>Hello {seller.username},</p>\n<p>Your offer for the request '<b>{req.title}</b>' has been approved by the buyer and payment has been released to your Stripe account.</p>\n<p>Amount: <b>${payout_amount/100:.2f}</b></p>\n<p>Log in to your account for details.</p>"
    await EmailUtils.send_email(seller.email, subject, body, background_tasks)
    await background_tasks()

    return {
        "status": "released",
        "transfer_id": transfer.id,
        "platform_fee": platform_fee,
        "payout_amount": payout_amount
    }

# -----------------------
# Refund
# -----------------------
@app.post("/payments/refund")
def refund_payment(payment_intent_id: str = Form(...), db=Depends(get_db), user=Depends(current_user_dep)):
    req = db.query(RequestItem).filter(RequestItem.payment_intent_id == payment_intent_id).first()
    if not req:
        raise HTTPException(404, "Request not found")
    if req.buyer_id != user.id:
        raise HTTPException(403, "Not allowed")
    
    if not STRIPE_API_KEY:
        raise HTTPException(500, "Stripe not configured")
    
    try:
        refund = stripe.Refund.create(payment_intent=payment_intent_id)
    except stripe.error.StripeError as e:
        raise HTTPException(400, f"Stripe refund error: {str(e)}")
    
    req.status = "refunded"
    db.add(req)
    db.commit()
    return {"status": "refunded", "refund_id": refund.id}

# -----------------------
# Webhook endpoint
# -----------------------
@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    event = None
    
    if STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Webhook signature verification failed: {str(e)}")
    else:
        try:
            event = json.loads(payload)
        except Exception:
            raise HTTPException(400, "Invalid payload")
    
    # Handle events
    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})
    
    if event_type == "payment_intent.canceled":
        metadata = data.get("metadata", {})
        req_id = metadata.get("request_id")
        if req_id:
            db = SessionLocal()
            req = db.query(RequestItem).filter(RequestItem.id == int(req_id)).first()
            if req:
                req.status = "canceled"
                db.add(req)
                db.commit()
            db.close()
    
    return JSONResponse({"status": "ok"})

# -----------------------
# Messaging with file uploads
# -----------------------
@app.post("/messages", response_model=MessageOut)
async def send_message(
    receiver_id: int = Form(...),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db=Depends(get_db),
    user=Depends(current_user_dep)
):
    rec = db.query(User).filter(User.id == receiver_id).first()
    if not rec:
        raise HTTPException(404, "Receiver not found")
    
    attachment_url = None
    if file:
        if file.content_type not in ("image/png", "image/jpeg", "image/jpg", "image/webp"):
            raise HTTPException(400, "Unsupported attachment type")
        
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(400, "Attachment too large")
        
        fname = f"{uuid.uuid4().hex}_{file.filename}"
        path = os.path.join(UPLOAD_DIR, fname)
        with open(path, "wb") as f:
            f.write(contents)
        attachment_url = f"/uploads/{fname}"

    m = Message(
        sender_id=user.id,
        receiver_id=receiver_id,
        content=content,
        attachment=attachment_url
    )
    db.add(m)
    db.commit()
    db.refresh(m)

    # Send email notification to receiver
    from app.utils.email import EmailUtils
    from fastapi import BackgroundTasks
    background_tasks = BackgroundTasks()
    subject = "You have a new message on RevMark"
    body = f"<p>Hello {rec.username},</p>\n<p>You received a new message from {user.username}:</p>\n<p><b>{content}</b></p>\n<p>Log in to your account to view and reply.</p>"
    await EmailUtils.send_email(rec.email, subject, body, background_tasks)
    # Run background tasks (for FastAPI, this is usually handled by dependency injection, but we call it manually here)
    await background_tasks()
    
    return MessageOut(
        id=m.id,
        sender_id=m.sender_id,
        receiver_id=m.receiver_id,
        content=m.content,
        attachment=m.attachment,
        is_read=bool(m.is_read),
        created_at=m.created_at
    )

@app.get("/messages/inbox", response_model=List[MessageOut])
def get_inbox(db=Depends(get_db), user=Depends(current_user_dep)):
    msgs = db.query(Message).filter(Message.receiver_id == user.id).order_by(Message.created_at.desc()).all()
    return [
        MessageOut(
            id=m.id,
            sender_id=m.sender_id,
            receiver_id=m.receiver_id,
            content=m.content,
            attachment=m.attachment,
            is_read=bool(m.is_read),
            created_at=m.created_at
        )
        for m in msgs
    ]

@app.get("/messages/sent", response_model=List[MessageOut])
def get_sent(db=Depends(get_db), user=Depends(current_user_dep)):
    msgs = db.query(Message).filter(Message.sender_id == user.id).order_by(Message.created_at.desc()).all()
    return [
        MessageOut(
            id=m.id,
            sender_id=m.sender_id,
            receiver_id=m.receiver_id,
            content=m.content,
            attachment=m.attachment,
            is_read=bool(m.is_read),
            created_at=m.created_at
        )
        for m in msgs
    ]

# -----------------------
# Request management
# -----------------------
@app.post("/requests")
def create_request(
    title: str = Form(...),
    description: str = Form(""),
    budget_dollars: float = Form(...),
    db=Depends(get_db),
    user=Depends(current_user_dep)
):
    cents = int(round(budget_dollars * 100))
    r = RequestItem(
        title=title,
        description=description,
        budget=cents,
        buyer_id=user.id
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return {"id": r.id, "title": r.title, "budget": r.budget, "status": r.status}

@app.get("/requests")
def list_requests(db=Depends(get_db)):
    rs = db.query(RequestItem).order_by(RequestItem.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "budget": r.budget,
            "buyer_id": r.buyer_id,
            "seller_id": r.seller_id,
            "status": r.status,
            "payment_intent_id": r.payment_intent_id,
            "created_at": r.created_at
        }
        for r in rs
    ]

@app.get("/requests/{request_id}")
def get_request(request_id: int, db=Depends(get_db)):
    r = db.query(RequestItem).filter(RequestItem.id == request_id).first()
    if not r:
        raise HTTPException(404, "Request not found")
    
    return {
        "id": r.id,
        "title": r.title,
        "description": r.description,
        "budget": r.budget,
        "buyer_id": r.buyer_id,
        "seller_id": r.seller_id,
        "status": r.status,
        "payment_intent_id": r.payment_intent_id,
        "created_at": r.created_at
    }

# -----------------------
# File downloads
# -----------------------
@app.get("/uploads/{filename}")
def uploaded_file(filename: str):
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(404, "File not found")
    return FileResponse(path)

# -----------------------
# Health check
# -----------------------
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "RevMark Escrow API is running"}

@app.get("/")
async def root():
    return {"message": "Welcome to RevMark Escrow + Messaging API!"}