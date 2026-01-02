from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.region import Region
from app.models.user import User  # Needed for type hint
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

from app.schemas.region import RegionCreate
from app.api.deps import get_current_active_superuser

@router.post("/", response_model=RegionRead, status_code=201)
def create_region(
    region_in: RegionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    # Check for duplicate name
    existing = db.query(Region).filter(Region.name == region_in.name).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Region with name '{region_in.name}' already exists.")
    
    new_region = Region(
        name=region_in.name,
        latitude=region_in.latitude,
        longitude=region_in.longitude
    )
    db.add(new_region)
    db.commit()
    db.refresh(new_region)
    return new_region
