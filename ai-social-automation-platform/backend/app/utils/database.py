"""
Database Configuration for VelocityPost.ai
Supports both local MongoDB and MongoDB Atlas
"""

import os
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db = None
        self.client = None
        self.database_name = 'velocitypost'  # Fixed database name to match
    
    def connect(self, app=None):
        """Connect to MongoDB with fallback support"""
        try:
            # Try MongoDB Atlas first if URI provided
            atlas_uri = os.getenv('MONGODB_ATLAS_URI')
            if atlas_uri:
                logger.info("Attempting to connect to MongoDB Atlas...")
                self.client = MongoClient(
                    atlas_uri,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    maxPoolSize=50,
                    minPoolSize=5
                )
                self.db = self.client[self.database_name]
                # Test connection
                self.client.server_info()
                logger.info("Connected to MongoDB Atlas successfully")
                return True
        except Exception as e:
            logger.warning(f"MongoDB Atlas connection failed: {e}")
        
        try:
            # Fallback to local MongoDB
            local_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/velocitypost')
            logger.info(f"Attempting to connect to local MongoDB: {local_uri}")
            
            # Parse database name from URI
            if '/velocitypost' in local_uri:
                self.database_name = 'velocitypost'
            
            self.client = MongoClient(
                local_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            self.db = self.client[self.database_name]
            # Test connection
            self.client.server_info()
            logger.info(f"Connected to local MongoDB successfully. Database: {self.database_name}")
            return True
        except Exception as e:
            logger.error(f"Local MongoDB connection failed: {e}")
            raise Exception("Failed to connect to any MongoDB instance")
    
    def get_db(self):
        """Get database instance"""
        if self.db is None:
            self.connect()
        return self.db
    
    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

# Global database manager instance
db_manager = DatabaseManager()

def init_db(app=None):
    """Initialize database connection"""
    try:
        db_manager.connect(app)
        if app:
            app.db = db_manager.get_db()
        
        # Create indexes for performance
        create_indexes()
        
        return db_manager.get_db()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def get_db():
    """Get database instance"""
    return db_manager.get_db()

def get_database():
    """Alias for get_db() for compatibility with platforms.py"""
    return get_db()

# MISSING FUNCTION - This is what auth.py needs!
def get_collection(collection_name):
    """Get a specific collection from database"""
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
        try:
            db.users.create_index("email", unique=True)
        except Exception:
            pass  # Index may already exist
            
        db.users.create_index("created_at")
        db.users.create_index([("email", 1), ("is_active", 1)])
        
        # Platform connections collection indexes (renamed from social_accounts)
        try:
            db.platform_connections.create_index([("user_id", 1), ("platform", 1)], unique=True)
        except Exception:
            pass
            
        db.platform_connections.create_index("is_active")
        db.platform_connections.create_index("last_used_at")
        db.platform_connections.create_index("token_expires_at")
        
        # Social accounts collection indexes (for auth.py compatibility)
        try:
            db.social_accounts.create_index([("user_id", 1), ("platform", 1)], unique=True)
        except Exception:
            pass
            
        db.social_accounts.create_index("is_active")
        db.social_accounts.create_index("last_used_at")
        
        # Posts collection indexes
        db.posts.create_index([("user_id", 1), ("created_at", -1)])
        db.posts.create_index([("user_id", 1), ("platform", 1)])
        db.posts.create_index("scheduled_for")
        db.posts.create_index("status")
        db.posts.create_index([("status", 1), ("scheduled_for", 1)])
        
        # Generated content collection indexes
        db.generated_content.create_index([("user_id", 1), ("created_at", -1)])
        db.generated_content.create_index("domain")
        db.generated_content.create_index("platform")
        db.generated_content.create_index([("user_id", 1), ("domain", 1)])
        
        # Automation settings collection indexes
        try:
            db.automation_settings.create_index("user_id", unique=True)
        except Exception:
            pass
            
        db.automation_settings.create_index("is_active")
        
        # Analytics collection indexes
        db.analytics.create_index([("user_id", 1), ("date", -1)])
        db.analytics.create_index([("user_id", 1), ("platform", 1)])
        
        # Subscriptions collection indexes
        try:
            db.subscriptions.create_index("user_id", unique=True)
            db.subscriptions.create_index("stripe_subscription_id", unique=True, sparse=True)
        except Exception:
            pass
            
        db.subscriptions.create_index("plan_type")
        db.subscriptions.create_index("expires_at")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")

# Database Models and Helper Functions

class UserModel:
    """User model for database operations"""
    
    @staticmethod
    def create_user(email, password_hash, name, plan_type='free'):
        """Create a new user"""
        db = get_db()
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'name': name,
            'plan_type': plan_type,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'profile_data': {},
            'settings': {
                'timezone': 'UTC',
                'notifications_enabled': True,
                'auto_posting_enabled': False
            }
        }
        
        result = db.users.insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        db = get_db()
        return db.users.find_one({'email': email})
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        db = get_db()
        from bson import ObjectId
        return db.users.find_one({'_id': ObjectId(user_id)})

class PlatformConnectionModel:
    """Platform connection model for OAuth tokens"""
    
    @staticmethod
    def save_connection(user_id, platform, token_data, profile_data):
        """Save or update platform connection"""
        db = get_db()
        from bson import ObjectId
        
        # Calculate token expiry
        expires_at = None
        if token_data.get('expires_in'):
            expires_at = datetime.utcnow() + timedelta(seconds=int(token_data['expires_in']))
        
        connection_data = {
            'user_id': ObjectId(user_id),
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
            'is_active': True
        }
        
        # Update existing or insert new
        result = db.platform_connections.update_one(
            {'user_id': ObjectId(user_id), 'platform': platform},
            {'$set': connection_data},
            upsert=True
        )
        
        return result.upserted_id or True
    
    @staticmethod
    def get_connections_by_user(user_id):
        """Get all connected platforms for user"""
        db = get_db()
        from bson import ObjectId
        
        connections = list(db.platform_connections.find(
            {'user_id': ObjectId(user_id), 'is_active': True}
        ))
        
        # Remove sensitive data and convert ObjectIds
        for connection in connections:
            connection['_id'] = str(connection['_id'])
            connection['user_id'] = str(connection['user_id'])
            connection.pop('access_token', None)
            connection.pop('refresh_token', None)
        
        return connections
    
    @staticmethod
    def get_connection_by_platform(user_id, platform):
        """Get specific platform connection"""
        db = get_db()
        from bson import ObjectId
        
        return db.platform_connections.find_one({
            'user_id': ObjectId(user_id),
            'platform': platform,
            'is_active': True
        })

class PostModel:
    """Post model for content management"""
    
    @staticmethod
    def create_post(user_id, platform, content, media_urls=None, scheduled_for=None):
        """Create a new post"""
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
            'is_ai_generated': True,
            'engagement_data': {},
            'performance_score': None,
            'platform_post_id': None,
            'error_message': None,
            'posted_at': None
        }
        
        result = db.posts.insert_one(post_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_user_posts(user_id, limit=50, platform=None, status=None):
        """Get user's posts with filters"""
        db = get_db()
        from bson import ObjectId
        
        filter_query = {'user_id': ObjectId(user_id)}
        if platform:
            filter_query['platform'] = platform
        if status:
            filter_query['status'] = status
        
        posts = list(db.posts.find(filter_query)
                    .sort('created_at', -1)
                    .limit(limit))
        
        # Convert ObjectIds to strings
        for post in posts:
            post['_id'] = str(post['_id'])
            post['user_id'] = str(post['user_id'])
        
        return posts
    
    @staticmethod
    def update_post_status(post_id, status, platform_post_id=None, error_message=None):
        """Update post status after posting"""
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
        
        return db.posts.update_one(
            {'_id': ObjectId(post_id)},
            {'$set': update_data}
        )

class ContentModel:
    """Generated content model"""
    
    @staticmethod
    def save_generated_content(user_id, domain, platform, content, performance_prediction=None):
        """Save AI-generated content"""
        db = get_db()
        from bson import ObjectId
        
        content_data = {
            'user_id': ObjectId(user_id),
            'domain': domain,
            'platform': platform,
            'content': content,
            'performance_prediction': performance_prediction,
            'is_used': False,
            'created_at': datetime.utcnow(),
            'hashtags': extract_hashtags(content),
            'word_count': len(content.split()),
            'character_count': len(content)
        }
        
        result = db.generated_content.insert_one(content_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_generated_content(user_id, domain=None, platform=None, limit=20):
        """Get generated content with filters"""
        db = get_db()
        from bson import ObjectId
        
        filter_query = {'user_id': ObjectId(user_id)}
        if domain:
            filter_query['domain'] = domain
        if platform:
            filter_query['platform'] = platform
        
        content = list(db.generated_content.find(filter_query)
                      .sort('created_at', -1)
                      .limit(limit))
        
        # Convert ObjectIds to strings
        for item in content:
            item['_id'] = str(item['_id'])
            item['user_id'] = str(item['user_id'])
        
        return content

def extract_hashtags(content):
    """Extract hashtags from content"""
    import re
    return re.findall(r'#\w+', content)

def test_database_connection():
    """Test database connection"""
    try:
        db = get_db()
        # Test with a simple operation
        result = db.list_collection_names()
        logger.info(f"Database connection test successful. Collections: {len(result)}")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

# Plan limits and validation
PLAN_LIMITS = {
    'free': {
        'max_platforms': 2,
        'max_posts_per_day': 2,
        'max_generated_content': 10,
        'ai_credits': 50
    },
    'pro': {
        'max_platforms': 5,
        'max_posts_per_day': 20,
        'max_generated_content': 1000,
        'ai_credits': 1000
    },
    'agency': {
        'max_platforms': -1,
        'max_posts_per_day': -1,
        'max_generated_content': -1,
        'ai_credits': -1
    }
}

def check_user_limits(user_id, action, platform=None):
    """Check if user can perform action based on their plan"""
    db = get_db()
    from bson import ObjectId
    
    user = db.users.find_one({'_id': ObjectId(user_id)})
    if not user:
        raise ValueError("User not found")
    
    plan_type = user.get('plan_type', 'free')
    limits = PLAN_LIMITS[plan_type]
    
    if action == 'connect_platform':
        connected_count = db.platform_connections.count_documents({
            'user_id': ObjectId(user_id),
            'is_active': True
        })
        
        max_platforms = limits['max_platforms']
        if max_platforms != -1 and connected_count >= max_platforms:
            return False, f"Plan limit reached: {max_platforms} platforms maximum"
    
    elif action == 'create_post':
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        posts_today = db.posts.count_documents({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': today, '$lt': tomorrow}
        })
        
        max_posts = limits['max_posts_per_day']
        if max_posts != -1 and posts_today >= max_posts:
            return False, f"Daily limit reached: {max_posts} posts maximum"
    
    elif action == 'generate_content':
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        generated_today = db.generated_content.count_documents({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': today, '$lt': tomorrow}
        })
        
        max_generated = limits['max_generated_content']
        if max_generated != -1 and generated_today >= max_generated:
            return False, f"Daily generation limit reached: {max_generated} maximum"
    
    return True, "Action allowed"

def validate_user_data(data):
    """Validate user data"""
    required_fields = ['email', 'password', 'name']
    for field in required_fields:
        if not data.get(field):
            raise ValueError(f"Missing required field: {field}")
    
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, data['email']):
        raise ValueError("Invalid email format")
    
    return True

def validate_platform(platform):
    """Validate supported platform"""
    supported_platforms = [
        'facebook', 'instagram', 'twitter', 'linkedin', 
        'youtube', 'pinterest', 'tiktok'
    ]
    
    if platform not in supported_platforms:
        raise ValueError(f"Unsupported platform: {platform}")
    
    return True

def validate_content_domain(domain):
    """Validate content domain"""
    supported_domains = [
        'tech', 'memes', 'business', 'lifestyle', 'fitness',
        'finance', 'travel', 'food', 'entertainment', 'education'
    ]
    
    if domain not in supported_domains:
        raise ValueError(f"Unsupported domain: {domain}")
    
    return True

if __name__ == '__main__':
    try:
        init_db()
        print("Database connection successful")
        test_database_connection()
    except Exception as e:
        print(f"Database connection failed: {e}")