from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.region import Region
from app.schemas.region import RegionRead

router = APIRouter()

@router.get("/", response_model=List[RegionRead])
def read_regions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    regions = db.query(Region).offset(skip).limit(limit).all()
    return regions

@router.get("/{region_id}", response_model=RegionRead)
def read_region(region_id: int, db: Session = Depends(get_db)):
    region = db.query(Region).filter(Region.id == region_id).first()
    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return region
