from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

# Request schemas
class ResumeCreate(BaseModel):
    content: str
    file_url: str | None = None

class ResumeUpdate(BaseModel):
    content: str | None = None
    file_url: str | None = None
    is_active: bool | None = None

# Response schemas
class ResumeResponse(BaseModel):
    id: UUID
    user_id: UUID
    content: str
    parsed_skills: dict | None
    file_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ResumeListResponse(BaseModel):
    id: UUID
    is_active: bool
    created_at: datetime
    parsed_skills: dict | None
    
    class Config:
        from_attributes = True