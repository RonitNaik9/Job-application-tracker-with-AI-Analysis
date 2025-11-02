from pydantic import BaseModel
from app.models.application import ApplicationStatus

class AnalyticsSummary(BaseModel):
    total_applications: int
    by_status: dict[ApplicationStatus, int]
    response_rate: float
    avg_days_to_response: float | None
    applications_this_week: int
    applications_this_month: int

class ApplicationTrend(BaseModel):
    date: str
    count: int

class InsightResponse(BaseModel):
    insight_type: str
    message: str
    data: dict | None = None