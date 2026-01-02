import pandas as pd
import xgboost as xgb
import pickle
import json
import os
import argparse
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

def train_model(dataset_path: str, model_out: str, crop_id: int = None):
    print(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    
    if crop_id:
        print(f"Filtering for crop_id={crop_id}")
        df = df[df['crop_id'] == crop_id]
        out_dir = os.path.join(model_out, f"crop_{crop_id}")
    else:
        print("Training global model (all crops)")
        out_dir = os.path.join(model_out, "global")
        
    if df.empty:
        print("No data to train on for this selection.")
        return

    os.makedirs(out_dir, exist_ok=True)
    
    # Features as specified in instructions
    features = [
        'tmin_c', 'tmax_c', 'tmean_c', 'rainfall_mm', 'evapotranspiration_mm',
        'rain_7d', 'rain_30d', 'gdd'
    ]
    target = 'yield_index_target'
    
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training XGBRegressor on {len(X_train)} samples...")
    model = xgb.XGBRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    import numpy as np
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    
    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    
    # Save artifacts
    model_path = os.path.join(out_dir, "model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
        
    metadata = {
        "features": features,
        "crop_id": crop_id,
        "trained_at": datetime.now().isoformat(),
        "metrics": {
            "mae": float(mae),
            "rmse": float(rmse)
        },
        "samples": len(df)
    }
    
    with open(os.path.join(out_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)
        
    print(f"Model and metadata saved to {out_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train XGBoost model for yield prediction")
    parser.add_argument("--dataset", type=str, required=True, help="Path to training CSV")
    parser.add_argument("--model_out", type=str, default="app/ml/artifacts", help="Base directory for model artifacts")
    parser.add_argument("--crop_id", type=int, help="Optional crop ID to train a specific model")
    
    args = parser.parse_args()
    # Correct relative path if running from Backend root
    train_model(args.dataset, args.model_out, args.crop_id)
