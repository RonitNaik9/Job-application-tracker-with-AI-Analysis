from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, applications, resumes

app = FastAPI(title=settings.APP_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(applications.router, prefix="/api/v1")
app.include_router(resumes.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Job Tracker API is running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "kafka": "connected"
    }