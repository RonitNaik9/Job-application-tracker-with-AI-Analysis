from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserResponse,
    Token,
    TokenData
)
from app.schemas.resume import (
    ResumeCreate,
    ResumeUpdate,
    ResumeResponse,
    ResumeListResponse
)
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationStatusUpdate,
    ApplicationResponse,
    ApplicationListResponse
)
from app.schemas.ai_analysis import AIAnalysisResponse
from app.schemas.interaction import (
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse
)
from app.schemas.analytics import (
    AnalyticsSummary,
    ApplicationTrend,
    InsightResponse
)

__all__ = [
    # User
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenData",
    # Resume
    "ResumeCreate",
    "ResumeUpdate",
    "ResumeResponse",
    "ResumeListResponse",
    # Application
    "ApplicationCreate",
    "ApplicationUpdate",
    "ApplicationStatusUpdate",
    "ApplicationResponse",
    "ApplicationListResponse",
    # AI Analysis
    "AIAnalysisResponse",
    # Interaction
    "InteractionCreate",
    "InteractionUpdate",
    "InteractionResponse",
    # Analytics
    "AnalyticsSummary",
    "ApplicationTrend",
    "InsightResponse",
]