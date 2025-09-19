"""
Multi-User Database Manager for Facebook, Instagram, Threads Automation
Persistent token storage with one-time authentication
Enhanced user management and automation scheduling
"""

import asyncio
import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from cryptography.fernet import Fernet
import base64
import json
import hashlib

try:
    import motor.motor_asyncio
    import pymongo
    from bson import ObjectId
    MOTOR_AVAILABLE = True
except ImportError:
    logging.warning("Motor/PyMongo not available")
    MOTOR_AVAILABLE = False

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

logger = logging.getLogger(__name__)

class MultiUserSocialDatabase:
    """Enhanced database manager for multi-platform social media automation"""
    
    def __init__(self, mongodb_uri: str):
        self.mongodb_uri = mongodb_uri
        self.client = None
        self.database = None
        self.connected = False
        
        # Security configuration
        self.jwt_secret = os.getenv("JWT_SECRET_KEY") or secrets.token_urlsafe(32)
        self.encryption_key = os.getenv("TOKEN_ENCRYPTION_KEY") or Fernet.generate_key().decode()
        self.cipher_suite = Fernet(self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key)
        
        # Collection names for multi-platform support
        self.collections = {
            "users": "users",
            "social_tokens": "social_tokens",  # Facebook, Instagram, Threads tokens
            "automation_configs": "automation_configs",
            "post_queue": "post_queue",  # Scheduled posts
            "post_history": "post_history",  # Posted content history
            "user_analytics": "user_analytics",
            "ai_usage": "ai_usage_logs",
            "platform_connections": "platform_connections"
        }

    async def connect(self) -> bool:
        """Connect to MongoDB Atlas with enhanced error handling"""
        try:
            if not MOTOR_AVAILABLE:
                logger.error("Motor/PyMongo not available")
                return False
            
            connection_params = {
                "serverSelectionTimeoutMS": 10000,
                "connectTimeoutMS": 20000,
                "socketTimeoutMS": 30000,
                "maxPoolSize": 50,
                "retryWrites": True,
                "w": "majority"
            }
            
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongodb_uri, **connection_params)
            self.database = self.client.socialAutomation
            
            # Test connection
            await asyncio.wait_for(self.client.admin.command('ping'), timeout=10.0)
            self.connected = True
            
            # Create indexes
            await self._create_indexes()
            
            logger.info("Multi-user social media database connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from database"""
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
            finally:
                self.connected = False

    async def _create_indexes(self):
        """Create database indexes for optimal performance"""
        if not self.connected:
            return
            
        try:
            # User indexes
            await self.database.users.create_index("email", unique=True)
            await self.database.users.create_index([("created_at", -1)])
            await self.database.users.create_index("is_active")
            
            # Social tokens indexes (persistent auth)
            await self.database.social_tokens.create_index([("user_id", 1), ("platform", 1)], unique=True)
            await self.database.social_tokens.create_index("expires_at")
            await self.database.social_tokens.create_index("is_active")
            
            # Automation config indexes
            await self.database.automation_configs.create_index([("user_id", 1), ("platform", 1)])
            await self.database.automation_configs.create_index("enabled")
            await self.database.automation_configs.create_index("next_run_time")
            
            # Post queue indexes for scheduling
            await self.database.post_queue.create_index([("user_id", 1), ("scheduled_time", 1)])
            await self.database.post_queue.create_index("status")
            await self.database.post_queue.create_index("platform")
            
            # Post history indexes
            await self.database.post_history.create_index([("user_id", 1), ("posted_at", -1)])
            await self.database.post_history.create_index([("platform", 1), ("success", 1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Index creation failed: {e}")

    def _encrypt_token(self, token: str) -> str:
        """Encrypt sensitive tokens"""
        if not token:
            return ""
        encrypted = self.cipher_suite.encrypt(token.encode())
        return base64.b64encode(encrypted).decode()

    def _decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt tokens for use"""
        if not encrypted_token:
            return ""
        try:
            encrypted_data = base64.b64decode(encrypted_token.encode())
            decrypted = self.cipher_suite.decrypt(encrypted_data)
            return decrypted.decode()
        except Exception:
            return ""

    def _hash_password(self, password: str) -> bytes:
        """Hash password securely"""
        if BCRYPT_AVAILABLE:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        else:
            salt = secrets.token_hex(16)
            hash_obj = hashlib.sha256((salt + password).encode())
            return f"{salt}:{hash_obj.hexdigest()}".encode()

    def _verify_password(self, password: str, password_hash: bytes) -> bool:
        """Verify password"""
        if BCRYPT_AVAILABLE:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash)
        else:
            try:
                hash_str = password_hash.decode('utf-8')
                salt, hash_value = hash_str.split(':', 1)
                computed_hash = hashlib.sha256((salt + password).encode()).hexdigest()
                return computed_hash == hash_value
            except:
                return False

    def _generate_jwt_token(self, user_id: str, email: str, name: str) -> str:
        """Generate JWT token for persistent authentication"""
        if JWT_AVAILABLE:
            payload = {
                'user_id': user_id,
                'email': email,
                'name': name,
                'exp': datetime.utcnow() + timedelta(days=30),  # 30-day token
                'iat': datetime.utcnow(),
                'type': 'persistent_access'
            }
            return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        else:
            token_data = {
                'user_id': user_id,
                'email': email,
                'name': name,
                'exp': (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
            return base64.b64encode(json.dumps(token_data).encode()).decode()

    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            if JWT_AVAILABLE:
                payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
                return {"valid": True, "user_id": payload['user_id'], "email": payload['email'], "name": payload.get('name', '')}
            else:
                payload = json.loads(base64.b64decode(token.encode()).decode())
                exp_time = datetime.fromisoformat(payload['exp'])
                if datetime.utcnow() > exp_time:
                    return {"valid": False, "error": "Token expired"}
                return {"valid": True, "user_id": payload['user_id'], "email": payload['email'], "name": payload.get('name', '')}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    # User Management
    async def register_user(self, email: str, password: str, name: str, business_type: str = "", domain: str = "") -> Dict[str, Any]:
        """Register new user with enhanced profile"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            email = email.lower().strip()
            
            # Check existing user
            existing_user = await self.database.users.find_one({"email": email})
            if existing_user:
                return {"success": False, "error": "User already exists"}
            
            # Validate inputs
            if len(password) < 6:
                return {"success": False, "error": "Password must be at least 6 characters"}
            if len(name.strip()) < 2:
                return {"success": False, "error": "Name must be at least 2 characters"}
            
            password_hash = self._hash_password(password)
            
            user_doc = {
                "email": email,
                "name": name.strip(),
                "password_hash": password_hash,
                "business_type": business_type,
                "domain": domain,
                "created_at": datetime.utcnow(),
                "last_login": None,
                "is_active": True,
                "subscription_tier": "free",
                "connected_platforms": [],
                "automation_enabled": False,
                "total_posts": 0,
                "profile": {"bio": "", "website": "", "location": ""},
                "preferences": {"timezone": "UTC", "notifications": True, "auto_posting": False}
            }
            
            result = await self.database.users.insert_one(user_doc)
            user_id = str(result.inserted_id)
            
            token = self._generate_jwt_token(user_id, email, name)
            
            logger.info(f"User registered: {email} (ID: {user_id})")
            
            return {
                "success": True,
                "user_id": user_id,
                "email": email,
                "name": name,
                "token": token,
                "message": "User registered successfully"
            }
            
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            return {"success": False, "error": str(e)}

    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Login user with persistent authentication"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            email = email.lower().strip()
            
            user = await self.database.users.find_one({"email": email, "is_active": True})
            if not user or not self._verify_password(password, user['password_hash']):
                return {"success": False, "error": "Invalid credentials"}
            
            user_id = str(user['_id'])
            
            # Update last login
            await self.database.users.update_one({"_id": user['_id']}, {"$set": {"last_login": datetime.utcnow()}})
            
            token = self._generate_jwt_token(user_id, email, user['name'])
            
            # Get connected platforms
            platforms = await self.get_connected_platforms(user_id)
            
            return {
                "success": True,
                "user_id": user_id,
                "email": user['email'],
                "name": user['name'],
                "token": token,
                "connected_platforms": platforms,
                "message": "Login successful"
            }
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user by JWT token"""
        if not self.connected:
            return None
            
        token_data = self.verify_jwt_token(token)
        if not token_data.get("valid"):
            return None
        
        try:
            user = await self.database.users.find_one({"_id": ObjectId(token_data["user_id"]), "is_active": True})
            if user:
                user["id"] = str(user["_id"])
                del user["_id"]
                del user["password_hash"]
                return user
        except Exception as e:
            logger.error(f"Get user by token failed: {e}")
        return None






    # Platform Token Management (Persistent Authentication)
    async def store_platform_tokens(self, user_id: str, platform: str, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store platform tokens with encryption - ONE TIME AUTH"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            current_time = datetime.utcnow()
            expires_at = current_time + timedelta(seconds=token_data.get("expires_in", 5184000))  # 60 days default
            
            token_doc = {
                "user_id": user_id,
                "platform": platform,  # 'facebook', 'instagram', 'threads'
                "access_token": self._encrypt_token(token_data["access_token"]),
                "refresh_token": self._encrypt_token(token_data.get("refresh_token", "")),
                "platform_user_id": token_data.get("user_id"),
                "platform_username": token_data.get("username"),
                "expires_at": expires_at,
                "pages": token_data.get("pages", []),  # For Facebook pages
                "permissions": token_data.get("permissions", []),
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True,
                "last_used": current_time,
                "auto_refresh": True  # Enable automatic token refresh
            }
            
            # Upsert token (one per user per platform)
            await self.database.social_tokens.update_one(
                {"user_id": user_id, "platform": platform},
                {"$set": token_doc},
                upsert=True
            )
            
            # Update user's connected platforms
            await self.database.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$addToSet": {"connected_platforms": platform},
                    "$set": {f"last_{platform}_connection": current_time}
                }
            )
            
            logger.info(f"{platform.title()} tokens stored for user {user_id}")
            
            return {
                "success": True,
                "message": f"{platform.title()} connected successfully",
                "platform": platform,
                "expires_at": expires_at.isoformat(),
                "persistent_auth": True
            }
            
        except Exception as e:
            logger.error(f"Store {platform} tokens failed: {e}")
            return {"success": False, "error": str(e)}





    async def get_platform_tokens(self, user_id: str, platform: str) -> Optional[Dict[str, Any]]:
        """Get platform tokens with auto-refresh if needed"""
        try:
            if not self.connected:
                return None
                
            token_doc = await self.database.social_tokens.find_one({
                "user_id": user_id,
                "platform": platform,
                "is_active": True
            })
            
            if not token_doc:
                return None
            
            current_time = datetime.utcnow()
            
            # Check if token is expired
            if token_doc["expires_at"] <= current_time:
                if token_doc.get("refresh_token") and token_doc.get("auto_refresh"):
                    return {
                        "needs_refresh": True,
                        "refresh_token": self._decrypt_token(token_doc["refresh_token"]),
                        "platform": platform
                    }
                else:
                    # Mark as inactive - user needs to reconnect
                    await self.database.social_tokens.update_one(
                        {"user_id": user_id, "platform": platform},
                        {"$set": {"is_active": False, "expired_at": current_time}}
                    )
                    return None
            
            # Update last used
            await self.database.social_tokens.update_one(
                {"user_id": user_id, "platform": platform},
                {"$set": {"last_used": current_time}}
            )
            
            return {
                "access_token": self._decrypt_token(token_doc["access_token"]),
                "refresh_token": self._decrypt_token(token_doc.get("refresh_token", "")),
                "platform_user_id": token_doc.get("platform_user_id"),
                "platform_username": token_doc.get("platform_username"),
                "expires_at": token_doc["expires_at"],
                "pages": token_doc.get("pages", []),
                "permissions": token_doc.get("permissions", []),
                "is_valid": True
            }
            
        except Exception as e:
            logger.error(f"Get {platform} tokens failed: {e}")
            return None

    async def get_connected_platforms(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all connected platforms for user"""
        try:
            if not self.connected:
                return []
            
            cursor = self.database.social_tokens.find({
                "user_id": user_id,
                "is_active": True
            })
            
            platforms = []
            async for token_doc in cursor:
                platforms.append({
                    "platform": token_doc["platform"],
                    "username": token_doc.get("platform_username"),
                    "connected_at": token_doc.get("created_at"),
                    "last_used": token_doc.get("last_used"),
                    "expires_at": token_doc.get("expires_at"),
                    "pages_count": len(token_doc.get("pages", []))
                })
            
            return platforms
            
        except Exception as e:
            logger.error(f"Get connected platforms failed: {e}")
            return []

    # Automation Configuration
    async def store_automation_config(self, user_id: str, platform: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store automation configuration for user and platform"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            config_doc = {
                "user_id": user_id,
                "platform": platform,
                "config_type": "auto_posting",
                "enabled": config_data.get("enabled", True),
                "domain": config_data.get("domain"),
                "business_type": config_data.get("business_type"),
                "business_description": config_data.get("business_description", ""),
                "posts_per_day": config_data.get("posts_per_day", 2),
                "posting_times": config_data.get("posting_times", []),
                "content_style": config_data.get("content_style", "engaging"),
                "target_audience": config_data.get("target_audience", "general"),
                "auto_hashtags": config_data.get("auto_hashtags", True),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "next_run_time": self._calculate_next_run_time(config_data.get("posting_times", []))
            }
            
            await self.database.automation_configs.update_one(
                {"user_id": user_id, "platform": platform, "config_type": "auto_posting"},
                {"$set": config_doc},
                upsert=True
            )
            
            # Update user automation status
            await self.database.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"automation_enabled": True}}
            )
            
            logger.info(f"Automation config stored for user {user_id} - {platform}")
            
            return {
                "success": True,
                "message": f"{platform.title()} automation configured",
                "next_run": config_doc["next_run_time"].isoformat() if config_doc["next_run_time"] else None
            }
            
        except Exception as e:
            logger.error(f"Store automation config failed: {e}")
            return {"success": False, "error": str(e)}

    def _calculate_next_run_time(self, posting_times: List[str]) -> Optional[datetime]:
        """Calculate next automation run time"""
        if not posting_times:
            return None
        
        current_time = datetime.utcnow()
        today = current_time.date()
        
        # Find next posting time today or tomorrow
        for time_str in sorted(posting_times):
            try:
                hour, minute = map(int, time_str.split(':'))
                run_time = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
                
                if run_time > current_time:
                    return run_time
            except:
                continue
        
        # No more times today, use first time tomorrow
        try:
            hour, minute = map(int, posting_times[0].split(':'))
            tomorrow = today + timedelta(days=1)
            return datetime.combine(tomorrow, datetime.min.time().replace(hour=hour, minute=minute))
        except:
            return None

    async def get_automation_config(self, user_id: str, platform: str) -> Optional[Dict[str, Any]]:
        """Get automation configuration"""
        try:
            if not self.connected:
                return None
                
            config = await self.database.automation_configs.find_one({
                "user_id": user_id,
                "platform": platform,
                "config_type": "auto_posting",
                "enabled": True
            })
            
            return config
            
        except Exception as e:
            logger.error(f"Get automation config failed: {e}")
            return None

    async def get_pending_automations(self) -> List[Dict[str, Any]]:
        """Get all pending automations for scheduler"""
        try:
            if not self.connected:
                return []
            
            current_time = datetime.utcnow()
            
            cursor = self.database.automation_configs.find({
                "enabled": True,
                "next_run_time": {"$lte": current_time}
            })
            
            automations = []
            async for config in cursor:
                automations.append(config)
            
            return automations
            
        except Exception as e:
            logger.error(f"Get pending automations failed: {e}")
            return []

    # Post Queue Management
    async def add_to_post_queue(self, user_id: str, platform: str, content_data: Dict[str, Any], scheduled_time: datetime = None) -> Dict[str, Any]:
        """Add post to queue for scheduling"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            post_doc = {
                "user_id": user_id,
                "platform": platform,
                "content": content_data.get("content", ""),
                "title": content_data.get("title", ""),
                "image_prompt": content_data.get("image_prompt", ""),
                "hashtags": content_data.get("hashtags", []),
                "scheduled_time": scheduled_time or datetime.utcnow(),
                "status": "queued",
                "created_at": datetime.utcnow(),
                "attempts": 0,
                "max_attempts": 3,
                "automated": True
            }
            
            result = await self.database.post_queue.insert_one(post_doc)
            
            return {
                "success": True,
                "queue_id": str(result.inserted_id),
                "scheduled_time": post_doc["scheduled_time"].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Add to post queue failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_due_posts(self) -> List[Dict[str, Any]]:
        """Get posts due for posting"""
        try:
            if not self.connected:
                return []
            
            current_time = datetime.utcnow()
            
            cursor = self.database.post_queue.find({
                "status": "queued",
                "scheduled_time": {"$lte": current_time},
                "attempts": {"$lt": 3}
            }).sort("scheduled_time", 1)
            
            posts = []
            async for post in cursor:
                post["id"] = str(post["_id"])
                posts.append(post)
            
            return posts
            
        except Exception as e:
            logger.error(f"Get due posts failed: {e}")
            return []

    async def update_post_status(self, queue_id: str, status: str, result_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Update post status after posting attempt"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            update_doc = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if status == "failed":
                update_doc["$inc"] = {"attempts": 1}
                
            if result_data:
                update_doc.update(result_data)
            
            await self.database.post_queue.update_one(
                {"_id": ObjectId(queue_id)},
                {"$set": update_doc}
            )
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Update post status failed: {e}")
            return {"success": False, "error": str(e)}

    # Post History
    async def log_post_activity(self, user_id: str, platform: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log posted content activity"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            activity_doc = {
                "user_id": user_id,
                "platform": platform,
                "post_id": activity_data.get("post_id"),
                "content": activity_data.get("content", ""),
                "title": activity_data.get("title", ""),
                "success": activity_data.get("success", True),
                "post_url": activity_data.get("post_url", ""),
                "engagement": {"likes": 0, "comments": 0, "shares": 0, "views": 0},
                "posted_at": datetime.utcnow(),
                "automated": activity_data.get("automated", False),
                "ai_service": activity_data.get("ai_service", ""),
                "error_message": activity_data.get("error_message", "")
            }
            
            await self.database.post_history.insert_one(activity_doc)
            
            # Update user total posts count
            if activity_data.get("success"):
                await self.database.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$inc": {"total_posts": 1}}
                )
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Log post activity failed: {e}")
            return {"success": False, "error": str(e)}

    # User Analytics
    async def get_user_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive user analytics"""
        try:
            if not self.connected:
                return {"error": "Database not connected"}
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Aggregation pipeline for analytics
            pipeline = [
                {"$match": {"user_id": user_id, "posted_at": {"$gte": start_date}}},
                {"$group": {
                    "_id": {"platform": "$platform", "success": "$success"},
                    "count": {"$sum": 1},
                    "total_engagement": {"$sum": {"$add": ["$engagement.likes", "$engagement.comments", "$engagement.shares"]}}
                }}
            ]
            
            cursor = self.database.post_history.aggregate(pipeline)
            results = []
            async for result in cursor:
                results.append(result)
            
            # Process results
            analytics = {
                "total_posts": 0,
                "successful_posts": 0,
                "failed_posts": 0,
                "total_engagement": 0,
                "platforms": {},
                "period_days": days
            }
            
            for result in results:
                platform = result["_id"]["platform"]
                success = result["_id"]["success"]
                count = result["count"]
                engagement = result["total_engagement"]
                
                if platform not in analytics["platforms"]:
                    analytics["platforms"][platform] = {"posts": 0, "successful": 0, "failed": 0, "engagement": 0}
                
                analytics["total_posts"] += count
                analytics["total_engagement"] += engagement
                analytics["platforms"][platform]["posts"] += count
                analytics["platforms"][platform]["engagement"] += engagement
                
                if success:
                    analytics["successful_posts"] += count
                    analytics["platforms"][platform]["successful"] += count
                else:
                    analytics["failed_posts"] += count
                    analytics["platforms"][platform]["failed"] += count
            
            # Calculate success rate
            if analytics["total_posts"] > 0:
                analytics["success_rate"] = round((analytics["successful_posts"] / analytics["total_posts"]) * 100, 2)
            else:
                analytics["success_rate"] = 0
            
            return analytics
            
        except Exception as e:
            logger.error(f"Get user analytics failed: {e}")
            return {"error": str(e)}

    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get user dashboard data"""
        try:
            if not self.connected:
                return {"error": "Database not connected"}
            
            user = await self.database.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return {"error": "User not found"}
            
            # Get connected platforms
            platforms = await self.get_connected_platforms(user_id)
            
            # Get today's posts
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            posts_today = await self.database.post_history.count_documents({
                "user_id": user_id,
                "posted_at": {"$gte": today, "$lt": tomorrow},
                "success": True
            })
            
            # Get automation status
            active_automations = await self.database.automation_configs.count_documents({
                "user_id": user_id,
                "enabled": True
            })
            
            return {
                "user_name": user.get("name", ""),
                "user_email": user.get("email", ""),
                "posts_today": posts_today,
                "total_posts": user.get("total_posts", 0),
                "connected_platforms": platforms,
                "active_automations": active_automations,
                "automation_enabled": user.get("automation_enabled", False),
                "member_since": user.get("created_at", datetime.utcnow()).isoformat(),
                "subscription_tier": user.get("subscription_tier", "free")
            }
            
        except Exception as e:
            logger.error(f"Get user dashboard failed: {e}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Database health check"""
        try:
            if not self.connected:
                return {"healthy": False, "error": "Not connected"}
            
            await self.client.admin.command('ping')
            
            # Get collection counts
            users_count = await self.database.users.count_documents({"is_active": True})
            tokens_count = await self.database.social_tokens.count_documents({"is_active": True})
            automations_count = await self.database.automation_configs.count_documents({"enabled": True})
            
            return {
                "healthy": True,
                "connected": True,
                "database_name": "socialAutomation",
                "collections": {
                    "active_users": users_count,
                    "active_tokens": tokens_count,
                    "active_automations": automations_count
                },
                "features": {
                    "persistent_auth": True,
                    "multi_platform": True,
                    "automation_scheduling": True,
                    "analytics": True
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"healthy": False, "error": str(e)}

# Global instance
social_database = None

async def get_social_database(mongodb_uri: str = None) -> MultiUserSocialDatabase:
    """Get or create database instance"""
    global social_database
    
    if social_database is None and mongodb_uri:
        social_database = MultiUserSocialDatabase(mongodb_uri)
        await social_database.connect()
    
    return social_database