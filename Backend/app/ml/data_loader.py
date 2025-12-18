import pandas as pd
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.weather import WeatherDaily, Region
from app.models.yield_data import YieldHistory

def load_weather_data(region_ids: list[int]) -> pd.DataFrame:
    """Load weather data for specific regions."""
    with SessionLocal() as db:
        query = db.query(WeatherDaily).filter(WeatherDaily.region_id.in_(region_ids))
        df = pd.read_sql(query.statement, db.bind)
    return df

def load_yield_data(crop: str) -> pd.DataFrame:
    """Load historical yield data for a specific crop."""
    with SessionLocal() as db:
        query = db.query(YieldHistory).filter(YieldHistory.crop == crop)
        df = pd.read_sql(query.statement, db.bind)
    return df

def load_training_data(crop: str):
    """
    Load and merge data to create a training dataset.
    Returns X (features) and y (target).
    This is a simplified version; real-world usage would involve complex joining 
    on time windows (e.g. growing season).
    """
    yield_df = load_yield_data(crop)
    if yield_df.empty:
        return pd.DataFrame(), pd.Series()
    
    region_ids = yield_df['region_id'].unique().tolist()
    weather_df = load_weather_data(region_ids)
    
    if weather_df.empty:
        return pd.DataFrame(), pd.Series()

    # Simple feature aggregation example: average weather per year per region
    # Assuming weather_daily has a 'date' column, we extract year.
    weather_df['date'] = pd.to_datetime(weather_df['date'])
    weather_df['year'] = weather_df['date'].dt.year
    
    # Aggregating weather by region and year
    weather_yearly = weather_df.groupby(['region_id', 'year']).agg({
        'tavg': 'mean',
        'tmin': 'mean',
        'tmax': 'mean',
        'precipitation': 'sum'
    }).reset_index()
    
    # Merge with yield data
    merged_df = pd.merge(yield_df, weather_yearly, on=['region_id', 'year'], how='inner')
    
    if merged_df.empty:
        return pd.DataFrame(), pd.Series()

    # Define features and target
    feature_cols = ['tavg', 'tmin', 'tmax', 'precipitation', 'latitude', 'longitude']
    # Merge region info for lat/long if needed, but for now assuming we use simple weather features.
    
    # Let's verify if region lat/lon is needed. The plan mentioned GDD/ET0 in features.py.
    # We will let features.py handle transformation, here we return the merged raw-ish dataframe.
    
    # Dropping non-feature columns for X
    # Actually, let's return the merged dataframe so features.py can process it.
    # But the function signature requested X, y.
    
    X = merged_df[['tavg', 'tmin', 'tmax', 'precipitation']]
    y = merged_df['yield_index']
    
    return X, y
