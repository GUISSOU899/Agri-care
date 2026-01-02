from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.crop import Crop
from app.schemas.crop import CropCreate, CropRead

router = APIRouter()

@router.get("/", response_model=List[CropRead])
async def read_crops(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Crop).offset(skip).limit(limit).all()

@router.post("/", response_model=CropRead, status_code=status.HTTP_201_CREATED)
async def create_crop(crop: CropCreate, db: Session = Depends(get_db)):
    # Ensure unique name
    existing = db.query(Crop).filter(Crop.name == crop.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Crop with this name already exists")
    new_crop = Crop(
        name=crop.name,
        type=crop.type,
        variety=crop.variety,
        water_need=crop.water_need,
        temp_low=crop.temp_low,
        temp_high=crop.temp_high,
        rain_threshold=crop.rain_threshold,
    )
    db.add(new_crop)
    db.commit()
    db.refresh(new_crop)
    return new_crop
