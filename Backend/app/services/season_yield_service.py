import os
import pickle
import json
import pandas as pd
import numpy as np
import argparse
from sqlalchemy import create_engine
from app.core.config import settings

class SeasonYieldService:
    _model = None
    _features = None
    _metadata = None
    
    ARTIFACT_DIR = "app/ml/artifacts/seasonal"

    @classmethod
    def _load_model(cls):
        if cls._model is not None:
            return True
            
        model_path = os.path.join(cls.ARTIFACT_DIR, "model.pkl")
        meta_path = os.path.join(cls.ARTIFACT_DIR, "metadata.json")
        
        if not os.path.exists(model_path):
            return False
            
        try:
            with open(model_path, "rb") as f:
                cls._model = pickle.load(f)
            with open(meta_path, "r") as f:
                cls._metadata = json.load(f)
            cls._features = cls._metadata.get("features", [])
            return True
        except Exception as e:
            print(f"Error loading seasonal model: {e}")
            return False

    @classmethod
    def predict_seasonal_yield(cls, region_id: int, crop_id: int, season_year: int):
        if not cls._load_model():
            return None, "Model not trained"
            
        engine = create_engine(settings.DATABASE_URL)
        
        # 1. Fetch Calendar
        # We need dates to aggregate features for the prediction
        cal_query = f"SELECT * FROM season_calendar WHERE region_id={region_id} AND crop_id={crop_id} AND season_year={season_year}"
        cal_df = pd.read_sql(cal_query, engine)
        if cal_df.empty:
            return None, "Season calendar missing for this context"
        
        cal = cal_df.iloc[0]
        sow, harv = cal['sowing_date'], cal['harvest_date']
        
        # 2. Extract Features (Same logic as make_season_dataset)
        weather_query = f"SELECT * FROM weather_daily WHERE region_id={region_id} AND date >= '{sow}' AND date <= '{harv}'"
        w_df = pd.read_sql(weather_query, engine)
        
        if w_df.empty:
             return None, "No weather data found for the season"
             
        weather_features = {
            "rain_sum": w_df['precipitation'].sum(),
            "rain_days": (w_df['precipitation'] > 0.1).sum(),
            "tmean_mean": w_df['tavg'].mean(),
            "tmax_p95": w_df['tmax'].quantile(0.95),
            "heat_days": (w_df['tmax'] > 35).sum(),
            "cold_days": (w_df['tmin'] < 2).sum(),
            "gdd_sum": (w_df['tavg'] - 10).clip(lower=0).sum()
        }
        
        ndvi_query = f"SELECT * FROM ndvi_timeseries WHERE region_id={region_id} AND crop_id={crop_id} AND date >= '{sow}' AND date <= '{harv}'"
        n_df = pd.read_sql(ndvi_query, engine)
        
        if n_df.empty:
            ndvi_features = {"ndvi_mean": 0.4, "ndvi_max": 0.5, "ndvi_integral": 0}
        else:
            ndvi_features = {
                "ndvi_mean": n_df['ndvi'].mean(),
                "ndvi_max": n_df['ndvi'].max(),
                "ndvi_integral": n_df['ndvi'].sum()
            }
            
        features_dict = {
            "rain_sum": float(weather_features["rain_sum"]),
            "rain_days": int(weather_features["rain_days"]),
            "tmean_mean": float(weather_features["tmean_mean"]),
            "tmax_p95": float(weather_features["tmax_p95"]),
            "heat_days": int(weather_features["heat_days"]),
            "cold_days": int(weather_features["cold_days"]),
            "gdd_sum": float(weather_features["gdd_sum"]),
            "ndvi_mean": float(ndvi_features["ndvi_mean"]),
            "ndvi_max": float(ndvi_features["ndvi_max"]),
            "ndvi_integral": float(ndvi_features["ndvi_integral"])
        }
        
        # 3. Predict
        input_data = [features_dict.get(f, 0) for f in cls._features]
        input_df = pd.DataFrame([input_data], columns=cls._features)
        
        pred = cls._model.predict(input_df)[0]
        confidence = 0.85 # Mock confidence for now
        
        return {
            "yield_t_ha": float(pred),
            "confidence": confidence,
            "version": cls._metadata.get("version_tag"),
            "features_used": features_dict
        }, None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--region_id", type=int, required=True)
    parser.add_argument("--crop_id", type=int, required=True)
    parser.add_argument("--season_year", type=int, required=True)
    args = parser.parse_args()
    
    res, err = SeasonYieldService.predict_seasonal_yield(args.region_id, args.crop_id, args.season_year)
    if err:
        print(f"Error: {err}")
    else:
        print(f"Prediction: {res['yield_t_ha']:.2f} t/ha (Confidence: {res['confidence']})")
