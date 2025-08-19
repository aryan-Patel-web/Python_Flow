"""
Logging utilities for AI Social Media Automation Platform
"""
import logging
import logging.handlers
import os
import json
from datetime import datetime
from flask import request, g
from typing import Optional, Dict, Any
import sys

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'platform'):
            log_data['platform'] = record.platform
        if hasattr(record, 'action'):
            log_data['action'] = record.action
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        
        return json.dumps(log_data)

class ContextFilter(logging.Filter):
    """Add Flask request context to log records"""
    
    def filter(self, record):
        """Add context information to log record"""
        try:
            # Add request context if available
            if request:
                record.request_id = getattr(request, 'id', 'unknown')
                record.endpoint = request.endpoint
                record.method = request.method
                record.url = request.url
                record.remote_addr = request.remote_addr
                record.user_agent = request.headers.get('User-Agent', 'unknown')
            
            # Add user context if available
            if hasattr(g, 'user_id'):
                record.user_id = g.user_id
            
        except RuntimeError:
            # Outside of request context
            pass
        
        return True

def setup_logger(name: str = None, level: str = 'INFO', log_file: str = None) -> logging.Logger:
    """
    Setup application logger with proper configuration
    
    Args:
        name: Logger name (defaults to 'ai_social_automation')
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    
    Returns:
        Configured logger instance
    """
    if name is None:
        name = 'ai_social_automation'
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    json_formatter = JsonFormatter()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(ContextFilter())
    logger.addHandler(console_handler)
    
    # File handler if log_file specified
    if log_file:
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Rotating file handler (10MB max, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setFormatter(json_formatter)
        file_handler.addFilter(ContextFilter())
        logger.addHandler(file_handler)
    
    # Error file handler for errors and above
    error_log_file = os.environ.get('ERROR_LOG_FILE', 'logs/errors.log')
    if error_log_file:
        error_dir = os.path.dirname(error_log_file)
        if error_dir and not os.path.exists(error_dir):
            os.makedirs(error_dir)
        
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file, maxBytes=10*1024*1024, backupCount=10
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(json_formatter)
        error_handler.addFilter(ContextFilter())
        logger.addHandler(error_handler)
    
    return logger

def log_user_action(action: str, user_id: str = None, platform: str = None, 
                   details: Dict[str, Any] = None, level: str = 'INFO'):
    """
    Log user actions for audit trail
    
    Args:
        action: Action being performed
        user_id: User ID (optional, will try to get from context)
        platform: Platform name (optional)
        details: Additional details dictionary
        level: Log level
    """
    logger = logging.getLogger('user_actions')
    
    # Get user_id from context if not provided
    if user_id is None:
        user_id = getattr(g, 'user_id', 'anonymous')
    
    log_data = {
        'action': action,
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat(),
        'details': details or {}
    }
    
    if platform:
        log_data['platform'] = platform
    
    # Log with appropriate level
    log_level = getattr(logging, level.upper())
    logger.log(log_level, f"User action: {action}", extra=log_data)

def log_automation_event(platform: str, action: str, status: str, 
                        user_id: str = None, details: Dict[str, Any] = None):
    """
    Log automation events
    
    Args:
        platform: Social media platform
        action: Action being performed
        status: Status (success, failed, pending)
        user_id: User ID
        details: Additional details
    """
    logger = logging.getLogger('automation')
    
    if user_id is None:
        user_id = getattr(g, 'user_id', 'system')
    
    log_data = {
        'platform': platform,
        'action': action,
        'status': status,
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat(),
        'details': details or {}
    }
    
    level = logging.INFO if status == 'success' else logging.ERROR
    logger.log(level, f"Automation: {platform} {action} {status}", extra=log_data)

def log_api_request(endpoint: str, method: str, user_id: str = None, 
                   response_code: int = None, duration: float = None):
    """
    Log API requests
    
    Args:
        endpoint: API endpoint
        method: HTTP method
        user_id: User ID
        response_code: HTTP response code
        duration: Request duration in seconds
    """
    logger = logging.getLogger('api_requests')
    
    if user_id is None:
        user_id = getattr(g, 'user_id', 'anonymous')
    
    log_data = {
        'endpoint': endpoint,
        'method': method,
        'user_id': user_id,
        'response_code': response_code,
        'duration': duration,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if hasattr(request, 'remote_addr'):
        log_data['ip_address'] = request.remote_addr
    if hasattr(request, 'user_agent'):
        log_data['user_agent'] = str(request.user_agent)
    
    logger.info(f"API request: {method} {endpoint}", extra=log_data)

def log_content_generation(domain: str, platform: str, user_id: str = None, 
                          success: bool = True, ai_service: str = None,
                          content_length: int = None, generation_time: float = None):
    """
    Log content generation events
    
    Args:
        domain: Content domain
        platform: Target platform
        user_id: User ID
        success: Whether generation was successful
        ai_service: AI service used (mistral, groq)
        content_length: Length of generated content
        generation_time: Time taken to generate content
    """
    logger = logging.getLogger('content_generation')
    
    if user_id is None:
        user_id = getattr(g, 'user_id', 'system')
    
    log_data = {
        'domain': domain,
        'platform': platform,
        'user_id': user_id,
        'success': success,
        'ai_service': ai_service,
        'content_length': content_length,
        'generation_time': generation_time,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    level = logging.INFO if success else logging.WARNING
    status = 'success' if success else 'failed'
    logger.log(level, f"Content generation {status}: {domain} for {platform}", extra=log_data)

def log_billing_event(event_type: str, user_id: str, amount: float = None, 
                     plan: str = None, details: Dict[str, Any] = None):
    """
    Log billing and subscription events
    
    Args:
        event_type: Type of billing event (subscribe, cancel, payment, etc.)
        user_id: User ID
        amount: Amount involved
        plan: Subscription plan
        details: Additional details
    """
    logger = logging.getLogger('billing')
    
    log_data = {
        'event_type': event_type,
        'user_id': user_id,
        'amount': amount,
        'plan': plan,
        'timestamp': datetime.utcnow().isoformat(),
        'details': details or {}
    }
    
    logger.info(f"Billing event: {event_type}", extra=log_data)

def log_security_event(event_type: str, user_id: str = None, ip_address: str = None,
                      details: Dict[str, Any] = None, severity: str = 'INFO'):
    """
    Log security-related events
    
    Args:
        event_type: Type of security event
        user_id: User ID
        ip_address: IP address
        details: Additional details
        severity: Security event severity
    """
    logger = logging.getLogger('security')
    
    if user_id is None:
        user_id = getattr(g, 'user_id', 'unknown')
    
    if ip_address is None and hasattr(request, 'remote_addr'):
        ip_address = request.remote_addr
    
    log_data = {
        'event_type': event_type,
        'user_id': user_id,
        'ip_address': ip_address,
        'severity': severity,
        'timestamp': datetime.utcnow().isoformat(),
        'details': details or {}
    }
    
    level = getattr(logging, severity.upper(), logging.INFO)
    logger.log(level, f"Security event: {event_type}", extra=log_data)

# Performance logging
class PerformanceLogger:
    """Log performance metrics"""
    
    def __init__(self, logger_name='performance'):
        self.logger = logging.getLogger(logger_name)
    
    def log_database_query(self, query_type: str, collection: str, 
                          duration: float, result_count: int = None):
        """Log database query performance"""
        log_data = {
            'query_type': query_type,
            'collection': collection,
            'duration': duration,
            'result_count': result_count,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        level = logging.WARNING if duration > 1.0 else logging.INFO
        self.logger.log(level, f"DB Query: {query_type} on {collection}", extra=log_data)
    
    def log_api_response_time(self, endpoint: str, method: str, duration: float):
        """Log API response times"""
        log_data = {
            'endpoint': endpoint,
            'method': method,
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        level = logging.WARNING if duration > 2.0 else logging.INFO
        self.logger.log(level, f"API Response: {method} {endpoint}", extra=log_data)
    
    def log_automation_performance(self, platform: str, action: str, 
                                  duration: float, success: bool):
        """Log automation performance"""
        log_data = {
            'platform': platform,
            'action': action,
            'duration': duration,
            'success': success,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        level = logging.INFO if success else logging.ERROR
        self.logger.log(level, f"Automation Performance: {platform} {action}", extra=log_data)

# Global performance logger
performance_logger = PerformanceLogger()

# Decorator for logging function performance
def log_performance(logger_name='performance'):
    """Decorator to log function performance"""
    def decorator(func):
        import time
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger = logging.getLogger(logger_name)
                logger.info(f"Function {func.__name__} completed in {duration:.3f}s", extra={
                    'function': func.__name__,
                    'duration': duration,
                    'success': True
                })
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                logger = logging.getLogger(logger_name)
                logger.error(f"Function {func.__name__} failed after {duration:.3f}s: {str(e)}", extra={
                    'function': func.__name__,
                    'duration': duration,
                    'success': False,
                    'error': str(e)
                })
                
                raise
        
        return wrapper
    return decorator