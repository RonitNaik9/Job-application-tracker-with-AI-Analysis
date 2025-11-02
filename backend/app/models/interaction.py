from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class InteractionType(enum.Enum):
    phone_screen = "phone_screen"
    technical_interview = "technical_interview"
    behavioral_interview = "behavioral_interview"
    offer_received = "offer_received"
    rejection = "rejection"
    follow_up_email = "follow_up_email"

class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_type = Column(SQLEnum(InteractionType), nullable=False)
    interaction_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    application = relationship("Application", back_populates="interactions")