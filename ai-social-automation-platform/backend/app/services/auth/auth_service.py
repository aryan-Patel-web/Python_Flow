"""
Authentication Service
Handles user authentication, token management, and security
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from app.models.user import User
from app.utils.logger import setup_logger, log_security_event
from app.utils.validators import validate_email, validate_password
from app.utils.helpers import generate_uuid, hash_password, verify_password
import os
import secrets
import time

logger = setup_logger('auth_service')

class AuthService:
    """Handle authentication operations"""
    
    def __init__(self):
        self.secret_key = os.environ.get('JWT_SECRET_KEY', 'default-secret-key')
        self.algorithm = 'HS256'
        self.access_token_expire_hours = 24
        self.refresh_token_expire_days = 30
        self.max_login_attempts = 5
        self.lockout_duration_minutes = 15
    
    def register_user(self, user_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            user_data: Dictionary containing user registration data
        
        Returns:
            Dictionary with registration result
        """
        try:
            # Validate input data
            validation_result = self._validate_registration_data(user_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': 'Validation failed',
                    'details': validation_result['errors']
                }
            
            # Check if user already exists
            existing_user = User.objects(email=user_data['email']).first()
            if existing_user:
                log_security_event(
                    'registration_attempt_existing_email',
                    details={'email': user_data['email']}
                )
                return {
                    'success': False,
                    'error': 'User with this email already exists'
                }
            
            # Check username availability
            existing_username = User.objects(username=user_data['username']).first()
            if existing_username:
                return {
                    'success': False,
                    'error': 'Username already taken'
                }
            
            # Hash password
            hashed_password, salt = hash_password(user_data['password'])
            
            # Create user
            user = User(
                email=user_data['email'],
                username=user_data['username'],
                full_name=user_data['full_name'],
                password_hash=hashed_password,
                password_salt=salt,
                is_active=True,
                email_verified=False,
                created_at=datetime.utcnow()
            )
            user.save()
            
            # Generate tokens
            tokens = self._generate_tokens(user)
            
            # Log successful registration
            log_security_event(
                'user_registered',
                user_id=str(user.id),
                details={'email': user.email, 'username': user.username}
            )
            
            logger.info(f"User registered successfully: {user.email}")
            
            return {
                'success': True,
                'user': user.to_dict(),
                'tokens': tokens,
                'message': 'User registered successfully'
            }
            
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            return {
                'success': False,
                'error': 'Registration failed',
                'details': str(e)
            }
    
    def authenticate_user(self, email: str, password: str, ip_address: str = None) -> Dict[str, Any]:
        """
        Authenticate user with email and password
        
        Args:
            email: User's email
            password: User's password
            ip_address: Client IP address for security logging
        
        Returns:
            Dictionary with authentication result
        """
        try:
            # Find user by email
            user = User.objects(email=email).first()
            if not user:
                log_security_event(
                    'login_attempt_invalid_email',
                    ip_address=ip_address,
                    details={'email': email}
                )
                return {
                    'success': False,
                    'error': 'Invalid email or password'
                }
            
            # Check if account is locked
            if self._is_account_locked(user):
                log_security_event(
                    'login_attempt_locked_account',
                    user_id=str(user.id),
                    ip_address=ip_address,
                    severity='WARNING'
                )
                return {
                    'success': False,
                    'error': 'Account temporarily locked due to multiple failed attempts'
                }
            
            # Verify password
            if not verify_password(password, user.password_hash, user.password_salt):
                self._handle_failed_login(user, ip_address)
                return {
                    'success': False,
                    'error': 'Invalid email or password'
                }
            
            # Check if account is active
            if not user.is_active:
                log_security_event(
                    'login_attempt_inactive_account',
                    user_id=str(user.id),
                    ip_address=ip_address,
                    severity='WARNING'
                )
                return {
                    'success': False,
                    'error': 'Account is deactivated'
                }
            
            # Reset failed attempts on successful login
            self._reset_failed_attempts(user)
            
            # Update last login
            user.last_login = datetime.utcnow()
            user.save()
            
            # Generate tokens
            tokens = self._generate_tokens(user)
            
            # Log successful login
            log_security_event(
                'user_login_success',
                user_id=str(user.id),
                ip_address=ip_address,
                details={'email': user.email}
            )
            
            logger.info(f"User authenticated successfully: {user.email}")
            
            return {
                'success': True,
                'user': user.to_dict(),
                'tokens': tokens,
                'message': 'Authentication successful'
            }
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return {
                'success': False,
                'error': 'Authentication failed',
                'details': str(e)
            }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            Dictionary with new tokens
        """
        try:
            # Decode refresh token
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get('type') != 'refresh':
                return {
                    'success': False,
                    'error': 'Invalid token type'
                }
            
            # Get user
            user_id = payload.get('user_id')
            user = User.objects(id=user_id).first()
            
            if not user or not user.is_active:
                return {
                    'success': False,
                    'error': 'User not found or inactive'
                }
            
            # Generate new tokens
            tokens = self._generate_tokens(user)
            
            logger.info(f"Token refreshed for user: {user.email}")
            
            return {
                'success': True,
                'tokens': tokens,
                'user': user.to_dict()
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'error': 'Refresh token expired'
            }
        except jwt.InvalidTokenError:
            return {
                'success': False,
                'error': 'Invalid refresh token'
            }
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return {
                'success': False,
                'error': 'Token refresh failed'
            }
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode access token
        
        Args:
            token: JWT access token
        
        Returns:
            Dictionary with verification result and user data
        """
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get('type') != 'access':
                return {
                    'valid': False,
                    'error': 'Invalid token type'
                }
            
            # Get user
            user_id = payload.get('user_id')
            user = User.objects(id=user_id).first()
            
            if not user or not user.is_active:
                return {
                    'valid': False,
                    'error': 'User not found or inactive'
                }
            
            return {
                'valid': True,
                'user': user.to_dict(),
                'user_id': user_id
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'valid': False,
                'error': 'Token expired'
            }
        except jwt.InvalidTokenError:
            return {
                'valid': False,
                'error': 'Invalid token'
            }
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return {
                'valid': False,
                'error': 'Token verification failed'
            }
    
    def logout_user(self, user_id: str, token: str = None) -> Dict[str, Any]:
        """
        Logout user (token blacklisting would go here in production)
        
        Args:
            user_id: User ID
            token: Access token to invalidate
        
        Returns:
            Dictionary with logout result
        """
        try:
            user = User.objects(id=user_id).first()
            if user:
                log_security_event(
                    'user_logout',
                    user_id=user_id,
                    details={'email': user.email}
                )
                logger.info(f"User logged out: {user.email}")
            
            # In a production system, you would add the token to a blacklist
            # For now, we just return success
            
            return {
                'success': True,
                'message': 'Logout successful'
            }
            
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return {
                'success': False,
                'error': 'Logout failed'
            }
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> Dict[str, Any]:
        """
        Change user password
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
        
        Returns:
            Dictionary with result
        """
        try:
            user = User.objects(id=user_id).first()
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Verify current password
            if not verify_password(current_password, user.password_hash, user.password_salt):
                log_security_event(
                    'password_change_invalid_current',
                    user_id=user_id,
                    severity='WARNING'
                )
                return {
                    'success': False,
                    'error': 'Current password is incorrect'
                }
            
            # Validate new password
            password_validation = validate_password(new_password)
            if not password_validation['is_valid']:
                return {
                    'success': False,
                    'error': 'New password does not meet requirements',
                    'details': password_validation['errors']
                }
            
            # Hash new password
            new_hash, new_salt = hash_password(new_password)
            
            # Update user
            user.password_hash = new_hash
            user.password_salt = new_salt
            user.password_changed_at = datetime.utcnow()
            user.save()
            
            log_security_event(
                'password_changed',
                user_id=user_id,
                details={'email': user.email}
            )
            
            logger.info(f"Password changed for user: {user.email}")
            
            return {
                'success': True,
                'message': 'Password changed successfully'
            }
            
        except Exception as e:
            logger.error(f"Password change failed: {str(e)}")
            return {
                'success': False,
                'error': 'Password change failed'
            }
    
    def reset_password_request(self, email: str) -> Dict[str, Any]:
        """
        Request password reset
        
        Args:
            email: User's email
        
        Returns:
            Dictionary with result
        """
        try:
            user = User.objects(email=email).first()
            if not user:
                # Don't reveal if email exists or not
                return {
                    'success': True,
                    'message': 'If the email exists, a reset link will be sent'
                }
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            reset_expires = datetime.utcnow() + timedelta(hours=1)
            
            user.password_reset_token = reset_token
            user.password_reset_expires = reset_expires
            user.save()
            
            log_security_event(
                'password_reset_requested',
                user_id=str(user.id),
                details={'email': user.email}
            )
            
            # In production, send email with reset link here
            # For now, we'll just log it
            logger.info(f"Password reset requested for: {user.email}")
            
            return {
                'success': True,
                'message': 'If the email exists, a reset link will be sent',
                'reset_token': reset_token  # Remove this in production
            }
            
        except Exception as e:
            logger.error(f"Password reset request failed: {str(e)}")
            return {
                'success': False,
                'error': 'Password reset request failed'
            }
    
    def reset_password_confirm(self, reset_token: str, new_password: str) -> Dict[str, Any]:
        """
        Confirm password reset with token
        
        Args:
            reset_token: Password reset token
            new_password: New password
        
        Returns:
            Dictionary with result
        """
        try:
            user = User.objects(
                password_reset_token=reset_token,
                password_reset_expires__gte=datetime.utcnow()
            ).first()
            
            if not user:
                return {
                    'success': False,
                    'error': 'Invalid or expired reset token'
                }
            
            # Validate new password
            password_validation = validate_password(new_password)
            if not password_validation['is_valid']:
                return {
                    'success': False,
                    'error': 'Password does not meet requirements',
                    'details': password_validation['errors']
                }
            
            # Hash new password
            new_hash, new_salt = hash_password(new_password)
            
            # Update user
            user.password_hash = new_hash
            user.password_salt = new_salt
            user.password_reset_token = None
            user.password_reset_expires = None
            user.password_changed_at = datetime.utcnow()
            user.save()
            
            log_security_event(
                'password_reset_completed',
                user_id=str(user.id),
                details={'email': user.email}
            )
            
            logger.info(f"Password reset completed for: {user.email}")
            
            return {
                'success': True,
                'message': 'Password reset successfully'
            }
            
        except Exception as e:
            logger.error(f"Password reset confirmation failed: {str(e)}")
            return {
                'success': False,
                'error': 'Password reset failed'
            }
    
    def _generate_tokens(self, user: User) -> Dict[str, str]:
        """Generate access and refresh tokens for user"""
        now = datetime.utcnow()
        
        # Access token payload
        access_payload = {
            'user_id': str(user.id),
            'email': user.email,
            'type': 'access',
            'iat': now,
            'exp': now + timedelta(hours=self.access_token_expire_hours)
        }
        
        # Refresh token payload
        refresh_payload = {
            'user_id': str(user.id),
            'type': 'refresh',
            'iat': now,
            'exp': now + timedelta(days=self.refresh_token_expire_days)
        }
        
        # Generate tokens
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': self.access_token_expire_hours * 3600
        }
    
    def _validate_registration_data(self, user_data: Dict[str, str]) -> Dict[str, Any]:
        """Validate user registration data"""
        errors = []
        
        # Validate email
        if not user_data.get('email'):
            errors.append("Email is required")
        elif not validate_email(user_data['email']):
            errors.append("Invalid email format")
        
        # Validate username
        username = user_data.get('username', '').strip()
        if not username:
            errors.append("Username is required")
        elif len(username) < 3 or len(username) > 50:
            errors.append("Username must be 3-50 characters long")
        elif not re.match(r'^[a-zA-Z0-9._]+, username):
            errors.append("Username can only contain letters, numbers, dots, and underscores")
        
        # Validate password
        if not user_data.get('password'):
            errors.append("Password is required")
        else:
            password_validation = validate_password(user_data['password'])
            if not password_validation['is_valid']:
                errors.extend(password_validation['errors'])
        
        # Validate full name
        full_name = user_data.get('full_name', '').strip()
        if not full_name:
            errors.append("Full name is required")
        elif len(full_name) < 2 or len(full_name) > 100:
            errors.append("Full name must be 2-100 characters long")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _is_account_locked(self, user: User) -> bool:
        """Check if account is locked due to failed login attempts"""
        if not hasattr(user, 'failed_login_attempts') or not user.failed_login_attempts:
            return False
        
        if user.failed_login_attempts >= self.max_login_attempts:
            if user.last_failed_login:
                lockout_expires = user.last_failed_login + timedelta(minutes=self.lockout_duration_minutes)
                return datetime.utcnow() < lockout_expires
        
        return False
    
    def _handle_failed_login(self, user: User, ip_address: str = None):
        """Handle failed login attempt"""
        if not hasattr(user, 'failed_login_attempts'):
            user.failed_login_attempts = 0
        
        user.failed_login_attempts += 1
        user.last_failed_login = datetime.utcnow()
        user.save()
        
        log_security_event(
            'login_attempt_failed',
            user_id=str(user.id),
            ip_address=ip_address,
            severity='WARNING',
            details={
                'email': user.email,
                'failed_attempts': user.failed_login_attempts
            }
        )
        
        logger.warning(f"Failed login attempt for {user.email} (attempt {user.failed_login_attempts})")
    
    def _reset_failed_attempts(self, user: User):
        """Reset failed login attempts on successful login"""
        user.failed_login_attempts = 0
        user.last_failed_login = None
        user.save()

# Create singleton instance
auth_service = AuthService()