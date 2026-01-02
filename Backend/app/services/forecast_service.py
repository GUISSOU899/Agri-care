import json
import hashlib
import logging
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.core.redis_client import get_redis_client
from app.services.season_yield_service import SeasonYieldService

logger = logging.getLogger(__name__)

class ForecastService:
    @staticmethod
    def get_forecast_run(
        db: Session, 
        region_id: int, 
        crop_id: int, 
        horizon_days: int, 
        as_of_date: str
    ) -> Dict[str, Any]:
        """
        Get forecast and recommendations using Redis cache for determinism.
        """
        # 1. Construct deterministic cache key
        # We include region, crop, horizon, and the reference date. 
        # If the user clicks "Load" multiple times with same params, they get same result.
        raw_key = f"forecast:{region_id}:{crop_id}:{horizon_days}:{as_of_date}"
        cache_key = hashlib.sha256(raw_key.encode()).hexdigest()
        redis_key = f"agri:run:{cache_key}"

        # 2. Try Redis
        r = get_redis_client()
        try:
            cached = r.get(redis_key)
            if cached:
                logger.info(f"Cache HIT for key {raw_key}")
                data = json.loads(cached)
                data["meta"]["cache_hit"] = True
                return data
        except Exception as e:
            logger.warning(f"Redis get failed: {e}")

        # 3. Compute (Cache Miss)
        logger.info(f"Cache MISS for key {raw_key} - Computing...")
        
        # Determine season year from reference date (simple logic for now)
        try:
           year = int(as_of_date.split("-")[0])
        except:
           year = 2025

        if settings.ML_URL:
            # 3a. Call Microservice
            try:
                import requests
                payload = {"region_id": region_id, "crop_id": crop_id, "year": year}
                resp = requests.post(f"{settings.ML_URL}/predict/seasonal", json=payload, timeout=10)
                if resp.status_code == 200:
                    yield_data = resp.json()
                else:
                    logger.error(f"ML Service returned {resp.status_code}: {resp.text}")
                    yield_data = {"error": f"ML Service error: {resp.text}"}
            except Exception as e:
                logger.error(f"Failed to call ML Service: {e}")
                yield_data = {"error": str(e)}
        else:
            # 3b. Call Local Service (Legacy/Monolith mode)
            try:
                yield_res, err = SeasonYieldService.predict_seasonal_yield(region_id, crop_id, year)
                if err:
                    logger.error(f"Prediction error: {err}")
                    yield_data = {"error": err}
                else:
                    yield_data = yield_res
            except Exception as e:
                logger.error(f"ML Service crashed: {e}")
                yield_data = {"error": str(e)}

        # Build response structure (mocking recommendations for PFA scope if ML doesn't provide them)
        # In a real app, recommendations would be derived from yield_data + rules.
        response_data = {
            "forecast": {
                "dates": [], # TODO: populate dates based on horizon
                "yield_index": yield_data.get("yield_t_ha", 0.0)
            },
            "recommendations": [
                {
                    "date": as_of_date,
                    "irrigation_mm": 0 if "error" in yield_data else 15, # Mock rule
                    "comment": "Irrigation recommandée" if "error" not in yield_data else "Pas de données",
                    "reason_code": "REQ_WATER"
                }
            ],
            "alerts": [],
            "meta": {
                "cache_hit": False,
                "run_id": cache_key[:10],
                "as_of_date": as_of_date,
                "inputs_hash": cache_key
            }
        }

        # 4. Save to Redis
        try:
            r.set(redis_key, json.dumps(response_data), ex=3600*24) # 24h cache
        except Exception as e:
            logger.warning(f"Redis set failed: {e}")

        return response_data
