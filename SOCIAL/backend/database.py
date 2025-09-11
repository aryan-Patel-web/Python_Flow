"""
Database Manager for Multi-Platform Automation System
Handles MongoDB operations, user data, platform credentials, and analytics
"""

import motor.motor_asyncio
from pymongo import MongoClient
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from bson import ObjectId
import json

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Production-ready MongoDB database manager with async operations
    """
    
    def __init__(self, mongodb_uri: str = "mongodb://localhost:27017/socialMedia"):
        """
        Initialize database manager
        
        Args:
            mongodb_uri: MongoDB connection URI
        """
        self.mongodb_uri = mongodb_uri
        self.client = None
        self.database = None
        self.connected = False
        
        # Collection names for different platforms
        self.collections = {
            "users": "users",
            "reddit_data": "reddit_posts",
            "reddit_credentials": "reddit_credentials", 
            "reddit_activity": "reddit_activity",
            "twitter_data": "twitter_posts",
            "twitter_credentials": "twitter_credentials",
            "twitter_activity": "twitter_activity",
            "stackoverflow_data": "stackoverflow_answers",
            "stackoverflow_credentials": "stackoverflow_credentials",
            "stackoverflow_activity": "stackoverflow_activity",
            "webmd_data": "webmd_answers",
            "webmd_activity": "webmd_activity",
            "ai_usage": "ai_content_generation",
            "analytics": "platform_analytics",
            "scheduled_content": "scheduled_posts",
            "earnings": "user_earnings"
        }
    
    async def connect(self) -> bool:
        """
        Connect to MongoDB database
        
        Returns:
            Boolean indicating connection success
        """
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongodb_uri)
            self.database = self.client.socialMedia
            
            # Test connection
            await self.client.admin.command('ping')
            self.connected = True
            
            # Create indexes for better performance
            await self._create_indexes()
            
            logger.info("MongoDB connected successfully to socialMedia database")
            return True
            
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("MongoDB disconnected")
    
    async def _create_indexes(self) -> None:
        """Create database indexes for better performance"""
        try:
            # User indexes
            await self.database.users.create_index("email", unique=True)
            await self.database.users.create_index("created_at")
            
            # Reddit indexes
            await self.database.reddit_posts.create_index([("user_id", 1), ("created_at", -1)])
            await self.database.reddit_posts.create_index("post_id", unique=True)
            await self.database.reddit_activity.create_index([("user_id", 1), ("timestamp", -1)])
            
            # Platform activity indexes
            await self.database.platform_analytics.create_index([("user_id", 1), ("platform", 1), ("date", -1)])
            await self.database.ai_content_generation.create_index([("user_id", 1), ("created_at", -1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Index creation failed: {e}")
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new user in database
        
        Args:
            user_data: User information
            
        Returns:
            Creation result
        """
        try:
            user_doc = {
                "email": user_data["email"],
                "name": user_data["name"],
                "password_hash": user_data.get("password_hash"),
                "created_at": datetime.now(),
                "last_login": None,
                "subscription_tier": "free",
                "is_active": True,
                "platforms_connected": [],
                "total_posts": 0,
                "total_earnings": 0.0
            }
            
            result = await self.database.users.insert_one(user_doc)
            
            return {
                "success": True,
                "user_id": str(result.inserted_id),
                "message": "User created successfully"
            }
            
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create user"
            }
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User document or None
        """
        try:
            user = await self.database.users.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
                del user["_id"]
            return user
            
        except Exception as e:
            logger.error(f"Get user failed: {e}")
            return None
    
    async def store_reddit_credentials(self, user_id: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store Reddit API credentials for user
        
        Args:
            user_id: User ID
            credentials: Reddit credentials
            
        Returns:
            Storage result
        """
        try:
            cred_doc = {
                "user_id": user_id,
                "platform": "reddit",
                "username": credentials.get("username"),
                "access_token": credentials.get("access_token"),  # Encrypted in production
                "refresh_token": credentials.get("refresh_token"),  # Encrypted in production
                "created_at": datetime.now(),
                "last_used": datetime.now(),
                "is_active": True
            }
            
            # Upsert credentials
            await self.database.reddit_credentials.replace_one(
                {"user_id": user_id},
                cred_doc,
                upsert=True
            )
            
            # Update user's connected platforms
            await self.database.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$addToSet": {"platforms_connected": "reddit"}}
            )
            
            return {
                "success": True,
                "message": "Reddit credentials stored successfully"
            }
            
        except Exception as e:
            logger.error(f"Store Reddit credentials failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to store Reddit credentials"
            }
    
    async def log_reddit_activity(self, user_id: str, activity_type: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log Reddit activity (posts, comments, etc.)
        
        Args:
            user_id: User ID
            activity_type: Type of activity (post, comment, upvote)
            activity_data: Activity details
            
        Returns:
            Logging result
        """
        try:
            activity_doc = {
                "user_id": user_id,
                "platform": "reddit",
                "activity_type": activity_type,
                "timestamp": datetime.now(),
                "data": activity_data,
                "success": activity_data.get("success", True),
                "subreddit": activity_data.get("subreddit"),
                "post_id": activity_data.get("post_id"),
                "score": activity_data.get("score", 0),
                "engagement": activity_data.get("num_comments", 0)
            }
            
            await self.database.reddit_activity.insert_one(activity_doc)
            
            # Update user statistics
            if activity_type == "post" and activity_data.get("success"):
                await self.database.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$inc": {"total_posts": 1}}
                )
            
            return {
                "success": True,
                "message": "Reddit activity logged successfully"
            }
            
        except Exception as e:
            logger.error(f"Log Reddit activity failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to log Reddit activity"
            }
    
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """
        Get dashboard data for user
        
        Args:
            user_id: User ID
            
        Returns:
            Dashboard data
        """
        try:
            # Get user info
            user = await self.get_user(user_id)
            if not user:
                return {"error": "User not found"}
            
            # Get today's activity
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Reddit activity today
            reddit_posts_today = await self.database.reddit_activity.count_documents({
                "user_id": user_id,
                "activity_type": "post",
                "timestamp": {"$gte": today},
                "success": True
            })
            
            # Total engagement this week
            week_ago = datetime.now() - timedelta(days=7)
            total_engagement = await self.database.reddit_activity.aggregate([
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
            ]).to_list(1)
            
            engagement = total_engagement[0] if total_engagement else {"total_score": 0, "total_engagement": 0}
            
            # Earnings calculation (placeholder)
            total_earnings = user.get("total_earnings", 0)
            
            dashboard_data = {
                "posts_today": reddit_posts_today,
                "total_engagement": engagement["total_engagement"],
                "qa_earnings": total_earnings,
                "active_platforms": len(user.get("platforms_connected", [])),
                "posts_change": 2,  # Placeholder
                "engagement_change": 15,  # Placeholder
                "earnings_change": 50,  # Placeholder
                "platforms_change": 0
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Get dashboard data failed: {e}")
            return {"error": str(e)}
    
    async def log_ai_usage(self, user_id: str, platform: str, content_length: int) -> Dict[str, Any]:
        """
        Log AI content generation usage
        
        Args:
            user_id: User ID
            platform: Platform used
            content_length: Length of generated content
            
        Returns:
            Logging result
        """
        try:
            usage_doc = {
                "user_id": user_id,
                "platform": platform,
                "content_length": content_length,
                "timestamp": datetime.now(),
                "tokens_used": content_length // 4,  # Rough estimate
                "cost": content_length * 0.0001  # Placeholder cost calculation
            }
            
            await self.database.ai_content_generation.insert_one(usage_doc)
            
            return {
                "success": True,
                "message": "AI usage logged successfully"
            }
            
        except Exception as e:
            logger.error(f"Log AI usage failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to log AI usage"
            }
    
    async def create_scheduled_content(self, user_id: str, schedule_data: Dict[str, Any]) -> str:
        """
        Create scheduled content entry
        
        Args:
            user_id: User ID
            schedule_data: Scheduling information
            
        Returns:
            Schedule ID
        """
        try:
            schedule_doc = {
                "user_id": user_id,
                "platforms": schedule_data["platforms"],
                "content": schedule_data["content"],
                "scheduled_time": datetime.fromisoformat(schedule_data["scheduled_time"]),
                "created_at": datetime.now(),
                "status": "pending",
                "results": {}
            }
            
            result = await self.database.scheduled_posts.insert_one(schedule_doc)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Create scheduled content failed: {e}")
            raise
    
    async def get_platform_performance(self, user_id: str, platform: str, days: int) -> Dict[str, Any]:
        """
        Get platform performance metrics
        
        Args:
            user_id: User ID
            platform: Platform name
            days: Number of days to analyze
            
        Returns:
            Performance data
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            collection_name = f"{platform}_activity"
            if collection_name not in self.collections.values():
                return {"error": f"Platform {platform} not supported"}
            
            # Get activity stats
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "timestamp": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "posts_count": {"$sum": 1},
                        "total_engagement": {"$sum": "$engagement"},
                        "avg_score": {"$avg": "$score"},
                        "success_count": {
                            "$sum": {"$cond": [{"$eq": ["$success", True]}, 1, 0]}
                        }
                    }
                }
            ]
            
            stats = await self.database[collection_name].aggregate(pipeline).to_list(1)
            
            if stats:
                result = stats[0]
                result["success_rate"] = (result["success_count"] / result["posts_count"] * 100) if result["posts_count"] > 0 else 0
                del result["_id"]
                del result["success_count"]
            else:
                result = {
                    "posts_count": 0,
                    "total_engagement": 0,
                    "avg_score": 0,
                    "success_rate": 0
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Get platform performance failed: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check database connection health
        
        Returns:
            Health status
        """
        try:
            if not self.connected:
                return {
                    "success": False,
                    "status": "disconnected",
                    "message": "Database not connected"
                }
            
            # Test database operation
            await self.client.admin.command('ping')
            
            # Check collections
            collections = await self.database.list_collection_names()
            
            return {
                "success": True,
                "status": "healthy",
                "connected": self.connected,
                "database": "socialMedia",
                "collections_count": len(collections),
                "message": "Database health check passed"
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "success": False,
                "status": "unhealthy",
                "error": str(e),
                "message": "Database health check failed"
            }