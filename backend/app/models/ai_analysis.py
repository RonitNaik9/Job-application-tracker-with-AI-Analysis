from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class AnalysisStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

class AIAnalysis(Base):
    __tablename__ = "ai_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=True)  # Changed to nullable=True
    match_score = Column(Integer, nullable=True)
    matching_skills = Column(JSONB, nullable=True)
    missing_skills = Column(JSONB, nullable=True)
    suggestions = Column(Text, nullable=True)
    analysis_status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.pending)
    error_message = Column(Text, nullable=True)
    analyzed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    application = relationship("Application", back_populates="ai_analysis")
    resume = relationship("Resume", back_populates="ai_analyses")