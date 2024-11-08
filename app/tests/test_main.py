import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User  # Import the User model to clear records

# Use a file-based SQLite database for persistence across test functions
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the file-based test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Set up test client
client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Set up the database before any tests run, and clean up after all tests."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables and close the engine after all tests
    Base.metadata.drop_all(bind=engine)
    engine.dispose()  # Explicitly close the database connection
    try:
        os.remove("./test_database.db")
    except PermissionError:
        pass  # Ignore the error if the file is still in use

@pytest.fixture(autouse=True)
def setup_function():
    """Clear the User table before each test to ensure isolation."""
    db = TestingSessionLocal()
    db.query(User).delete()
    db.commit()
    db.close()

@pytest.fixture
def create_and_login_user():
    """Create a new user, return user data and an authorization token."""
    user_data = {
        "username": "testuser_" + os.urandom(4).hex(),
        "email": f"{os.urandom(4).hex()}@example.com",
        "password": "password123"
    }
    client.post("/users/", json=user_data)
    response = client.post("/token", data={"username": user_data["username"], "password": user_data["password"]})
    assert response.status_code == 200, "User login failed with 401 error"
    token = response.json()["access_token"]
    return user_data, f"Bearer {token}"

def test_create_user():
    response = client.post(
        "/users/",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data

def test_login_for_access_token(create_and_login_user):
    user_data, _ = create_and_login_user
    response = client.post("/token", data={"username": user_data["username"], "password": user_data["password"]})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_read_users(create_and_login_user):
    _, token = create_and_login_user
    response = client.get("/users/", headers={"Authorization": token})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_read_user(create_and_login_user):
    user_data, token = create_and_login_user
    response = client.get("/users/1", headers={"Authorization": token})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]


def test_update_user(create_and_login_user):
    user_data, token = create_and_login_user

    # Full payload with all fields to match `UserUpdate` schema
    update_data = {
        "username": user_data["username"],
        "email": "updateduser@example.com",
        "first_name": "Updated",
        "last_name": "User",
        "gender": "Non-binary",
        "is_active": True,
        "is_admin": False
    }

    response = client.put(f"/users/1", headers={"Authorization": token}, json=update_data)

    if response.status_code != 200:
        print("Validation error details:", response.json())  # Log error details for further insights

    assert response.status_code == 200  # Expecting success with a complete payload
    data = response.json()
    assert data["email"] == "updateduser@example.com"
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "User"


def test_unauthorized_access():
    response = client.get("/users/1")
    assert response.status_code == 401
