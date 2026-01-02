from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.forecast import Forecast
from datetime import date
from app.schemas.forecast import ForecastRead, ForecastRunRequest
from app.services.forecast_service import ForecastService

router = APIRouter()

@router.get("/", response_model=List[ForecastRead])
def read_forecasts(
    region_id: int,
    crop_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Forecast)\
        .filter(Forecast.region_id == region_id)\
        .filter(Forecast.crop_id == crop_id)\
        .order_by(Forecast.date.asc())
        
    forecasts = query.offset(skip).limit(limit).all()
    return forecasts

@router.post("/run")
def run_forecast(
    request: ForecastRunRequest,
    db: Session = Depends(get_db)
):
    """
    Generate or retrieve cached forecast, recommendations, and alerts.
    Deterministic based on inputs.
    """
    as_of = request.as_of_date or date.today().isoformat()
    return ForecastService.get_forecast_run(
        db,
        request.region_id,
        request.crop_id,
        request.horizon_days,
        as_of
    )
