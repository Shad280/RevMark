from pytest import fixture
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db, SessionLocal

@fixture(scope="module")
def test_client():
    client = TestClient(app)
    yield client

@fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()

def override_get_db():
    return db_session()

app.dependency_overrides[get_db] = override_get_db