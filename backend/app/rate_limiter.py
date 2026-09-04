from datetime import datetime, timedelta
from typing import Dict, List
from .config import settings

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, List[datetime]] = {}
        self.limit = settings.rate_limit_requests if hasattr(settings, 'rate_limit_requests') else 100
        self.period = settings.rate_limit_period if hasattr(settings, 'rate_limit_period') else 60
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if client is allowed to make a request"""
        now = datetime.utcnow()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Clean old requests
        cutoff = now - timedelta(seconds=self.period)
        self.requests[client_ip] = [t for t in self.requests[client_ip] if t > cutoff]
        
        # Check limit
        if len(self.requests[client_ip]) >= self.limit:
            return False
        
        # Add request
        self.requests[client_ip].append(now)
        return True
    
    def get_remaining(self, client_ip: str) -> int:
        """Get remaining requests for client"""
        if client_ip not in self.requests:
            return self.limit
        
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.period)
        recent = [t for t in self.requests[client_ip] if t > cutoff]
        
        return max(0, self.limit - len(recent))

rate_limiter = RateLimiter()