from fastapi import HTTPException
from stripe import Stripe, PaymentIntent, Account, Transfer
from app.core.config import settings

stripe = Stripe(settings.STRIPE_SECRET_KEY)

async def create_payment_intent(amount: int, currency: str, customer_id: str):
    try:
        payment_intent = PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=customer_id,
            payment_method_types=["card"],
        )
        return payment_intent
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def create_stripe_account(email: str):
    try:
        account = Account.create(
            type="express",
            country="US",
            email=email,
        )
        return account
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def create_transfer(amount: int, currency: str, destination_account_id: str):
    try:
        transfer = Transfer.create(
            amount=amount,
            currency=currency,
            destination=destination_account_id,
        )
        return transfer
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))