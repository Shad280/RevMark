from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.escrow import RequestItem
from app.schemas.escrow import RequestItemCreate
from app.services.stripe_service import create_payment_intent

async def create_request_item(db: Session, request_item: RequestItemCreate, buyer_id: int, seller_id: int):
    payment_intent = await create_payment_intent(request_item.budget)
    
    if not payment_intent:
        raise HTTPException(status_code=400, detail="Failed to create payment intent")

    new_request_item = RequestItem(
        title=request_item.title,
        description=request_item.description,
        budget=request_item.budget,
        buyer_id=buyer_id,
        seller_id=seller_id,
        payment_intent_id=payment_intent.id,
        status="pending"
    )
    
    db.add(new_request_item)
    db.commit()
    db.refresh(new_request_item)
    
    return new_request_item

def get_request_item(db: Session, request_id: int):
    request_item = db.query(RequestItem).filter(RequestItem.id == request_id).first()
    if request_item is None:
        raise HTTPException(status_code=404, detail="Request item not found")
    return request_item

def update_request_item_status(db: Session, request_id: int, status: str):
    request_item = get_request_item(db, request_id)
    request_item.status = status
    db.commit()
    db.refresh(request_item)
    return request_item