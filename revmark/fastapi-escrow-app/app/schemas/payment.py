from pydantic import BaseModel, Field
from typing import Optional

class PaymentCreate(BaseModel):
    amount: float = Field(..., gt=0, description="The amount to be charged")
    currency: str = Field(..., description="The currency for the payment")
    description: Optional[str] = Field(None, description="Description of the payment")
    payment_method_id: str = Field(..., description="The payment method ID from Stripe")

class PaymentResponse(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    description: Optional[str]

class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    status: str