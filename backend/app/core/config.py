from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI
    GEMINI_API_KEY: str
    
    # App
    APP_NAME: str = "Job Tracker API"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()