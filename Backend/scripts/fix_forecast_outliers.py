from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Forecast
from datetime import date
from app.core.forecast_sanity import sanitize_forecast

def fix_outliers():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Find future forecasts
        forecasts = db.query(Forecast).filter(Forecast.date >= date.today()).all()
        
        updated_count = 0
        
        for f in forecasts:
            original_temp = f.temperature_c
            original_rain = f.rainfall_mm
            
            new_temp, new_rain = sanitize_forecast(original_temp, original_rain, f.date)
            
            if new_temp != original_temp or new_rain != original_rain:
                print(f"Fixing outlier for {f.date} (Region {f.region_id}): Temp {original_temp}->{new_temp}, Rain {original_rain}->{new_rain}")
                f.temperature_c = new_temp
                f.rainfall_mm = new_rain
                updated_count += 1
                
        db.commit()
        print(f"Repair complete. Fixed {updated_count} rows.")
        
    except Exception as e:
        print(f"Error during repair: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_outliers()
