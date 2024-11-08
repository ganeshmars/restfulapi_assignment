import pytest
from datetime import timedelta
from jose import jwt
from app.auth import (
    authenticate_user,
    create_access_token,
    verify_password,
    get_current_user
)
from app.schemas import TokenData
from app import models
from app.database import get_db
from app.utils import get_password_hash

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@pytest.fixture
def db_session():
    # Mock the DB session or use an in-memory test DB if needed
    # For now, we will mock it in each function where applicable
    pass

def test_verify_password():
    password = "testpassword"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)
    assert not verify_password("wrongpassword", hashed_password)

def test_get_password_hash():
    password = "testpassword"
    hashed_password = get_password_hash(password)
    assert hashed_password != password  # Password should be hashed
    assert verify_password(password, hashed_password)  # It should match when verified

def test_create_access_token():
    data = {"sub": "testuser"}
    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data=data, expires_delta=expires)
    decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_data.get("sub") == "testuser"
    assert "exp" in decoded_data

def test_authenticate_user(mocker):
    # Mock the user returned by crud.get_user_by_username
    user = models.User(username="testuser", hashed_password=get_password_hash("testpassword"))
    mocker.patch("app.crud.get_user_by_username", return_value=user)

    # Test successful authentication
    db = mocker.MagicMock()
    assert authenticate_user(db, "testuser", "testpassword") == user

    # Test failed authentication with wrong password
    assert not authenticate_user(db, "testuser", "wrongpassword")

    # Test failed authentication with non-existent user
    mocker.patch("app.crud.get_user_by_username", return_value=None)
    assert not authenticate_user(db, "nonexistent", "testpassword")

def test_get_current_user(mocker):
    # Mock the token payload and database
    user_data = {"username": "testuser", "hashed_password": get_password_hash("testpassword")}
    user = models.User(**user_data)
    db = mocker.MagicMock()

    # Mock `get_user` to return the expected user
    mocker.patch("app.auth.get_user", return_value=user)
    token_data = {"sub": "testuser"}
    token = create_access_token(data=token_data)

    # Test valid token
    result = get_current_user(db, token=token)
    assert result.username == "testuser"

    # Test invalid token (wrong secret)
    with pytest.raises(Exception):
        invalid_token = jwt.encode({"sub": "testuser"}, "wrong_secret", algorithm=ALGORITHM)
        get_current_user(db, token=invalid_token)

    # Test token with no user found in DB
    mocker.patch("app.auth.get_user", return_value=None)
    with pytest.raises(Exception):
        get_current_user(db, token=token)
