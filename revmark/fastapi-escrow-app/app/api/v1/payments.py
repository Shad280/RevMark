from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.stripe_service import create_payment_intent, capture_payment, refund_payment
from app.api.deps import get_db, get_current_user

router = APIRouter()

@router.post("/create", response_model=PaymentResponse)
async def create_payment(payment: PaymentCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
        payment_intent = await create_payment_intent(payment.amount, payment.currency, current_user)
        return PaymentResponse(client_secret=payment_intent['client_secret'])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/capture/{payment_intent_id}", response_model=PaymentResponse)
async def capture_payment_route(payment_intent_id: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
        payment = await capture_payment(payment_intent_id)
        return PaymentResponse(client_secret=payment['client_secret'])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/refund/{payment_intent_id}", response_model=PaymentResponse)
async def refund_payment_route(payment_intent_id: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
        refund = await refund_payment(payment_intent_id)
        return PaymentResponse(client_secret=refund['client_secret'])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))