import argparse
import shap
import mlflow
import pandas as pd
import matplotlib.pyplot as plt
import os

from app.ml.data_loader import load_training_data
from app.ml.features import prepare_features

def explain_model_for_crop(crop: str, run_id: str):
    """
    Explain a specific model run using SHAP.
    """
    print(f"Loading model from run_id: {run_id}...")
    try:
        # Try loading as sklearn or xgboost; MLflow usually handles this via pyfunc but here we want specific
        model_uri = f"runs:/{run_id}/model"
        model = mlflow.pyfunc.load_model(model_uri)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    print("Loading validation data...")
    X_raw, _ = load_training_data(crop)
    if X_raw.empty:
        print("No data found.")
        return
        
    X = prepare_features(X_raw)
    
    # Compute SHAP values
    # For independent generic model explanation, we might need the underlying estimator
    # mlflow.pyfunc loads a wrapper. To get the underlying model for TreeExplainer:
    # This part can be tricky with pyfunc. 
    # For simplicity in this demo, we'll try to use a generic KernelExplainer or TreeExplainer if possible.
    
    # Ideally we should load via mlflow.sklearn or mlflow.xgboost directly if we know the type,
    # or rely on the fact that pyfunc might expose it.
    
    # Let's try to assume it's a tree model and use TreeExplainer if possible, otherwise KernelExplainer (slow).
    # Since we saved it as sklearn/xgboost native, we should try loading natively if possible or 
    # just unpickling the artifact.
    # For this script, let's just attempt to use the loaded pyfunc if it's compatible or warn user.
    
    print("Calculating SHAP values...")
    # Using a small background sample for speed
    background = X.sample(min(100, len(X)))
    
    explainer = shap.Explainer(model.predict, background)
    shap_values = explainer(X)
    
    print("SHAP values calculated.")
    
    # Summary plot (text based summary for now)
    # real plot would be: shap.summary_plot(shap_values, X)
    
    vals = pd.DataFrame(shap_values.values, columns=X.columns)
    importance = vals.abs().mean().sort_values(ascending=False)
    
    print("\nFeature Importance (mean |SHAP value|):")
    print(importance)
    
    return importance.to_dict()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Explain yield model.")
    parser.add_argument("--crop", type=str, required=True, help="Crop name")
    parser.add_argument("--run_id", type=str, required=True, help="MLflow Run ID")
    args = parser.parse_args()
    
    explain_model_for_crop(args.crop, args.run_id)
