import math
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Region, ClimatologyDaily
from app.db.session import SessionLocal

def build_synthetic_climatology():
    """
    Populates climatology_daily with synthetic data respecting Moroccan seasonality.
    """
    db = SessionLocal()
    try:
        regions = db.query(Region).all()
        if not regions:
            print("No regions found.")
            return

        db.query(ClimatologyDaily).delete() # Refresh
        
        objects = []
        for region in regions:
            print(f"Building climatology for {region.name}...")
            # Base temperature varies by region (dummy logic)
            # Coastal (Tanger, Casa, Rabat, Agadir) vs Inland (Marrakech, Fes, Oujda)
            is_coastal = region.name in ["Tanger", "Casablanca", "Rabat", "Agadir"]
            
            base_mean = 20.0 if is_coastal else 22.0
            amp = 8.0 if is_coastal else 15.0 # Inland has more variance
            
            for doy in range(1, 367):
                # Peak heat in July (approx day 200)
                # Cosine wave: -cos((doy - 20) / 365 * 2pi) has peak around day 200
                season = -math.cos((doy - 20) / 365.0 * 2 * math.pi)
                
                tmean = base_mean + (season * amp)
                tmax = tmean + (5 if is_coastal else 8)
                tmin = tmean - (5 if is_coastal else 8)
                
                # Cap winter max (DOY < 60 or DOY > 330)
                if doy < 60 or doy > 330:
                     if tmax > 28.0: tmax = 28.0 # Strict cap for baseline
                
                # Rain: Peak in winter (Nov-Mar)
                # Inverted season curve roughly
                rain_prob = max(0, -season) # High in winter, low in summer
                rain_amount = rain_prob * (2.0 if is_coastal else 1.5) # Average daily mm
                
                # Add some randomness for std dev simulation? No, just clean baseline.
                
                obj = ClimatologyDaily(
                    region_id=region.id,
                    day_of_year=doy,
                    tmin_c=round(tmin, 1),
                    tmax_c=round(tmax, 1),
                    rainfall_mm=round(rain_amount, 1),
                    std_t=2.0,
                    std_r=5.0
                )
                objects.append(obj)
        
        db.bulk_save_objects(objects)
        db.commit()
        print(f"Inserted {len(objects)} climatology rows.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    build_synthetic_climatology()
