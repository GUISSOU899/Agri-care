from sqlalchemy.orm import Session
from app.models.crop import Crop
from app.models.region import Region
from app.models.seasonal import SeasonCalendar
from datetime import date

def seed_realistic_crops(db: Session):
    """
    Seed realistic crop data. Idempotent.
    """
    print("Seeding realistic crops...")
    crops_data = [
        {
            "name": "Wheat",
            "type": "Cereal",
            "variety": "Winter Wheat",
            "water_need": 1.0,
            "temp_low": 5.0,
            "temp_high": 35.0,
            "rain_threshold": 5.0  # gt=0
        },
        {
            "name": "Corn",
            "type": "Cereal",
            "variety": "Sweet Corn",
            "water_need": 1.2,
            "temp_low": 10.0,
            "temp_high": 38.0,
            "rain_threshold": 6.0
        },
        {
            "name": "Olive",
            "type": "Tree",
            "variety": "Picholine",
            "water_need": 0.7,
            "temp_low": 2.0,
            "temp_high": 40.0,
            "rain_threshold": 2.0
        },
        {
            "name": "Tomato",
            "type": "Vegetable",
            "variety": "Roma",
            "water_need": 1.1,
            "temp_low": 10.0,
            "temp_high": 35.0,
            "rain_threshold": 4.0
        },
    ]

    for data in crops_data:
        crop = db.query(Crop).filter(Crop.name == data["name"]).first()
        if crop:
            # Update
            crop.type = data["type"]
            crop.variety = data["variety"]
            crop.water_need = data["water_need"]
            crop.temp_low = data["temp_low"]
            crop.temp_high = data["temp_high"]
            crop.rain_threshold = data["rain_threshold"]
        else:
            # Insert
            db.add(Crop(**data))
    
    db.commit()
    print("Crops seeded.")

def seed_season_calendar(db: Session):
    """
    Ensure season calendar exists for all regions/crops for current and next year.
    """
    print("Seeding season calendar...")
    regions = db.query(Region).all()
    crops = db.query(Crop).all()
    
    current_year = date.today().year
    years = [current_year, current_year + 1]

    # Baseline windows (month-day)
    calendar_specs = {
        "Wheat": {"sow": (11, 1), "harv": (5, 31)},   # Winter -> Spring
        "Corn": {"sow": (4, 1), "harv": (9, 30)},     # Spring -> Autumn
        "Olive": {"sow": (3, 1), "harv": (11, 30)},   # Long season
        "Tomato": {"sow": (2, 1), "harv": (6, 30)},   # Spring
    }

    count = 0
    for r in regions:
        for c in crops:
            spec = calendar_specs.get(c.name, {"sow": (1, 1), "harv": (12, 31)})
            
            for y in years:
                # Calculate dates
                sow_date = date(y, *spec["sow"])
                harv_date = date(y, *spec["harv"])
                
                # Handle year crossover for harvest if needed (e.g. sow Nov, harv May next year)
                # But here we simplify: if harvest month < sow month, harvest is next year relative to sow?
                # Actually season_year usually denotes the harvest year or the main growing year.
                # Let's assume sow is in 'y' or 'y-1' depending on logic.
                # For Wheat (Nov-May), if season_year=2025, sow=Nov 2024, harv=May 2025.
                # For simplicity in this PFA context, we set sow/harv in the same calendar year 'y' unless specific logic.
                # Except Wheat which is winter.
                
                final_sow = sow_date
                final_harv = harv_date
                
                if c.name == "Wheat":
                    # Wheat harvested in May 2025 was sown in Nov 2024
                    final_sow = date(y-1, *spec["sow"])
                    final_harv = date(y, *spec["harv"])
                
                existing = db.query(SeasonCalendar).filter_by(
                    region_id=r.id, crop_id=c.id, season_year=y
                ).first()
                
                if not existing:
                    sc = SeasonCalendar(
                        region_id=r.id,
                        crop_id=c.id,
                        season_year=y,
                        sowing_date=final_sow,
                        harvest_date=final_harv,
                        notes=f"Auto-seeded {c.name} calendar for {y}"
                    )
                    db.add(sc)
                    count += 1
    
    db.commit()
    db.commit()
    print(f"Season calendar seeded: {count} entries added.")

def seed_users(db: Session):
    """
    Seed default admin user.
    """
    from app.models.user import User
    from app.core.config import settings
    from app.core.security import get_password_hash
    
    print("Seeding users...")
    user = db.query(User).filter(User.email == settings.DEFAULT_ADMIN_EMAIL).first()
    if not user:
        print(f"Creating default admin: {settings.DEFAULT_ADMIN_EMAIL}")
        user = User(
            email=settings.DEFAULT_ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
            role="admin",
            is_active=True
        )
        db.add(user)
        db.commit()
    else:
        print("Default admin already exists.")
