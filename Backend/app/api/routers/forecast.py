from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.forecast import Forecast
from app.schemas.forecast import ForecastRead

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
