import pandas as pd
import xgboost as xgb
import pickle
import json
import os
import argparse
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

def train_season_model(dataset_path: str, model_out: str):
    print(f"Loading seasonal dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    
    if df.empty:
        print("Dataset is empty.")
        return

    out_dir = os.path.join(model_out, "seasonal")
    os.makedirs(out_dir, exist_ok=True)
    
    features = [
        'rain_sum', 'rain_days', 'tmean_mean', 'tmax_p95', 
        'heat_days', 'cold_days', 'gdd_sum', 'ndvi_mean', 'ndvi_max', 'ndvi_integral'
    ]
    target = 'yield_t_ha_target'
    
    X = df[features]
    y = df[target]
    
    # Stratified split by label_source? Or just random for now. 
    # Usually temporal split is better (e.g., train on years < 2024, test on 2024).
    # Since we have few samples in mock, we use random.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training Seasonal XGBRegressor on {len(X_train)} samples...")
    model = xgb.XGBRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=4,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    
    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R2: {r2:.4f}")
    
    # Save artifacts
    model_path = os.path.join(out_dir, "model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
        
    metadata = {
        "features": features,
        "target_unit": "t/ha",
        "trained_at": datetime.now().isoformat(),
        "metrics": {
            "mae": float(mae),
            "rmse": float(rmse),
            "r2": float(r2)
        },
        "label_mix": df['label_source'].value_counts().to_dict(),
        "samples": len(df),
        "version_tag": "seasonal_v1"
    }
    
    with open(os.path.join(out_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)
        
    print(f"Seasonal model artifacts saved to {out_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, required=True)
    parser.add_argument("--model_out", type=str, default="app/ml/artifacts")
    args = parser.parse_args()
    train_season_model(args.dataset, args.model_out)
