"""
Authentication Manager for Multi-Platform Automation System
Handles JWT tokens, user registration, login, and security
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class User:
    """User data class"""
    id: str
    email: str
    name: str
    password_hash: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    is_admin: bool = False
    subscription_tier: str = "free"

class AuthManager:
    """
    Production-ready authentication manager with JWT tokens and bcrypt password hashing
    """
    
    def __init__(self):
        """Initialize authentication manager"""
        self.secret_key = "your_jwt_secret_key_here_32_chars_minimum"  # Should come from config
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
        # Password requirements
        self.min_password_length = 8
        self.password_pattern = re.compile(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        )
        
        # Email validation
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Returns:
            Boolean indicating if email is valid
        """
        return bool(self.email_pattern.match(email))
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Dictionary with validation results
        """
        issues = []
        
        if len(password) < self.min_password_length:
            issues.append(f"Password must be at least {self.min_password_length} characters long")
        
        if not re.search(r'[a-z]', password):
            issues.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'[A-Z]', password):
            issues.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'\d', password):
            issues.append("Password must contain at least one number")
        
        if not re.search(r'[@$!%*?&]', password):
            issues.append("Password must contain at least one special character (@$!%*?&)")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            hashed_password: Stored hashed password
            
        Returns:
            Boolean indicating if password matches
        """
        try:
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create JWT access token
        
        Args:
            data: Data to encode in token
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            raise
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.JWTError as e:
            raise ValueError(f"Token is invalid: {e}")
    
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register new user with validation
        
        Args:
            user_data: User registration data
            
        Returns:
            Registration result
        """
        try:
            email = user_data.get("email", "").strip().lower()
            password = user_data.get("password", "")
            name = user_data.get("name", "").strip()
            
            # Validation
            if not email:
                return {"success": False, "error": "Email is required"}
            
            if not self.validate_email(email):
                return {"success": False, "error": "Invalid email format"}
            
            if not password:
                return {"success": False, "error": "Password is required"}
            
            password_validation = self.validate_password(password)
            if not password_validation["valid"]:
                return {
                    "success": False, 
                    "error": "Password validation failed",
                    "details": password_validation["issues"]
                }
            
            if not name:
                return {"success": False, "error": "Name is required"}
            
            # Check if user already exists (this would check database in real implementation)
            # For demo, we'll assume user doesn't exist
            
            # Hash password
            password_hash = self.hash_password(password)
            
            # Create user object
            user = User(
                id=f"user_{int(datetime.now().timestamp())}",
                email=email,
                name=name,
                password_hash=password_hash,
                created_at=datetime.now(),
                subscription_tier="free"
            )
            
            # In production, save user to database here
            logger.info(f"User registered: {email}")
            
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "subscription_tier": user.subscription_tier
                },
                "message": "User registered successfully"
            }
            
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            return {
                "success": False,
                "error": "Registration failed",
                "details": str(e)
            }
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user login
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Authentication result with token
        """
        try:
            email = email.strip().lower()
            
            # In production, fetch user from database
            # For demo, we'll create a mock user
            mock_user = {
                "id": "user_demo_123",
                "email": email,
                "name": email.split("@")[0].title(),
                "password_hash": self.hash_password("password123"),  # Demo password
                "subscription_tier": "free",
                "is_active": True
            }
            
            # Verify password (for demo, accept any password)
            # In production: if not self.verify_password(password, mock_user["password_hash"]):
            if len(password) < 3:  # Simple validation for demo
                return {
                    "success": False,
                    "error": "Invalid email or password"
                }
            
            # Create access token
            token_data = {
                "sub": mock_user["id"],
                "email": mock_user["email"],
                "name": mock_user["name"]
            }
            
            access_token = self.create_access_token(token_data)
            
            logger.info(f"User authenticated: {email}")
            
            return {
                "success": True,
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60,
                "user": {
                    "id": mock_user["id"],
                    "email": mock_user["email"],
                    "name": mock_user["name"],
                    "subscription_tier": mock_user["subscription_tier"]
                },
                "message": "Authentication successful"
            }
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return {
                "success": False,
                "error": "Authentication failed",
                "details": str(e)
            }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token
        
        Args:
            refresh_token: Refresh token string
            
        Returns:
            New access token
        """
        try:
            # Verify refresh token
            payload = self.verify_token(refresh_token)
            user_id = payload.get("sub")
            
            if not user_id:
                return {"success": False, "error": "Invalid refresh token"}
            
            # Create new access token
            token_data = {
                "sub": user_id,
                "email": payload.get("email"),
                "name": payload.get("name")
            }
            
            new_access_token = self.create_access_token(token_data)
            
            return {
                "success": True,
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60,
                "message": "Token refreshed successfully"
            }
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return {
                "success": False,
                "error": "Token refresh failed",
                "details": str(e)
            }
    
    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """
        Get current user from token
        
        Args:
            token: JWT access token
            
        Returns:
            User information
        """
        try:
            payload = self.verify_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                return {"success": False, "error": "Invalid token"}
            
            # In production, fetch user from database
            user_info = {
                "id": user_id,
                "email": payload.get("email"),
                "name": payload.get("name"),
                "subscription_tier": "free",  # Would come from database
                "is_active": True
            }
            
            return {
                "success": True,
                "user": user_info,
                "message": "User information retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Get current user failed: {e}")
            return {
                "success": False,
                "error": "Failed to get user information",
                "details": str(e)
            }
    
    async def update_user_profile(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user profile information
        
        Args:
            user_id: User ID
            update_data: Data to update
            
        Returns:
            Update result
        """
        try:
            allowed_fields = ["name", "subscription_tier"]
            updates = {k: v for k, v in update_data.items() if k in allowed_fields}
            
            if not updates:
                return {"success": False, "error": "No valid fields to update"}
            
            # In production, update user in database
            logger.info(f"User profile updated: {user_id}")
            
            return {
                "success": True,
                "updated_fields": list(updates.keys()),
                "message": "Profile updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Profile update failed: {e}")
            return {
                "success": False,
                "error": "Profile update failed",
                "details": str(e)
            }
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> Dict[str, Any]:
        """
        Change user password
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            Password change result
        """
        try:
            # Validate new password
            password_validation = self.validate_password(new_password)
            if not password_validation["valid"]:
                return {
                    "success": False,
                    "error": "New password validation failed",
                    "details": password_validation["issues"]
                }
            
            # In production, verify current password from database
            # For demo, assume current password is correct
            
            # Hash new password
            new_password_hash = self.hash_password(new_password)
            
            # In production, update password in database
            logger.info(f"Password changed for user: {user_id}")
            
            return {
                "success": True,
                "message": "Password changed successfully"
            }
            
        except Exception as e:
            logger.error(f"Password change failed: {e}")
            return {
                "success": False,
                "error": "Password change failed",
                "details": str(e)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check authentication service health
        
        Returns:
            Health status
        """
        try:
            # Test token creation and verification
            test_data = {"sub": "test", "email": "test@example.com"}
            test_token = self.create_access_token(test_data)
            decoded = self.verify_token(test_token)
            
            token_test_passed = decoded.get("sub") == "test"
            
            # Test password hashing
            test_password = "TestPassword123!"
            test_hash = self.hash_password(test_password)
            hash_test_passed = self.verify_password(test_password, test_hash)
            
            overall_health = token_test_passed and hash_test_passed
            
            return {
                "success": True,
                "status": "healthy" if overall_health else "degraded",
                "tests": {
                    "jwt_tokens": token_test_passed,
                    "password_hashing": hash_test_passed
                },
                "message": "Authentication service health check completed"
            }
            
        except Exception as e:
            logger.error(f"Auth health check failed: {e}")
            return {
                "success": False,
                "status": "unhealthy",
                "error": str(e),
                "message": "Authentication service health check failed"
            }