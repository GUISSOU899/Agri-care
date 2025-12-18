from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Region, Crop, Forecast, Alert
from datetime import date

def debug_db():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    print("--- REGIONS ---")
    regions = db.query(Region).all()
    for r in regions:
        print(f"ID: {r.id}, Name: {r.name}")

    print("\n--- CROPS ---")
    crops = db.query(Crop).all()
    for c in crops:
        print(f"ID: {c.id}, Name: {c.name}")

    print("\n--- FORECASTS (Sample) ---")
    # Check for extreme weather
    extreme = db.query(Forecast).filter(Forecast.temperature_c > 40).all()
    print(f"Found {len(extreme)} forecasts with Temp > 40C")
    if extreme:
        f = extreme[0]
        print(f"Sample: Region {f.region_id}, Crop {f.crop_id}, Date {f.date}, Temp {f.temperature_c}")

    print("\n--- ALERTS ---")
    alerts = db.query(Alert).all()
    print(f"Total Alerts: {len(alerts)}")
    for a in alerts:
        print(f"ID: {a.id}, Region: {a.region_id}, Crop: {a.crop_id}, Type: {a.alert_type}, Severity: {a.severity}")

if __name__ == "__main__":
    debug_db()
