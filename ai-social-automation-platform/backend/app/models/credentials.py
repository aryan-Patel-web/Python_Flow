# backend/app/models/credentials.py
from datetime import datetime, timezone
from mongoengine import Document, StringField, BooleanField, DateTimeField, ReferenceField, DictField, ListField
from .user import User
from app.services.credentials.credential_manager import CredentialManager

class PlatformCredentials(Document):
    """Model for storing encrypted platform credentials"""
    
    user = ReferenceField(User, required=True)
    platform = StringField(required=True, choices=[
        'instagram', 'facebook', 'youtube', 'twitter', 'linkedin', 
        'tiktok', 'pinterest', 'snapchat', 'whatsapp_business'
    ])
    
    # Encrypted credential data
    encrypted_data = StringField(required=True)  # JSON string of encrypted credentials
    
    # Credential metadata
    account_name = StringField(max_length=100)  # Display name for the account
    account_id = StringField(max_length=100)    # Platform-specific account ID
    
    # Status tracking
    is_active = BooleanField(default=True)
    is_verified = BooleanField(default=False)
    last_verified_at = DateTimeField()
    verification_error = StringField()
    
    # Usage tracking
    posts_count = DictField(default=lambda: {
        'total': 0,
        'today': 0,
        'this_week': 0,
        'this_month': 0
    })
    
    # API limits and quotas
    api_limits = DictField(default=lambda: {
        'daily_posts': 50,
        'hourly_posts': 5,
        'current_daily_usage': 0,
        'current_hourly_usage': 0,
        'last_reset': datetime.now(timezone.utc).isoformat()
    })
    
    # Platform-specific settings
    platform_settings = DictField(default=dict)
    
    # Automation settings
    auto_post_enabled = BooleanField(default=True)
    post_schedule = DictField(default=lambda: {
        'frequency': 'daily',  # daily, weekly, custom
        'times': ['09:00', '15:00', '20:00'],
        'days': [1, 2, 3, 4, 5],  # Monday = 1, Sunday = 7
        'timezone': 'UTC'
    })
    
    # Timestamps
    created_at = DateTimeField(default=datetime.now(timezone.utc))
    updated_at = DateTimeField(default=datetime.now(timezone.utc))
    last_used_at = DateTimeField()
    
    meta = {
        'collection': 'platform_credentials',
        'indexes': [
            ('user', 'platform'),  # Compound index for user-platform queries
            'user',
            'platform',
            'is_active',
            'created_at'
        ]
    }
    
    def __str__(self):
        return f"{self.platform.title()} - {self.account_name or 'Unnamed'}"
    
    def clean(self):
        """Validate and clean data before saving"""
        self.updated_at = datetime.now(timezone.utc)
        if self.platform:
            self.platform = self.platform.lower()
    
    def get_credentials(self):
        """Decrypt and return credentials"""
        try:
            return CredentialManager.decrypt_credentials(self.encrypted_data)
        except Exception as e:
            raise ValueError(f"Failed to decrypt credentials: {str(e)}")
    
    def set_credentials(self, credentials_dict):
        """Encrypt and store credentials"""
        try:
            self.encrypted_data = CredentialManager.encrypt_credentials(credentials_dict)
        except Exception as e:
            raise ValueError(f"Failed to encrypt credentials: {str(e)}")
    
    def verify_credentials(self):
        """Verify that credentials are valid"""
        from app.services.credentials.credential_validator import CredentialValidator
        
        try:
            validator = CredentialValidator(self.platform)
            result = validator.verify(self.get_credentials())
            
            self.is_verified = result['valid']
            self.last_verified_at = datetime.now(timezone.utc)
            
            if not result['valid']:
                self.verification_error = result.get('error', 'Unknown verification error')
            else:
                self.verification_error = None
                self.account_id = result.get('account_id')
                self.account_name = result.get('account_name', self.account_name)
            
            self.save()
            return result
            
        except Exception as e:
            self.is_verified = False
            self.verification_error = str(e)
            self.last_verified_at = datetime.now(timezone.utc)
            self.save()
            return {'valid': False, 'error': str(e)}
    
    def can_post(self):
        """Check if account can post based on rate limits"""
        now = datetime.now(timezone.utc)
        limits = self.api_limits
        
        # Check daily limit
        if limits['current_daily_usage'] >= limits['daily_posts']:
            return False, "Daily post limit reached"
        
        # Check hourly limit
        if limits['current_hourly_usage'] >= limits['hourly_posts']:
            return False, "Hourly post limit reached"
        
        # Check if account is active and verified
        if not self.is_active:
            return False, "Account is inactive"
        
        if not self.is_verified:
            return False, "Account credentials not verified"
        
        return True, "OK"
    
    def increment_usage(self):
        """Increment usage counters"""
        self.api_limits['current_daily_usage'] += 1
        self.api_limits['current_hourly_usage'] += 1
        self.posts_count['total'] += 1
        self.posts_count['today'] += 1
        self.posts_count['this_week'] += 1
        self.posts_count['this_month'] += 1
        self.last_used_at = datetime.now(timezone.utc)
        self.save()
    
    def reset_daily_limits(self):
        """Reset daily usage counters"""
        self.api_limits['current_daily_usage'] = 0
        self.posts_count['today'] = 0
        self.save()
    
    def reset_hourly_limits(self):
        """Reset hourly usage counters"""
        self.api_limits['current_hourly_usage'] = 0
        self.save()
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': str(self.id),
            'platform': self.platform,
            'account_name': self.account_name,
            'account_id': self.account_id,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_verified_at': self.last_verified_at.isoformat() if self.last_verified_at else None,
            'verification_error': self.verification_error,
            'posts_count': self.posts_count,
            'api_limits': self.api_limits,
            'auto_post_enabled': self.auto_post_enabled,
            'post_schedule': self.post_schedule,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None
        }
    
    @classmethod
    def get_user_credentials(cls, user, platform=None, active_only=True):
        """Get credentials for a user, optionally filtered by platform"""
        query = {'user': user}
        
        if platform:
            query['platform'] = platform.lower()
        
        if active_only:
            query['is_active'] = True
        
        return cls.objects(**query).order_by('-created_at')
    
    @classmethod
    def get_verified_credentials(cls, user, platform=None):
        """Get only verified credentials for a user"""
        query = {
            'user': user,
            'is_active': True,
            'is_verified': True
        }
        
        if platform:
            query['platform'] = platform.lower()
        
        return cls.objects(**query).order_by('-created_at')