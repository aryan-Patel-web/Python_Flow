#!/usr/bin/env python3
"""
Authentication Helper Functions for VelocityPost.ai
Provides JWT utilities, password hashing, and security functions
"""

import os
import re
import jwt
import secrets
import hashlib
import base64
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRY_HOURS = 24
REFRESH_TOKEN_EXPIRY_DAYS = 30

# Password Configuration
PASSWORD_MIN_LENGTH = 8
PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]')

class AuthError(Exception):
    """Custom authentication error"""
    def __init__(self, message, status_code=401):
        super().__init__(message)
        self.status_code = status_code

class JWTManager:
    """JWT Token Management Class"""
    
    def __init__(self, secret_key=None, algorithm='HS256'):
        self.secret_key = secret_key or JWT_SECRET
        self.algorithm = algorithm
    
    def generate_token(self, user_id, email, token_type='access', expires_in=None):
        """Generate JWT access or refresh token"""
        if expires_in is None:
            if token_type == 'refresh':
                expires_in = timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS)
            else:
                expires_in = timedelta(hours=JWT_EXPIRY_HOURS)
        
        payload = {
            'user_id': str(user_id),
            'email': email,
            'token_type': token_type,
            'exp': datetime.utcnow() + expires_in,
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(16)  # JWT ID for token blacklisting
        }
        
        try:
            return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        except Exception as e:
            logger.error(f"Token generation failed: {str(e)}")
            raise AuthError("Failed to generate token")
    
    def verify_token(self, token, token_type='access'):
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get('token_type') != token_type:
                raise AuthError("Invalid token type")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthError(f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise AuthError("Token verification failed")
    
    def refresh_token(self, refresh_token):
        """Generate new access token from refresh token"""
        try:
            payload = self.verify_token(refresh_token, 'refresh')
            user_id = payload['user_id']
            email = payload['email']
            
            # Generate new access token
            new_access_token = self.generate_token(user_id, email, 'access')
            
            return {
                'access_token': new_access_token,
                'token_type': 'Bearer',
                'expires_in': JWT_EXPIRY_HOURS * 3600
            }
            
        except AuthError:
            raise
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise AuthError("Token refresh failed")

class PasswordManager:
    """Password Management Class"""
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if not password:
            return False, "Password is required"
        
        if len(password) < PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[@$!%*?&]', password):
            return False, "Password must contain at least one special character (@$!%*?&)"
        
        # Check for common weak passwords
        weak_passwords = ['password', '12345678', 'qwerty', 'admin', 'letmein']
        if password.lower() in weak_passwords:
            return False, "Password is too common. Please choose a stronger password"
        
        return True, "Password is valid"
    
    @staticmethod
    def hash_password(password):
        """Hash password using secure method"""
        return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    @staticmethod
    def verify_password(password_hash, password):
        """Verify password against hash"""
        return check_password_hash(password_hash, password)
    
    @staticmethod
    def generate_reset_token():
        """Generate secure password reset token"""
        return secrets.token_urlsafe(32)

class EmailValidator:
    """Email Validation Class"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            return False, "Email is required"
        
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        if not email_pattern.match(email):
            return False, "Invalid email format"
        
        # Check for disposable email domains (basic check)
        disposable_domains = [
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
            'mailinator.com', 'yopmail.com', 'temp-mail.org'
        ]
        
        domain = email.split('@')[1].lower()
        if domain in disposable_domains:
            return False, "Disposable email addresses are not allowed"
        
        return True, "Email is valid"

class TokenEncryption:
    """Token Encryption for OAuth tokens"""
    
    def __init__(self, encryption_key=None):
        if encryption_key is None:
            encryption_key = os.getenv('TOKEN_ENCRYPTION_KEY')
            if not encryption_key:
                # Generate a key for development (not recommended for production)
                encryption_key = Fernet.generate_key()
                logger.warning("Using generated encryption key. Set TOKEN_ENCRYPTION_KEY in production!")
        
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()
        
        self.cipher = Fernet(encryption_key)
    
    def encrypt_token(self, token):
        """Encrypt access token for secure storage"""
        if not token:
            return None
        
        try:
            encrypted = self.cipher.encrypt(token.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Token encryption failed: {str(e)}")
            return None
    
    def decrypt_token(self, encrypted_token):
        """Decrypt access token for API calls"""
        if not encrypted_token:
            return None
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_token.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Token decryption failed: {str(e)}")
            return None

class StateManager:
    """OAuth State Management"""
    
    @staticmethod
    def generate_state(user_id, platform, timestamp=None):
        """Generate secure state parameter for OAuth"""
        if timestamp is None:
            timestamp = str(int(datetime.utcnow().timestamp()))
        
        random_str = secrets.token_urlsafe(16)
        data = f"{user_id}:{platform}:{timestamp}:{random_str}"
        
        return base64.urlsafe_b64encode(data.encode()).decode()
    
    @staticmethod
    def verify_state(state, user_id, platform, max_age_minutes=10):
        """Verify OAuth state parameter"""
        try:
            decoded = base64.urlsafe_b64decode(state.encode()).decode()
            parts = decoded.split(':')
            
            if len(parts) < 4:
                return False, "Invalid state format"
            
            state_user_id, state_platform, timestamp, random_str = parts
            
            # Verify user ID and platform
            if state_user_id != str(user_id):
                return False, "User ID mismatch"
            
            if state_platform != platform:
                return False, "Platform mismatch"
            
            # Verify timestamp (not too old)
            state_time = datetime.fromtimestamp(int(timestamp))
            age = datetime.utcnow() - state_time
            
            if age > timedelta(minutes=max_age_minutes):
                return False, "State has expired"
            
            return True, "State is valid"
            
        except Exception as e:
            logger.error(f"State verification failed: {str(e)}")
            return False, "State verification failed"

class RateLimiter:
    """Simple rate limiting for authentication endpoints"""
    
    def __init__(self):
        self.attempts = {}  # In production, use Redis
    
    def is_rate_limited(self, key, max_attempts=5, window_minutes=15):
        """Check if key is rate limited"""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Clean old entries
        if key in self.attempts:
            self.attempts[key] = [
                attempt_time for attempt_time in self.attempts[key]
                if attempt_time > window_start
            ]
        
        # Check current attempts
        current_attempts = len(self.attempts.get(key, []))
        return current_attempts >= max_attempts
    
    def record_attempt(self, key):
        """Record a failed attempt"""
        if key not in self.attempts:
            self.attempts[key] = []
        
        self.attempts[key].append(datetime.utcnow())

# Global instances
jwt_manager = JWTManager()
password_manager = PasswordManager()
email_validator = EmailValidator()
token_encryption = TokenEncryption()
state_manager = StateManager()
rate_limiter = RateLimiter()

# Decorator functions
def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authentication required',
                'error': 'Missing or invalid authorization header'
            }), 401
        
        try:
            token = auth_header.split(' ')[1]
            payload = jwt_manager.verify_token(token)
            
            # Add user info to request
            request.user_id = payload['user_id']
            request.user_email = payload['email']
            request.token_payload = payload
            
            return f(*args, **kwargs)
            
        except AuthError as e:
            return jsonify({
                'success': False,
                'message': 'Authentication failed',
                'error': str(e)
            }), e.status_code
        except Exception as e:
            logger.error(f"Authentication decorator error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Authentication failed',
                'error': 'Invalid token'
            }), 401
    
    return decorated_function

def require_plan(allowed_plans):
    """Decorator to require specific subscription plan"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This assumes require_auth has already been applied
            if not hasattr(request, 'user_id'):
                return jsonify({
                    'success': False,
                    'message': 'Authentication required',
                    'error': 'Please authenticate first'
                }), 401
            
            # Get user's plan (you'd fetch this from database)
            # For now, we'll assume it's passed in the token or fetched separately
            user_plan = getattr(request, 'user_plan', 'free')
            
            if user_plan not in allowed_plans:
                return jsonify({
                    'success': False,
                    'message': 'Subscription required',
                    'error': f'This feature requires {" or ".join(allowed_plans)} plan'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(max_attempts=5, window_minutes=15, key_func=None):
    """Decorator for rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Determine rate limit key
            if key_func:
                key = key_func()
            else:
                key = request.remote_addr or 'unknown'
            
            # Check rate limit
            if rate_limiter.is_rate_limited(key, max_attempts, window_minutes):
                return jsonify({
                    'success': False,
                    'message': 'Rate limit exceeded',
                    'error': f'Too many attempts. Try again in {window_minutes} minutes'
                }), 429
            
            try:
                result = f(*args, **kwargs)
                
                # If the request failed (like wrong password), record attempt
                if hasattr(result, 'status_code') and result.status_code >= 400:
                    rate_limiter.record_attempt(key)
                
                return result
                
            except Exception as e:
                # Record failed attempt
                rate_limiter.record_attempt(key)
                raise
        
        return decorated_function
    return decorator

# Utility functions
def get_client_ip():
    """Get client IP address"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    elif request.environ.get('HTTP_X_REAL_IP'):
        return request.environ['HTTP_X_REAL_IP']
    else:
        return request.environ.get('REMOTE_ADDR', 'unknown')

def generate_secure_filename(original_filename):
    """Generate secure filename for uploads"""
    if not original_filename:
        return f"upload_{secrets.token_urlsafe(8)}"
    
    # Remove dangerous characters
    safe_name = re.sub(r'[^\w\.-]', '_', original_filename)
    
    # Add random suffix to prevent conflicts
    name, ext = os.path.splitext(safe_name)
    return f"{name}_{secrets.token_urlsafe(8)}{ext}"

def validate_object_id(id_string):
    """Validate MongoDB ObjectId"""
    try:
        ObjectId(id_string)
        return True
    except:
        return False

def sanitize_input(data):
    """Basic input sanitization"""
    if isinstance(data, str):
        # Remove potentially dangerous characters
        data = re.sub(r'[<>"\']', '', data)
        return data.strip()
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    else:
        return data

def create_audit_log(user_id, action, details=None, ip_address=None):
    """Create audit log entry"""
    log_entry = {
        'user_id': user_id,
        'action': action,
        'details': details or {},
        'ip_address': ip_address or get_client_ip(),
        'user_agent': request.headers.get('User-Agent', ''),
        'timestamp': datetime.utcnow()
    }
    
    # In production, save to database
    logger.info(f"Audit log: {log_entry}")
    return log_entry

def check_password_breach(password):
    """Check if password has been compromised (simplified version)"""
    # In production, you'd integrate with HaveIBeenPwned API
    # This is a simplified local check
    
    password_hash = hashlib.sha1(password.encode()).hexdigest().upper()
    
    # For demo purposes, we'll just check against a few known bad passwords
    bad_hashes = {
        # "password"
        "5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8",
        # "123456"
        "7C4A8D09CA3762AF61E59520943DC26494F8941B",
        # "admin"
        "D033E22AE348AEB5660FC2140AEC35850C4DA997"
    }
    
    if password_hash in bad_hashes:
        return True, "This password has been compromised in data breaches"
    
    return False, "Password appears secure"

def validate_user_input(data, required_fields=None):
    """Validate user input data"""
    errors = {}
    
    if not data:
        return False, {"general": "No data provided"}
    
    # Check required fields
    if required_fields:
        for field in required_fields:
            if field not in data or not data[field]:
                errors[field] = f"{field} is required"
    
    # Validate email if present
    if 'email' in data:
        is_valid, message = email_validator.validate_email(data['email'])
        if not is_valid:
            errors['email'] = message
    
    # Validate password if present
    if 'password' in data:
        is_valid, message = password_manager.validate_password(data['password'])
        if not is_valid:
            errors['password'] = message
        else:
            # Check for breached passwords
            is_breached, breach_message = check_password_breach(data['password'])
            if is_breached:
                errors['password'] = breach_message
    
    # Validate name if present
    if 'name' in data:
        name = data['name'].strip()
        if len(name) < 2:
            errors['name'] = "Name must be at least 2 characters long"
        elif len(name) > 50:
            errors['name'] = "Name must be less than 50 characters"
        elif not re.match(r'^[a-zA-Z\s\-\.\']+$', name):
            errors['name'] = "Name contains invalid characters"
    
    return len(errors) == 0, errors

# Security headers middleware
def add_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

# Helper function for generating API responses
def create_response(success=True, message="", data=None, error=None, status_code=200):
    """Create standardized API response"""
    response_data = {
        'success': success,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response_data.update(data)
    
    if error is not None:
        response_data['error'] = error
    
    return jsonify(response_data), status_code

# Test functions
def test_auth_helpers():
    """Test authentication helper functions"""
    print("Testing Authentication Helpers...")
    
    # Test password validation
    valid_password = "TestPassword123!"
    weak_password = "weak"
    
    is_valid, message = password_manager.validate_password(valid_password)
    print(f"Valid password test: {is_valid} - {message}")
    
    is_valid, message = password_manager.validate_password(weak_password)
    print(f"Weak password test: {is_valid} - {message}")
    
    # Test email validation
    valid_email = "test@example.com"
    invalid_email = "invalid-email"
    
    is_valid, message = email_validator.validate_email(valid_email)
    print(f"Valid email test: {is_valid} - {message}")
    
    is_valid, message = email_validator.validate_email(invalid_email)
    print(f"Invalid email test: {is_valid} - {message}")
    
    # Test JWT token generation and verification
    user_id = "507f1f77bcf86cd799439011"
    email = "test@example.com"
    
    token = jwt_manager.generate_token(user_id, email)
    print(f"Generated token: {token[:50]}...")
    
    try:
        payload = jwt_manager.verify_token(token)
        print(f"Token verification successful: {payload['user_id']}")
    except AuthError as e:
        print(f"Token verification failed: {str(e)}")
    
    # Test state generation and verification
    state = state_manager.generate_state(user_id, "instagram")
    print(f"Generated state: {state}")
    
    is_valid, message = state_manager.verify_state(state, user_id, "instagram")
    print(f"State verification: {is_valid} - {message}")
    
    print("Authentication helpers test completed!")

if __name__ == '__main__':
    test_auth_helpers()