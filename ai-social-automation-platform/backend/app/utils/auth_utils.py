import jwt
import logging
from functools import wraps
from flask import request, jsonify, current_app
from models.user import User

logger = logging.getLogger(__name__)

def token_required(f):
    """Decorator to require JWT token authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Token format invalid'}), 401
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        try:
            # Verify token and get user
            current_user = User.verify_token(token)
            
            if not current_user:
                return jsonify({'error': 'Token invalid or expired'}), 401
            
            if not current_user.is_active:
                return jsonify({'error': 'Account deactivated'}), 401
            
            return f(current_user, *args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid'}), 401
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return jsonify({'error': 'Token verification failed'}), 401
    
    return decorated

def optional_token(f):
    """Decorator for optional authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        current_user = None
        
        # Get token from headers if present
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
                current_user = User.verify_token(token)
            except Exception:
                pass  # Token invalid, but that's ok for optional auth
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Token format invalid'}), 401
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        try:
            current_user = User.verify_token(token)
            
            if not current_user:
                return jsonify({'error': 'Token invalid or expired'}), 401
            
            # Check admin privileges (you'll need to add this field to User model)
            if not getattr(current_user, 'is_admin', False):
                return jsonify({'error': 'Admin privileges required'}), 403
            
            return f(current_user, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Admin token verification error: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated

def get_current_user_from_token():
    """Get current user from request token"""
    try:
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(" ")[1]
            return User.verify_token(token)
        return None
    except Exception:
        return None