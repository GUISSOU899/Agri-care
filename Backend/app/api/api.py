from fastapi import APIRouter
from app.api.endpoints import health
from app.api.routers import regions, crops, forecast, alerts, ml

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(regions.router, prefix="/regions", tags=["regions"])
api_router.include_router(crops.router, prefix="/crops", tags=["crops"])
api_router.include_router(forecast.router, prefix="/forecast", tags=["forecast"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(ml.router, prefix="/ml", tags=["ml"])
