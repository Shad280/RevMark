from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.testclient import TestClient
from app.models.message import Message
from app.schemas.message import MessageCreate
from app.services.message import send_message, get_messages
from app.core.database import SessionLocal
import pytest

app = FastAPI()

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()

@app.post("/messages/", response_model=Message)
def create_message(message: MessageCreate, db: SessionLocal = db_session):
    return send_message(db=db, message=message)

@app.get("/messages/{user_id}", response_model=list[Message])
def read_messages(user_id: int, db: SessionLocal = db_session):
    return get_messages(db=db, user_id=user_id)

def test_create_message(client):
    response = client.post("/messages/", json={"sender_id": 1, "receiver_id": 2, "content": "Hello!"})
    assert response.status_code == 200
    assert response.json()["content"] == "Hello!"

def test_read_messages(client):
    response = client.get("/messages/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Ensure the response is a list

def test_upload_file(client):
    file_content = b"test file content"
    response = client.post("/messages/upload/", files={"file": ("test.txt", file_content)})
    assert response.status_code == 200
    assert "attachment_url" in response.json()  # Check if the response contains an attachment URL

def test_invalid_message(client):
    response = client.post("/messages/", json={"sender_id": 1, "receiver_id": 2})
    assert response.status_code == 422  # Unprocessable Entity due to missing content