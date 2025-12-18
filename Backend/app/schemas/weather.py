from datetime import date
from typing import Optional
from pydantic import BaseModel

class WeatherDailyRead(BaseModel):
    id: int
    region_id: int
    date: date
    tmin: Optional[float] = None
    tmax: Optional[float] = None
    tavg: Optional[float] = None
    precipitation: Optional[float] = None

    class Config:
        from_attributes = True
