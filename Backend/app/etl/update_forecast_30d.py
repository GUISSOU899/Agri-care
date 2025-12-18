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
        
        for region in regions:
            print(f"Processing {region.name}...")
            
            # 1. Fetch Real API Data (J+0 to J+16)
            api_data = fetch_open_meteo(region.latitude or 31.6, region.longitude or -7.9)
            real_forecasts = {} # key: date_obj -> dict
            
            if api_data and "daily" in api_data:
                daily = api_data["daily"]
                times = daily["time"]
                
                for i, t_str in enumerate(times):
                    d_obj = datetime.strptime(t_str, "%Y-%m-%d").date()
                    real_forecasts[d_obj] = {
                        "tmin": daily["temperature_2m_min"][i],
                        "tmax": daily["temperature_2m_max"][i],
                        "tmean": daily["temperature_2m_mean"][i],
                        "rain": daily["precipitation_sum"][i],
                        "et": daily.get("et0_fao_evapotranspiration", [0]*16)[i] or 0
                    }

            # 2. Prepare Blending (Climatology)
            # Pre-fetch climatology for this region
            clim_rows = db.query(ClimatologyDaily).filter(ClimatologyDaily.region_id == region.id).all()
            clim_map = {c.day_of_year: c for c in clim_rows}
            
            # Anchor for blending (Last real day)
            last_real_date = sorted(real_forecasts.keys())[-1] if real_forecasts else today
            anchor = real_forecasts.get(last_real_date, {"tmin": 15, "tmax": 25, "rain": 0})
            
            for crop in crops:
                for i in range(30):
                    f_date = today + timedelta(days=i)
                    day_offset = (f_date - today).days
                    doy = f_date.timetuple().tm_yday
                    
                    # Data selection
                    if f_date in real_forecasts:
                        data = real_forecasts[f_date]
                        source = "api"
                        tmin, tmax, rain_val = data["tmin"], data["tmax"], data["rain"]
                        tmean = data["tmean"]
                        et = data["et"]
                    else:
                        # Estimation
                        source = "estimation"
                        clim = clim_map.get(doy)
                        if not clim:
                            # Fallback if clim missing
                            tmin, tmax, rain_val, tmean = 10, 20, 0, 15
                        else:
                            # Blending Logic
                            # Alpha 0 at J+17 (1 day after anchor), 1 at J+30
                            # anchor is J+15 or J+16.
                            # dist from anchor
                            gap = (f_date - last_real_date).days
                            alpha = min(1.0, max(0.0, gap / 14.0)) # Blend over 2 weeks
                            
                            tmin = (1 - alpha) * anchor["tmin"] + alpha * clim.tmin_c
                            tmax = (1 - alpha) * anchor["tmax"] + alpha * clim.tmax_c
                            # Rain is hard to blend, maybe just noise or clim?
                            # Let's transition prob? simpler: just take clim
                            rain_val = clim.rainfall_mm 
                            tmean = (tmin + tmax) / 2
                            
                        et = (tmean / 5) # simple estimation
                    
                    # Upsert
                    # Check existing
                    existing = db.query(Forecast).filter(
                        Forecast.region_id == region.id,
                        Forecast.crop_id == crop.id,
                        Forecast.date == f_date
                    ).first()
                    
                    # Yield Index sim (keep random/sine for now)
                    y_idx = 100 + math.sin(i/5)*10
                    
                    if existing:
                        existing.tmin_c = tmin
                        existing.tmax_c = tmax
                        existing.tmean_c = tmean
                        existing.temperature_c = tmean # Legacy alias
                        existing.rainfall_mm = rain_val
                        existing.evapotranspiration_mm = et
                        existing.source = source
                        existing.horizon_days = day_offset
                        existing.yield_index = y_idx # Update yield too
                        existing.updated_at = func.now()
                    else:
                        new_f = Forecast(
                            region_id=region.id,
                            crop_id=crop.id,
                            date=f_date,
                            horizon_days=day_offset,
                            yield_index=y_idx,
                            temperature_c=tmean,
                            tmin_c=tmin,
                            tmax_c=tmax,
                            tmean_c=tmean,
                            rainfall_mm=rain_val,
                            evapotranspiration_mm=et,
                            source=source
                        )
                        db.add(new_f)
                
        db.commit()
        print("Forecast update complete.")

    except Exception as e:
        print(f"Error updating forecasts: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_forecasts_30d()
