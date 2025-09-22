"""
Multi-User Database Manager with Authentication and Individual Reddit Connections
Fixed for PyMongo 4.15.0 + Python 3.13 compatibility
Each user has their own Reddit tokens and automation settings
Persistent token storage with automatic refresh handling
"""

import asyncio
import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

# Fix PyMongo compatibility issues
try:
    import motor.motor_asyncio
    import pymongo
    from bson import ObjectId
    MOTOR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Motor/PyMongo import failed: {e}")
    MOTOR_AVAILABLE = False

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    logging.warning("bcrypt not available, using basic password hashing")

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logging.warning("JWT not available, using basic tokens")

logger = logging.getLogger(__name__)

class MultiUserDatabaseManager:
    """
    Enhanced database manager supporting multiple users with individual Reddit connections
    Handles JWT authentication, per-user Reddit tokens, and automation configs
    Compatible with PyMongo 4.15.0 and Python 3.13
    """
    
    def __init__(self, mongodb_uri: str):
        self.mongodb_uri = mongodb_uri
        self.client = None
        self.database = None
        self.connected = False
        
        # JWT secret from environment or generate secure one
        self.jwt_secret = os.getenv("JWT_SECRET_KEY") or secrets.token_urlsafe(32)
        if len(self.jwt_secret) < 32:
            self.jwt_secret = secrets.token_urlsafe(32)
            logger.warning("JWT_SECRET_KEY too short, generated new one")
        
        # Collections for multi-user system
        self.collections = {
            "users": "users",
            "user_sessions": "user_sessions", 
            "reddit_tokens": "reddit_tokens",  # Per-user Reddit tokens
            "reddit_activity": "reddit_activity",  # Per-user activity
            "automation_configs": "automation_configs",  # Per-user automation settings
            "ai_usage": "ai_content_generation",
            "analytics": "platform_analytics",
            "automation_logs": "automation_logs",
            "oauth_states": "oauth_states",  # ADDED: OAuth state storage
            "migrations": "migrations"
        }

    async def connect(self) -> bool:
        """Connect to MongoDB Atlas with multi-user support and compatibility fixes"""
        try:
            if not MOTOR_AVAILABLE:
                logger.error("Motor/PyMongo not available - using fallback")
                return False
            
            # Create connection with proper configuration for Python 3.13
            connection_params = {
                "serverSelectionTimeoutMS": 5000,  # 5 second timeout
                "connectTimeoutMS": 10000,  # 10 second connection timeout
                "socketTimeoutMS": 20000,   # 20 second socket timeout
                "maxPoolSize": 10,
                "retryWrites": True,
                "w": "majority"  # Write concern
            }
            
            # Handle potential SSL/TLS issues in new Python versions
            if "ssl=true" in self.mongodb_uri or "ssl_cert_reqs" in self.mongodb_uri:
                connection_params["ssl"] = True
                connection_params["ssl_cert_reqs"] = 0  # Don't require SSL certs
            
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                self.mongodb_uri,
                **connection_params
            )
            
            self.database = self.client.socialMedia
            
            # Test connection with proper error handling
            try:
                await asyncio.wait_for(
                    self.client.admin.command('ping'), 
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                logger.error("MongoDB connection timeout")
                return False
            
            self.connected = True
            
            # Create indexes for multi-user system
            await self._create_indexes()
            
            # Run any needed migrations
            await self.migrate_data_if_needed()
            
            logger.info("Multi-user MongoDB Atlas connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from MongoDB"""
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                logger.warning(f"Error closing MongoDB connection: {e}")
            finally:
                self.connected = False
                logger.info("MongoDB disconnected")

    async def _create_indexes(self) -> None:
        """Create database indexes for multi-user system performance with error handling"""
        if not self.connected:
            return
            
        try:
            # User indexes with error handling
            try:
                await self.database.users.create_index("email", unique=True)
                await self.database.users.create_index("created_at")
                await self.database.users.create_index("is_active")
                logger.debug("User indexes created")
            except Exception as e:
                logger.warning(f"User indexes creation failed: {e}")
            
            # Reddit token indexes (per user)
            try:
                await self.database.reddit_tokens.create_index("user_id", unique=True)
                await self.database.reddit_tokens.create_index("reddit_username")
                await self.database.reddit_tokens.create_index("expires_at")
                await self.database.reddit_tokens.create_index("is_active")
                logger.debug("Reddit token indexes created")
            except Exception as e:
                logger.warning(f"Reddit token indexes creation failed: {e}")
            
            # Automation config indexes
            try:
                await self.database.automation_configs.create_index([("user_id", 1), ("config_type", 1)], unique=True)
                await self.database.automation_configs.create_index("enabled")
                logger.debug("Automation config indexes created")
            except Exception as e:
                logger.warning(f"Automation config indexes creation failed: {e}")
            
            # Activity indexes (per user)
            try:
                await self.database.reddit_activity.create_index([("user_id", 1), ("timestamp", -1)])
                await self.database.reddit_activity.create_index([("user_id", 1), ("activity_type", 1)])
                await self.database.reddit_activity.create_index("timestamp")
                logger.debug("Activity indexes created")
            except Exception as e:
                logger.warning(f"Activity indexes creation failed: {e}")
            
            # ADDED: OAuth state indexes
            try:
                await self.database.oauth_states.create_index("expires_at", expireAfterSeconds=900)  # Auto-cleanup after 15 min
                await self.database.oauth_states.create_index("user_id")
                await self.database.oauth_states.create_index("created_at")
                logger.debug("OAuth state indexes created")
            except Exception as e:
                logger.warning(f"OAuth state indexes creation failed: {e}")
            
            logger.info("Multi-user database indexes setup completed")
            
        except Exception as e:
            logger.warning(f"Index creation failed: {e}")

    def _hash_password(self, password: str) -> bytes:
        """Hash password with fallback for systems without bcrypt"""
        if BCRYPT_AVAILABLE:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        else:
            # Basic fallback hashing (not recommended for production)
            import hashlib
            salt = secrets.token_hex(16)
            return f"{salt}:{hashlib.sha256((salt + password).encode()).hexdigest()}".encode()

    def _verify_password(self, password: str, password_hash: bytes) -> bool:
        """Verify password with fallback for systems without bcrypt"""
        if BCRYPT_AVAILABLE:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash)
        else:
            # Basic fallback verification
            import hashlib
            try:
                hash_str = password_hash.decode('utf-8')
                salt, hash_value = hash_str.split(':', 1)
                computed_hash = hashlib.sha256((salt + password).encode()).hexdigest()
                return computed_hash == hash_value
            except:
                return False

    # ADDED: OAuth State Management Methods
    async def store_oauth_state(self, state: str, user_id: str, expires_at: datetime) -> Dict[str, Any]:
        """Store OAuth state for Reddit authorization flow"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            state_doc = {
                "_id": state,  # Use state as the document ID for easy lookup
                "user_id": user_id,
                "expires_at": expires_at,
                "created_at": datetime.utcnow(),
                "oauth_type": "reddit"
            }
            
            await self.database.oauth_states.insert_one(state_doc)
            
            logger.info(f"OAuth state stored: {state} for user {user_id}")
            
            return {"success": True, "message": "OAuth state stored successfully"}
            
        except Exception as e:
            logger.error(f"Store OAuth state failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_oauth_state(self, state: str) -> Optional[Dict[str, Any]]:
        """Get OAuth state from database"""
        try:
            if not self.connected:
                return None
                
            state_doc = await self.database.oauth_states.find_one({"_id": state})
            
            if not state_doc:
                logger.warning(f"OAuth state not found: {state}")
                return None
            
            # Check if expired
            if state_doc["expires_at"] <= datetime.utcnow():
                logger.warning(f"OAuth state expired: {state}")
                # Clean up expired state
                await self.database.oauth_states.delete_one({"_id": state})
                return None
            
            logger.info(f"OAuth state found: {state} for user {state_doc['user_id']}")
            return {
                "user_id": state_doc["user_id"],
                "expires_at": state_doc["expires_at"],
                "created_at": state_doc["created_at"]
            }
            
        except Exception as e:
            logger.error(f"Get OAuth state failed: {e}")
            return None

    async def cleanup_oauth_state(self, state: str) -> Dict[str, Any]:
        """Remove OAuth state from database after use"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            result = await self.database.oauth_states.delete_one({"_id": state})
            
            if result.deleted_count > 0:
                logger.info(f"OAuth state cleaned up: {state}")
                return {"success": True, "message": "OAuth state cleaned up"}
            else:
                return {"success": False, "message": "OAuth state not found"}
            
        except Exception as e:
            logger.error(f"Cleanup OAuth state failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_all_oauth_states(self) -> List[str]:
        """Debug method to get all stored OAuth states"""
        try:
            if not self.connected:
                return []
            
            cursor = self.database.oauth_states.find({}, {"_id": 1})
            states = []
            async for doc in cursor:
                states.append(doc["_id"])
            
            return states
            
        except Exception as e:
            logger.error(f"Get all OAuth states failed: {e}")
            return []

    # User Authentication Methods
    async def register_user(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """
        Register new user with email and password
        Compatible with PyMongo 4.15.0 and Python 3.13
        """
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            # Normalize email
            email = email.lower().strip()
            
            # Check if user already exists
            try:
                existing_user = await self.database.users.find_one({"email": email})
                if existing_user:
                    return {
                        "success": False,
                        "error": "User already exists",
                        "message": "An account with this email already exists"
                    }
            except Exception as e:
                logger.error(f"Error checking existing user: {e}")
                return {"success": False, "error": "Database query failed"}
            
            # Validate inputs
            if len(password) < 6:
                return {
                    "success": False,
                    "error": "Password too short",
                    "message": "Password must be at least 6 characters long"
                }
            
            if len(name.strip()) < 2:
                return {
                    "success": False,
                    "error": "Invalid name",
                    "message": "Name must be at least 2 characters long"
                }
            
            # Hash password securely
            password_hash = self._hash_password(password)
            
            # Create user document
            user_doc = {
                "email": email,
                "name": name.strip(),
                "password_hash": password_hash,
                "created_at": datetime.utcnow(),
                "last_login": None,
                "is_active": True,
                "subscription_tier": "free",
                "platforms_connected": [],
                "total_posts": 0,
                "total_earnings": 0.0,
                "preferences": {
                    "auto_posting": False,
                    "auto_replies": False,
                    "notification_email": True,
                    "timezone": "UTC"
                },
                "profile": {
                    "bio": "",
                    "website": "",
                    "location": ""
                }
            }
            
            # Insert user into database
            result = await self.database.users.insert_one(user_doc)
            user_id = str(result.inserted_id)
            
            # Generate JWT token
            token = self._generate_jwt_token(user_id, email, name)
            
            logger.info(f"New user registered: {email} (ID: {user_id})")
            
            return {
                "success": True,
                "user_id": user_id,
                "email": email,
                "name": name,
                "token": token,
                "message": "User registered successfully",
                "expires_in": "7 days"
            }
            
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Registration failed due to server error"
            }
    
    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Login user with email and password - PyMongo 4.15.0 compatible"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            # Normalize email
            email = email.lower().strip()
            
            # Find user by email
            try:
                user = await self.database.users.find_one({"email": email, "is_active": True})
                if not user:
                    return {
                        "success": False,
                        "error": "Invalid credentials",
                        "message": "Email or password is incorrect"
                    }
            except Exception as e:
                logger.error(f"Error finding user: {e}")
                return {"success": False, "error": "Database query failed"}
            
            # Verify password
            if not self._verify_password(password, user['password_hash']):
                return {
                    "success": False,
                    "error": "Invalid credentials", 
                    "message": "Email or password is incorrect"
                }
            
            # Update last login
            user_id = str(user['_id'])
            try:
                await self.database.users.update_one(
                    {"_id": user['_id']},
                    {"$set": {"last_login": datetime.utcnow()}}
                )
            except Exception as e:
                logger.warning(f"Failed to update last login: {e}")
            
            # Generate JWT token
            token = self._generate_jwt_token(user_id, email, user['name'])
            
            # Check Reddit connection status
            reddit_status = await self.check_reddit_connection(user_id)
            
            logger.info(f"User logged in: {email} (ID: {user_id})")
            
            return {
                "success": True,
                "user_id": user_id,
                "email": user['email'],
                "name": user['name'],
                "token": token,
                "reddit_connected": reddit_status.get("connected", False),
                "reddit_username": reddit_status.get("reddit_username"),
                "message": "Login successful",
                "expires_in": "7 days"
            }
            
        except Exception as e:
            logger.error(f"User login failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Login failed due to server error"
            }
    
    def _generate_jwt_token(self, user_id: str, email: str, name: str) -> str:
        """Generate JWT token for user authentication with fallback"""
        if JWT_AVAILABLE:
            payload = {
                'user_id': user_id,
                'email': email,
                'name': name,
                'exp': datetime.utcnow() + timedelta(days=7),
                'iat': datetime.utcnow(),
                'type': 'access_token'
            }
            return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        else:
            # Basic token fallback
            import base64
            import json
            token_data = {
                'user_id': user_id,
                'email': email,
                'name': name,
                'exp': (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
            return base64.b64encode(json.dumps(token_data).encode()).decode()
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return user info with fallback"""
        try:
            if JWT_AVAILABLE:
                payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
                return {
                    "valid": True,
                    "user_id": payload['user_id'],
                    "email": payload['email'],
                    "name": payload.get('name', ''),
                    "expires": payload.get('exp')
                }
            else:
                # Basic token verification fallback
                import base64
                import json
                from datetime import datetime
                
                payload = json.loads(base64.b64decode(token.encode()).decode())
                exp_time = datetime.fromisoformat(payload['exp'])
                
                if datetime.utcnow() > exp_time:
                    return {"valid": False, "error": "Token expired"}
                
                return {
                    "valid": True,
                    "user_id": payload['user_id'],
                    "email": payload['email'],
                    "name": payload.get('name', ''),
                    "expires": payload.get('exp')
                }
        except Exception as e:
            logger.warning(f"Token verification failed: {e}")
            return {"valid": False, "error": "Invalid token"}

    async def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from JWT token - PyMongo 4.15.0 compatible"""
        if not self.connected:
            return None
            
        token_data = self.verify_jwt_token(token)
        if not token_data.get("valid"):
            return None
        
        try:
            user = await self.database.users.find_one({
                "_id": ObjectId(token_data["user_id"]),
                "is_active": True
            })
            
            if user:
                user["id"] = str(user["_id"])
                del user["_id"]
                del user["password_hash"]  # Never return password hash
                
                # Add Reddit connection status
                reddit_status = await self.check_reddit_connection(user["id"])
                user["reddit_connected"] = reddit_status["connected"]
                if reddit_status["connected"]:
                    user["reddit_username"] = reddit_status.get("reddit_username")
                
            return user
        except Exception as e:
            logger.error(f"Get user by token failed: {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID without password hash - PyMongo 4.15.0 compatible"""
        try:
            if not self.connected:
                return None
                
            user = await self.database.users.find_one({
                "_id": ObjectId(user_id),
                "is_active": True
            })
            if user:
                user["id"] = str(user["_id"])
                del user["_id"]
                del user["password_hash"]  # Never return password hash
            return user
        except Exception as e:
            logger.error(f"Get user by ID failed: {e}")
            return None

    # Reddit Token Management (Per-User) - PyMongo 4.15.0 Compatible
    async def store_reddit_tokens(self, user_id: str, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store Reddit tokens for specific user permanently"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            current_time = datetime.utcnow()
            expires_in = token_data.get("expires_in", 3600)
            expires_at = current_time + timedelta(seconds=expires_in)
            
            token_doc = {
                "user_id": user_id,
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token"),
                "token_type": token_data.get("token_type", "bearer"),
                "expires_in": expires_in,
                "expires_at": expires_at,
                "reddit_username": token_data.get("reddit_username", "Unknown"),
                "reddit_user_id": token_data.get("reddit_user_id"),
                "scopes": token_data.get("scope", "").split() if token_data.get("scope") else ["submit", "edit", "read"],
                "created_at": current_time,
                "updated_at": current_time,
                "is_active": True,
                "last_used": current_time
            }
            
            # Upsert token document (one per user)
            await self.database.reddit_tokens.update_one(
                {"user_id": user_id},
                {"$set": token_doc},
                upsert=True
            )
            
            # Update user's platform connections
            try:
                await self.database.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {
                        "$addToSet": {"platforms_connected": "reddit"},
                        "$set": {"last_reddit_connection": current_time}
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to update user platforms: {e}")
            
            logger.info(f"Reddit tokens stored permanently for user {user_id} as {token_data.get('reddit_username')}")
            
            return {
                "success": True,
                "message": "Reddit tokens stored successfully",
                "expires_at": expires_at.isoformat(),
                "reddit_username": token_data.get("reddit_username"),
                "stored_at": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Store Reddit tokens failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_reddit_tokens(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get Reddit tokens for specific user with auto-refresh logic"""
        try:
            if not self.connected:
                return None
                
            token_doc = await self.database.reddit_tokens.find_one({
                "user_id": user_id,
                "is_active": True
            })
            
            if not token_doc:
                return None
            
            current_time = datetime.utcnow()
            
            # Check if token is expired
            if token_doc["expires_at"] <= current_time:
                logger.warning(f"Reddit token expired for user {user_id}")
                
                if token_doc.get("refresh_token"):
                    return {
                        "need_refresh": True,
                        "refresh_token": token_doc["refresh_token"],
                        "reddit_username": token_doc["reddit_username"],
                        "expired_at": token_doc["expires_at"].isoformat()
                    }
                else:
                    # Mark as inactive and require reconnection
                    await self.database.reddit_tokens.update_one(
                        {"user_id": user_id},
                        {"$set": {"is_active": False, "expired_at": current_time}}
                    )
                    return None
            
            # Update last accessed time
            try:
                await self.database.reddit_tokens.update_one(
                    {"user_id": user_id},
                    {"$set": {"last_used": current_time}}
                )
            except Exception as e:
                logger.warning(f"Failed to update last used time: {e}")
            
            return {
                "access_token": token_doc["access_token"],
                "refresh_token": token_doc.get("refresh_token"),
                "token_type": token_doc.get("token_type", "bearer"),
                "expires_at": token_doc["expires_at"],
                "reddit_username": token_doc["reddit_username"],
                "reddit_user_id": token_doc.get("reddit_user_id"),
                "scopes": token_doc.get("scopes", []),
                "is_valid": True,
                "last_used": token_doc.get("last_used", token_doc["created_at"]).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Get Reddit tokens failed: {e}")
            return None

    async def check_reddit_connection(self, user_id: str) -> Dict[str, Any]:
        """Check Reddit connection status for specific user"""
        try:
            tokens = await self.get_reddit_tokens(user_id)
            
            if not tokens:
                return {
                    "connected": False, 
                    "message": "No Reddit connection found"
                }
            
            if tokens.get("need_refresh"):
                return {
                    "connected": True,
                    "needs_refresh": True,
                    "reddit_username": tokens["reddit_username"],
                    "message": "Token needs refresh"
                }
            
            return {
                "connected": True,
                "reddit_username": tokens["reddit_username"],
                "expires_at": tokens["expires_at"],
                "scopes": tokens.get("scopes", []),
                "last_used": tokens.get("last_used"),
                "message": "Reddit connection active"
            }
            
        except Exception as e:
            logger.error(f"Check Reddit connection failed: {e}")
            return {"connected": False, "error": str(e)}

    async def revoke_reddit_connection(self, user_id: str) -> Dict[str, Any]:
        """Revoke Reddit connection for specific user"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            # Mark tokens as inactive
            result = await self.database.reddit_tokens.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "is_active": False,
                        "revoked_at": datetime.utcnow()
                    }
                }
            )
            
            # Remove from user's connected platforms
            try:
                await self.database.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$pull": {"platforms_connected": "reddit"}}
                )
            except Exception as e:
                logger.warning(f"Failed to update user platforms: {e}")
            
            if result.modified_count > 0:
                logger.info(f"Reddit connection revoked for user {user_id}")
                return {"success": True, "message": "Reddit connection revoked"}
            else:
                return {"success": False, "message": "No active Reddit connection found"}
            
        except Exception as e:
            logger.error(f"Revoke Reddit connection failed: {e}")
            return {"success": False, "error": str(e)}

    # User-Specific Automation Settings
    async def store_automation_config(self, user_id: str, config_type: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store automation configuration for specific user"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            config_doc = {
                "user_id": user_id,
                "config_type": config_type,  # 'auto_posting' or 'auto_replies'
                "config_data": config_data,
                "enabled": config_data.get("enabled", True),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Upsert config (one per user per type)
            await self.database.automation_configs.update_one(
                {"user_id": user_id, "config_type": config_type},
                {"$set": config_doc},
                upsert=True
            )
            
            logger.info(f"Automation config stored for user {user_id}: {config_type}")
            
            return {"success": True, "message": "Automation config saved"}
            
        except Exception as e:
            logger.error(f"Store automation config failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_automation_config(self, user_id: str, config_type: str) -> Optional[Dict[str, Any]]:
        """Get automation configuration for specific user"""
        try:
            if not self.connected:
                return None
                
            config = await self.database.automation_configs.find_one({
                "user_id": user_id,
                "config_type": config_type,
                "enabled": True
            })
            
            return config["config_data"] if config else None
            
        except Exception as e:
            logger.error(f"Get automation config failed: {e}")
            return None
        











    async def get_all_active_automations(self, config_type: str) -> List[Dict[str, Any]]:
        """Get all active automation configs for scheduling across all users"""
        try:
            if not self.connected:
                return []
                
            cursor = self.database.automation_configs.find({
                "config_type": config_type,
                "enabled": True
            })
            
            # Convert cursor to list with proper error handling
            configs = []
            async for config in cursor:
                configs.append(config)
            
            return configs
            
        except Exception as e:
            logger.error(f"Get active automations failed: {e}")
            return []

    # User-Specific Activity Logging
    async def log_reddit_activity(self, user_id: str, activity_type: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log Reddit activity for specific user"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            activity_doc = {
                "user_id": user_id,
                "platform": "reddit",
                "activity_type": activity_type,  # 'post', 'comment', 'reply'
                "timestamp": datetime.utcnow(),
                "data": activity_data,
                "success": activity_data.get("success", True),
                "subreddit": activity_data.get("subreddit"),
                "post_id": activity_data.get("post_id"),
                "post_url": activity_data.get("post_url"),
                "title": activity_data.get("title", ""),
                "score": activity_data.get("score", 0),
                "engagement": activity_data.get("num_comments", 0),
                "automated": activity_data.get("automated", False)
            }
            
            await self.database.reddit_activity.insert_one(activity_doc)
            
            # Update user statistics
            if activity_type == "post" and activity_data.get("success"):
                try:
                    await self.database.users.update_one(
                        {"_id": ObjectId(user_id)},
                        {"$inc": {"total_posts": 1}}
                    )
                except Exception as e:
                    logger.warning(f"Failed to update user stats: {e}")
            
            return {"success": True, "message": "Activity logged successfully"}
            
        except Exception as e:
            logger.error(f"Log Reddit activity failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_user_activity(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get user's Reddit activity for specified days"""
        try:
            if not self.connected:
                return {"error": "Database not connected"}
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get activities for this user only
            cursor = self.database.reddit_activity.find({
                "user_id": user_id,
                "timestamp": {"$gte": start_date}
            }).sort("timestamp", -1)
            
            # Convert cursor to list
            activities = []
            async for activity in cursor:
                activities.append(activity)
            
            # Separate by type
            posts = [a for a in activities if a["activity_type"] == "post"]
            replies = [a for a in activities if a["activity_type"] == "reply"]
            
            # Calculate stats
            total_karma = sum(a.get("score", 0) for a in activities)
            successful_posts = len([p for p in posts if p.get("success")])
            
            return {
                "posts": posts,
                "replies": replies,
                "total_posts": len(posts),
                "total_replies": len(replies),
                "successful_posts": successful_posts,
                "total_karma": total_karma,
                "period_days": days,
                "start_date": start_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Get user activity failed: {e}")
            return {"error": str(e)}

    async def get_user_analytics(self, user_id: str, period: str = "week") -> Dict[str, Any]:
        """Get analytics data for specific user - PyMongo 4.15.0 compatible"""
        try:
            if not self.connected:
                return {"error": "Database not connected"}
            
            # Calculate date range
            if period == "week":
                start_date = datetime.utcnow() - timedelta(days=7)
            elif period == "month":
                start_date = datetime.utcnow() - timedelta(days=30)
            elif period == "year":
                start_date = datetime.utcnow() - timedelta(days=365)
            else:
                start_date = datetime.utcnow() - timedelta(days=7)
            
            # Use compatible aggregation pipeline
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "timestamp": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$activity_type",
                        "count": {"$sum": 1},
                        "total_score": {"$sum": "$score"},
                        "successful": {
                            "$sum": {"$cond": [{"$eq": ["$success", True]}, 1, 0]}
                        }
                    }
                }
            ]
            
            cursor = self.database.reddit_activity.aggregate(pipeline)
            
            # Convert cursor to list safely
            results = []
            async for result in cursor:
                results.append(result)
            
            # Process results
            analytics = {
                "posts_count": 0,
                "replies_count": 0,
                "total_karma": 0,
                "successful_posts": 0,
                "success_rate": 0,
                "period": period
            }
            
            for result in results:
                if result["_id"] == "post":
                    analytics["posts_count"] = result["count"]
                    analytics["successful_posts"] = result["successful"]
                    analytics["total_karma"] += result["total_score"]
                elif result["_id"] == "reply":
                    analytics["replies_count"] = result["count"]
                    analytics["total_karma"] += result["total_score"]
            
            # Calculate success rate
            if analytics["posts_count"] > 0:
                analytics["success_rate"] = round(
                    (analytics["successful_posts"] / analytics["posts_count"]) * 100, 2
                )
            
            # Get top subreddits for this user
            top_subreddits_pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "timestamp": {"$gte": start_date},
                        "subreddit": {"$exists": True, "$ne": ""}
                    }
                },
                {
                    "$group": {
                        "_id": "$subreddit",
                        "count": {"$sum": 1},
                        "total_score": {"$sum": "$score"}
                    }
                },
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            
            cursor = self.database.reddit_activity.aggregate(top_subreddits_pipeline)
            
            # Convert cursor to list safely
            top_subreddits = []
            async for item in cursor:
                top_subreddits.append(item)
            
            analytics["top_subreddits"] = [
                {
                    "subreddit": item["_id"],
                    "posts": item["count"],
                    "total_karma": item["total_score"]
                }
                for item in top_subreddits
            ]
            
            return analytics
            
        except Exception as e:
            logger.error(f"Get user analytics failed: {e}")
            return {"error": str(e)}

    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for specific user"""
        try:
            if not self.connected:
                return {"error": "Database not connected"}
            
            user = await self.get_user_by_id(user_id)
            if not user:
                return {"error": "User not found"}
            
            # Get Reddit connection status
            reddit_status = await self.check_reddit_connection(user_id)
            
            # Get today's activity for this user only
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            posts_today = await self.database.reddit_activity.count_documents({
                "user_id": user_id,
                "activity_type": "post",
                "timestamp": {"$gte": today, "$lt": tomorrow},
                "success": True
            })
            
            # Get weekly engagement for this user
            week_ago = datetime.utcnow() - timedelta(days=7)
            engagement_pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "timestamp": {"$gte": week_ago}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_score": {"$sum": "$score"},
                        "total_engagement": {"$sum": "$engagement"}
                    }
                }
            ]
            
            cursor = self.database.reddit_activity.aggregate(engagement_pipeline)
            
            # Get engagement result safely
            engagement_result = []
            async for result in cursor:
                engagement_result.append(result)
            
            engagement = engagement_result[0] if engagement_result else {"total_score": 0, "total_engagement": 0}
            
            # Get automation status
            auto_posting_enabled = bool(await self.get_automation_config(user_id, "auto_posting"))
            auto_replies_enabled = bool(await self.get_automation_config(user_id, "auto_replies"))
            
            return {
                "posts_today": posts_today,
                "total_engagement": engagement["total_engagement"],
                "total_karma": engagement["total_score"],
                "qa_earnings": user.get("total_earnings", 0),
                "active_platforms": len(user.get("platforms_connected", [])),
                "reddit_connected": reddit_status["connected"],
                "reddit_username": reddit_status.get("reddit_username", ""),
                "user_name": user.get("name", ""),
                "user_email": user.get("email", ""),
                "automation_enabled": auto_posting_enabled or auto_replies_enabled,
                "auto_posting_enabled": auto_posting_enabled,
                "auto_replies_enabled": auto_replies_enabled,
                "member_since": user.get("created_at", datetime.utcnow()).isoformat(),
                "subscription_tier": user.get("subscription_tier", "free")
            }
            
        except Exception as e:
            logger.error(f"Get dashboard data failed: {e}")
            return {"error": str(e)}

    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile information"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            # Allowed fields to update
            update_doc = {}
            
            if "name" in profile_data and len(profile_data["name"].strip()) >= 2:
                update_doc["name"] = profile_data["name"].strip()
            
            if "bio" in profile_data:
                update_doc["profile.bio"] = profile_data["bio"][:500]  # Limit bio length
            
            if "website" in profile_data:
                update_doc["profile.website"] = profile_data["website"][:200]
            
            if "location" in profile_data:
                update_doc["profile.location"] = profile_data["location"][:100]
            
            if "preferences" in profile_data and isinstance(profile_data["preferences"], dict):
                for key, value in profile_data["preferences"].items():
                    if key in ["auto_posting", "auto_replies", "notification_email"]:
                        update_doc[f"preferences.{key}"] = bool(value)
                    elif key == "timezone":
                        update_doc[f"preferences.{key}"] = str(value)[:50]
            
            if not update_doc:
                return {"success": False, "message": "No valid fields to update"}
            
            update_doc["updated_at"] = datetime.utcnow()
            
            result = await self.database.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_doc}
            )
            
            if result.modified_count > 0:
                logger.info(f"Profile updated for user {user_id}")
                return {"success": True, "message": "Profile updated successfully"}
            else:
                return {"success": False, "message": "No changes made"}
            
        except Exception as e:
            logger.error(f"Update user profile failed: {e}")
            return {"success": False, "error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Check database health and connection status - PyMongo 4.15.0 compatible"""
        try:
            if not self.connected:
                return {"healthy": False, "error": "Not connected to database"}
            
            # Test database operation
            try:
                await asyncio.wait_for(
                    self.client.admin.command('ping'), 
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                logger.error("Database health check timeout")
                return {"healthy": False, "error": "Database ping timeout"}
            
            # Get collection stats with error handling
            try:
                users_count = await self.database.users.count_documents({"is_active": True})
            except Exception as e:
                logger.warning(f"Failed to count users: {e}")
                users_count = 0
            
            try:
                reddit_tokens_count = await self.database.reddit_tokens.count_documents({"is_active": True})
            except Exception as e:
                logger.warning(f"Failed to count reddit tokens: {e}")
                reddit_tokens_count = 0
            
            try:
                active_automations = await self.database.automation_configs.count_documents({"enabled": True})
            except Exception as e:
                logger.warning(f"Failed to count automations: {e}")
                active_automations = 0
            
            return {
                "healthy": True,
                "connected": True,
                "database_name": "socialMedia",
                "collections": {
                    "users": users_count,
                    "reddit_tokens": reddit_tokens_count,
                    "active_automations": active_automations
                },
                "multi_user_features": {
                    "authentication": True,
                    "per_user_reddit_tokens": True,
                    "per_user_automation": True,
                    "activity_tracking": True,
                    "analytics": True
                },
                "compatibility": {
                    "pymongo_version": getattr(pymongo, "__version__", "unknown"),
                    "motor_available": MOTOR_AVAILABLE,
                    "bcrypt_available": BCRYPT_AVAILABLE,
                    "jwt_available": JWT_AVAILABLE
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"healthy": False, "error": str(e)}

    # AI Usage Tracking - PyMongo 4.15.0 Compatible
    async def log_ai_usage(self, user_id: str, ai_service: str, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log AI usage for billing and analytics"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            usage_doc = {
                "user_id": user_id,
                "ai_service": ai_service,  # 'mistral', 'groq', etc.
                "timestamp": datetime.utcnow(),
                "usage_type": usage_data.get("usage_type", "content_generation"),
                "tokens_used": usage_data.get("tokens_used", 0),
                "cost": usage_data.get("cost", 0.0),
                "success": usage_data.get("success", True),
                "domain": usage_data.get("domain"),
                "content_length": usage_data.get("content_length", 0)
            }
            
            await self.database.ai_usage.insert_one(usage_doc)
            
            return {"success": True, "message": "AI usage logged"}
            
        except Exception as e:
            logger.error(f"Log AI usage failed: {e}")
            return {"success": False, "error": str(e)}

    # Additional Methods for Enhanced Multi-User Support
    async def refresh_reddit_token(self, user_id: str, new_token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh expired Reddit token for specific user"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            current_time = datetime.utcnow()
            expires_in = new_token_data.get("expires_in", 3600)
            expires_at = current_time + timedelta(seconds=expires_in)
            
            update_doc = {
                "access_token": new_token_data["access_token"],
                "expires_in": expires_in,
                "expires_at": expires_at,
                "updated_at": current_time,
                "last_used": current_time,
                "is_active": True
            }
            
            if "refresh_token" in new_token_data:
                update_doc["refresh_token"] = new_token_data["refresh_token"]
            
            result = await self.database.reddit_tokens.update_one(
                {"user_id": user_id},
                {"$set": update_doc}
            )
            
            if result.modified_count > 0:
                logger.info(f"Reddit token refreshed for user {user_id}")
                return {
                    "success": True,
                    "message": "Token refreshed successfully",
                    "expires_at": expires_at.isoformat()
                }
            else:
                return {"success": False, "message": "No token found to refresh"}
            
        except Exception as e:
            logger.error(f"Refresh Reddit token failed: {e}")
            return {"success": False, "error": str(e)}

    async def cleanup_expired_tokens(self) -> Dict[str, Any]:
        """Clean up expired Reddit tokens (maintenance task)"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            current_time = datetime.utcnow()
            
            # Mark expired tokens as inactive
            result = await self.database.reddit_tokens.update_many(
                {
                    "expires_at": {"$lte": current_time},
                    "is_active": True
                },
                {
                    "$set": {
                        "is_active": False,
                        "expired_at": current_time
                    }
                }
            )
            
            logger.info(f"Cleaned up {result.modified_count} expired Reddit tokens")
            
            return {
                "success": True,
                "expired_tokens_cleaned": result.modified_count,
                "cleanup_time": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Token cleanup failed: {e}")
            return {"success": False, "error": str(e)}

    # Database Migration and Maintenance
    async def migrate_data_if_needed(self) -> Dict[str, Any]:
        """Handle database schema migrations for updates"""
        try:
            if not self.connected:
                return {"success": False, "error": "Database not connected"}
            
            # Check if migration is needed
            try:
                migration_status = await self.database.migrations.find_one({"_id": "latest"})
                current_version = migration_status.get("version", 0) if migration_status else 0
            except Exception as e:
                logger.warning(f"Failed to check migration status: {e}")
                current_version = 0
            
            target_version = 1  # Current target version
            
            if current_version >= target_version:
                return {"success": True, "message": "Database already up to date"}
            
            # Perform migrations
            migrations_performed = []
            
            # Migration 1: Add indexes if they don't exist
            if current_version < 1:
                await self._create_indexes()
                migrations_performed.append("indexes_created")
            
            # Update migration status
            try:
                await self.database.migrations.update_one(
                    {"_id": "latest"},
                    {
                        "$set": {
                            "version": target_version,
                            "updated_at": datetime.utcnow(),
                            "migrations_performed": migrations_performed
                        }
                    },
                    upsert=True
                )
            except Exception as e:
                logger.warning(f"Failed to update migration status: {e}")
            
            logger.info(f"Database migrated to version {target_version}")
            
            return {
                "success": True,
                "from_version": current_version,
                "to_version": target_version,
                "migrations_performed": migrations_performed
            }
            
        except Exception as e:
            logger.error(f"Database migration failed: {e}")
            return {"success": False, "error": str(e)}

# Create a global instance that can be imported
database_manager = None

async def get_database_manager(mongodb_uri: str = None) -> MultiUserDatabaseManager:
    """Get or create database manager instance"""
    global database_manager
    
    if database_manager is None and mongodb_uri:
        database_manager = MultiUserDatabaseManager(mongodb_uri)
        await database_manager.connect()
    
    return database_manager

async def close_database_connection():
    """Close database connection"""
    global database_manager
    
    if database_manager:
        await database_manager.disconnect()
        database_manager = None