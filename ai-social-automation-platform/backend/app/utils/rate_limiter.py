"""
Rate limiting utilities for API and automation requests
"""
import time
import redis
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, jsonify, g
import logging
import hashlib





logger = logging.getLogger(__name__)

class RateLimiter:
    """Redis-based rate limiter with multiple strategies"""
    


    
    def __init__(self, redis_client=None, prefix="rate_limit"):
        """Initialize rate limiter"""
        self.redis_client = redis_client or redis.Redis(
            host='localhost', 
            port=6379, 
            db=0, 
            decode_responses=True
        )
        self.prefix = prefix
    
    
    def _get_key(self, identifier: str, window: str) -> str:
        """Generate Redis key for rate limiting"""
        return f"{self.prefix}:{identifier}:{window}"
    
    def _get_window_start(self, window_size: int) -> int:
        """Get the start of current time window"""
        return int(time.time()) // window_size * window_size
    
    def check_rate_limit(self, identifier: str, limit: int, window: int) -> Dict[str, Any]:
        """
        Check if request is within rate limit
        
        Args:
            identifier: Unique identifier (user_id, ip, etc.)
            limit: Number of requests allowed
            window: Time window in seconds
        
        Returns:
            Dict with rate limit status
        """
        try:
            window_start = self._get_window_start(window)
            key = self._get_key(identifier, str(window_start))
            
            # Get current count
            current_count = self.redis_client.get(key)
            current_count = int(current_count) if current_count else 0
            
            # Calculate remaining requests and reset time
            remaining = max(0, limit - current_count)
            reset_time = window_start + window
            
            if current_count >= limit:
                return {
                    'allowed': False,
                    'limit': limit,
                    'remaining': 0,
                    'reset_time': reset_time,
                    'retry_after': reset_time - int(time.time())
                }
            
            # Increment counter
            pipeline = self.redis_client.pipeline()
            pipeline.incr(key)
            pipeline.expire(key, window)
            pipeline.execute()
            
            return {
                'allowed': True,
                'limit': limit,
                'remaining': remaining - 1,
                'reset_time': reset_time,
                'retry_after': 0
            }
        
        except Exception as e:
            logger.error(f"Rate limiter error: {str(e)}")
            # Allow request if rate limiter fails
            return {
                'allowed': True,
                'limit': limit,
                'remaining': limit - 1,
                'reset_time': int(time.time()) + window,
                'retry_after': 0
            }
    
    def sliding_window_check(self, identifier: str, limit: int, window: int) -> Dict[str, Any]:
        """
        Sliding window rate limiting (more precise but resource intensive)
        """
        try:
            now = time.time()
            key = self._get_key(identifier, "sliding")
            
            # Remove old entries
            self.redis_client.zremrangebyscore(key, 0, now - window)
            
            # Count current entries
            current_count = self.redis_client.zcard(key)
            
            if current_count >= limit:
                # Get oldest entry to calculate retry_after
                oldest = self.redis_client.zrange(key, 0, 0, withscores=True)
                retry_after = int(oldest[0][1] + window - now) if oldest else window
                
                return {
                    'allowed': False,
                    'limit': limit,
                    'remaining': 0,
                    'reset_time': int(now + retry_after),
                    'retry_after': max(1, retry_after)
                }
            
            # Add current request
            self.redis_client.zadd(key, {str(now): now})
            self.redis_client.expire(key, window)
            
            return {
                'allowed': True,
                'limit': limit,
                'remaining': limit - current_count - 1,
                'reset_time': int(now + window),
                'retry_after': 0
            }
        
        except Exception as e:
            logger.error(f"Sliding window rate limiter error: {str(e)}")
            return {
                'allowed': True,
                'limit': limit,
                'remaining': limit - 1,
                'reset_time': int(time.time()) + window,
                'retry_after': 0
            }

# Global rate limiter instance
_rate_limiter = None

def get_rate_limiter():
    """Get global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter

def rate_limit(limit: int, window: int, per: str = 'user', sliding: bool = False):
    """
    Decorator for rate limiting Flask routes
    
    Args:
        limit: Number of requests allowed
        window: Time window in seconds
        per: Rate limit per ('user', 'ip', 'endpoint')
        sliding: Use sliding window algorithm
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get identifier based on 'per' parameter
            if per == 'user':
                identifier = getattr(g, 'user_id', None)
                if not identifier:
                    identifier = request.remote_addr
            elif per == 'ip':
                identifier = request.remote_addr
            elif per == 'endpoint':
                identifier = f"{request.endpoint}:{request.remote_addr}"
            else:
                identifier = request.remote_addr
            
            # Hash identifier for privacy
            identifier_hash = hashlib.md5(str(identifier).encode()).hexdigest()
            
            # Check rate limit
            limiter = get_rate_limiter()
            if sliding:
                result = limiter.sliding_window_check(identifier_hash, limit, window)
            else:
                result = limiter.check_rate_limit(identifier_hash, limit, window)
            
            if not result['allowed']:
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Limit: {limit} per {window} seconds',
                    'retry_after': result['retry_after']
                })
                response.status_code = 429
                response.headers['X-RateLimit-Limit'] = str(limit)
                response.headers['X-RateLimit-Remaining'] = '0'
                response.headers['X-RateLimit-Reset'] = str(result['reset_time'])
                response.headers['Retry-After'] = str(result['retry_after'])
                return response
            
            # Add rate limit headers to successful responses
            response = func(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(limit)
                response.headers['X-RateLimit-Remaining'] = str(result['remaining'])
                response.headers['X-RateLimit-Reset'] = str(result['reset_time'])
            
            return response
        
        return wrapper
    return decorator

# Platform-specific rate limiters
class PlatformRateLimiter:
    """Rate limiter for social media platform APIs"""
    
    # Platform-specific limits (requests per hour)
    PLATFORM_LIMITS = {
        'instagram': {'posts': 100, 'likes': 1000, 'follows': 200},
        'facebook': {'posts': 200, 'likes': 5000, 'shares': 100},
        'youtube': {'uploads': 50, 'comments': 1000},
        'twitter': {'tweets': 300, 'likes': 1000, 'follows': 400},
        'linkedin': {'posts': 100, 'connections': 500}
    }
    
    def __init__(self, redis_client=None):
        self.limiter = RateLimiter(redis_client, "platform_rate_limit")
    
    def check_platform_limit(self, user_id: str, platform: str, action: str) -> Dict[str, Any]:
        """Check rate limit for platform action"""
        limits = self.PLATFORM_LIMITS.get(platform, {})
        if action not in limits:
            return {'allowed': True, 'limit': 1000, 'remaining': 999}
        
        limit = limits[action]
        identifier = f"{user_id}:{platform}:{action}"
        
        return self.limiter.check_rate_limit(identifier, limit, 3600)  # 1 hour window
    
    def is_action_allowed(self, user_id: str, platform: str, action: str) -> bool:
        """Simple check if action is allowed"""
        result = self.check_platform_limit(user_id, platform, action)
        return result['allowed']

def platform_rate_limit(platform: str, action: str):
    """Decorator for platform-specific rate limiting"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = getattr(g, 'user_id', None)
            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            platform_limiter = PlatformRateLimiter()
            result = platform_limiter.check_platform_limit(user_id, platform, action)
            
            if not result['allowed']:
                return jsonify({
                    'error': f'{platform.title()} rate limit exceeded',
                    'message': f'Too many {action} requests for {platform}',
                    'retry_after': result.get('retry_after', 3600)
                }), 429
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# Utility functions
def get_user_rate_limit_status(user_id: str) -> Dict[str, Any]:
    """Get rate limit status for all platforms for a user"""
    platform_limiter = PlatformRateLimiter()
    status = {}
    
    for platform, actions in platform_limiter.PLATFORM_LIMITS.items():
        status[platform] = {}
        for action, limit in actions.items():
            result = platform_limiter.check_platform_limit(user_id, platform, action)
            status[platform][action] = {
                'limit': limit,
                'remaining': result.get('remaining', limit),
                'reset_time': result.get('reset_time', int(time.time()) + 3600)
            }
    
    return status

def reset_user_rate_limits(user_id: str, platform: str = None):
    """Reset rate limits for a user (admin function)"""
    try:
        limiter = get_rate_limiter()
        pattern = f"platform_rate_limit:{user_id}:*"
        
        if platform:
            pattern = f"platform_rate_limit:{user_id}:{platform}:*"
        
        keys = limiter.redis_client.keys(pattern)
        if keys:
            limiter.redis_client.delete(*keys)
        
        return True
    except Exception as e:
        logger.error(f"Error resetting rate limits: {str(e)}")
        return False