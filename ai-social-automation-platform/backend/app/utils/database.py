#!/usr/bin/env python3
"""
Database Configuration for VelocityPost.ai
Supports both local MongoDB and MongoDB Atlas with complete error handling
"""

import os
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure, ConnectionFailure
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db = None
        self.client = None
        self.database_name = 'velocitypost'
        self.connection_string = None
    
    def connect(self, app=None):
        """Connect to MongoDB with comprehensive fallback support"""
        connection_attempts = [
            ("MongoDB Atlas", os.getenv('MONGODB_ATLAS_URI')),
            ("MongoDB Atlas (fallback)", os.getenv('MONGODB_URI')),
            ("Local MongoDB", 'mongodb://localhost:27017/velocitypost')
        ]
        
        for name, uri in connection_attempts:
            if not uri:
                continue
                
            try:
                logger.info(f"Attempting to connect to {name}...")
                
                self.client = MongoClient(
                    uri,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    maxPoolSize=50,
                    minPoolSize=5,
                    retryWrites=True,
                    w='majority'
                )
                
                # Extract database name from URI or use default
                if '/velocitypost' in uri:
                    self.database_name = 'velocitypost'
                else:
                    # Try to extract from URI
                    try:
                        parsed = urllib.parse.urlparse(uri)
                        if parsed.path and len(parsed.path) > 1:
                            self.database_name = parsed.path[1:]  # Remove leading '/'
                        else:
                            self.database_name = 'velocitypost'
                    except:
                        self.database_name = 'velocitypost'
                
                self.db = self.client[self.database_name]
                
                # Test connection with admin command
                self.client.admin.command('ping')
                
                # Test database operation
                self.db.command('ping')
                
                self.connection_string = uri
                logger.info(f"Successfully connected to {name}. Database: {self.database_name}")
                
                if app:
                    app.db = self.db
                    app.mongo_client = self.client
                
                return True
                
            except (ServerSelectionTimeoutError, ConnectionFailure) as e:
                logger.warning(f"{name} connection failed: {e}")
                if self.client:
                    try:
                        self.client.close()
                    except:
                        pass
                    self.client = None
                continue
            except Exception as e:
                logger.error(f"Unexpected error connecting to {name}: {e}")
                if self.client:
                    try:
                        self.client.close()
                    except:
                        pass
                    self.client = None
                continue
        
        raise Exception("Failed to connect to any MongoDB instance. Please check your connection settings.")
    
    def get_db(self):
        """Get database instance"""
        if self.db is None:
            self.connect()
        return self.db
    
    def get_client(self):
        """Get MongoDB client instance"""
        if self.client is None:
            self.connect()
        return self.client
    
    def close_connection(self):
        """Close database connection"""
        if self.client:
            try:
                self.client.close()
                logger.info("Database connection closed successfully")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
            finally:
                self.client = None
                self.db = None

# Global database manager instance
db_manager = DatabaseManager()

def init_db(app=None):
    """Initialize database connection and create indexes"""
    try:
        success = db_manager.connect(app)
        if success:
            # Create indexes for performance
            create_indexes()
            logger.info("Database initialized successfully with indexes")
        return db_manager.get_db()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def get_db():
    """Get database instance"""
    try:
        db = db_manager.get_db()
        if db is None:
            raise Exception("Database not initialized")
        return db
    except Exception as e:
        logger.error(f"Failed to get database: {e}")
        raise

def get_database():
    """Alias for get_db() for compatibility"""
    return get_db()

def get_collection(collection_name):
    """Get a specific collection from database with error handling"""
    try:
        db = get_db()
        if db is None:
            logger.error("Database not initialized")
            return None
        
        collection = db[collection_name]
        logger.debug(f"Retrieved collection: {collection_name}")
        return collection
        
    except Exception as e:
        logger.error(f"Failed to get collection {collection_name}: {e}")
        return None

def create_indexes():
    """Create database indexes for optimal performance"""
    try:
        db = db_manager.get_db()
        
        # Users collection indexes
        users_collection = db.users
        try:
            users_collection.create_index([("email", ASCENDING)], unique=True)
        except Exception as e:
            logger.debug(f"Users email index already exists or failed: {e}")
        
        users_collection.create_index([("created_at", DESCENDING)])
        users_collection.create_index([("plan_type", ASCENDING)])
        users_collection.create_index([("is_active", ASCENDING)])
        users_collection.create_index([("email", ASCENDING), ("is_active", ASCENDING)])
        
        # Password reset indexes
        users_collection.create_index([("password_reset_token", ASCENDING)], sparse=True)
        users_collection.create_index([("password_reset_expires", ASCENDING)], sparse=True)
        
        # Social accounts collection indexes
        social_accounts = db.social_accounts
        try:
            social_accounts.create_index([("user_id", ASCENDING), ("platform", ASCENDING)], unique=True)
        except Exception as e:
            logger.debug(f"Social accounts compound index already exists or failed: {e}")
        
        social_accounts.create_index([("user_id", ASCENDING)])
        social_accounts.create_index([("platform", ASCENDING)])
        social_accounts.create_index([("is_active", ASCENDING)])
        social_accounts.create_index([("last_used_at", DESCENDING)])
        social_accounts.create_index([("token_expires_at", ASCENDING)])
        social_accounts.create_index([("connected_at", DESCENDING)])
        
        # Platform connections collection indexes (for compatibility)
        platform_connections = db.platform_connections
        try:
            platform_connections.create_index([("user_id", ASCENDING), ("platform", ASCENDING)], unique=True)
        except Exception as e:
            logger.debug(f"Platform connections compound index already exists or failed: {e}")
        
        platform_connections.create_index([("user_id", ASCENDING)])
        platform_connections.create_index([("is_active", ASCENDING)])
        platform_connections.create_index([("last_used_at", DESCENDING)])
        
        # Posts collection indexes
        posts = db.posts
        posts.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
        posts.create_index([("user_id", ASCENDING), ("platform", ASCENDING)])
        posts.create_index([("user_id", ASCENDING), ("status", ASCENDING)])
        posts.create_index([("scheduled_for", ASCENDING)])
        posts.create_index([("status", ASCENDING)])
        posts.create_index([("platform_post_id", ASCENDING)], sparse=True)
        posts.create_index([("is_automated", ASCENDING)])
        posts.create_index([("status", ASCENDING), ("scheduled_for", ASCENDING)])
        
        # Automation settings collection indexes
        automation_settings = db.automation_settings
        try:
            automation_settings.create_index([("user_id", ASCENDING)], unique=True)
        except Exception as e:
            logger.debug(f"Automation settings user_id index already exists or failed: {e}")
        
        automation_settings.create_index([("is_active", ASCENDING)])
        automation_settings.create_index([("created_at", DESCENDING)])
        automation_settings.create_index([("updated_at", DESCENDING)])
        
        # Generated content collection indexes
        generated_content = db.generated_content
        generated_content.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
        generated_content.create_index([("user_id", ASCENDING), ("domain", ASCENDING)])
        generated_content.create_index([("user_id", ASCENDING), ("platform", ASCENDING)])
        generated_content.create_index([("domain", ASCENDING)])
        generated_content.create_index([("platform", ASCENDING)])
        generated_content.create_index([("is_used", ASCENDING)])
        
        # Analytics collection indexes
        analytics = db.analytics
        analytics.create_index([("user_id", ASCENDING), ("date", DESCENDING)])
        analytics.create_index([("user_id", ASCENDING), ("platform", ASCENDING)])
        analytics.create_index([("date", DESCENDING)])
        
        # Subscriptions collection indexes
        subscriptions = db.subscriptions
        try:
            subscriptions.create_index([("user_id", ASCENDING)], unique=True)
            subscriptions.create_index([("stripe_subscription_id", ASCENDING)], unique=True, sparse=True)
            subscriptions.create_index([("razorpay_subscription_id", ASCENDING)], unique=True, sparse=True)
        except Exception as e:
            logger.debug(f"Subscriptions indexes already exist or failed: {e}")
        
        subscriptions.create_index([("plan_type", ASCENDING)])
        subscriptions.create_index([("status", ASCENDING)])
        subscriptions.create_index([("expires_at", ASCENDING)])
        subscriptions.create_index([("created_at", DESCENDING)])
        
        # OAuth states collection (for temporary storage)
        oauth_states = db.oauth_states
        oauth_states.create_index([("state", ASCENDING)], unique=True)
        oauth_states.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)
        oauth_states.create_index([("user_id", ASCENDING)])
        oauth_states.create_index([("platform", ASCENDING)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")

def test_database_connection():
    """Test database connection"""
    try:
        db = get_db()
        # Test with a simple operation
        result = db.list_collection_names()
        logger.info(f"Database connection test successful. Collections: {len(result)}")
        
        # Test write operation
        test_collection = db.connection_test
        test_doc = {"test": True, "timestamp": datetime.utcnow()}
        insert_result = test_collection.insert_one(test_doc)
        
        # Test read operation
        found_doc = test_collection.find_one({"_id": insert_result.inserted_id})
        
        # Clean up test document
        test_collection.delete_one({"_id": insert_result.inserted_id})
        
        if found_doc:
            logger.info("Database read/write test successful")
            return True
        else:
            logger.error("Database read test failed")
            return False
            
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

# Database Models and Helper Functions
class UserModel:
    """User model for database operations"""
    
    @staticmethod
    def create_user(email, password_hash, name, plan_type='free'):
        """Create a new user"""
        try:
            db = get_db()
            user_data = {
                'email': email.lower().strip(),
                'password': password_hash,
                'name': name.strip(),
                'plan_type': plan_type,
                'is_active': True,
                'email_verified': False,
                'connected_platforms': [],
                'posts_this_month': 0,
                'total_posts': 0,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'last_login': None,
                'profile_data': {},
                'preferences': {
                    'timezone': 'UTC',
                    'email_notifications': True,
                    'auto_posting_enabled': False,
                    'content_approval_required': True,
                    'max_posts_per_day': 2 if plan_type == 'free' else 20
                },
                'usage_stats': {
                    'posts_generated': 0,
                    'posts_published': 0,
                    'platforms_connected': 0,
                    'last_active': datetime.utcnow()
                }
            }
            
            result = db.users.insert_one(user_data)
            logger.info(f"User created successfully: {email}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to create user {email}: {e}")
            raise
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        try:
            db = get_db()
            user = db.users.find_one({'email': email.lower().strip()})
            return user
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        try:
            db = get_db()
            from bson import ObjectId
            user = db.users.find_one({'_id': ObjectId(user_id)})
            return user
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            return None
    
    @staticmethod
    def update_user(user_id, update_data):
        """Update user data"""
        try:
            db = get_db()
            from bson import ObjectId
            
            update_data['updated_at'] = datetime.utcnow()
            result = db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"User {user_id} updated successfully")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            return False
    
    @staticmethod
    def increment_usage(user_id, metric, amount=1):
        """Increment usage statistics"""
        try:
            db = get_db()
            from bson import ObjectId
            
            db.users.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$inc': {f'usage_stats.{metric}': amount},
                    '$set': {'usage_stats.last_active': datetime.utcnow()}
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to increment usage for user {user_id}: {e}")
            return False

class SocialAccountModel:
    """Social account model for OAuth tokens"""
    
    @staticmethod
    def save_account(user_id, platform, token_data, profile_data):
        """Save or update social media account connection"""
        try:
            db = get_db()
            from bson import ObjectId
            
            # Calculate token expiry
            expires_at = None
            if token_data.get('expires_in'):
                expires_at = datetime.utcnow() + timedelta(seconds=int(token_data['expires_in']))
            
            account_data = {
                'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id,
                'platform': platform,
                'platform_user_id': profile_data.get('id', ''),
                'username': profile_data.get('username', ''),
                'display_name': profile_data.get('name', ''),
                'profile_picture': profile_data.get('picture', ''),
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token'),
                'token_expires_at': expires_at,
                'profile_data': profile_data,
                'permissions': token_data.get('scope', '').split() if token_data.get('scope') else [],
                'connected_at': datetime.utcnow(),
                'last_used_at': datetime.utcnow(),
                'is_active': True,
                'connection_status': 'active',
                'error_count': 0,
                'last_error': None
            }
            
            # Update existing or insert new
            result = db.social_accounts.update_one(
                {'user_id': ObjectId(user_id), 'platform': platform},
                {'$set': account_data},
                upsert=True
            )
            
            # Update user's connected platforms count
            connected_count = db.social_accounts.count_documents({
                'user_id': ObjectId(user_id),
                'is_active': True
            })
            
            db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'usage_stats.platforms_connected': connected_count}}
            )
            
            logger.info(f"Social account saved: {platform} for user {user_id}")
            return result.upserted_id or True
            
        except Exception as e:
            logger.error(f"Failed to save social account {platform} for user {user_id}: {e}")
            return False
    
    @staticmethod
    def get_accounts_by_user(user_id):
        """Get all connected accounts for user"""
        try:
            db = get_db()
            from bson import ObjectId
            
            accounts = list(db.social_accounts.find({
                'user_id': ObjectId(user_id),
                'is_active': True
            }))
            
            # Remove sensitive data and convert ObjectIds
            for account in accounts:
                account['_id'] = str(account['_id'])
                account['user_id'] = str(account['user_id'])
                # Don't remove tokens as they might be needed for API calls
                # account.pop('access_token', None)
                # account.pop('refresh_token', None)
            
            return accounts
            
        except Exception as e:
            logger.error(f"Failed to get accounts for user {user_id}: {e}")
            return []
    
    @staticmethod
    def get_account_by_platform(user_id, platform):
        """Get specific platform connection"""
        try:
            db = get_db()
            from bson import ObjectId
            
            account = db.social_accounts.find_one({
                'user_id': ObjectId(user_id),
                'platform': platform,
                'is_active': True
            })
            
            return account
            
        except Exception as e:
            logger.error(f"Failed to get {platform} account for user {user_id}: {e}")
            return None
    
    @staticmethod
    def update_account_usage(user_id, platform):
        """Update last used timestamp"""
        try:
            db = get_db()
            from bson import ObjectId
            
            db.social_accounts.update_one(
                {'user_id': ObjectId(user_id), 'platform': platform},
                {'$set': {'last_used_at': datetime.utcnow()}}
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to update account usage for {platform}: {e}")
            return False
    
    @staticmethod
    def record_error(user_id, platform, error_message):
        """Record connection error"""
        try:
            db = get_db()
            from bson import ObjectId
            
            db.social_accounts.update_one(
                {'user_id': ObjectId(user_id), 'platform': platform},
                {
                    '$inc': {'error_count': 1},
                    '$set': {
                        'last_error': error_message,
                        'last_error_at': datetime.utcnow()
                    }
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to record error for {platform}: {e}")
            return False

class PostModel:
    """Post model for content management"""
    
    @staticmethod
    def create_post(user_id, platform, content, media_urls=None, scheduled_for=None, is_automated=True, domain=None):
        """Create a new post"""
        try:
            db = get_db()
            from bson import ObjectId
            
            post_data = {
                'user_id': ObjectId(user_id),
                'platform': platform,
                'content': content,
                'media_urls': media_urls or [],
                'scheduled_for': scheduled_for,
                'status': 'scheduled' if scheduled_for else 'draft',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_automated': is_automated,
                'is_ai_generated': is_automated,
                'domain': domain,
                'engagement_data': {},
                'performance_score': None,
                'platform_post_id': None,
                'error_message': None,
                'posted_at': None,
                'retry_count': 0,
                'hashtags': extract_hashtags(content),
                'word_count': len(content.split()),
                'character_count': len(content)
            }
            
            result = db.posts.insert_one(post_data)
            logger.info(f"Post created: {platform} for user {user_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to create post for user {user_id}: {e}")
            return None
    
    @staticmethod
    def get_user_posts(user_id, limit=50, platform=None, status=None, days=None):
        """Get user's posts with filters"""
        try:
            db = get_db()
            from bson import ObjectId
            
            filter_query = {'user_id': ObjectId(user_id)}
            
            if platform:
                filter_query['platform'] = platform
            
            if status:
                filter_query['status'] = status
            
            if days:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                filter_query['created_at'] = {'$gte': cutoff_date}
            
            posts = list(db.posts.find(filter_query)
                        .sort('created_at', DESCENDING)
                        .limit(limit))
            
            # Convert ObjectIds to strings
            for post in posts:
                post['_id'] = str(post['_id'])
                post['user_id'] = str(post['user_id'])
            
            return posts
            
        except Exception as e:
            logger.error(f"Failed to get posts for user {user_id}: {e}")
            return []
    
    @staticmethod
    def update_post_status(post_id, status, platform_post_id=None, error_message=None):
        """Update post status after posting"""
        try:
            db = get_db()
            from bson import ObjectId
            
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow()
            }
            
            if platform_post_id:
                update_data['platform_post_id'] = platform_post_id
                update_data['posted_at'] = datetime.utcnow()
            
            if error_message:
                update_data['error_message'] = error_message
                update_data['$inc'] = {'retry_count': 1}
            
            result = db.posts.update_one(
                {'_id': ObjectId(post_id)},
                {'$set': update_data} if not error_message else {
                    '$set': {k: v for k, v in update_data.items() if k != '$inc'},
                    '$inc': update_data.get('$inc', {})
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to update post {post_id}: {e}")
            return False

def extract_hashtags(content):
    """Extract hashtags from content"""
    import re
    return re.findall(r'#\w+', content)

# Plan limits and validation
PLAN_LIMITS = {
    'free': {
        'max_platforms': 2,
        'max_posts_per_day': 2,
        'max_generated_content': 10,
        'ai_credits': 50,
        'max_scheduled_posts': 10,
        'analytics_history_days': 30
    },
    'pro': {
        'max_platforms': 5,
        'max_posts_per_day': 20,
        'max_generated_content': 1000,
        'ai_credits': 1000,
        'max_scheduled_posts': 500,
        'analytics_history_days': 365
    },
    'agency': {
        'max_platforms': -1,  # unlimited
        'max_posts_per_day': -1,
        'max_generated_content': -1,
        'ai_credits': -1,
        'max_scheduled_posts': -1,
        'analytics_history_days': 730
    }
}

def check_user_limits(user_id, action, platform=None, amount=1):
    """Check if user can perform action based on their plan"""
    try:
        user = UserModel.get_user_by_id(user_id)
        if not user:
            return False, "User not found"
        
        plan_type = user.get('plan_type', 'free')
        limits = PLAN_LIMITS.get(plan_type, PLAN_LIMITS['free'])
        
        if action == 'connect_platform':
            db = get_db()
            from bson import ObjectId
            
            connected_count = db.social_accounts.count_documents({
                'user_id': ObjectId(user_id),
                'is_active': True
            })
            
            max_platforms = limits['max_platforms']
            if max_platforms != -1 and connected_count >= max_platforms:
                return False, f"Plan limit reached: {max_platforms} platforms maximum. Upgrade to connect more platforms."
        
        elif action == 'create_post':
            db = get_db()
            from bson import ObjectId
            
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            posts_today = db.posts.count_documents({
                'user_id': ObjectId(user_id),
                'created_at': {'$gte': today, '$lt': tomorrow}
            })
            
            max_posts = limits['max_posts_per_day']
            if max_posts != -1 and (posts_today + amount) > max_posts:
                return False, f"Daily limit reached: {max_posts} posts maximum. Current: {posts_today}"
        
        elif action == 'generate_content':
            db = get_db()
            from bson import ObjectId
            
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            generated_today = db.generated_content.count_documents({
                'user_id': ObjectId(user_id),
                'created_at': {'$gte': today, '$lt': tomorrow}
            })
            
            max_generated = limits['max_generated_content']
            if max_generated != -1 and (generated_today + amount) > max_generated:
                return False, f"Daily generation limit reached: {max_generated} maximum. Current: {generated_today}"
        
        return True, "Action allowed"
        
    except Exception as e:
        logger.error(f"Failed to check user limits: {e}")
        return False, "Failed to check limits"

def get_user_stats(user_id, days=30):
    """Get comprehensive user statistics"""
    try:
        db = get_db()
        from bson import ObjectId
        
        user_id_obj = ObjectId(user_id)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get basic counts
        total_posts = db.posts.count_documents({'user_id': user_id_obj})
        recent_posts = db.posts.count_documents({
            'user_id': user_id_obj,
            'created_at': {'$gte': cutoff_date}
        })
        
        connected_platforms = db.social_accounts.count_documents({
            'user_id': user_id_obj,
            'is_active': True
        })
        
        # Get platform breakdown
        platform_pipeline = [
            {'$match': {'user_id': user_id_obj, 'created_at': {'$gte': cutoff_date}}},
            {'$group': {'_id': '$platform', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        
        platform_stats = list(db.posts.aggregate(platform_pipeline))
        
        return {
            'total_posts': total_posts,
            'recent_posts': recent_posts,
            'connected_platforms': connected_platforms,
            'platform_breakdown': platform_stats,
            'period_days': days
        }
        
    except Exception as e:
        logger.error(f"Failed to get user stats for {user_id}: {e}")
        return {}

# Cleanup functions
def cleanup_expired_data():
    """Clean up expired data from database"""
    try:
        db = get_db()
        
        # Clean up expired OAuth states
        result = db.oauth_states.delete_many({
            'expires_at': {'$lt': datetime.utcnow()}
        })
        logger.info(f"Cleaned up {result.deleted_count} expired OAuth states")
        
        # Clean up old password reset tokens
        result = db.users.update_many(
            {'password_reset_expires': {'$lt': datetime.utcnow()}},
            {'$unset': {'password_reset_token': '', 'password_reset_expires': ''}}
        )
        logger.info(f"Cleaned up {result.modified_count} expired password reset tokens")
        
        return True
        
    except Exception as e:
        logger.error(f"Data cleanup failed: {e}")
        return False

# Connection health check
def get_database_health():
    """Get comprehensive database health information"""
    try:
        client = db_manager.get_client()
        db = get_db()
        
        # Server status
        server_status = db.command('serverStatus')
        
        # Database stats
        db_stats = db.command('dbStats')
        
        # Connection info
        connection_info = {
            'server_version': server_status.get('version', 'unknown'),
            'uptime_seconds': server_status.get('uptime', 0),
            'connections': server_status.get('connections', {}),
            'database_size_mb': round(db_stats.get('dataSize', 0) / 1024 / 1024, 2),
            'collections_count': len(db.list_collection_names()),
            'indexes_count': sum(len(db[col].list_indexes()) for col in db.list_collection_names())
        }
        
        return {
            'status': 'healthy',
            'connection_string': db_manager.connection_string.split('@')[1] if '@' in str(db_manager.connection_string) else 'local',
            'database_name': db_manager.database_name,
            'info': connection_info
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            'status': 'unhealthy',
            'error': str(e)
        }

if __name__ == '__main__':
    try:
        init_db()
        print("Database connection successful")
        health = get_database_health()
        print(f"Database health: {health}")
        
        # Run connection test
        if test_database_connection():
            print("Database read/write test passed")
        else:
            print("Database read/write test failed")
            
    except Exception as e:
        print(f"Database setup failed: {e}")
        logger.error(f"Database setup failed: {e}")