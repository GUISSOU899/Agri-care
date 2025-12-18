import pytest
import pandas as pd
import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models.weather import Region, WeatherDaily
from app.models.yield_data import YieldHistory
from app.ml.data_loader import load_training_data
from app.ml.features import prepare_features
from app.ml.train_model import train_yield_model

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def db_session(db_engine):
    Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = Session()
    yield session
    session.close()

def test_ml_pipeline(db_session, monkeypatch):
    # 1. Setup mock data
    region = Region(name="Test Region", latitude=30.0, longitude=-5.0)
    db_session.add(region)
    db_session.commit()
    db_session.refresh(region)
    
    # Add generic weather data for multiple years/locations to ensure enough samples
    for i in range(10):
        # Create yields for 10 years
        year = 2010 + i
        # Weather
        wd = WeatherDaily(
            region_id=region.id,
            date=pd.to_datetime(f"{year}-06-01").date(),
            tavg=25.0 + i, tmin=15.0, tmax=35.0 + i, precipitation=10.0 + i
        )
        db_session.add(wd)
        
        # Yield
        yh = YieldHistory(
            region_id=region.id, crop="wheat", year=year, 
            date_harvest=pd.to_datetime(f"{year}-07-01").date(),
            yield_value=4.0 + (i*0.1), yield_index=0.5 + (i*0.05)
        )
        db_session.add(yh)
    
    db_session.commit()
    
    # Patch get_db or SessionLocal to use our test session
    # Since load_training_data uses SessionLocal inside, we need to mock it.
    
    mock_session_cls = lambda: db_session
    monkeypatch.setattr("app.ml.data_loader.SessionLocal", mock_session_cls)
    
    # 2. Test data loading
    X, y = load_training_data("wheat")
    assert not X.empty
    assert len(X) >= 5
    assert "tavg" in X.columns
    
    # 3. Test feature engineering
    X_feat = prepare_features(X)
    assert "gdd" in X_feat.columns
    
    # 4. Test training (integration)
    # Patch MLflow to avoid real file logging or at least use a tmp dir
    tmp_mlruns = "/tmp/test_mlruns"
    os.makedirs(tmp_mlruns, exist_ok=True)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", f"file://{tmp_mlruns}")
    
    # We also need to monkeypatch load_training_data to return the data we just verified,
    # or let it run (it uses the patched SessionLocal).
    # Since we patched SessionLocal in app.ml.data_loader, it should work.
    
    # But train_model imports load_training_data.
    
    try:
        train_yield_model("wheat", model_type="random_forest")
        # If no exception, it passed basic smoke test
    finally:
        if os.path.exists(tmp_mlruns):
            try:
                shutil.rmtree(tmp_mlruns)
            except:
                pass
