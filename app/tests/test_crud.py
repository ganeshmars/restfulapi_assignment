import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models, schemas, crud
from app.database import Base
from app.auth import get_password_hash

# Set up an in-memory SQLite test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize the database
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def db_session():
    """Fixture to create a new database session for each test."""
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_create_user(db_session):
    """Test creating a new user."""
    user_data = schemas.UserCreate(
        username="testuser",
        email="testuser@example.com",
        password="testpassword"
    )
    user = crud.create_user(db=db_session, user=user_data)
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"
    assert user.hashed_password != "testpassword"  # Password should be hashed

def test_create_user_existing_email(db_session):
    """Test creating a user with an existing email raises ValueError."""
    user_data = schemas.UserCreate(
        username="testuser2",
        email="testuser@example.com",  # Reusing email from the previous test
        password="anotherpassword"
    )
    with pytest.raises(ValueError):
        crud.create_user(db=db_session, user=user_data)

def test_get_user_by_username(db_session):
    """Test retrieving a user by username."""
    user = crud.get_user_by_username(db=db_session, username="testuser")
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"

def test_get_user_by_email(db_session):
    """Test retrieving a user by email."""
    user = crud.get_user_by_email(db=db_session, email="testuser@example.com")
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"

def test_get_users(db_session):
    """Test retrieving multiple users with pagination."""
    # Add additional user for testing pagination
    user_data = schemas.UserCreate(
        username="testuser3",
        email="testuser3@example.com",
        password="password3"
    )
    crud.create_user(db=db_session, user=user_data)

    users = crud.get_users(db=db_session, skip=0, limit=2)
    assert len(users) == 2
    assert users[0].username == "testuser"
    assert users[1].username == "testuser3"

def test_update_user(db_session):
    """Test updating an existing user's information."""
    user_update_data = schemas.UserUpdate(
        first_name="Updated",
        last_name="User",
        is_active=False
    )
    updated_user = crud.update_user(db=db_session, user_id=1, user_update=user_update_data)
    assert updated_user is not None
    assert updated_user.first_name == "Updated"
    assert updated_user.last_name == "User"
    assert updated_user.is_active is False
