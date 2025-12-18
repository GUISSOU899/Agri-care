import random
from datetime import date, timedelta
import math
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import Region, Crop, Forecast

# Database setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def generate_weather_data(day_offset: int):
    """Generate somewhat realistic weather data using sine waves + noise."""
    # Simulate seasonal curve
    base_temp = 20 + 10 * math.sin(day_offset / 30)
    temperature = base_temp + random.uniform(-2, 2)
    
    # Deterministic Heat Wave for testing: Every 5th and 15th day
    # But only if it makes sense seasonally? Or we let sanity check catch it?
    # Let sanity check catch it.
    if day_offset == 5 or day_offset == 15:
        temperature = 42.0 # Critical Heat (Will be capped by sanity check in winter)

    # Random rainfall
    rainfall = 0.0
    if random.random() > 0.7: 
        rainfall = random.uniform(1, 10)

    # Deterministic Heavy Rain: Every 10th day
    if day_offset == 10:
        rainfall = 45.0 # Heavy Rain
        
    # ET based loosely on temp
    evapotranspiration = max(0, (temperature / 5) + random.uniform(-1, 1))

    return round(temperature, 1), round(rainfall, 1), round(evapotranspiration, 1)

def generate_mock_forecasts():
    db = SessionLocal()
    try:
        regions = db.query(Region).all()
        crops = db.query(Crop).all()

        if not regions:
            print("No regions found. Run ETL first.")
            return
        if not crops:
            # Create a default crop if none exist
            print("No crops found. Creating default 'Wheat'.")
            wheat = Crop(name="Wheat", code="wheat", description="Winter wheat")
            db.add(wheat)
            db.commit()
            db.refresh(wheat)
            crops = [wheat]

        print(f"Generating forecasts for {len(regions)} regions and {len(crops)} crops...")

        for region in regions:
            for crop in crops:
                # Generate 30 days of forecast
                today = date.today()
                
                # Cleanup existing forecasts for this pair to avoid duplicates in this demo script
                db.query(Forecast).filter(
                    Forecast.region_id == region.id,
                    Forecast.crop_id == crop.id,
                    Forecast.date >= today
                ).delete()

                for i in range(30):
                    forecast_date = today + timedelta(days=i)
                    raw_temp, raw_rain, raw_et = generate_weather_data(i)
                    
                    from app.core.forecast_sanity import sanitize_forecast
                    
                    # Sanitize
                    temp, rain = sanitize_forecast(raw_temp, raw_rain, forecast_date)

                    # Recalculate ET if temp changed significantly? 
                    # For simplicity, let's just clamp ET too or recompute
                    et = max(0, (temp / 5) + random.uniform(-1, 1))

                    # Yield index simulation: slowly increasing or random
                    yield_index = 100 + (math.sin(i/10) * 10) + random.uniform(-2, 2)
                    
                    forecast = Forecast(
                        region_id=region.id,
                        crop_id=crop.id,
                        date=forecast_date,
                        horizon_days=i,
                        yield_index=round(yield_index, 2),
                        temperature_c=temp,
                        rainfall_mm=rain,
                        evapotranspiration_mm=round(et, 1)
                    )
                    db.add(forecast)
        
        db.commit()
        print("Mock forecast generation completed successfully.")

    except Exception as e:
        print(f"Error generating mock forecasts: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_mock_forecasts()
