from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import date

class PredictResponse(BaseModel):
    yield_prediction: float

class SeasonalPredictResponse(BaseModel):
    yield_t_ha: float
    confidence: float
    version: str
    features_used: Dict[str, Any]

class AdvisorRequest(BaseModel):
    region_id: int
    crop_id: int
    date_at: Optional[date] = None

class AdvisorRecommendation(BaseModel):
    title: str
    priority: str # low, medium, high
    why: str
    steps: List[str]
    time_window_days: str
    expected_impact: str

class AdvisorAlert(BaseModel):
    type: str
    severity: str # info, warning, critical
    trigger: str
    details: str
    action_now: str

class AdvisorEvidence(BaseModel):
    metrics: Dict[str, Any]
    reasoning_trace: List[str]

class AdvisorResponse(BaseModel):
    answer: str

