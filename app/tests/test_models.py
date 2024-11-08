import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Base
from app.database import get_db

# Set up an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture to create tables and return a session for testing
@pytest.fixture(scope="module")
def test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    # Drop tables after testing
    Base.metadata.drop_all(bind=engine)

def test_create_user(test_db):
    """Test creating a user in the database."""
    user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashedpassword123",
        first_name="Test",
        last_name="User",
        gender="Other",
        is_active=True,
        is_admin=False,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"
    assert user.hashed_password == "hashedpassword123"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.gender == "Other"
    assert user.is_active is True
    assert user.is_admin is False
    assert user.created_at is not None

def test_read_user(test_db):
    """Test reading a user from the database."""
    user = test_db.query(User).filter(User.username == "testuser").first()
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"

def test_update_user(test_db):
    """Test updating a user in the database."""
    user = test_db.query(User).filter(User.username == "testuser").first()
    user.first_name = "Updated"
    user.last_name = "Name"
    user.is_active = False
    test_db.commit()
    test_db.refresh(user)

    assert user.first_name == "Updated"
    assert user.last_name == "Name"
    assert user.is_active is False
    assert user.updated_at is not None  # Should be updated by `onupdate=func.now()`

def test_delete_user(test_db):
    """Test deleting a user from the database."""
    user = test_db.query(User).filter(User.username == "testuser").first()
    test_db.delete(user)
    test_db.commit()

    deleted_user = test_db.query(User).filter(User.username == "testuser").first()
    assert deleted_user is None
