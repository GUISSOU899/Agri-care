from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_superuser
from app.db.session import get_db

router = APIRouter()

# Schemas
class EtlRunRequest(BaseModel):
    type: str = "all"

class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[str] = None

# --- CSV Uploads ---

@router.post("/upload/regions-csv")
async def upload_regions_csv(file: UploadFile = File(...), current_user = Depends(get_current_active_superuser)):
    # Save file logic here
    # with open(f"data/uploads/regions.csv", "wb") as f:
    #     f.write(await file.read())
    return {"message": "Regions CSV uploaded successfully"}

@router.post("/upload/crops-csv")
async def upload_crops_csv(file: UploadFile = File(...), current_user = Depends(get_current_active_superuser)):
    return {"message": "Crops CSV uploaded successfully"}

@router.post("/upload/alerts-csv")
async def upload_alerts_csv(file: UploadFile = File(...), current_user = Depends(get_current_active_superuser)):
    return {"message": "Alerts CSV uploaded successfully"}

# --- ETL Controls ---

@router.post("/etl/run")
async def run_etl(request: EtlRunRequest, current_user = Depends(get_current_active_superuser)):
    # Trigger ETL logic
    return {"message": f"ETL triggered for {request.type}", "status": "running"}

@router.get("/etl/status")
async def get_etl_status(current_user = Depends(get_current_active_superuser)):
    return {"status": "idle", "last_run": "2026-01-01T12:00:00Z"}

@router.get("/etl/logs")
async def get_etl_logs(current_user = Depends(get_current_active_superuser)):
    return {"logs": ["Log 1", "Log 2"]}

# --- ML Controls ---

@router.post("/ml/train")
async def train_model(current_user = Depends(get_current_active_superuser)):
    return {"message": "Training started", "job_id": "job_123"}

@router.get("/ml/runs")
async def get_ml_runs(current_user = Depends(get_current_active_superuser)):
    return [
        {"id": "run_1", "date": "2026-01-01", "status": "Success", "accuracy": "95%", "model": "RF"},
        {"id": "run_2", "date": "2025-12-31", "status": "Success", "accuracy": "94%", "model": "RF"}
    ]

# --- User Management (Admin only) ---

@router.patch("/users/{user_id}")
async def update_user(
    user_id: int, 
    user_in: UserUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_superuser)
):
    # Logic to update user role/active status
    # user = db.query(User).filter(User.id == user_id).first()
    # if not user: raise HTTPException(404)
    # Update fields...
    # db.commit()
    return {"message": "User updated"}
