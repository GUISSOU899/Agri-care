import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.seasonal import NDVITimeseries, SeasonCalendar
from app.models import Region, Crop

def generate_mock_ndvi(date_obj, region_id, crop_id):
    """Generates a realistic NDVI curve based on day of year."""
    doy = date_obj.timetuple().tm_yday
    # NDVI typically peaks in mid-season
    # Base NDVI ~0.2 (soil), peak ~0.8
    # Simple bell curve centered around doy 150 (example)
    center = 150 + (region_id % 3) * 20
    std = 40
    val = 0.2 + 0.6 * np.exp(-0.5 * ((doy - center) / std) ** 2)
    # Add noise
    val += np.random.normal(0, 0.03)
    return np.clip(val, 0.1, 0.9)

def fetch_ndvi(mode: str, start_date: str, end_date: str):
    db = SessionLocal()
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        regions = db.query(Region).all()
        crops = db.query(Crop).all()
        
        print(f"Fetching NDVI in {mode} mode from {start} to {end}...")
        
        records_added = 0
        current = start
        while current <= end:
            # For each region/crop
            for region in regions:
                for crop in crops:
                    if mode == "mock":
                        ndvi_val = generate_mock_ndvi(current, region.id, crop.id)
                        source = "mock"
                    else:
                        # Real implementation would use SentinelHub/GEE
                        print("Real mode not fully implemented (requires credentials), falling back to mock.")
                        ndvi_val = generate_mock_ndvi(current, region.id, crop.id)
                        source = "mock_fallback"
                    
                    # Store
                    # Check existing for this date/region/crop
                    # Optimization: only store every 5-10 days? Sentinel is every 5 days.
                    if current.day % 5 == 0:
                        new_n = NDVITimeseries(
                            region_id=region.id,
                            crop_id=crop.id,
                            date=current,
                            ndvi=ndvi_val,
                            source=source
                        )
                        db.add(new_n)
                        records_added += 1
            
            # Commit every week or so to avoid huge memory
            if current.day == 1:
                db.commit()
                
            current += timedelta(days=1)
            
        db.commit()
        print(f"Added {records_added} NDVI records.")
    except Exception as e:
        print(f"Error fetching NDVI: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch or Mock NDVI timeseries")
    parser.add_argument("--mode", type=str, choices=["mock", "real"], default="mock")
    parser.add_argument("--start", type=str, default="2023-01-01")
    parser.add_argument("--end", type=str, default="2024-12-31")
    args = parser.parse_args()
    fetch_ndvi(args.mode, args.start, args.end)
