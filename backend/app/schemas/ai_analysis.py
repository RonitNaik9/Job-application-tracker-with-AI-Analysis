from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from app.models.ai_analysis import AnalysisStatus

# Response schemas
class AIAnalysisResponse(BaseModel):
    id: UUID
    application_id: UUID
    resume_id: UUID
    match_score: int | None
    matching_skills: dict | None
    missing_skills: dict | None
    suggestions: str | None
    analysis_status: AnalysisStatus
    error_message: str | None
    analyzed_at: datetime | None
    created_at: datetime
    
    class Config:
        from_attributes = True