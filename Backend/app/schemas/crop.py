from typing import Optional
from pydantic import BaseModel

class CropBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None

class CropCreate(CropBase):
    pass

class CropRead(CropBase):
    id: int

    class Config:
        from_attributes = True
