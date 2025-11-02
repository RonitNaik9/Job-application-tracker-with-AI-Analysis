from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class ApplicationStatus(enum.Enum):
    applied = "applied"
    screening = "screening"
    interviewing = "interviewing"
    offered = "offered"
    rejected = "rejected"
    withdrawn = "withdrawn"

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_name = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    job_url = Column(String, nullable=True)
    job_description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    salary_range = Column(String, nullable=True)
    date_applied = Column(Date, nullable=False, index=True)
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.applied, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="applications")
    ai_analysis = relationship("AIAnalysis", back_populates="application", uselist=False)
    interactions = relationship("Interaction", back_populates="application", cascade="all, delete-orphan")