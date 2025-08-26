from datetime import datetime, timedelta
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import os
from config.database import db_instance

class User:
    def __init__(self, data=None):
        if data:
            self.id = str(data.get('_id', ''))
            self.email = data.get('email', '')
            self.name = data.get('name', '')
            self.password_hash = data.get('password_hash', '')
            self.plan_type = data.get('plan_type', 'free')
            self.is_active = data.get('is_active', True)
            self.created_at = data.get('created_at', datetime.utcnow())
            self.updated_at = data.get('updated_at', datetime.utcnow())
            self.profile_data = data.get('profile_data', {})
            self.subscription_data = data.get('subscription_data', {})

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'plan_type': self.plan_type,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'profile_data': self.profile_data,
            'subscription_data': self.subscription_data
        }

    @staticmethod
    def create_user(email, name, password, plan_type='free'):
        """Create a new user"""
        try:
            db = db_instance.get_db()
            
            # Check if user already exists
            existing_user = db.users.find_one({'email': email})
            if existing_user:
                raise ValueError("User with this email already exists")
            
            # Create user document
            user_data = {
                'email': email.lower().strip(),
                'name': name.strip(),
                'password_hash': generate_password_hash(password),
                'plan_type': plan_type,
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'profile_data': {
                    'posts_this_month': 0,
                    'total_posts': 0,
                    'connected_platforms': [],
                    'last_login': None
                },
                'subscription_data': {
                    'started_at': datetime.utcnow(),
                    'expires_at': None,
                    'status': 'active'
                }
            }
            
            # Insert user
            result = db.users.insert_one(user_data)
            
            # Return created user
            user_data['_id'] = result.inserted_id
            return User(user_data)
            
        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")

    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        try:
            db = db_instance.get_db()
            user_data = db.users.find_one({'email': email.lower().strip()})
            
            if user_data:
                return User(user_data)
            return None
            
        except Exception as e:
            raise Exception(f"Error finding user: {str(e)}")

    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        try:
            db = db_instance.get_db()
            
            # Handle both string and ObjectId
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            user_data = db.users.find_one({'_id': user_id})
            
            if user_data:
                return User(user_data)
            return None
            
        except Exception as e:
            raise Exception(f"Error finding user by ID: {str(e)}")

    def verify_password(self, password):
        """Verify user password"""
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        """Generate JWT token for user"""
        try:
            payload = {
                'user_id': self.id,
                'email': self.email,
                'exp': datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
            }
            
            token = jwt.encode(
                payload,
                os.getenv('JWT_SECRET_KEY', 'default-secret-key'),
                algorithm='HS256'
            )
            
            return token
            
        except Exception as e:
            raise Exception(f"Error generating token: {str(e)}")

    @staticmethod
    def verify_token(token):
        """Verify JWT token and return user"""
        try:
            payload = jwt.decode(
                token,
                os.getenv('JWT_SECRET_KEY', 'default-secret-key'),
                algorithms=['HS256']
            )
            
            user_id = payload.get('user_id')
            if not user_id:
                return None
            
            return User.find_by_id(user_id)
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None

    def update_profile(self, data):
        """Update user profile"""
        try:
            db = db_instance.get_db()
            
            update_data = {
                'updated_at': datetime.utcnow()
            }
            
            # Update allowed fields
            allowed_fields = ['name', 'profile_data']
            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field]
            
            # Update in database
            db.users.update_one(
                {'_id': ObjectId(self.id)},
                {'$set': update_data}
            )
            
            # Update current instance
            for field, value in update_data.items():
                setattr(self, field, value)
            
            return True
            
        except Exception as e:
            raise Exception(f"Error updating profile: {str(e)}")

    def update_plan(self, plan_type):
        """Update user plan"""
        try:
            db = db_instance.get_db()
            
            update_data = {
                'plan_type': plan_type,
                'updated_at': datetime.utcnow(),
                'subscription_data.status': 'active',
                'subscription_data.started_at': datetime.utcnow()
            }
            
            db.users.update_one(
                {'_id': ObjectId(self.id)},
                {'$set': update_data}
            )
            
            self.plan_type = plan_type
            return True
            
        except Exception as e:
            raise Exception(f"Error updating plan: {str(e)}")

    def increment_posts_count(self):
        """Increment user's posts count"""
        try:
            db = db_instance.get_db()
            
            db.users.update_one(
                {'_id': ObjectId(self.id)},
                {
                    '$inc': {
                        'profile_data.posts_this_month': 1,
                        'profile_data.total_posts': 1
                    },
                    '$set': {
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            return True
            
        except Exception as e:
            raise Exception(f"Error incrementing posts count: {str(e)}")

    def get_usage_stats(self):
        """Get user usage statistics"""
        try:
            db = db_instance.get_db()
            
            # Get posts count
            posts_count = db.posts.count_documents({'user_id': self.id})
            
            # Get connected platforms
            platforms_count = db.social_accounts.count_documents({
                'user_id': self.id,
                'is_active': True
            })
            
            # Get plan limits
            plan_limits = self.get_plan_limits()
            
            return {
                'posts_this_month': self.profile_data.get('posts_this_month', 0),
                'total_posts': posts_count,
                'connected_platforms': platforms_count,
                'plan_limits': plan_limits,
                'plan_type': self.plan_type
            }
            
        except Exception as e:
            raise Exception(f"Error getting usage stats: {str(e)}")

    def get_plan_limits(self):
        """Get plan limits based on user plan"""
        limits = {
            'free': {
                'max_platforms': 2,
                'max_posts_per_day': 2,
                'ai_generations_per_month': 50,
                'features': ['2 social media platforms', '2 posts per day', '50 AI generations']
            },
            'pro': {
                'max_platforms': 10,
                'max_posts_per_day': 20,
                'ai_generations_per_month': 1000,
                'features': ['10 platforms', '20 posts per day', '1000 AI generations', 'Advanced analytics']
            },
            'enterprise': {
                'max_platforms': -1,  # Unlimited
                'max_posts_per_day': -1,  # Unlimited
                'ai_generations_per_month': -1,  # Unlimited
                'features': ['Unlimited platforms', 'Unlimited posts', 'Unlimited AI', 'White-label']
            }
        }
        
        return limits.get(self.plan_type, limits['free'])

    def can_create_post(self):
        """Check if user can create more posts today"""
        try:
            if self.plan_type == 'enterprise':
                return True
            
            db = db_instance.get_db()
            
            # Count posts created today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_posts = db.posts.count_documents({
                'user_id': self.id,
                'created_at': {'$gte': today_start}
            })
            
            limits = self.get_plan_limits()
            return today_posts < limits['max_posts_per_day']
            
        except Exception as e:
            return False

    def can_connect_platform(self):
        """Check if user can connect more platforms"""
        try:
            if self.plan_type == 'enterprise':
                return True
            
            db = db_instance.get_db()
            
            connected_count = db.social_accounts.count_documents({
                'user_id': self.id,
                'is_active': True
            })
            
            limits = self.get_plan_limits()
            return connected_count < limits['max_platforms']
            
        except Exception as e:
            return False