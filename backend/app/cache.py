from redis import Redis
from typing import Any, Optional
import json
from .config import settings
from loguru import logger

class CacheManager:
    def __init__(self):
        try:
            self.redis = Redis.from_url(settings.redis_url, decode_responses=True)
            self.default_ttl = getattr(settings, 'cache_ttl', 300)
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Running without cache.")
            self.redis = None
            self.default_ttl = 300
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if not self.redis:
            return None
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set cached value"""
        if not self.redis:
            return
        try:
            ttl = ttl or self.default_ttl
            self.redis.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete cached value"""
        if not self.redis:
            return
        try:
            self.redis.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern"""
        if not self.redis:
            return
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
    
    def get_status(self) -> dict:
        """Get cache status"""
        if not self.redis:
            return {"connected": False}
        try:
            info = self.redis.info()
            return {
                "connected": True,
                "keys": info.get("db0", {}).get("keys", 0),
                "used_memory": info.get("used_memory_human", "unknown")
            }
        except:
            return {"connected": False}

cache_manager = CacheManager()