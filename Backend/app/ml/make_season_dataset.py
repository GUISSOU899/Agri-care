import pandas as pd
import numpy as np
import argparse
from sqlalchemy import create_engine
from app.core.config import settings
from app.models.seasonal import SeasonCalendar, YieldObserved, NDVITimeseries, AquaCropSim
from app.models import WeatherDaily

def make_season_dataset(output_path: str):
    engine = create_engine(settings.DATABASE_URL)
    
    print("Extracting seasonal calendars...")
    calendars = pd.read_sql("SELECT * FROM season_calendar", engine)
    
    dataset = []
    
    for _, cal in calendars.iterrows():
        rid, cid, year = cal['region_id'], cal['crop_id'], cal['season_year']
        sow, harv = cal['sowing_date'], cal['harvest_date']
        
        print(f"Aggregating features for Region {rid}, Crop {cid}, Season {year}...")
        
        # 1. Weather Aggregates
        # Note: In a real app, join with WeatherDaily. 
        # For simplicity, we query the SQL directly or via pandas
        weather_query = f"""
            SELECT * FROM weather_daily 
            WHERE region_id = {rid} 
            AND date >= '{sow}' 
            AND date <= '{harv}'
        """
        w_df = pd.read_sql(weather_query, engine)
        
        if w_df.empty:
            weather_features = {
                "rain_sum": 0, "rain_days": 0, "tmean_mean": 15, 
                "tmax_p95": 25, "heat_days": 0, "cold_days": 0, "gdd_sum": 0
            }
        else:
            weather_features = {
                "rain_sum": w_df['precipitation'].sum(),
                "rain_days": (w_df['precipitation'] > 0.1).sum(),
                "tmean_mean": w_df['tavg'].mean(),
                "tmax_p95": w_df['tmax'].quantile(0.95),
                "heat_days": (w_df['tmax'] > 35).sum(),
                "cold_days": (w_df['tmin'] < 2).sum(),
                "gdd_sum": (w_df['tavg'] - 10).clip(lower=0).sum()
            }
            
        # 2. NDVI Aggregates
        ndvi_query = f"""
            SELECT * FROM ndvi_timeseries 
            WHERE region_id = {rid} AND crop_id = {cid} 
            AND date >= '{sow}' AND date <= '{harv}'
        """
        n_df = pd.read_sql(ndvi_query, engine)
        
        if n_df.empty:
            ndvi_features = {"ndvi_mean": 0.4, "ndvi_max": 0.5, "ndvi_integral": 0}
        else:
            ndvi_features = {
                "ndvi_mean": n_df['ndvi'].mean(),
                "ndvi_max": n_df['ndvi'].max(),
                "ndvi_integral": n_df['ndvi'].sum() # Simple proxy for AUC
            }
            
        # 3. Target (Observed or AquaCrop)
        observed = pd.read_sql(f"SELECT yield_t_ha FROM yield_observed WHERE region_id={rid} AND crop_id={cid} AND season_year={year}", engine)
        
        if not observed.empty:
            target = observed.iloc[0]['yield_t_ha']
            source = "observed"
        else:
            sim = pd.read_sql(f"SELECT simulated_yield_t_ha FROM aquacrop_sim WHERE region_id={rid} AND crop_id={cid} AND season_year={year}", engine)
            if not sim.empty:
                target = sim.iloc[0]['simulated_yield_t_ha']
                source = "aquacrop"
            else:
                continue # Skip if no target available
                
        row = {
            "region_id": rid,
            "crop_id": cid,
            "season_year": year,
            **weather_features,
            **ndvi_features,
            "yield_t_ha_target": target,
            "label_source": source
        }
        dataset.append(row)
        
    df_result = pd.DataFrame(dataset)
    df_result.to_csv(output_path, index=False)
    print(f"Seasonal dataset generated at {output_path} ({len(df_result)} lines)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, default="app/ml/data/season_yield_dataset.csv")
    args = parser.parse_args()
    make_season_dataset(args.output)
