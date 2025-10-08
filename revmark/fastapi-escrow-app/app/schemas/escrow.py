from pydantic import BaseModel
from typing import Optional

class EscrowCreate(BaseModel):
    title: str
    description: str
    budget: float
    buyer_id: int
    seller_id: int

class EscrowUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[float] = None
    status: Optional[str] = None

class EscrowResponse(BaseModel):
    id: int
    title: str
    description: str
    budget: float
    buyer_id: int
    seller_id: int
    payment_intent_id: Optional[str] = None
    status: str

    class Config:
        orm_mode = True