import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class EncryptionService:
    def __init__(self):
        # Get encryption key from environment
        password = os.getenv('ENCRYPTION_KEY', 'default-key-change-this').encode()
        salt = b'salt_1234567890'  # In production, use random salt per user
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.fernet = Fernet(key)
    
    def encrypt_token(self, token):
        """Encrypt access token for secure storage"""
        if not token:
            return None
        return self.fernet.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token):
        """Decrypt access token for API calls"""
        if not encrypted_token:
            return None
        return self.fernet.decrypt(encrypted_token.encode()).decode()

# Global instance
encryption_service = EncryptionService()

def encrypt_token(token):
    return encryption_service.encrypt_token(token)

def decrypt_token(encrypted_token):
    return encryption_service.decrypt_token(encrypted_token)
