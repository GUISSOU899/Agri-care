from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.core.redis_client import get_redis_client

router = APIRouter()

@router.get("/")
def health_check(db: Session = Depends(get_db)):
    status = {"status": "ok", "db": "unknown", "redis": "unknown"}
    
    # Check DB
    try:
        db.execute(text("SELECT 1"))
        status["db"] = "connected"
    except Exception as e:
        status["db"] = f"error: {str(e)}"
        status["status"] = "degraded"

    # Check Redis
    try:
        r = get_redis_client()
        if r and r.ping():
            status["redis"] = "connected"
        else:
            status["redis"] = "unreachable"
            status["status"] = "degraded"
    except Exception as e:
        status["redis"] = f"error: {str(e)}"
        status["status"] = "degraded"
        
    return status
