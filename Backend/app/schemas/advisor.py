from pydantic import BaseModel, Field

class AdvisorRequest(BaseModel):
    region_id: int = Field(..., ge=1)
    crop_id: int = Field(..., ge=1)

class AdvisorResponse(BaseModel):
    answer: str  # texte lisible (Markdown)
