from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertRead

router = APIRouter()


@router.get("/", response_model=List[AlertRead])
def read_alerts(
    region_id: int,
    crop_id: Optional[int] = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Alert).filter(Alert.region_id == region_id)
    
    if crop_id:
        query = query.filter(Alert.crop_id == crop_id)
    if active_only:
        query = query.filter(Alert.resolved_at == None)

    alerts = (
        query.order_by(Alert.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return alerts


@router.post("/", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    new_alert = Alert(
        region_id=alert.region_id,
        crop_id=alert.crop_id,
        alert_type=alert.alert_type,
        message=alert.message,
        severity=alert.severity,
    )

    db.add(new_alert)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        # Ça arrive typiquement si region_id ou crop_id n'existent pas
        raise HTTPException(
            status_code=400,
            detail="region_id ou crop_id invalide (clé étrangère).",
        ) from e

    db.refresh(new_alert)
    return new_alert

@router.post("/generate", status_code=status.HTTP_200_OK)
def generate_alerts(
    region_id: int,
    crop_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    from app.services.alert_service import generate_alerts_from_forecasts
    count = generate_alerts_from_forecasts(db, region_id, crop_id)
    return {"message": f"Analysis complete. {count} alerts generated."}
