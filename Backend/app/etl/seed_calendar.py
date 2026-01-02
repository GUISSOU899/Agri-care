import argparse
from datetime import date
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.seasonal import SeasonCalendar
from app.models import Region, Crop

def seed_calendar(year: int):
    db = SessionLocal()
    try:
        regions = db.query(Region).all()
        crops = db.query(Crop).all()
        
        print(f"Seeding default season calendar for {year}...")
        
        for region in regions:
            for crop in crops:
                # Check exist
                existing = db.query(SeasonCalendar).filter(
                    SeasonCalendar.region_id == region.id,
                    SeasonCalendar.crop_id == crop.id,
                    SeasonCalendar.season_year == year
                ).first()
                
                if not existing:
                    # Defaulting to some dates
                    # Wheat: Sown in Nov, Harvest in May
                    if "wheat" in crop.name.lower():
                        sow = date(year-1, 11, 15)
                        harv = date(year, 5, 20)
                    # Corn: Sown in April, Harvest in Sept
                    elif "corn" in crop.name.lower():
                        sow = date(year, 4, 1)
                        harv = date(year, 9, 15)
                    else:
                        sow = date(year, 2, 1)
                        harv = date(year, 7, 1)
                        
                    db.add(SeasonCalendar(
                        region_id=region.id,
                        crop_id=crop.id,
                        season_year=year,
                        sowing_date=sow,
                        harvest_date=harv,
                        notes="Auto-generated default"
                    ))
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2024)
    args = parser.parse_args()
    seed_calendar(args.year)
