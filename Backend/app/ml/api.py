from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.season_yield_service import SeasonYieldService

app = FastAPI(title="Agri-Care ML Service")

class PredictionRequest(BaseModel):
    region_id: int
    crop_id: int
    year: int

@app.get("/health")
def health():
    return {"status": "ok", "service": "ml"}

@app.post("/predict/seasonal")
def predict_seasonal(req: PredictionRequest):
    """
    Predict yield for a given season context.
    The service pulls weather/soil features from DB itself.
    """
    result, error = SeasonYieldService.predict_seasonal_yield(req.region_id, req.crop_id, req.year)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result
