from datetime import date, datetime
from pydantic import BaseModel

class ForecastBase(BaseModel):
    region_id: int
    crop_id: int
    date: date
    horizon_days: int
    yield_index: float
    temperature_c: float | None = None
    rainfall_mm: float | None = None
    source: str = "api"
    model_version: str | None = None

class ForecastCreate(ForecastBase):
    pass

class ForecastRead(ForecastBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ForecastRunRequest(BaseModel):
    region_id: int
    crop_id: int
    horizon_days: int
    as_of_date: str | None = None # YYYY-MM-DD
    cache_key: str | None = None

