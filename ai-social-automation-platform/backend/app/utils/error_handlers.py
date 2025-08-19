"""
Centralized error handling utilities
"""
import logging
import traceback
from functools import wraps
from flask import jsonify, request, g
from werkzeug.exceptions import HTTPException
from mongoengine.errors import ValidationError, NotUniqueError, DoesNotExist
from datetime import datetime
import sys

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom API exception class"""
    
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        error_dict = {
            'error': True,
            'message': self.message,
            'status_code': self.status_code,
            'timestamp': datetime.utcnow().isoformat()
        }
        if self.payload:
            error_dict['details'] = self.payload
        return error_dict

class AutomationError(Exception):
    """Exception for automation-related errors"""
    
    def __init__(self, platform, action, message, details=None):
        super().__init__(message)
        self.platform = platform
        self.action = action
        self.message = message
        self.details = details or {}
    
    def to_dict(self):
        return {
            'error': True,
            'type': 'automation_error',
            'platform': self.platform,
            'action': self.action,
            'message': self.message,
            'details': self.details,
            'timestamp': datetime.utcnow().isoformat()
        }

class ValidationError(Exception):
    """Custom validation error"""
    
    def __init__(self, field, message, value=None):
        super().__init__(message)
        self.field = field
        self.message = message
        self.value = value
    
    def to_dict(self):
        return {
            'error': True,
            'type': 'validation_error',
            'field': self.field,
            'message': self.message,
            'value': self.value,
            'timestamp': datetime.utcnow().isoformat()
        }

def handle_api_error(error):
    """Global API error handler"""
    error_id = f"error_{int(datetime.utcnow().timestamp())}"
    
    try:
        # Log error details
        logger.error(f"API Error [{error_id}]: {str(error)}", extra={
            'error_id': error_id,
            'user_id': getattr(g, 'user_id', None),
            'endpoint': request.endpoint,
            'method': request.method,
            'url': request.url,
            'user_agent': request.headers.get('User-Agent'),
            'ip_address': request.remote_addr,
            'traceback': traceback.format_exc()
        })
        
        # Handle different error types
        if isinstance(error, APIError):
            response = error.to_dict()
            response['error_id'] = error_id
            return jsonify(response), error.status_code
        
        elif isinstance(error, HTTPException):
            return jsonify({
                'error': True,
                'message': error.description,
                'status_code': error.code,
                'error_id': error_id,
                'timestamp': datetime.utcnow().isoformat()
            }), error.code
        
        elif isinstance(error, (mongoengine.ValidationError, ValidationError)):
            return jsonify({
                'error': True,
                'type': 'validation_error',
                'message': str(error),
                'error_id': error_id,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        elif isinstance(error, NotUniqueError):
            return jsonify({
                'error': True,
                'type': 'duplicate_error',
                'message': 'Resource already exists',
                'error_id': error_id,
                'timestamp': datetime.utcnow().isoformat()
            }), 409
        
        elif isinstance(error, DoesNotExist):
            return jsonify({
                'error': True,
                'type': 'not_found',
                'message': 'Resource not found',
                'error_id': error_id,
                'timestamp': datetime.utcnow().isoformat()
            }), 404
        
        else:
            # Generic error
            return jsonify({
                'error': True,
                'type': 'internal_error',
                'message': 'An internal error occurred',
                'error_id': error_id,
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    
    except Exception as e:
        # Fallback error handling
        logger.critical(f"Error in error handler: {str(e)}")
        return jsonify({
            'error': True,
            'message': 'Critical system error',
            'error_id': error_id,
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def handle_automation_error(error):
    """Handle automation-specific errors"""
    if isinstance(error, AutomationError):
        logger.error(f"Automation Error - Platform: {error.platform}, Action: {error.action}, Message: {error.message}")
        return error.to_dict()
    
    return {
        'error': True,
        'type': 'automation_error',
        'message': str(error),
        'timestamp': datetime.utcnow().isoformat()
    }

def safe_execute(func, *args, **kwargs):
    """Safely execute a function with error handling"""
    try:
        return {'success': True, 'result': func(*args, **kwargs)}
    except Exception as e:
        logger.error(f"Safe execution failed: {str(e)}")
        return {'success': False, 'error': str(e)}

def api_error_handler(func):
    """Decorator for automatic API error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return handle_api_error(e)
    return wrapper

def automation_error_handler(func):
    """Decorator for automation error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_data = handle_automation_error(e)
            # Log to automation logs
            log_automation_error(error_data)
            raise AutomationError(
                platform=error_data.get('platform', 'unknown'),
                action=error_data.get('action', 'unknown'),
                message=error_data.get('message', str(e)),
                details=error_data.get('details', {})
            )
    return wrapper

def log_automation_error(error_data):
    """Log automation errors to database"""
    try:
        from app.models.automation_log import AutomationLog
        
        log_entry = AutomationLog(
            user_id=getattr(g, 'user_id', None),
            platform=error_data.get('platform'),
            action=error_data.get('action'),
            status='failed',
            error_message=error_data.get('message'),
            error_details=error_data.get('details', {}),
            timestamp=datetime.utcnow()
        )
        log_entry.save()
    except Exception as e:
        logger.error(f"Failed to log automation error: {str(e)}")

def register_error_handlers(app):
    """Register all error handlers with Flask app"""
    
    @app.errorhandler(APIError)
    def handle_api_error_flask(error):
        return handle_api_error(error)
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'error': True,
            'message': 'Endpoint not found',
            'status_code': 404,
            'timestamp': datetime.utcnow().isoformat()
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({
            'error': True,
            'message': 'Method not allowed',
            'status_code': 405,
            'timestamp': datetime.utcnow().isoformat()
        }), 405
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'error': True,
            'message': 'Internal server error',
            'status_code': 500,
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    @app.errorhandler(ValidationError)
    def handle_validation_error_flask(error):
        return jsonify(error.to_dict()), 400
    
    @app.errorhandler(AutomationError)
    def handle_automation_error_flask(error):
        return jsonify(error.to_dict()), 400

# Custom exception classes for specific scenarios
class CredentialsError(APIError):
    """Exception for credential-related errors"""
    
    def __init__(self, platform, message):
        super().__init__(f"{platform.title()} credentials error: {message}", 401)
        self.platform = platform

class ContentGenerationError(APIError):
    """Exception for content generation errors"""
    
    def __init__(self, service, message):
        super().__init__(f"Content generation failed ({service}): {message}", 500)
        self.service = service

class PlatformAPIError(APIError):
    """Exception for platform API errors"""
    
    def __init__(self, platform, api_response=None, message=None):
        if not message:
            message = f"{platform.title()} API error"
        super().__init__(message, 503)
        self.platform = platform
        self.api_response = api_response

# Error monitoring utilities
class ErrorMonitor:
    """Monitor and track application errors"""
    
    def __init__(self):
        self.error_counts = {}
        self.recent_errors = []
    
    def track_error(self, error_type, error_message, context=None):
        """Track error occurrence"""
        timestamp = datetime.utcnow()
        
        # Count errors by type
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        # Store recent errors (keep last 100)
        error_data = {
            'type': error_type,
            'message': error_message,
            'context': context or {},
            'timestamp': timestamp,
            'count': self.error_counts[error_type]
        }
        
        self.recent_errors.append(error_data)
        
        # Keep only last 100 errors
        if len(self.recent_errors) > 100:
            self.recent_errors = self.recent_errors[-100:]
    
    def get_error_summary(self):
        """Get summary of recent errors"""
        return {
            'total_errors': sum(self.error_counts.values()),
            'error_counts': self.error_counts,
            'recent_errors': self.recent_errors[-10:],  # Last 10 errors
            'most_common_errors': sorted(
                self.error_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        }
    
    def should_alert(self, error_type, threshold=10, time_window=3600):
        """Check if error frequency requires alerting"""
        recent_count = sum(1 for error in self.recent_errors 
                          if error['type'] == error_type and 
                          (datetime.utcnow() - error['timestamp']).seconds < time_window)
        return recent_count >= threshold

# Global error monitor
error_monitor = ErrorMonitor()

def track_error(error_type, error_message, context=None):
    """Global error tracking function"""
    error_monitor.track_error(error_type, error_message, context)

# Recovery utilities
def retry_with_backoff(func, max_retries=3, backoff_factor=2, *args, **kwargs):
    """Retry function with exponential backoff"""
    import time
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            wait_time = backoff_factor ** attempt
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time}s...")
            time.sleep(wait_time)

def circuit_breaker(failure_threshold=5, recovery_timeout=60, expected_exception=Exception):
    """Circuit breaker pattern decorator"""
    def decorator(func):
        func._failure_count = 0
        func._last_failure_time = None
        func._circuit_open = False
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if circuit is open
            if func._circuit_open:
                if time.time() - func._last_failure_time > recovery_timeout:
                    func._circuit_open = False
                    func._failure_count = 0
                else:
                    raise APIError("Service temporarily unavailable", 503)
            
            try:
                result = func(*args, **kwargs)
                # Reset failure count on success
                func._failure_count = 0
                return result
            
            except expected_exception as e:
                func._failure_count += 1
                func._last_failure_time = time.time()
                
                if func._failure_count >= failure_threshold:
                    func._circuit_open = True
                    logger.error(f"Circuit breaker opened for {func.__name__}")
                
                raise e
        
        return wrapper
    return decorator