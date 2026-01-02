from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional

class CropBase(BaseModel):
    name: str = Field(..., max_length=100)
    type: str
    variety: Optional[str] = None
    water_need: float = Field(..., ge=0)
    temp_low: float
    temp_high: float
    rain_threshold: float = Field(..., gt=0)

    @field_validator('temp_low')
    @classmethod
    def low_must_be_lt_high(cls, v, info):
        values = info.data
        if 'temp_high' in values and v >= values['temp_high']:
            raise ValueError('temp_low must be lower than temp_high')
        return v

class CropCreate(CropBase):
    pass

class CropRead(CropBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
