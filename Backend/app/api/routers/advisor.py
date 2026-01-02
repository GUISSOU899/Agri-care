from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.ml import AdvisorRequest, AdvisorResponse
from app.services.advisor_service import AdvisorService
from app.db.session import get_db

router = APIRouter(prefix="/ml/advisor", tags=["ml"])

@router.post("/recommend", response_model=AdvisorResponse)
async def recommend(req: AdvisorRequest, db: Session = Depends(get_db)):
    # Basic static context for testing when DB is not fully populated
    context = {
        "region": {"id": req.region_id, "name": "Région Test", "lat": 31.63, "lon": -8.0},
        "crop": {"id": req.crop_id, "name": "Culture Test"},
        "forecast_14d_summary": {
            "rain_sum_mm": 5.0,
            "rain_days": 2,
            "tmean_mean_c": 18.0,
            "tmax_p95_c": 30.0,
            "heat_days_gt_32c": 0,
            "cold_days_lt_5c": 0,
            "et0_sum_mm": 40.0,
            "dry_spell_max_days": 10
        },
        "seasonal_yield": { "yield_t_ha": 5.5, "confidence": 0.85, "version": "v1" },
        "ndvi": { "mean": 0.35, "max": 0.70, "integral": 35.0 },
        "derived_agro": { "gdd_sum": 1500.0 },
        "notes_optional": {
            "soil_type": "argileux",
            "irrigation": "disponible",
            "growth_stage": "floraison"
        }
    }
    
    answer_md = await AdvisorService.get_recommendations(context)
    return AdvisorResponse(answer=answer_md)
