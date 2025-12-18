import pandas as pd
import numpy as np

def calc_gdd(tmax, tmin, base_temp=10):
    """Calculate Growing Degree Days."""
    avg_temp = (tmax + tmin) / 2
    return np.maximum(avg_temp - base_temp, 0)

def prepare_features(X: pd.DataFrame) -> pd.DataFrame:
    """
    Apply feature engineering to the input DataFrame.
    """
    X_new = X.copy()
    
    # Example: Calculate GDD if columns exist
    if 'tmax' in X_new.columns and 'tmin' in X_new.columns:
        X_new['gdd'] = calc_gdd(X_new['tmax'], X_new['tmin'])
        
    # Example: Interaction term
    if 'precipitation' in X_new.columns and 'tavg' in X_new.columns:
        X_new['rain_temp_ratio'] = X_new['precipitation'] / (X_new['tavg'] + 1) # Avoid div by zero
        
    return X_new
