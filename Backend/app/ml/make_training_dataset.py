import pandas as pd
import numpy as np
import argparse
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Forecast, WeatherDaily, Crop, Region

def generate_demo_label(row):
    """Generates a demo yield index label based on weather features."""
    tmax = row['tmax_c']
    tmin = row['tmin_c']
    rain = row['rainfall_mm']
    et = row['evapotranspiration_mm']
    
    water_stress = max(0, et - 0.7 * rain)
    heat_stress = max(0, tmax - 35)
    cold_stress = max(0, 2 - tmin)
    
    base = 85
    target = base - 5 * water_stress - 2 * heat_stress - 3 * cold_stress
    target += np.random.normal(0, 2) # Add some noise
    return np.clip(target, 0, 100)

def make_dataset(days_back: int, output_path: str, use_demo_label: bool):
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # We fetch data from Forecast table as it's the primary source for the UI and contains enriched fields.
        # Alternatively we could use WeatherDaily for historical data.
        start_date = date.today() - timedelta(days=days_back)
        
        print(f"Fetching data from {start_date} to today...")
        
        # Load Forecasts
        query = db.query(Forecast).filter(Forecast.date >= start_date)
        df = pd.read_sql(query.statement, engine)
        
        if df.empty:
            print("No data found in Forecast table for the given period.")
            return

        print(f"Loaded {len(df)} forecast records.")
        
        # Sort by region, crop, date for rolling features
        df = df.sort_values(['region_id', 'crop_id', 'date'])
        
        # Feature Engineering
        # Mock GDD (Growing Degree Days) - Base 10C
        df['gdd'] = (df['tmean_c'] - 10).clip(lower=0)
        
        # Rolling averages for rainfall
        df['rain_7d'] = df.groupby(['region_id', 'crop_id'])['rainfall_mm'].transform(lambda x: x.rolling(window=7, min_periods=1).sum())
        df['rain_30d'] = df.groupby(['region_id', 'crop_id'])['rainfall_mm'].transform(lambda x: x.rolling(window=30, min_periods=1).sum())
        
        if use_demo_label:
            print("Generating demo labels...")
            df['yield_index_target'] = df.apply(generate_demo_label, axis=1)
        else:
            # Here you would join with a real YieldHistory table if available
            print("Using existing yield_index as target.")
            df['yield_index_target'] = df['yield_index']

        # Select relevant columns
        final_cols = [
            'region_id', 'crop_id', 'date', 
            'tmin_c', 'tmax_c', 'tmean_c', 'rainfall_mm', 'evapotranspiration_mm',
            'rain_7d', 'rain_30d', 'gdd', 'yield_index_target'
        ]
        
        df_final = df[final_cols]
        df_final.to_csv(output_path, index=False)
        
        regions = df['region_id'].nunique()
        crops = df['crop_id'].nunique()
        print(f"Dataset generated at {output_path}")
        print(f"Summary: {len(df_final)} lines, {regions} regions, {crops} crops covered.")

    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate yield training dataset from DB")
    parser.add_argument("--days", type=int, default=730, help="Number of days to go back")
    parser.add_argument("--output", type=str, default="app/ml/data/yield_training.csv", help="Output CSV path")
    parser.add_argument("--demo-label", type=bool, default=True, help="Generate demo labels if true")
    
    args = parser.parse_args()
    make_dataset(args.days, args.output, args.demo_label)
