from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.crop import Crop
from app.schemas.crop import CropCreate, CropRead

router = APIRouter()

@router.get("/", response_model=List[CropRead])
def read_crops(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    crops = db.query(Crop).offset(skip).limit(limit).all()
    return crops

@router.post("/", response_model=CropRead, status_code=status.HTTP_201_CREATED)
def create_crop(crop: CropCreate, db: Session = Depends(get_db)):
    db_crop = db.query(Crop).filter(Crop.code == crop.code).first()
    if db_crop:
        raise HTTPException(status_code=400, detail="Crop code already registered")
    
    new_crop = Crop(name=crop.name, code=crop.code, description=crop.description)
    db.add(new_crop)
    db.commit()
    db.refresh(new_crop)
    return new_crop
