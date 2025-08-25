"""
Database Models and Connection Management
MongoDB with Pymongo for VelocityPost.ai
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import json

# Global database connection
db = None
client = None

class DatabaseManager:
    """Database connection and operations manager"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.cipher_suite = None
        
    def init_app(self, app):
        """Initialize database connection with Flask app"""
        # Try MongoDB Atlas first, then local
        mongodb_uri = app.config.get('MONGODB_ATLAS_URI') or app.config.get('MONGODB_URI')
        
        try:
            self.client = MongoClient(mongodb_uri)
            # Test connection
            self.client.admin.command('ping')
            
            # Get database name from URI or default
            db_name = mongodb_uri.split('/')[-1].split('?')[0] if '/' in mongodb_uri else 'velocitypost'
            self.db = self.client[db_name]
            
            # Initialize encryption
            encryption_key = app.config.get('ENCRYPTION_KEY', Fernet.generate_key())
            self.cipher_suite = Fernet(encryption_key)
            
            # Create indexes
            self._create_indexes()
            
            app.logger.info(f"Connected to MongoDB: {db_name}")
            
        except ConnectionFailure as e:
            app.logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create database indexes for performance"""
        # Users collection indexes
        self.db.users.create_index([("email", ASCENDING)], unique=True)
        self.db.users.create_index([("created_at", DESCENDING)])
        
        # 🔥 NEW: Platform connections indexes
        self.db.platform_connections.create_index([("user_id", ASCENDING), ("platform", ASCENDING)], unique=True)
        self.db.platform_connections.create_index([("created_at", DESCENDING)])
        
        # 🔥 NEW: Content generation indexes
        self.db.generated_content.create_index([("user_id", ASCENDING)])
        self.db.generated_content.create_index([("created_at", DESCENDING)])
        self.db.generated_content.create_index([("status", ASCENDING)])
        
        # 🔥 NEW: Auto-posting logs indexes
        self.db.auto_posting_logs.create_index([("user_id", ASCENDING)])
        self.db.auto_posting_logs.create_index([("posted_at", DESCENDING)])
        self.db.auto_posting_logs.create_index([("platform", ASCENDING)])
        
        # Posts collection indexes
        self.db.posts.create_index([("user_id", ASCENDING)])
        self.db.posts.create_index([("scheduled_time", ASCENDING)])
        self.db.posts.create_index([("created_at", DESCENDING)])
        
        # Subscriptions indexes
        self.db.subscriptions.create_index([("user_id", ASCENDING)], unique=True)
        self.db.subscriptions.create_index([("status", ASCENDING)])
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

# Global database manager instance
db_manager = DatabaseManager()

def init_db(app):
    """Initialize database with Flask app"""
    global db, client
    db_manager.init_app(app)
    db = db_manager.db
    client = db_manager.client

# Model Classes
class User:
    """User model for authentication and profile management"""
    
    @staticmethod
    def create(email: str, password: str, name: str, **kwargs) -> Dict:
        """Create a new user"""
        user_data = {
            'email': email.lower(),
            'password_hash': generate_password_hash(password),
            'name': name,
            'is_active': True,
            'is_verified': False,
            'plan': 'free',  # free, pro, agency
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'profile': {
                'avatar_url': kwargs.get('avatar_url'),
                'bio': kwargs.get('bio', ''),
                'timezone': kwargs.get('timezone', 'UTC'),
                'language': kwargs.get('language', 'en')
            },
            'settings': {
                'email_notifications': True,
                'push_notifications': True,
                'marketing_emails': False
            },
            # 🔥 NEW: Auto-posting settings
            'auto_posting': {
                'enabled': False,
                'daily_limit': 2,  # Free tier limit
                'domains': [],
                'posting_times': ['09:00', '18:00'],
                'timezone': 'UTC'
            }
        }
        
        result = db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return user_data
    
    @staticmethod
    def find_by_email(email: str) -> Optional[Dict]:
        """Find user by email"""
        return db.users.find_one({'email': email.lower()})
    
    @staticmethod
    def find_by_id(user_id: str) -> Optional[Dict]:
        """Find user by ID"""
        return db.users.find_one({'_id': ObjectId(user_id)})
    
    @staticmethod
    def verify_password(password_hash: str, password: str) -> bool:
        """Verify user password"""
        return check_password_hash(password_hash, password)
    
    @staticmethod
    def update(user_id: str, update_data: Dict) -> bool:
        """Update user data"""
        update_data['updated_at'] = datetime.utcnow()
        result = db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0

# 🔥 NEW: Platform Connection Model
class PlatformConnection:
    """Model for storing OAuth platform connections"""
    
    @staticmethod
    def create(user_id: str, platform: str, access_token: str, **kwargs) -> Dict:
        """Create a new platform connection"""
        connection_data = {
            'user_id': ObjectId(user_id),
            'platform': platform.lower(),
            'access_token': db_manager.encrypt_data(access_token),
            'refresh_token': db_manager.encrypt_data(kwargs.get('refresh_token', '')),
            'token_expires_at': kwargs.get('expires_at'),
            'platform_user_id': kwargs.get('platform_user_id'),
            'platform_username': kwargs.get('platform_username'),
            'profile_info': kwargs.get('profile_info', {}),
            'permissions': kwargs.get('permissions', []),
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'last_used_at': None
        }
        
        # Use upsert to handle reconnections
        result = db.platform_connections.update_one(
            {'user_id': ObjectId(user_id), 'platform': platform.lower()},
            {'$set': connection_data},
            upsert=True
        )
        
        if result.upserted_id:
            connection_data['_id'] = result.upserted_id
        
        return connection_data
    
    @staticmethod
    def get_user_connections(user_id: str) -> List[Dict]:
        """Get all platform connections for a user"""
        connections = list(db.platform_connections.find({
            'user_id': ObjectId(user_id),
            'is_active': True
        }))
        
        # Decrypt tokens for use (don't return in API)
        for conn in connections:
            if 'access_token' in conn:
                conn['access_token'] = db_manager.decrypt_data(conn['access_token'])
            if 'refresh_token' in conn:
                conn['refresh_token'] = db_manager.decrypt_data(conn['refresh_token'])
                
        return connections
    
    @staticmethod
    def get_connection(user_id: str, platform: str) -> Optional[Dict]:
        """Get specific platform connection"""
        connection = db.platform_connections.find_one({
            'user_id': ObjectId(user_id),
            'platform': platform.lower(),
            'is_active': True
        })
        
        if connection and 'access_token' in connection:
            connection['access_token'] = db_manager.decrypt_data(connection['access_token'])
            if 'refresh_token' in connection:
                connection['refresh_token'] = db_manager.decrypt_data(connection['refresh_token'])
                
        return connection
    
    @staticmethod
    def update_tokens(user_id: str, platform: str, access_token: str, refresh_token: str = None, expires_at: datetime = None):
        """Update platform tokens"""
        update_data = {
            'access_token': db_manager.encrypt_data(access_token),
            'updated_at': datetime.utcnow(),
            'last_used_at': datetime.utcnow()
        }
        
        if refresh_token:
            update_data['refresh_token'] = db_manager.encrypt_data(refresh_token)
        if expires_at:
            update_data['token_expires_at'] = expires_at
            
        return db.platform_connections.update_one(
            {'user_id': ObjectId(user_id), 'platform': platform.lower()},
            {'$set': update_data}
        )
    
    @staticmethod
    def disconnect(user_id: str, platform: str) -> bool:
        """Disconnect a platform"""
        result = db.platform_connections.update_one(
            {'user_id': ObjectId(user_id), 'platform': platform.lower()},
            {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
        )
        return result.modified_count > 0

# 🔥 NEW: Generated Content Model
class GeneratedContent:
    """Model for AI-generated content"""
    
    @staticmethod
    def create(user_id: str, content: str, domain: str, platforms: List[str], **kwargs) -> Dict:
        """Create generated content entry"""
        content_data = {
            'user_id': ObjectId(user_id),
            'content': content,
            'domain': domain,
            'platforms': platforms,
            'status': 'draft',  # draft, scheduled, posted, failed
            'metadata': {
                'tone': kwargs.get('tone', 'professional'),
                'length': kwargs.get('length', 'medium'),
                'hashtags': kwargs.get('hashtags', []),
                'mentions': kwargs.get('mentions', []),
                'ai_model': kwargs.get('ai_model', 'mistral'),
                'generation_time': kwargs.get('generation_time', 0),
                'performance_prediction': kwargs.get('performance_prediction', {})
            },
            'scheduled_for': kwargs.get('scheduled_for'),
            'posted_at': None,
            'engagement_stats': {},
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = db.generated_content.insert_one(content_data)
        content_data['_id'] = result.inserted_id
        return content_data
    
    @staticmethod
    def get_user_content(user_id: str, limit: int = 50, status: str = None) -> List[Dict]:
        """Get user's generated content"""
        query = {'user_id': ObjectId(user_id)}
        if status:
            query['status'] = status
            
        return list(db.generated_content.find(query)
                   .sort('created_at', DESCENDING)
                   .limit(limit))
    
    @staticmethod
    def update_status(content_id: str, status: str, **kwargs) -> bool:
        """Update content status"""
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow()
        }
        
        if status == 'posted':
            update_data['posted_at'] = datetime.utcnow()
            
        if 'engagement_stats' in kwargs:
            update_data['engagement_stats'] = kwargs['engagement_stats']
            
        result = db.generated_content.update_one(
            {'_id': ObjectId(content_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0

# 🔥 NEW: Auto-Posting Log Model
class AutoPostingLog:
    """Model for tracking auto-posting activities"""
    
    @staticmethod
    def create(user_id: str, platform: str, action: str, **kwargs) -> Dict:
        """Create auto-posting log entry"""
        log_data = {
            'user_id': ObjectId(user_id),
            'platform': platform,
            'action': action,  # generated, posted, failed, scheduled
            'content_id': kwargs.get('content_id'),
            'post_id': kwargs.get('post_id'),
            'status': kwargs.get('status', 'success'),
            'error_message': kwargs.get('error_message'),
            'metadata': kwargs.get('metadata', {}),
            'posted_at': datetime.utcnow(),
            'created_at': datetime.utcnow()
        }
        
        result = db.auto_posting_logs.insert_one(log_data)
        log_data['_id'] = result.inserted_id
        return log_data
    
    @staticmethod
    def get_user_logs(user_id: str, limit: int = 100) -> List[Dict]:
        """Get user's auto-posting logs"""
        return list(db.auto_posting_logs.find({'user_id': ObjectId(user_id)})
                   .sort('posted_at', DESCENDING)
                   .limit(limit))

# Subscription Model
class Subscription:
    """Subscription model for billing management"""
    
    @staticmethod
    def create(user_id: str, plan: str, **kwargs) -> Dict:
        """Create a subscription"""
        sub_data = {
            'user_id': ObjectId(user_id),
            'plan': plan,  # free, pro, agency
            'status': 'active',
            'billing_cycle': kwargs.get('billing_cycle', 'monthly'),
            'amount': kwargs.get('amount', 0),
            'currency': kwargs.get('currency', 'INR'),
            'payment_method': kwargs.get('payment_method'),
            'stripe_subscription_id': kwargs.get('stripe_subscription_id'),
            'razorpay_subscription_id': kwargs.get('razorpay_subscription_id'),
            'current_period_start': datetime.utcnow(),
            'current_period_end': datetime.utcnow() + timedelta(days=30),
            'trial_end': kwargs.get('trial_end'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            # Plan limits
            'limits': {
                'platforms': 2 if plan == 'free' else (5 if plan == 'pro' else 999),
                'daily_posts': 2 if plan == 'free' else (50 if plan == 'pro' else 999),
                'ai_generations': 10 if plan == 'free' else (1000 if plan == 'pro' else 9999),
                'team_members': 1 if plan == 'free' else (3 if plan == 'pro' else 25)
            }
        }
        
        result = db.subscriptions.insert_one(sub_data)
        sub_data['_id'] = result.inserted_id
        return sub_data
    
    @staticmethod
    def get_user_subscription(user_id: str) -> Optional[Dict]:
        """Get user's active subscription"""
        return db.subscriptions.find_one({
            'user_id': ObjectId(user_id),
            'status': 'active'
        })
    
    @staticmethod
    def update_plan(user_id: str, plan: str, **kwargs) -> bool:
        """Update subscription plan"""
        update_data = {
            'plan': plan,
            'updated_at': datetime.utcnow()
        }
        
        # Update limits based on plan
        if plan == 'free':
            update_data['limits'] = {
                'platforms': 2,
                'daily_posts': 2,
                'ai_generations': 10,
                'team_members': 1
            }
        elif plan == 'pro':
            update_data['limits'] = {
                'platforms': 5,
                'daily_posts': 50,
                'ai_generations': 1000,
                'team_members': 3
            }
        elif plan == 'agency':
            update_data['limits'] = {
                'platforms': 999,
                'daily_posts': 999,
                'ai_generations': 9999,
                'team_members': 25
            }
        
        result = db.subscriptions.update_one(
            {'user_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0

# 🔥 NEW: Usage Tracking Model
class UsageTracking:
    """Track user usage for billing and limits"""
    
    @staticmethod
    def track_usage(user_id: str, action: str, platform: str = None):
        """Track user action for billing/limits"""
        today = datetime.utcnow().date()
        
        usage_data = {
            'user_id': ObjectId(user_id),
            'date': today,
            'actions': {
                action: 1
            }
        }
        
        # Increment existing or create new
        db.usage_tracking.update_one(
            {'user_id': ObjectId(user_id), 'date': today},
            {
                '$inc': {f'actions.{action}': 1},
                '$set': {'updated_at': datetime.utcnow()}
            },
            upsert=True
        )
    
    @staticmethod
    def get_daily_usage(user_id: str, date: datetime = None) -> Dict:
        """Get usage for a specific date"""
        if not date:
            date = datetime.utcnow().date()
            
        usage = db.usage_tracking.find_one({
            'user_id': ObjectId(user_id),
            'date': date
        })
        
        return usage.get('actions', {}) if usage else {}
    
    @staticmethod
    def check_limit(user_id: str, action: str, limit: int) -> bool:
        """Check if user has exceeded daily limit"""
        today_usage = UsageTracking.get_daily_usage(user_id)
        current_usage = today_usage.get(action, 0)
        return current_usage < limit

# Utility functions
def serialize_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if key == '_id':
                result[key] = str(value)
            elif isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, (dict, list)):
                result[key] = serialize_doc(value)
            else:
                result[key] = value
        return result
    return doc