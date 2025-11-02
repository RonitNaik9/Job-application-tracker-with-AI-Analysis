from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID
from app.models.application import ApplicationStatus

# Request schemas
class ApplicationCreate(BaseModel):
    company_name: str
    job_title: str
    job_url: str | None = None
    job_description: str | None = None
    location: str | None = None
    salary_range: str | None = None
    date_applied: date
    notes: str | None = None

class ApplicationUpdate(BaseModel):
    company_name: str | None = None
    job_title: str | None = None
    job_url: str | None = None
    job_description: str | None = None
    location: str | None = None
    salary_range: str | None = None
    date_applied: date | None = None
    status: ApplicationStatus | None = None
    notes: str | None = None

class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus

# Response schemas
class ApplicationResponse(BaseModel):
    id: UUID
    user_id: UUID
    company_name: str
    job_title: str
    job_url: str | None
    job_description: str | None
    location: str | None
    salary_range: str | None
    date_applied: date
    status: ApplicationStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ApplicationListResponse(BaseModel):
    id: UUID
    company_name: str
    job_title: str
    location: str | None
    date_applied: date
    status: ApplicationStatus
    
    class Config:
        from_attributes = True