from datetime import datetime
import pytest
from app import schemas

def test_user_base_model():
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User",
        "gender": "Other"
    }
    user = schemas.UserBase(**user_data)
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.gender == "Other"

def test_user_create_model():
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "User"
    }
    user = schemas.UserCreate(**user_data)
    assert user.password == "testpassword"

def test_user_in_db_model():
    user_data = {
        "id": 1,
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "is_active": True,
        "is_admin": False,
        "first_name": "Test",
        "last_name": "User",
        "gender": "Other",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    user = schemas.UserInDB(**user_data)
    assert user.id == 1
    assert user.is_active is True
    assert user.is_admin is False
    assert user.created_at is not None
    assert user.updated_at is not None

from pydantic import ValidationError

def test_user_update_model():
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "first_name": "New",
        "last_name": "User",
        "is_active": False,
        "is_admin": True
    }
    try:
        user = schemas.UserUpdate(**user_data)
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.first_name == "New"
        assert user.last_name == "User"
        assert user.is_active is False
        assert user.is_admin is True
    except ValidationError as e:
        # Print detailed JSON error message from Pydantic
        print("Validation error details:", e.json())
        assert False, f"Unexpected validation error: {e}"
    except Exception as e:
        # General error handling, if any other exception occurs
        print("Unexpected error:", str(e))
        assert False, f"Unexpected error: {e}"



def test_user_out_model():
    user_data = {
        "id": 1,
        "username": "testuser",
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "gender": "Other",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True,
        "is_admin": False
    }
    user = schemas.UserOut(**user_data)
    assert user.id == 1
    assert user.username == "testuser"
    assert user.is_active is True
    assert user.is_admin is False

def test_token_model():
    token_data = {
        "access_token": "testtoken123",
        "token_type": "bearer"
    }
    token = schemas.Token(**token_data)
    assert token.access_token == "testtoken123"
    assert token.token_type == "bearer"

def test_token_data_model():
    token_data = {
        "username": "testuser"
    }
    token_data_model = schemas.TokenData(**token_data)
    assert token_data_model.username == "testuser"
