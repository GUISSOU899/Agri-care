import csv
import os
import app.db.base  # ✅ DOIT être importé avant les requêtes SQLAlchemy
from pathlib import Path
from datetime import date
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ✅ IMPORTANT: enregistre tous les modèles (Crop, Forecast, etc.) dans SQLAlchemy
import app.db.base  # noqa
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
    # Fields must match Crop model: name, type, water_need, temp_low, temp_high, rain_threshold
    default_crops = [
        {"name": "Wheat", "type": "Cereal", "water_need": 4.0, "temp_low": 5, "temp_high": 35, "rain_threshold": 20},
        {"name": "Corn", "type": "Cereal", "water_need": 6.0, "temp_low": 10, "temp_high": 40, "rain_threshold": 30},
        {"name": "Olive", "type": "Tree", "water_need": 2.5, "temp_low": -5, "temp_high": 45, "rain_threshold": 10},
        {"name": "Tomato", "type": "Vegetable", "water_need": 5.0, "temp_low": 10, "temp_high": 35, "rain_threshold": 25},
    ]
    
    for c in default_crops:
        db.add(Crop(
            name=c["name"], 
            type=c["type"], 
            water_need=c["water_need"],
            temp_low=c["temp_low"],
            temp_high=c["temp_high"],
            rain_threshold=c["rain_threshold"]
        ))
    db.commit()
    print("Default crops created.")

def run_etl():
    """Run full ETL pipeline."""
    with SessionLocal() as db:
        try:
            print("Starting ETL / Seeding...")
            # 1. Load Regions
            load_regions_from_csv(db)
            
            # 2. Ensure Crops exist
            create_default_crops(db)
            
            # 3. Run Seeds (Idempotent)
            from app.db.seeds import seed_realistic_crops, seed_season_calendar, seed_users
            seed_users(db)
            seed_realistic_crops(db)
            seed_season_calendar(db)
            
            # 4. Load Weather for each region
            regions = db.query(Region).all()
            print(f"Fetching weather data for {len(regions)} regions...")
            
            for region in regions:
                try:
                    records = fetch_daily_weather(region.latitude, region.longitude, date.today(), date.today() + relativedelta(days=30))
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
            
            # 5. Update Forecasts (30 days)
            print("Updating Forecasts (30 days)...")
            from app.etl.update_forecast_30d import update_forecasts_30d
            update_forecasts_30d()
            print("ETL process completed successfully.")
            
        except Exception as e:
            print(f"ETL failed: {e}")
            db.rollback()


if __name__ == "__main__":
    run_etl()
