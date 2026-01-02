import pandas as pd
import argparse
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.seasonal import YieldObserved

def import_yields(csv_path: str):
    db = SessionLocal()
    try:
        df = pd.read_csv(csv_path)
        print(f"Importing {len(df)} records from {csv_path}...")
        
        for idx, row in df.iterrows():
            # Check for existing
            existing = db.query(YieldObserved).filter(
                YieldObserved.region_id == int(row['region_id']),
                YieldObserved.crop_id == int(row['crop_id']),
                YieldObserved.season_year == int(row['season_year'])
            ).first()
            
            if existing:
                existing.yield_t_ha = float(row['yield_t_ha'])
                existing.source = row['source']
            else:
                new_y = YieldObserved(
                    region_id=int(row['region_id']),
                    crop_id=int(row['crop_id']),
                    season_year=int(row['season_year']),
                    yield_t_ha=float(row['yield_t_ha']),
                    source=row['source']
                )
                db.add(new_y)
        
        db.commit()
        print("Import successful.")
    except Exception as e:
        print(f"Error importing yields: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import observed yield data from CSV")
    parser.add_argument("--csv", type=str, required=True, help="Path to yield_observed.csv")
    args = parser.parse_args()
    import_yields(args.csv)
