from fastapi.testclient import TestClient
from app.main import app
from app.models.escrow import RequestItem
from app.models.user import User
from app.schemas.escrow import EscrowCreate
from app.schemas.user import UserCreate

client = TestClient(app)

def create_test_user():
    user_data = UserCreate(username="testuser", password="testpassword", email="test@example.com")
    response = client.post("/api/v1/auth/signup", json=user_data.dict())
    return response.json()

def test_create_escrow():
    create_test_user()
    
    # Log in to get the token
    login_response = client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "testpassword"})
    token = login_response.json().get("access_token")

    escrow_data = EscrowCreate(title="Test Escrow", description="This is a test escrow", budget=100.0)
    response = client.post("/api/v1/escrow", json=escrow_data.dict(), headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 201
    assert response.json()["title"] == escrow_data.title

def test_get_escrow():
    create_test_user()
    
    # Log in to get the token
    login_response = client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "testpassword"})
    token = login_response.json().get("access_token")

    # Create an escrow first
    escrow_data = EscrowCreate(title="Test Escrow", description="This is a test escrow", budget=100.0)
    client.post("/api/v1/escrow", json=escrow_data.dict(), headers={"Authorization": f"Bearer {token}"})

    response = client.get("/api/v1/escrow", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_delete_escrow():
    create_test_user()
    
    # Log in to get the token
    login_response = client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "testpassword"})
    token = login_response.json().get("access_token")

    # Create an escrow first
    escrow_data = EscrowCreate(title="Test Escrow", description="This is a test escrow", budget=100.0)
    response = client.post("/api/v1/escrow", json=escrow_data.dict(), headers={"Authorization": f"Bearer {token}"})
    escrow_id = response.json()["id"]

    # Now delete the escrow
    delete_response = client.delete(f"/api/v1/escrow/{escrow_id}", headers={"Authorization": f"Bearer {token}"})
    
    assert delete_response.status_code == 204

def test_escrow_not_found():
    create_test_user()
    
    # Log in to get the token
    login_response = client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "testpassword"})
    token = login_response.json().get("access_token")

    # Attempt to get a non-existent escrow
    response = client.get("/api/v1/escrow/99999", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Escrow not found"