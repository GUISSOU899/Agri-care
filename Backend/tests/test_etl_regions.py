from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Region, Crop
from app.etl.run_etl import load_regions_from_csv, create_default_crops

# Use a separate test database or just the main one if we are careful?
# For simplicity in this env, we test against the main DB but we rely on the fact 
# that load_regions_from_csv is idempotent (upsert).

def test_load_regions_from_csv():
    engine = create_engine(settings.DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        # Run the loader
        load_regions_from_csv(db)
        
        # Verify
        regions = db.query(Region).all()
        assert len(regions) >= 7, "Should have loaded at least 7 regions from CSV"
        
        # Check specific region
        marrakech = db.query(Region).filter_by(name="Marrakech").first()
        assert marrakech is not None
        assert abs(marrakech.latitude - 31.6295) < 0.0001
        
    finally:
        db.close()

def test_create_default_crops():
    engine = create_engine(settings.DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        create_default_crops(db)
        
        crops = db.query(Crop).all()
        assert len(crops) >= 4
        
        wheat = db.query(Crop).filter_by(name="Wheat").first()
        assert wheat is not None
        
    finally:
        db.close()
