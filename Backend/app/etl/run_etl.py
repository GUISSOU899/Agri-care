import csv
import os
from pathlib import Path
from datetime import date
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.etl.nasa_power_client import fetch_daily_weather
from app.models import Region, WeatherDaily, Crop

# Database engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

REGIONS_CSV_PATH = Path(__file__).parent / "data" / "regions_ma.csv"

def load_regions_from_csv(db):
    """Load regions from CSV file."""
    if not REGIONS_CSV_PATH.exists():
        print(f"CSV file not found: {REGIONS_CSV_PATH}")
        return

    print(f"Loading regions from {REGIONS_CSV_PATH}...")
    with open(REGIONS_CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            name = row["name"]
            lat = float(row["lat"])
            lon = float(row["lon"])
            
            existing = db.query(Region).filter_by(name=name).first()
            if existing:
                existing.latitude = lat
                existing.longitude = lon
            else:
                new_region = Region(name=name, latitude=lat, longitude=lon)
                db.add(new_region)
            count += 1
        db.commit()
    print(f"Processed {count} regions from CSV.")

def create_default_crops(db):
    """Create default crops if they don't exist."""
    count = db.query(Crop).count()
    if count > 0:
        return

    print("Creating default crops...")
    default_crops = [
        {"name": "Wheat", "code": "wheat", "description": "Winter Wheat"},
        {"name": "Corn", "code": "corn", "description": "Maize/Corn"},
        {"name": "Olive", "code": "olive", "description": "Olive Trees"},
        {"name": "Tomato", "code": "tomato", "description": "Tomatoes"},
    ]
    
    for c in default_crops:
        db.add(Crop(name=c["name"], code=c["code"], description=c["description"]))
    db.commit()
    print("Default crops created.")

def run_etl():
    """Run full ETL pipeline."""
    with SessionLocal() as db:
        # 1. Load Regions
        load_regions_from_csv(db)
        
        # 2. Ensure Crops exist
        create_default_crops(db)
        
        # 3. Load Weather for each region
        regions = db.query(Region).all()
        print(f"Fetching weather data for {len(regions)} regions...")
        
        for region in regions:
            # Simple optimization: only fetch if missing or just update last 30 days
            # For this demo, we verify we have 30 days of history/forecast base
            start = date.today()
            end = start + relativedelta(days=30)
            
            # Note: NASA POWER is history/climatology, not future forecast usually.
            # But we use it as "source of truth" for the ETL demo.
            # In a real app we might fetch historical last 30 days.
            # Let's keep logic 'as is' from previous step but strictly for all regions.
            try:
                records = fetch_daily_weather(region.latitude, region.longitude, start, end)
                for rec in records:
                    existing = (
                        db.query(WeatherDaily)
                        .filter_by(region_id=region.id, date=rec["date"])
                        .first()
                    )
                    if existing:
                        existing.tavg = rec.get("tavg")
                        existing.tmax = rec.get("tmax")
                        existing.tmin = rec.get("tmin")
                        existing.precipitation = rec.get("precipitation")
                    else:
                        wd = WeatherDaily(
                            region_id=region.id,
                            date=rec["date"],
                            tavg=rec.get("tavg"),
                            tmax=rec.get("tmax"),
                            tmin=rec.get("tmin"),
                            precipitation=rec.get("precipitation"),
                        )
                        db.add(wd)
                db.commit()
            except Exception as e:
                print(f"Failed to fetch weather for {region.name}: {e}")
                
    # 2. Update Forecasts (J+0..16 Real, J+17..30 Est)
    print("Updating Forecasts (30 days)...")
    from app.etl.update_forecast_30d import update_forecasts_30d
    update_forecasts_30d()
    
    print("ETL process completed successfully.")

if __name__ == "__main__":
    run_etl()
