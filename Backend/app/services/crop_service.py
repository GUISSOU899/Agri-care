from sqlalchemy.orm import Session
from ..models.crop import Crop
from ..schemas.crop import CropCreate


def get_crops(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Crop).offset(skip).limit(limit).all()


def get_crop_by_id(db: Session, crop_id: int):
    return db.query(Crop).filter(Crop.id == crop_id).first()


def create_crop(db: Session, payload: CropCreate):
    new_crop = Crop(
        name=payload.name,
        type=payload.type,
        variety=payload.variety,
        water_need=payload.water_need,
        temp_low=payload.temp_low,
        temp_high=payload.temp_high,
        rain_threshold=payload.rain_threshold,
    )
    db.add(new_crop)
    db.commit()
    db.refresh(new_crop)
    return new_crop
