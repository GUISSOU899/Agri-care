import os
import pickle
import json
import pandas as pd
import numpy as np

class MlService:
    _models = {} # Cache: crop_id -> (model, features)
    _global_model = None
    
    BASE_ARTIFACTS_PATH = "app/ml/artifacts"

    @classmethod
    def _load_model(cls, crop_id: int = None):
        """Loads a model from disk and caches it."""
        path_segment = f"crop_{crop_id}" if crop_id else "global"
        dir_path = os.path.join(cls.BASE_ARTIFACTS_PATH, path_segment)
        model_path = os.path.join(dir_path, "model.pkl")
        meta_path = os.path.join(dir_path, "metadata.json")
        
        if not os.path.exists(model_path) or not os.path.exists(meta_path):
            return None
            
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            with open(meta_path, "r") as f:
                meta = json.load(f)
            
            features = meta.get("features", [])
            return model, features, meta.get("trained_at")
        except Exception as e:
            print(f"Error loading model for {path_segment}: {e}")
            return None

    @classmethod
    def predict_yield_index(cls, crop_id: int, features: dict) -> tuple:
        """
        Predicts yield index (0-100) based on input features.
        Returns: (prediction, model_version) or (None, None)
        """
        # Try crop-specific cache
        if crop_id not in cls._models:
            loaded = cls._load_model(crop_id)
            if loaded:
                cls._models[crop_id] = loaded
            else:
                # If no crop model, try global cache
                if cls._global_model is None:
                    cls._global_model = cls._load_model(None)
                
                if cls._global_model:
                    cls._models[crop_id] = cls._global_model
                else:
                    return None, None

        model, feature_names, version = cls._models[crop_id]
        
        try:
            # Prepare input data in correct order
            input_data = [features.get(f, 0) for f in feature_names]
            input_df = pd.DataFrame([input_data], columns=feature_names)
            
            pred = model.predict(input_df)[0]
            # Clip between 0 and 100
            return float(np.clip(pred, 0, 100)), f"xgb_{version[:10]}"
        except Exception as e:
            print(f"Inference error for crop {crop_id}: {e}")
            return None, None

ml_service = MlService()
