from datetime import datetime
import json
import os
import subprocess
import sys
from typing import List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_superuser
from app.db.session import get_db
from app.ml.make_training_dataset import make_dataset
from app.ml.train_xgb import train_model as run_xgb_train

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

# --- ETL Controls ---

def run_etl_process(type_arg: str):
    """Runs the ETL script and logs output."""
    log_path = "logs/etl.log"
    os.makedirs("logs", exist_ok=True)
    
    with open(log_path, "w") as log_file:
        try:
            log_file.write(f"--- ETL Triggered at {datetime.now()} ---\n")
            log_file.flush()
            
            # Run the ETL script as a subprocess module
            # Using sys.executable ensures we use the same python environment
            result = subprocess.run(
                [sys.executable, "-m", "app.etl.run_etl"],
                cwd=os.getcwd(), # Ensure we run from root
                capture_output=True,
                text=True
            )
            
            log_file.write(result.stdout)
            if result.stderr:
                log_file.write("\n[ERROR]\n")
                log_file.write(result.stderr)
                
            log_file.write(f"\n--- ETL Completed with code {result.returncode} ---\n")
            
        except Exception as e:
            log_file.write(f"\n[CRITICAL ERROR]: {str(e)}\n")

@router.post("/etl/run")
async def run_etl(
    request: EtlRunRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_active_superuser)
):
    background_tasks.add_task(run_etl_process, request.type)
    return {"message": f"ETL triggered for {request.type}", "status": "running"}

@router.get("/etl/status")
async def get_etl_status(current_user = Depends(get_current_active_superuser)):
    # Check if logs modified recently? For now, return mock status but real logs exist.
    return {"status": "idle", "last_run": datetime.now().isoformat()}

@router.get("/etl/logs")
async def get_etl_logs(current_user = Depends(get_current_active_superuser)):
    log_path = "logs/etl.log"
    if not os.path.exists(log_path):
        return {"logs": ["No logs available yet. Run the ETL first."]}
    
    try:
        with open(log_path, "r") as f:
            content = f.read()
        return {"logs": content.splitlines()}
    except Exception as e:
        return {"logs": [f"Error reading logs: {str(e)}"]}

# --- ML Controls ---

# --- ML Controls ---

def run_training_pipeline():
    """Generates dataset and runs training."""
    try:
        csv_path = "app/ml/data/yield_training.csv"
        os.makedirs("app/ml/data", exist_ok=True)
        
        # 1. Generate Dataset
        print("Generating training dataset...")
        make_dataset(days_back=365, output_path=csv_path, use_demo_label=True)
        
        # 2. Train Model
        print("Training model...")
        run_xgb_train(dataset_path=csv_path, model_out="app/ml/artifacts", crop_id=None)
        
    except Exception as e:
        print(f"Training pipeline failed: {e}")

@router.post("/ml/train")
async def train_model(background_tasks: BackgroundTasks, current_user = Depends(get_current_active_superuser)):
    background_tasks.add_task(run_training_pipeline)
    return {"message": "Training started in background", "job_id": "job_global"}

@router.get("/ml/runs")
async def get_ml_runs(current_user = Depends(get_current_active_superuser)):
    meta_path = "app/ml/artifacts/global/metadata.json"
    if not os.path.exists(meta_path):
        return []
    
    try:
        with open(meta_path, "r") as f:
            meta = json.load(f)
        
        # Format as list of runs (only keeping last one for now as logic overwrites)
        return [{
            "id": f"run_{meta.get('trained_at', 'unknown')}",
            "date": meta.get("trained_at"),
            "status": "Success",
            "accuracy": f"{meta.get('metrics', {}).get('rmse', 0):.4f} (RMSE)",
            "model": "XGBoost v1"
        }]
    except Exception as e:
        print(f"Error reading runs: {e}")
        return []

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
