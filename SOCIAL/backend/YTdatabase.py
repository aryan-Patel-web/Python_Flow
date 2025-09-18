"""
YouTube Database Manager - MongoDB operations for YouTube automation
Handles user credentials, automation configs, and analytics
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo
from bson import ObjectId

logger = logging.getLogger(__name__)

class YouTubeDatabaseManager:
    """MongoDB database manager specifically for YouTube automation"""
    
    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.database_name = os.getenv("MONGODB_DATABASE", "youtube_automation")
        self.client = None
        self.db = None
        
        # Collections
        self.users_collection = None
        self.youtube_credentials_collection = None
        self.automation_configs_collection = None
        self.upload_history_collection = None
        self.analytics_collection = None
        
        logger.info("YouTube Database Manager initialized")
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_uri)
            self.db = self.client[self.database_name]
            
            # Initialize collections
            self.users_collection = self.db["users"]
            self.youtube_credentials_collection = self.db["youtube_credentials"]
            self.automation_configs_collection = self.db["automation_configs"]
            self.upload_history_collection = self.db["upload_history"]
            self.analytics_collection = self.db["analytics"]
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Create indexes
            await self._create_indexes()
            
            logger.info(f"Connected to YouTube MongoDB: {self.database_name}")
            return True
            
        except Exception as e:
            logger.error(f"YouTube MongoDB connection failed: {e}")
            return False
    
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Users collection indexes
            await self.users_collection.create_index("email", unique=True)
            await self.users_collection.create_index("created_at")
            
            # YouTube credentials indexes
            await self.youtube_credentials_collection.create_index("user_id", unique=True)
            await self.youtube_credentials_collection.create_index("channel_id")
            
            # Automation configs indexes
            await self.automation_configs_collection.create_index("user_id")
            await self.automation_configs_collection.create_index("config_type")
            
            # Upload history indexes
            await self.upload_history_collection.create_index("user_id")
            await self.upload_history_collection.create_index("video_id", unique=True)
            await self.upload_history_collection.create_index("upload_date")
            
            # Analytics indexes
            await self.analytics_collection.create_index("user_id")
            await self.analytics_collection.create_index("date")
            
            logger.info("YouTube database indexes created")
            
        except Exception as e:
            logger.error(f"Index creation failed: {e}")
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("YouTube database connection closed")
    
    # User Management
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        try:
            user_data["created_at"] = datetime.now()
            user_data["youtube_connected"] = False
            user_data["automation_enabled"] = False
            
            result = await self.users_collection.insert_one(user_data)
            
            return {
                "success": True,
                "user_id": str(result.inserted_id),
                "message": "User created successfully"
            }
            
        except pymongo.errors.DuplicateKeyError:
            return {"success": False, "error": "Email already exists"}
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            user = await self.users_collection.find_one({"email": email})
            return user
        except Exception as e:
            logger.error(f"Get user by email failed: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            user = await self.users_collection.find_one({"_id": user_id})
            return user
        except Exception as e:
            logger.error(f"Get user by ID failed: {e}")
            return None
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            update_data["updated_at"] = datetime.now()
            result = await self.users_collection.update_one(
                {"_id": user_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"User update failed: {e}")
            return False
    
    # YouTube Credentials Management
    async def store_youtube_credentials(
        self,
        user_id: str,
        credentials: Dict[str, Any]
    ) -> bool:
        """Store YouTube OAuth credentials for user"""
        try:
            credential_data = {
                "user_id": user_id,
                "access_token": credentials.get("access_token"),
                "refresh_token": credentials.get("refresh_token"),
                "token_uri": credentials.get("token_uri"),
                "client_id": credentials.get("client_id"),
                "client_secret": credentials.get("client_secret"),
                "scopes": credentials.get("scopes"),
                "expires_at": credentials.get("expires_at"),
                "channel_info": credentials.get("channel_info", {}),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Upsert (update if exists, insert if not)
            await self.youtube_credentials_collection.replace_one(
                {"user_id": user_id},
                credential_data,
                upsert=True
            )
            
            # Update user record to show YouTube connected
            await self.update_user(user_id, {
                "youtube_connected": True,
                "youtube_connected_at": datetime.now()
            })
            
            logger.info(f"YouTube credentials stored for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Store YouTube credentials failed: {e}")
            return False
    
    async def get_youtube_credentials(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get YouTube credentials for user"""
        try:
            credentials = await self.youtube_credentials_collection.find_one(
                {"user_id": user_id}
            )
            return credentials
        except Exception as e:
            logger.error(f"Get YouTube credentials failed: {e}")
            return None
    
    async def refresh_youtube_token(
        self,
        user_id: str,
        new_access_token: str,
        expires_at: datetime
    ) -> bool:
        """Update YouTube access token after refresh"""
        try:
            result = await self.youtube_credentials_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "access_token": new_access_token,
                        "expires_at": expires_at,
                        "updated_at": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"YouTube token refresh failed: {e}")
            return False
    
    async def revoke_youtube_access(self, user_id: str) -> bool:
        """Revoke YouTube access for user"""
        try:
            # Delete credentials
            await self.youtube_credentials_collection.delete_one({"user_id": user_id})
            
            # Update user record
            await self.update_user(user_id, {
                "youtube_connected": False,
                "automation_enabled": False
            })
            
            # Delete automation configs
            await self.automation_configs_collection.delete_many({
                "user_id": user_id,
                "platform": "youtube"
            })
            
            logger.info(f"YouTube access revoked for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Revoke YouTube access failed: {e}")
            return False
    
    # Automation Configuration Management
    async def store_automation_config(
        self,
        user_id: str,
        config_type: str,
        config_data: Dict[str, Any]
    ) -> bool:
        """Store automation configuration"""
        try:
            config_document = {
                "user_id": user_id,
                "platform": "youtube",
                "config_type": config_type,
                "config_data": config_data,
                "enabled": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Upsert configuration
            await self.automation_configs_collection.replace_one(
                {"user_id": user_id, "config_type": config_type},
                config_document,
                upsert=True
            )
            
            # Update user automation status
            await self.update_user(user_id, {"automation_enabled": True})
            
            return True
            
        except Exception as e:
            logger.error(f"Store automation config failed: {e}")
            return False
    
    async def get_automation_config(
        self,
        user_id: str,
        config_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get automation configuration"""
        try:
            config = await self.automation_configs_collection.find_one({
                "user_id": user_id,
                "config_type": config_type
            })
            return config
        except Exception as e:
            logger.error(f"Get automation config failed: {e}")
            return None
    
    async def get_all_automation_configs(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all automation configurations for user"""
        try:
            configs = []
            async for config in self.automation_configs_collection.find({"user_id": user_id}):
                configs.append(config)
            return configs
        except Exception as e:
            logger.error(f"Get all automation configs failed: {e}")
            return []
    
    async def disable_automation(self, user_id: str, config_type: str) -> bool:
        """Disable specific automation"""
        try:
            result = await self.automation_configs_collection.update_one(
                {"user_id": user_id, "config_type": config_type},
                {
                    "$set": {
                        "enabled": False,
                        "updated_at": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Disable automation failed: {e}")
            return False
    
    # Upload History Management
    async def log_video_upload(
        self,
        user_id: str,
        video_data: Dict[str, Any]
    ) -> bool:
        """Log video upload to history"""
        try:
            upload_record = {
                "user_id": user_id,
                "video_id": video_data.get("video_id"),
                "video_url": video_data.get("video_url"),
                "title": video_data.get("title"),
                "description": video_data.get("description"),
                "tags": video_data.get("tags", []),
                "privacy_status": video_data.get("privacy_status"),
                "content_type": video_data.get("content_type", "video"),
                "upload_date": datetime.now(),
                "status": "uploaded",
                "ai_generated": video_data.get("ai_generated", False)
            }
            
            await self.upload_history_collection.insert_one(upload_record)
            return True
            
        except Exception as e:
            logger.error(f"Log video upload failed: {e}")
            return False
    
    async def get_upload_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get user's upload history"""
        try:
            uploads = []
            async for upload in self.upload_history_collection.find(
                {"user_id": user_id}
            ).sort("upload_date", -1).limit(limit):
                uploads.append(upload)
            return uploads
        except Exception as e:
            logger.error(f"Get upload history failed: {e}")
            return []
    
    async def get_upload_stats(self, user_id: str) -> Dict[str, Any]:
        """Get upload statistics for user"""
        try:
            total_uploads = await self.upload_history_collection.count_documents(
                {"user_id": user_id}
            )
            
            # Get uploads from last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_uploads = await self.upload_history_collection.count_documents({
                "user_id": user_id,
                "upload_date": {"$gte": thirty_days_ago}
            })
            
            # Get shorts vs regular videos
            shorts_count = await self.upload_history_collection.count_documents({
                "user_id": user_id,
                "content_type": "shorts"
            })
            
            videos_count = total_uploads - shorts_count
            
            return {
                "total_uploads": total_uploads,
                "recent_uploads": recent_uploads,
                "shorts_count": shorts_count,
                "videos_count": videos_count,
                "success_rate": 100.0  # Placeholder - can be calculated based on status
            }
            
        except Exception as e:
            logger.error(f"Get upload stats failed: {e}")
            return {
                "total_uploads": 0,
                "recent_uploads": 0,
                "shorts_count": 0,
                "videos_count": 0,
                "success_rate": 0.0
            }
    
    # Analytics Management
    async def store_channel_analytics(
        self,
        user_id: str,
        analytics_data: Dict[str, Any]
    ) -> bool:
        """Store channel analytics data"""
        try:
            analytics_record = {
                "user_id": user_id,
                "date": datetime.now().date(),
                "channel_statistics": analytics_data.get("channel_statistics", {}),
                "recent_videos": analytics_data.get("recent_videos", []),
                "period_days": analytics_data.get("period_days", 30),
                "created_at": datetime.now()
            }
            
            # Upsert daily analytics
            await self.analytics_collection.replace_one(
                {
                    "user_id": user_id,
                    "date": datetime.now().date()
                },
                analytics_record,
                upsert=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Store channel analytics failed: {e}")
            return False
    
    async def get_channel_analytics(
        self,
        user_id: str,
        days: int = 30
    ) -> Optional[Dict[str, Any]]:
        """Get latest channel analytics"""
        try:
            analytics = await self.analytics_collection.find_one(
                {"user_id": user_id},
                sort=[("created_at", -1)]
            )
            return analytics
        except Exception as e:
            logger.error(f"Get channel analytics failed: {e}")
            return None
    
    # General utility methods
    async def get_user_credentials(self, user_id: str, platform: str) -> Optional[Dict[str, Any]]:
        """Get user credentials for any platform (for compatibility)"""
        if platform == "youtube":
            return await self.get_youtube_credentials(user_id)
        return None
    
    async def store_user_credentials(
        self,
        user_id: str,
        platform: str,
        credentials: Dict[str, Any],
        channel_info: Dict[str, Any] = None
    ) -> bool:
        """Store user credentials for any platform (for compatibility)"""
        if platform == "youtube":
            if channel_info:
                credentials["channel_info"] = channel_info
            return await self.store_youtube_credentials(user_id, credentials)
        return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            # Test connection
            await self.client.admin.command('ping')
            
            # Get collection counts
            users_count = await self.users_collection.count_documents({})
            credentials_count = await self.youtube_credentials_collection.count_documents({})
            
            return {
                "status": "healthy",
                "database": self.database_name,
                "collections": {
                    "users": users_count,
                    "youtube_credentials": credentials_count
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global instance
youtube_db_manager = None

def get_youtube_database() -> YouTubeDatabaseManager:
    """Get global YouTube database instance"""
    global youtube_db_manager
    if not youtube_db_manager:
        youtube_db_manager = YouTubeDatabaseManager()
    return youtube_db_manager