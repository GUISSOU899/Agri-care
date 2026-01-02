import argparse
import random
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import WeatherDaily, Region

def seed_weather(start_year: int, end_year: int):
    db = SessionLocal()
    try:
        regions = db.query(Region).all()
        print(f"Seeding historical weather for {start_year}-{end_year} for {len(regions)} regions...")
        
        start_date = date(start_year, 1, 1)
        end_date = date(end_year, 12, 31)
        
        current = start_date
        records_added = 0
        while current <= end_date:
            for region in regions:
                # Check exist
                existing = db.query(WeatherDaily).filter(
                    WeatherDaily.region_id == region.id,
                    WeatherDaily.date == current
                ).first()
                
                if not existing:
                    # Mock weather
                    month = current.month
                    # Simple seasonal temp: max in July (month 7), min in Jan (month 1)
                    temp_base = 20 + 10 * random.uniform(-0.5, 0.5) 
                    # Add seasonal variation
                    temp_seasonal = 5 * (6 - abs(month - 7)) # roughly 0 in Jan/Dec, 30 in July
                    tavg = 10 + temp_seasonal + random.uniform(-2, 2)
                    tmax = tavg + random.uniform(2, 8)
                    tmin = tavg - random.uniform(2, 8)
                    precip = random.choice([0, 0, 0, 0, random.uniform(0, 10)]) # 20% rain chance
                    
                    db.add(WeatherDaily(
                        region_id=region.id,
                        date=current,
                        tavg=tavg,
                        tmax=tmax,
                        tmin=tmin,
                        precipitation=precip
                    ))
                    records_added += 1
            
            if current.day == 1:
                db.commit()
                print(f"  Processed {current}")
            
            current += timedelta(days=1)
            
        db.commit()
        print(f"Added {records_added} historical weather records.")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=2023)
    parser.add_argument("--end", type=int, default=2024)
    args = parser.parse_args()
    seed_weather(args.start, args.end)
