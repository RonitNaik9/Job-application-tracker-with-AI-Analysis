import redis
import json
import hashlib
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.client = None
        self._connect()
    
    def _connect(self):
        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
    
    def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        if not self.client:
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    def set(self, key: str, value: str, expiry: int = 3600) -> bool:
        """Set value in Redis with expiry (default 1 hour)"""
        if not self.client:
            return False
        try:
            self.client.setex(key, expiry, value)
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.client:
            return False
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    def hash_text(self, text: str) -> str:
        """Create hash of text for cache key"""
        return hashlib.md5(text.encode()).hexdigest()
    
    # Specific caching methods
    
    def cache_ai_analysis(self, resume_id: str, job_description: str, analysis: dict, expiry: int = 86400):
        """Cache AI analysis result (24 hour expiry)"""
        job_hash = self.hash_text(job_description)
        key = f"ai_analysis:{resume_id}:{job_hash}"
        return self.set(key, json.dumps(analysis), expiry)
    
    def get_cached_ai_analysis(self, resume_id: str, job_description: str) -> Optional[dict]:
        """Get cached AI analysis"""
        job_hash = self.hash_text(job_description)
        key = f"ai_analysis:{resume_id}:{job_hash}"
        cached = self.get(key)
        if cached:
            logger.info(f"Cache HIT for AI analysis: {key}")
            return json.loads(cached)
        logger.info(f"Cache MISS for AI analysis: {key}")
        return None
    
    def cache_active_resume(self, user_id: str, resume_data: dict, expiry: int = 3600):
        """Cache active resume (1 hour expiry)"""
        key = f"active_resume:{user_id}"
        return self.set(key, json.dumps(resume_data), expiry)
    
    def get_cached_active_resume(self, user_id: str) -> Optional[dict]:
        """Get cached active resume"""
        key = f"active_resume:{user_id}"
        cached = self.get(key)
        if cached:
            logger.info(f"Cache HIT for active resume: {user_id}")
            return json.loads(cached)
        logger.info(f"Cache MISS for active resume: {user_id}")
        return None
    
    def invalidate_user_resume_cache(self, user_id: str):
        """Invalidate cached resume when user uploads new one"""
        key = f"active_resume:{user_id}"
        self.delete(key)
        logger.info(f"Invalidated resume cache for user: {user_id}")

# Singleton instance
redis_service = RedisService()