import requests
import math
from datetime import date, timedelta, datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import Region, Crop, Forecast, ClimatologyDaily

API_URL = "https://api.open-meteo.com/v1/forecast"

def fetch_open_meteo(lat, lon):
    try:
        resp = requests.get(API_URL, params={
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,et0_fao_evapotranspiration",
            "timezone": "auto",
            "forecast_days": 16
        })
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None

def update_forecasts_30d():
    db = SessionLocal()
    try:
        regions = db.query(Region).all()
        crops = db.query(Crop).all()
        
        today = date.today()
        
        # Cleanup: Delete past forecasts
        print("Cleaning up past forecasts...")
        db.query(Forecast).filter(Forecast.date < today).delete()
        db.commit()
        
        for region in regions:
            print(f"Processing region: {region.name} (ID: {region.id})")
            
            # Use region.latitude/longitude with fallback to Marrakech if NULL
            lat = region.latitude if region.latitude is not None else 31.6
            lon = region.longitude if region.longitude is not None else -7.9
            
            # 1. Fetch Real API Data (J+0 to J+16)
            api_data = fetch_open_meteo(lat, lon)
            real_forecasts = {} # key: date_obj -> dict
            
            if api_data and "daily" in api_data:
                daily = api_data["daily"]
                times = daily["time"]
                
                for i, t_str in enumerate(times):
                    try:
                        d_obj = datetime.strptime(t_str, "%Y-%m-%d").date()
                        real_forecasts[d_obj] = {
                            "tmin": daily["temperature_2m_min"][i],
                            "tmax": daily["temperature_2m_max"][i],
                            "tmean": daily["temperature_2m_mean"][i],
                            "rain": daily["precipitation_sum"][i],
                            "et": daily.get("et0_fao_evapotranspiration", [0]*31)[i] if "et0_fao_evapotranspiration" in daily else None
                        }
                    except (ValueError, IndexError):
                        continue

            # 2. Prepare Blending (Climatology)
            # Pre-fetch climatology for this region
            clim_rows = db.query(ClimatologyDaily).filter(ClimatologyDaily.region_id == region.id).all()
            clim_map = {c.day_of_year: c for c in clim_rows}
            
            # Anchor for blending (Last real day or today if none)
            last_real_date = sorted(real_forecasts.keys())[-1] if real_forecasts else today
            anchor = real_forecasts.get(last_real_date, {"tmin": 15, "tmax": 25, "tmean": 20, "rain": 0, "et": 4.0})
            
            for crop in crops:
                print(f"  Generating 30-day forecast for crop: {crop.name}")
                
                # Setup context for rolling features
                rain_history = [] # Last 30 days of rain
                
                for i in range(31): # 0 to 30 = 31 days
                    f_date = today + timedelta(days=i)
                    day_offset = (f_date - today).days
                    doy = f_date.timetuple().tm_yday
                    
                    # Data selection
                    if f_date in real_forecasts:
                        data = real_forecasts[f_date]
                        source = "api"
                        tmin, tmax, rain_val = data["tmin"], data["tmax"], data["rain"]
                        tmean = data["tmean"]
                        et = data["et"] if data["et"] is not None else (tmean / 5.0)
                    else:
                        # Estimation
                        source = "estimation"
                        clim = clim_map.get(doy)
                        
                        # Blending Logic
                        gap = (f_date - last_real_date).days
                        alpha = min(1.0, max(0.0, gap / 14.0)) if gap > 0 else 1.0
                        
                        if not clim:
                            tmin = (1 - alpha) * anchor["tmin"] + alpha * 10
                            tmax = (1 - alpha) * anchor["tmax"] + alpha * 20
                            rain_val = 0
                        else:
                            tmin = (1 - alpha) * anchor["tmin"] + alpha * clim.tmin_c
                            tmax = (1 - alpha) * anchor["tmax"] + alpha * clim.tmax_c
                            rain_val = clim.rainfall_mm
                        
                        tmean = (tmin + tmax) / 2
                        et = (tmean / 5.0)
                    
                    # Store rain for rolling features
                    rain_history.append(rain_val)
                    if len(rain_history) > 30:
                        rain_history.pop(0)
                        
                    # 3. YIELD INDEX PREDICTION (ML)
                    # Prepare features
                    rain_7d = sum(rain_history[-7:])
                    rain_30d = sum(rain_history)
                    gdd = max(0, tmean - 10) # Simple GDD base 10
                    
                    features = {
                        "tmin_c": tmin,
                        "tmax_c": tmax,
                        "tmean_c": tmean,
                        "rainfall_mm": rain_val,
                        "evapotranspiration_mm": et,
                        "rain_7d": rain_7d,
                        "rain_30d": rain_30d,
                        "gdd": gdd
                    }
                    
                    from app.services.ml_service import ml_service
                    y_idx, m_version = ml_service.predict_yield_index(crop.id, features)
                    
                    if y_idx is None:
                        # Fallback to simulation
                        y_idx = 100 + math.sin(day_offset/5.0)*10
                        m_version = "sim_legacy"

                    # 4. Upsert Forecast
                    existing = db.query(Forecast).filter(
                        Forecast.region_id == region.id,
                        Forecast.crop_id == crop.id,
                        Forecast.date == f_date
                    ).first()
                    
                    if existing:
                        existing.tmin_c = tmin
                        existing.tmax_c = tmax
                        existing.tmean_c = tmean
                        existing.temperature_c = tmean # Legacy alias
                        existing.rainfall_mm = rain_val
                        existing.evapotranspiration_mm = et
                        existing.source = source
                        existing.horizon_days = day_offset
                        existing.yield_index = y_idx
                        existing.model_version = m_version
                        # existing.fetched_at handled by auto onupdate
                    else:
                        new_f = Forecast(
                            region_id=region.id,
                            crop_id=crop.id,
                            date=f_date,
                            horizon_days=day_offset,
                            yield_index=y_idx,
                            model_version=m_version,
                            temperature_c=tmean,
                            tmin_c=tmin,
                            tmax_c=tmax,
                            tmean_c=tmean,
                            rainfall_mm=rain_val,
                            evapotranspiration_mm=et,
                            source=source
                        )
                        db.add(new_f)
                
                # Batch commit per crop/region to avoid huge transactions if many regions
                db.commit()
                
        print("Forecast update complete for all regions and crops.")

    except Exception as e:
        print(f"Error updating forecasts: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_forecasts_30d()
