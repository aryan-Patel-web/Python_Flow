from datetime import datetime
from bson import ObjectId
import bcrypt

class User:
    def __init__(self, db):
        self.collection = db.users
    
    def create_user(self, email, password, name):
        """Create a new user"""
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'name': name,
            'subscription_plan': 'starter',
            'credits_used': 0,
            'daily_post_count': 0,
            'last_reset_date': datetime.utcnow().date(),
            'created_at': datetime.utcnow(),
            'is_active': True,
            'automation_active': False,
            'settings': {
                'auto_posting_enabled': True,
                'preferred_posting_times': [],
                'content_approval_required': False
            }
        }
        
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    def find_by_email(self, email):
        """Find user by email"""
        return self.collection.find_one({'email': email})
    
    def find_by_id(self, user_id):
        """Find user by ID"""
        return self.collection.find_one({'_id': ObjectId(user_id)})
    
    def verify_password(self, email, password):
        """Verify user password"""
        user = self.find_by_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            return user
        return None
    
    def update_subscription(self, user_id, plan):
        """Update user subscription plan"""
        return self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'subscription_plan': plan, 'updated_at': datetime.utcnow()}}
        )
