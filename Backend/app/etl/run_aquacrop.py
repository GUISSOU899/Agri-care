import argparse
import random
import json
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.seasonal import AquaCropSim, SeasonCalendar
from app.models import Region, Crop

def run_aquacrop_sim(mode: str, year: int):
    db = SessionLocal()
    try:
        print(f"Running AquaCrop simulation in {mode} mode for {year}...")
        
        calendars = db.query(SeasonCalendar).filter(SeasonCalendar.season_year == year).all()
        
        for cal in calendars:
            if mode == "mock":
                # Generate realistic-looking yield (t/ha)
                # Base 5-10 t/ha, maybe crop dependent
                base = 6.0 if "wheat" in cal.crop.name.lower() else 8.0
                yield_val = base + random.uniform(-2, 2)
                params = {"sim_status": "success", "engine": "mock_v1"}
            else:
                # Real implementation would call aquacrop library
                # from aquacrop import AquaCropModel...
                print("Real AquaCrop mode not fully implemented (requires soil/crop params), using mock.")
                yield_val = 5.5 + random.uniform(-1, 1)
                params = {"engine": "aquacrop_stub"}
            
            # Upsert
            existing = db.query(AquaCropSim).filter(
                AquaCropSim.region_id == cal.region_id,
                AquaCropSim.crop_id == cal.crop_id,
                AquaCropSim.season_year == year
            ).first()
            
            if existing:
                existing.simulated_yield_t_ha = yield_val
                existing.params_json = params
            else:
                db.add(AquaCropSim(
                    region_id=cal.region_id,
                    crop_id=cal.crop_id,
                    season_year=year,
                    simulated_yield_t_ha=yield_val,
                    params_json=params
                ))
        
        db.commit()
        print("AquaCrop simulations completed.")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, choices=["mock", "real"], default="mock")
    parser.add_argument("--year", type=int, default=2024)
    args = parser.parse_args()
    run_aquacrop_sim(args.mode, args.year)
