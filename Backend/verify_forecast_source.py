from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Forecast
from datetime import date

def verify_forecasts():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    today = date.today()
    
    # Check a few rows
    forecasts = db.query(Forecast).filter(Forecast.region_id == 1, Forecast.crop_id == 1, Forecast.date >= today).order_by(Forecast.date).limit(20).all()
    
    print(f"Date       | Source | TMin | TMax | Rain")
    print(f"-----------|--------|------|------|-----")
    for f in forecasts:
        print(f"{f.date} | {f.source}    | {f.tmin_c} | {f.tmax_c} | {f.rainfall_mm}")

if __name__ == "__main__":
    verify_forecasts()
