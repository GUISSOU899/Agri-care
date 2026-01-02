from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Region, Crop, Forecast, Alert
from app.services.alert_service import generate_alerts_from_forecasts

def test_alert_generation():
    engine = create_engine(settings.DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        # Setup: Create dummy region/crop/forecast for testing
        # We assume IDs 1 exist from previous ETL, or we can fetch first.
        region = db.query(Region).first()
        crop = db.query(Crop).first()
        
        if not region or not crop:
            return # Skip if DB empty
            
        # Cleanup potential previous run data
        target_date = date.today() + timedelta(days=5)
        existing_f = db.query(Forecast).filter_by(
            region_id=region.id, crop_id=crop.id, date=target_date
        ).first()
        if existing_f:
            db.delete(existing_f)
            db.commit()
            
        # Create a "HEAT WAVE" forecast
        heat_forecast = Forecast(
            region_id=region.id,
            crop_id=crop.id,
            date=date.today() + timedelta(days=5),
            horizon_days=5,
            yield_index=100.0,
            temperature_c=42.0, # Trigger Critical
            rainfall_mm=0.0,
            evapotranspiration_mm=5.0
        )
        db.add(heat_forecast)
        db.commit()
        
        # Test Generation
        initial_count = db.query(Alert).filter(Alert.region_id == region.id).count()
        generated = generate_alerts_from_forecasts(db, region.id)
        
        # Check
        new_count = db.query(Alert).filter(Alert.region_id == region.id).count()
        assert new_count > initial_count, "Should generate new alerts"
        
        # Verify specific alert
        alert = db.query(Alert).filter(
            Alert.region_id == region.id, 
            Alert.alert_type == "Heat Wave"
        ).order_by(Alert.id.desc()).first()
        
        assert alert is not None
        assert "42.0" in alert.message
        assert alert.severity == "critical"
        
        # Cleanup
        db.delete(heat_forecast)
        db.delete(alert)
        db.commit()
        
    finally:
        db.close()
