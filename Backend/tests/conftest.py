import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base, get_db
from app.main import app
# Import models so Base.metadata knows about them
from app.models import Region, Crop, WeatherDaily, Forecast, Alert, YieldHistory

# Use in-memory SQLite for unrelated unit tests OR use a test DB. 
# Here using a separate test database or same logic as existing tests.
# The existing test 'test_ml_pipeline.py' used in-memory SQLite.
# We should replicate that or use a consistent approach.

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

from sqlalchemy.pool import StaticPool

@pytest.fixture(scope="session")
def db_engine():
    # Import models so Base.metadata knows about them
    import app.models  # noqa: F401
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(db_engine):
    Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture(scope="function")
def client(db) -> Generator:
    # Dependency override
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
