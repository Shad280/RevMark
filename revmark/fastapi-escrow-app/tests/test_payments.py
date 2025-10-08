from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from app.models.payment import Payment
from app.services.stripe_service import create_payment_intent, capture_payment, refund_payment

app = FastAPI()

client = TestClient(app)

def test_create_payment_intent():
    response = client.post("/api/v1/payments/create", json={"amount": 1000, "currency": "usd"})
    assert response.status_code == 200
    assert "client_secret" in response.json()

def test_capture_payment():
    payment_intent_id = "pi_123456789"  # Replace with a valid payment intent ID
    response = client.post(f"/api/v1/payments/capture/{payment_intent_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "succeeded"

def test_refund_payment():
    payment_id = "pi_123456789"  # Replace with a valid payment ID
    response = client.post(f"/api/v1/payments/refund/{payment_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "refunded"