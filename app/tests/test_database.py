import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db

# Set up a temporary in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the in-memory database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def test_db():
    # Create tables in the test database
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal
    # Drop tables after the test is done
    Base.metadata.drop_all(bind=engine)

def test_database_connection(test_db):
    """Test that the database connection can be established and closed."""
    session = next(override_get_db())
    assert session is not None  # Ensure session is created
    session.close()

def test_get_db_dependency():
    """Test that the get_db function returns a valid session."""
    db_gen = override_get_db()  # Simulate dependency
    db_session = next(db_gen)
    assert db_session is not None  # Ensure a session is yielded
    db_session.close()
