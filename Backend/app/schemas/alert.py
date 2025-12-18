from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class AlertBase(BaseModel):
    region_id: int
    crop_id: Optional[int] = None
    alert_type: str
    message: str
    severity: str = "info"

class AlertCreate(AlertBase):
    pass

class AlertRead(AlertBase):
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True
