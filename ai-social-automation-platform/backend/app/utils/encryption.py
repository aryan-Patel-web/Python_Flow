"""
Encryption utilities for secure credential storage
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import json
import logging

logger = logging.getLogger(__name__)

class EncryptionManager:
    """Handles encryption and decryption of sensitive data"""
    
    def __init__(self, secret_key=None):
        """Initialize encryption manager with secret key"""
        if secret_key is None:
            secret_key = os.environ.get('ENCRYPTION_SECRET_KEY', 'default-secret-key')
        
        self.secret_key = secret_key.encode()
        self._fernet = None
    
    def _get_fernet(self):
        """Get or create Fernet instance"""
        if self._fernet is None:
            # Generate a key from the secret
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'ai_social_salt',  # In production, use random salt
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.secret_key))
            self._fernet = Fernet(key)
        
        return self._fernet
    
    def encrypt_data(self, data):
        """Encrypt data (string or dict)"""
        try:
            if isinstance(data, dict):
                data = json.dumps(data)
            elif not isinstance(data, str):
                data = str(data)
            
            encrypted = self._get_fernet().encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise Exception("Failed to encrypt data")
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data back to original format"""
        try:
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            
            # Decrypt
            decrypted = self._get_fernet().decrypt(encrypted_bytes)
            decrypted_str = decrypted.decode()
            
            # Try to parse as JSON, otherwise return as string
            try:
                return json.loads(decrypted_str)
            except json.JSONDecodeError:
                return decrypted_str
        
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise Exception("Failed to decrypt data")
    
    def encrypt_credentials(self, credentials_dict):
        """Encrypt a dictionary of credentials"""
        encrypted_creds = {}
        
        for key, value in credentials_dict.items():
            if value is not None:
                encrypted_creds[f"enc_{key}"] = self.encrypt_data(value)
        
        return encrypted_creds
    
    def decrypt_credentials(self, encrypted_dict):
        """Decrypt a dictionary of encrypted credentials"""
        decrypted_creds = {}
        
        for key, value in encrypted_dict.items():
            if key.startswith('enc_') and value is not None:
                original_key = key[4:]  # Remove 'enc_' prefix
                decrypted_creds[original_key] = self.decrypt_data(value)
        
        return decrypted_creds

# Global encryption manager instance
_encryption_manager = None

def get_encryption_manager():
    """Get global encryption manager instance"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager

def encrypt_data(data):
    """Convenience function to encrypt data"""
    return get_encryption_manager().encrypt_data(data)

def decrypt_data(encrypted_data):
    """Convenience function to decrypt data"""
    return get_encryption_manager().decrypt_data(encrypted_data)

def encrypt_credentials(credentials_dict):
    """Convenience function to encrypt credentials"""
    return get_encryption_manager().encrypt_credentials(credentials_dict)

def decrypt_credentials(encrypted_dict):
    """Convenience function to decrypt credentials"""
    return get_encryption_manager().decrypt_credentials(encrypted_dict)

def generate_encryption_key():
    """Generate a new encryption key for production use"""
    return base64.urlsafe_b64encode(os.urandom(32)).decode()

# Platform-specific credential encryption helpers
def encrypt_instagram_credentials(username, password, email=None):
    """Encrypt Instagram credentials"""
    creds = {
        'username': username,
        'password': password
    }
    if email:
        creds['email'] = email
    
    return encrypt_credentials(creds)

def encrypt_facebook_credentials(email, password, page_id=None, access_token=None):
    """Encrypt Facebook credentials"""
    creds = {
        'email': email,
        'password': password
    }
    if page_id:
        creds['page_id'] = page_id
    if access_token:
        creds['access_token'] = access_token
    
    return encrypt_credentials(creds)

def encrypt_youtube_credentials(email, password, channel_id=None, api_key=None):
    """Encrypt YouTube credentials"""
    creds = {
        'email': email,
        'password': password
    }
    if channel_id:
        creds['channel_id'] = channel_id
    if api_key:
        creds['api_key'] = api_key
    
    return encrypt_credentials(creds)

def encrypt_twitter_credentials(username, password, api_key=None, api_secret=None, access_token=None, access_token_secret=None):
    """Encrypt Twitter credentials"""
    creds = {
        'username': username,
        'password': password
    }
    if api_key:
        creds.update({
            'api_key': api_key,
            'api_secret': api_secret,
            'access_token': access_token,
            'access_token_secret': access_token_secret
        })
    
    return encrypt_credentials(creds)

def encrypt_linkedin_credentials(email, password, company_page_id=None):
    """Encrypt LinkedIn credentials"""
    creds = {
        'email': email,
        'password': password
    }
    if company_page_id:
        creds['company_page_id'] = company_page_id
    
    return encrypt_credentials(creds)