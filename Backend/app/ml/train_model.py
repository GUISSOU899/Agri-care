import argparse
import os
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
try:
    import xgboost as xgb
except ImportError:
    xgb = None

from app.ml.data_loader import load_training_data
from app.ml.features import prepare_features

def train_yield_model(crop: str, model_type: str = "xgboost"):
    """
    Train a yield prediction model and log to MLflow.
    """
    print(f"Loading data for crop: {crop}...")
    X_raw, y = load_training_data(crop)
    
    if X_raw.empty:
        print("No data found for training.")
        return

    print("Engineering features...")
    X = prepare_features(X_raw)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Setup MLflow
    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "./mlruns")
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(f"yield_prediction_{crop}")
    
    with mlflow.start_run():
        mlflow.log_param("crop", crop)
        mlflow.log_param("model_type", model_type)
        mlflow.log_param("features", X.columns.tolist())
        
        model = None
        if model_type == "xgboost" and xgb:
            model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100)
            model.fit(X_train, y_train)
            mlflow.xgboost.log_model(model, "model")
        else:
            if model_type == "xgboost":
                print("XGBoost not installed, falling back to RandomForest.")
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            mlflow.sklearn.log_model(model, "model")
            
        # Evaluation
        predictions = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        print(f"Metrics: RMSE={rmse:.4f}, MAE={mae:.4f}, R2={r2:.4f}")
        
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2", r2)
        
        print("Training complete. Model logged to MLflow.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train yield prediction model.")
    parser.add_argument("--crop", type=str, required=True, help="Crop name (e.g. wheat)")
    parser.add_argument("--model_type", type=str, default="xgboost", help="Model type: xgboost or random_forest")
    args = parser.parse_args()
    
    train_yield_model(args.crop, args.model_type)
