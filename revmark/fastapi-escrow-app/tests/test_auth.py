from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth import create_user

client = TestClient(app)

def test_signup():
    response = client.post("/api/v1/auth/signup", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["username"] == "testuser"

def test_login():
    # First, create a user
    create_user(UserCreate(username="testuser", email="testuser@example.com", password="testpassword"))

    response = client.post("/api/v1/auth/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

def test_login_invalid_user():
    response = client.post("/api/v1/auth/login", data={
        "username": "invaliduser",
        "password": "wrongpassword"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"

def test_get_current_user():
    # First, create a user and log in to get the token
    create_user(UserCreate(username="testuser", email="testuser@example.com", password="testpassword"))
    login_response = client.post("/api/v1/auth/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]

    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "testuser"

def test_get_current_user_unauthenticated():
    response = client.get("/api/v1/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Not authenticated"