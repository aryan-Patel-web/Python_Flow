from datetime import datetime
from typing import Dict, Any, Optional

def create_response(
    success: bool,
    message: str,
    data: Optional[Any] = None,
    status_code: int = 200,
    errors: Optional[Dict] = None
) -> Dict:
    """
    Create standardized API response format
    
    Args:
        success: Whether the operation was successful
        message: Human-readable message
        data: Response data (optional)
        status_code: HTTP status code
        errors: Error details (optional)
    
    Returns:
        Standardized response dictionary
    """
    response = {
        'success': success,
        'message': message,
        'timestamp': datetime.utcnow().isoformat(),
        'status_code': status_code
    }
    
    if data is not None:
        response['data'] = data
    
    if errors:
        response['errors'] = errors
    
    return response

def success_response(
    message: str,
    data: Optional[Any] = None,
    status_code: int = 200
) -> Dict:
    """Create success response"""
    return create_response(True, message, data, status_code)

def error_response(
    message: str,
    status_code: int = 400,
    errors: Optional[Dict] = None,
    data: Optional[Any] = None
) -> Dict:
    """Create error response"""
    return create_response(False, message, data, status_code, errors)

def validation_error_response(errors: Dict) -> Dict:
    """Create validation error response"""
    return create_response(
        False,
        "Validation failed",
        None,
        422,
        errors
    )

def not_found_response(resource: str = "Resource") -> Dict:
    """Create not found response"""
    return create_response(
        False,
        f"{resource} not found",
        None,
        404
    )

def unauthorized_response(message: str = "Unauthorized") -> Dict:
    """Create unauthorized response"""
    return create_response(
        False,
        message,
        None,
        401
    )

def forbidden_response(message: str = "Access forbidden") -> Dict:
    """Create forbidden response"""
    return create_response(
        False,
        message,
        None,
        403
    )

def server_error_response(message: str = "Internal server error") -> Dict:
    """Create server error response"""
    return create_response(
        False,
        message,
        None,
        500
    )