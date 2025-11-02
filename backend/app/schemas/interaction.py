from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID
from app.models.interaction import InteractionType

# Request schemas
class InteractionCreate(BaseModel):
    application_id: UUID
    interaction_type: InteractionType
    interaction_date: date
    notes: str | None = None

class InteractionUpdate(BaseModel):
    interaction_type: InteractionType | None = None
    interaction_date: date | None = None
    notes: str | None = None

# Response schemas
class InteractionResponse(BaseModel):
    id: UUID
    application_id: UUID
    interaction_type: InteractionType
    interaction_date: date
    notes: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True