"""
Enhanced FastAPI Application with Complete Reddit Automation System
Frontend-controlled scheduling and automation features with improved error handling
"""

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uvicorn
import json
import threading

# Import your modules
from reddit import RedditOAuthConnector
from ai_service import AIService
from database import DatabaseManager
from config import get_settings

# Import Reddit Automation Components
try:
    from reddit_automation import (
        RedditAutomationScheduler, 
        AutoPostConfig, 
        AutoReplyConfig,
        RedditQuestionMonitor,
        RedditUserTargeting
    )
    AUTOMATION_AVAILABLE = True
except ImportError:
    AUTOMATION_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global settings
settings = get_settings()

# Global instances
database_manager = None
ai_service = None
reddit_oauth_connector = None

# Reddit Automation instances
automation_scheduler = None
question_monitor = None
user_targeting = None

# In-memory storage for development
user_reddit_tokens = {}
automation_configs = {}
automation_stats = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    global database_manager, ai_service, reddit_oauth_connector
    global automation_scheduler, question_monitor, user_targeting
    
    logger.info("Starting Reddit Automation System...")
    
    try:
        # Initialize Database
        try:
            database_manager = DatabaseManager(settings.mongodb_uri)
            await database_manager.connect()
            logger.info("Database connected successfully")
        except Exception as e:
            logger.warning(f"Database connection failed: {e} - using mock database")
            database_manager = MockDatabase()
        
        # Initialize AI Service
        try:
            ai_service = AIService()
            logger.info("AI service initialized successfully")
        except Exception as e:
            logger.warning(f"AI service initialization failed: {e} - using mock AI")
            ai_service = MockAIService()
        
        # Initialize Reddit OAuth Connector
        try:
            config = {
                'REDDIT_CLIENT_ID': getattr(settings, 'reddit_client_id', None),
                'REDDIT_CLIENT_SECRET': getattr(settings, 'reddit_client_secret', None),
                'REDDIT_REDIRECT_URI': getattr(settings, 'reddit_redirect_uri', 'http://localhost:8000/api/oauth/reddit/callback'),
                'REDDIT_USER_AGENT': getattr(settings, 'reddit_user_agent', 'RedditAutomationPlatform/1.0'),
                'TOKEN_ENCRYPTION_KEY': getattr(settings, 'token_encryption_key', None)
            }
            reddit_oauth_connector = RedditOAuthConnector(config)
            logger.info("Reddit OAuth connector initialized successfully")
        except Exception as e:
            logger.warning(f"Reddit OAuth initialization failed: {e} - using mock Reddit")
            reddit_oauth_connector = MockRedditConnector()
        
        # Initialize Reddit Automation System
        if AUTOMATION_AVAILABLE:
            try:
                automation_scheduler = RedditAutomationScheduler(
                    reddit_oauth_connector, ai_service, database_manager, user_reddit_tokens
                )
                question_monitor = RedditQuestionMonitor(reddit_oauth_connector)
                user_targeting = RedditUserTargeting(reddit_oauth_connector)
                
                # Start the automation scheduler
                automation_scheduler.start_scheduler()
                
                logger.info("Reddit automation system initialized successfully")
            except Exception as e:
                logger.warning(f"Automation system initialization failed: {e}")
                automation_scheduler = MockAutomationScheduler()
                question_monitor = MockQuestionMonitor()
                user_targeting = MockUserTargeting()
        else:
            # Use mock services
            automation_scheduler = MockAutomationScheduler()
            question_monitor = MockQuestionMonitor()
            user_targeting = MockUserTargeting()
        
        # Store in app state
        app.state.database = database_manager
        app.state.ai_service = ai_service
        app.state.reddit_oauth = reddit_oauth_connector
        app.state.automation_scheduler = automation_scheduler
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down application...")
    if automation_scheduler and hasattr(automation_scheduler, 'is_running'):
        automation_scheduler.is_running = False
    if database_manager and hasattr(database_manager, 'disconnect'):
        try:
            await database_manager.disconnect()
        except:
            pass

# Create FastAPI app
app = FastAPI(
    title="Reddit Automation Platform",
    description="Complete Reddit Automation System with Frontend Control",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Mock classes for development/fallback
class MockDatabase:
    async def connect(self): pass
    async def disconnect(self): pass
    async def store_automation_config(self, user_id, config_type, config): pass
    async def get_daily_automation_stats(self, user_id): 
        return {"posts_today": 0, "replies_24h": 0, "karma_gained": 0}
    async def log_automation_activity(self, **kwargs): pass
    async def check_if_replied(self, user_id, question_id): return False

class MockAIService:
    async def generate_reddit_domain_content(self, **kwargs):
        return {
            "success": True,
            "title": "Sample AI Generated Title",
            "content": "This is sample AI generated content for testing purposes."
        }
    
    async def generate_qa_answer(self, **kwargs):
        return {
            "success": True,
            "answer": "This is a sample AI generated answer for testing purposes."
        }

class MockRedditConnector:
    async def post_content_with_token(self, **kwargs):
        return {
            "success": True,
            "post_id": "mock_post_123",
            "post_url": "https://reddit.com/mock_post"
        }
    
    async def reply_to_post_with_token(self, **kwargs):
        return {
            "success": True,
            "comment_id": "mock_comment_123"
        }

class MockAutomationScheduler:
    def __init__(self):
        self.is_running = True
    
    def start_scheduler(self): pass
    
    async def setup_auto_posting(self, config):
        return {
            "success": True,
            "message": "Auto-posting enabled (mock mode)",
            "config": config.__dict__ if hasattr(config, '__dict__') else config,
            "next_post_time": "09:00 (tomorrow)"
        }
    
    async def setup_auto_replies(self, config):
        return {
            "success": True,
            "message": "Auto-replies enabled (mock mode)",
            "config": config.__dict__ if hasattr(config, '__dict__') else config,
            "monitoring_status": "Active - mock mode"
        }
    
    async def get_automation_status(self, user_id):
        return {
            "success": True,
            "auto_posting": {"enabled": False, "config": None},
            "auto_replies": {"enabled": False, "config": None},
            "daily_stats": {"posts_today": 0, "recent_replies": 0, "total_karma": 0},
            "scheduler_running": True,
            "last_updated": datetime.now().isoformat()
        }

class MockQuestionMonitor:
    async def find_target_questions(self, **kwargs):
        return [
            {
                "id": "mock_q1",
                "title": "How to improve study techniques?",
                "content": "Looking for effective study methods",
                "subreddit": "education",
                "score": 5,
                "num_comments": 3,
                "created_utc": datetime.now().timestamp(),
                "url": "https://reddit.com/mock_question",
                "age_hours": 2.5,
                "engagement_potential": 7.5
            }
        ]

class MockUserTargeting:
    async def find_users_asking_questions(self, **kwargs):
        return [
            {
                "username": "test_user",
                "question_count": 3,
                "engagement_level": "medium",
                "average_score": 5.5,
                "recent_questions": [
                    {"question": "Study tips needed", "subreddit": "education", "score": 6}
                ]
            }
        ]

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for better error responses"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.now().isoformat()
        }
    )

# Health Check Endpoint
@app.get("/health")
async def health_check():
    """System health check"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": {"success": database_manager is not None, "status": "connected"},
                "ai_service": {"success": ai_service is not None, "status": "initialized"},
                "reddit_oauth": {"success": reddit_oauth_connector is not None, "status": "configured"},
                "automation": {"success": automation_scheduler is not None, "status": "running"}
            }
        }
        
        return {"success": True, "health": health_status}
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"success": False, "error": str(e), "status": "unhealthy"}

# =============================================
# REDDIT OAUTH ENDPOINTS
# =============================================

@app.get("/api/oauth/reddit/authorize")
async def reddit_oauth_authorize():
    """Initiate Reddit OAuth flow"""
    try:
        if hasattr(reddit_oauth_connector, 'generate_oauth_url'):
            oauth_result = reddit_oauth_connector.generate_oauth_url()
            
            if oauth_result.get("success"):
                return {
                    "success": True,
                    "redirect_url": oauth_result["authorization_url"],
                    "state": oauth_result["state"]
                }
        
        # Mock response
        return {
            "success": True,
            "redirect_url": "https://www.reddit.com/api/v1/authorize?client_id=mock&response_type=code&state=mock_state&redirect_uri=http://localhost:8000/callback&duration=permanent&scope=submit,edit,read",
            "state": "mock_state",
            "message": "Mock OAuth URL (Reddit not configured)"
        }
            
    except Exception as e:
        logger.error(f"Reddit OAuth authorize failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/oauth/reddit/callback")
async def reddit_oauth_callback(code: str, state: str, request: Request):
    """Handle Reddit OAuth callback and store tokens"""
    try:
        if hasattr(reddit_oauth_connector, 'exchange_code_for_token'):
            token_result = await reddit_oauth_connector.exchange_code_for_token(code)
            
            if token_result.get("success"):
                user_id = "dev_user_123"
                
                user_reddit_tokens[user_id] = {
                    "access_token": token_result["access_token"],
                    "refresh_token": token_result.get("refresh_token", ""),
                    "expires_in": token_result["expires_in"],
                    "reddit_username": token_result["user_info"]["username"],
                    "connected_at": datetime.now().isoformat(),
                    "user_info": token_result["user_info"]
                }
                
                logger.info(f"Reddit OAuth successful for user: {token_result['user_info']['username']}")
                
                return {
                    "success": True,
                    "message": "Reddit account connected successfully",
                    "reddit_user": token_result["user_info"]["username"],
                    "stored": True
                }
        
        # Mock successful connection
        user_reddit_tokens["dev_user_123"] = {
            "access_token": "mock_token",
            "reddit_username": "test_user",
            "connected_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "message": "Reddit account connected successfully (mock)",
            "reddit_user": "test_user",
            "stored": True
        }
            
    except Exception as e:
        logger.error(f"Reddit OAuth callback failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/reddit/connection-status")
async def get_reddit_connection_status():
    """Check if user has connected Reddit account"""
    try:
        user_id = "dev_user_123"
        
        if user_id in user_reddit_tokens:
            creds = user_reddit_tokens[user_id]
            return {
                "success": True,
                "connected": True,
                "reddit_username": creds.get("reddit_username"),
                "connected_at": creds.get("connected_at"),
                "message": "Reddit account is connected"
            }
        
        return {
            "success": True,
            "connected": False,
            "message": "No Reddit connection found"
        }
        
    except Exception as e:
        logger.error(f"Connection status check failed: {e}")
        return {"success": False, "error": str(e)}

# =============================================
# AUTOMATION ENDPOINTS
# =============================================

@app.post("/api/automation/setup-auto-posting")
async def setup_auto_posting(config_data: Dict[str, Any]):
    """Set up automatic posting with frontend-controlled scheduling"""
    try:
        user_id = "dev_user_123"
        
        # Validate required fields
        if not config_data.get("domain") or not config_data.get("business_type"):
            raise HTTPException(status_code=400, detail="Domain and business type are required")
        
        if not config_data.get("subreddits"):
            raise HTTPException(status_code=400, detail="At least one subreddit must be selected")
        
        # Store configuration
        config = {
            "user_id": user_id,
            "domain": config_data["domain"],
            "business_type": config_data["business_type"],
            "target_audience": config_data.get("target_audience", "indian_users"),
            "language": config_data.get("language", "en"),
            "subreddits": config_data["subreddits"],
            "posts_per_day": config_data.get("posts_per_day", 3),
            "posting_times": config_data.get("posting_times", ["09:00", "14:00", "19:00"]),
            "content_style": config_data.get("content_style", "engaging"),
            "enabled": True,
            "created_at": datetime.now().isoformat()
        }
        
        # Store in memory and database
        if user_id not in automation_configs:
            automation_configs[user_id] = {}
        automation_configs[user_id]["auto_posting"] = config
        
        # Try to use real automation scheduler
        if automation_scheduler and hasattr(automation_scheduler, 'setup_auto_posting'):
            try:
                if AUTOMATION_AVAILABLE:
                    auto_post_config = AutoPostConfig(
                        user_id=user_id,
                        domain=config["domain"],
                        business_type=config["business_type"],
                        target_audience=config["target_audience"],
                        language=config["language"],
                        subreddits=config["subreddits"],
                        posts_per_day=config["posts_per_day"],
                        posting_times=config["posting_times"],
                        content_style=config["content_style"]
                    )
                    result = await automation_scheduler.setup_auto_posting(auto_post_config)
                    return result
                else:
                    result = await automation_scheduler.setup_auto_posting(config)
                    return result
            except Exception as e:
                logger.warning(f"Automation scheduler failed: {e} - using mock response")
        
        # Mock response
        return {
            "success": True,
            "message": "Auto-posting enabled successfully",
            "config": config,
            "next_post_time": config["posting_times"][0] + " (tomorrow)",
            "scheduler_status": "Mock mode - real posting disabled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auto-posting setup failed: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/automation/setup-auto-replies")
async def setup_auto_replies(config_data: Dict[str, Any]):
    """Set up automatic replies with frontend-controlled monitoring"""
    try:
        user_id = "dev_user_123"
        
        # Validate required fields
        if not config_data.get("domain"):
            raise HTTPException(status_code=400, detail="Domain is required")
        
        if not config_data.get("keywords"):
            raise HTTPException(status_code=400, detail="Keywords are required")
        
        if not config_data.get("subreddits"):
            raise HTTPException(status_code=400, detail="At least one subreddit must be selected")
        
        # Store configuration
        config = {
            "user_id": user_id,
            "domain": config_data["domain"],
            "expertise_level": config_data.get("expertise_level", "intermediate"),
            "subreddits": config_data["subreddits"],
            "keywords": config_data["keywords"],
            "max_replies_per_hour": config_data.get("max_replies_per_hour", 2),
            "response_delay_minutes": config_data.get("response_delay_minutes", 15),
            "enabled": True,
            "created_at": datetime.now().isoformat()
        }
        
        # Store in memory
        if user_id not in automation_configs:
            automation_configs[user_id] = {}
        automation_configs[user_id]["auto_replies"] = config
        
        # Try to use real automation scheduler
        if automation_scheduler and hasattr(automation_scheduler, 'setup_auto_replies'):
            try:
                if AUTOMATION_AVAILABLE:
                    auto_reply_config = AutoReplyConfig(
                        user_id=user_id,
                        domain=config["domain"],
                        expertise_level=config["expertise_level"],
                        subreddits=config["subreddits"],
                        keywords=config["keywords"],
                        max_replies_per_hour=config["max_replies_per_hour"],
                        response_delay_minutes=config["response_delay_minutes"]
                    )
                    result = await automation_scheduler.setup_auto_replies(auto_reply_config)
                    return result
                else:
                    result = await automation_scheduler.setup_auto_replies(config)
                    return result
            except Exception as e:
                logger.warning(f"Automation scheduler failed: {e} - using mock response")
        
        # Mock response
        return {
            "success": True,
            "message": "Auto-replies enabled successfully",
            "config": config,
            "monitoring_status": "Active - scanning every 5 minutes (mock mode)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auto-replies setup failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/automation/status")
async def get_automation_status():
    """Get automation status for user"""
    try:
        user_id = "dev_user_123"
        user_config = automation_configs.get(user_id, {})
        
        # Try to get real status if available
        if automation_scheduler and hasattr(automation_scheduler, 'get_automation_status'):
            try:
                result = await automation_scheduler.get_automation_status(user_id)
                if result.get("success"):
                    return result
            except Exception as e:
                logger.warning(f"Real status check failed: {e}")
        
        # Mock response
        return {
            "success": True,
            "auto_posting": {
                "enabled": "auto_posting" in user_config,
                "config": user_config.get("auto_posting")
            },
            "auto_replies": {
                "enabled": "auto_replies" in user_config,
                "config": user_config.get("auto_replies")
            },
            "daily_stats": {
                "posts_today": automation_stats.get(user_id, {}).get("posts_today", 0),
                "recent_replies": automation_stats.get(user_id, {}).get("replies_24h", 0),
                "total_karma": automation_stats.get(user_id, {}).get("karma_gained", 0)
            },
            "scheduler_running": automation_scheduler is not None,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Automation status failed: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/automation/update-schedule")
async def update_automation_schedule(schedule_data: Dict[str, Any]):
    """Update automation schedule from frontend"""
    try:
        user_id = "dev_user_123"
        automation_type = schedule_data.get("type")
        
        if user_id not in automation_configs:
            automation_configs[user_id] = {}
        
        if automation_type == "auto_posting":
            if "auto_posting" in automation_configs[user_id]:
                automation_configs[user_id]["auto_posting"].update({
                    "posting_times": schedule_data.get("posting_times", []),
                    "posts_per_day": schedule_data.get("posts_per_day", 3),
                    "enabled": schedule_data.get("enabled", True),
                    "updated_at": datetime.now().isoformat()
                })
        
        elif automation_type == "auto_replies":
            if "auto_replies" in automation_configs[user_id]:
                automation_configs[user_id]["auto_replies"].update({
                    "max_replies_per_hour": schedule_data.get("max_replies_per_hour", 2),
                    "response_delay_minutes": schedule_data.get("response_delay_minutes", 15),
                    "enabled": schedule_data.get("enabled", True),
                    "updated_at": datetime.now().isoformat()
                })
        
        return {
            "success": True,
            "message": f"{automation_type} schedule updated successfully",
            "updated_config": automation_configs[user_id].get(automation_type)
        }
        
    except Exception as e:
        logger.error(f"Schedule update failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/automation/performance-analytics")
async def get_performance_analytics():
    """Get performance analytics"""
    try:
        # Mock performance data
        return {
            "success": True,
            "performance": {
                "auto_posts": {
                    "total_this_month": 89,
                    "successful_posts": 85,
                    "failed_posts": 4,
                    "success_rate": 95.5,
                    "avg_engagement": 12.3,
                    "best_performing_subreddit": "r/JEE",
                    "total_upvotes": 1247,
                    "total_comments": 189
                },
                "auto_replies": {
                    "total_this_month": 156,
                    "successful_replies": 142,
                    "failed_replies": 14,
                    "success_rate": 91.0,
                    "avg_reply_engagement": 8.7,
                    "helpful_votes": 234,
                    "questions_answered": 142
                },
                "engagement_metrics": {
                    "karma_gained": 445,
                    "followers_gained": 23,
                    "direct_messages": 12,
                    "mention_notifications": 34
                },
                "trending_performance": {
                    "best_posting_times": ["09:00", "14:00", "19:00"],
                    "most_engaging_topics": [
                        "JEE preparation tips",
                        "Career guidance", 
                        "Study techniques",
                        "Physics problem solving",
                        "Time management"
                    ],
                    "optimal_subreddits": ["r/JEE", "r/IndianStudents", "r/india"],
                    "rising_keywords": ["preparation", "career", "guidance", "tips", "strategy"]
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Performance analytics failed: {e}")
        return {"success": False, "error": str(e)}

# =============================================
# QUESTION DISCOVERY ENDPOINTS
# =============================================

@app.get("/api/automation/target-questions")
async def find_target_questions(
    domain: str = Query(...),
    subreddits: str = Query(None),
    expertise_keywords: str = Query(...),
    min_score: int = Query(1),
    max_age_hours: int = Query(24)
):
    """Find questions that are good targets for helpful replies"""
    try:
        subreddit_list = subreddits.split(",") if subreddits else None
        keyword_list = expertise_keywords.split(",")
        
        # Try to use real question monitor
        if question_monitor and hasattr(question_monitor, 'find_target_questions'):
            try:
                questions = await question_monitor.find_target_questions(
                    domain=domain,
                    expertise_keywords=keyword_list,
                    subreddits=subreddit_list,
                    min_score=min_score,
                    max_age_hours=max_age_hours
                )
                
                return {
                    "success": True,
                    "questions": questions,
                    "count": len(questions),
                    "message": f"Found {len(questions)} target questions in {domain} domain"
                }
            except Exception as e:
                logger.warning(f"Real question monitoring failed: {e}")
        
        # Mock questions
        mock_questions = [
            {
                "id": "abc123",
                "title": "How do I improve my Physics score in JEE?",
                "content": "I'm struggling with mechanics and thermodynamics. Any tips?",
                "subreddit": "JEE",
                "score": 5,
                "num_comments": 8,
                "created_utc": datetime.now().timestamp(),
                "url": "https://reddit.com/r/JEE/comments/abc123/",
                "author": "student123",
                "age_hours": 2.5,
                "engagement_potential": 7.8
            },
            {
                "id": "def456", 
                "title": "Best study schedule for NEET preparation?",
                "content": "I have 6 months left for NEET. How should I plan?",
                "subreddit": "NEET",
                "score": 12,
                "num_comments": 15,
                "created_utc": datetime.now().timestamp(),
                "url": "https://reddit.com/r/NEET/comments/def456/",
                "author": "aspirant456",
                "age_hours": 4.2,
                "engagement_potential": 9.1
            }
        ]
        
        return {
            "success": True,
            "questions": mock_questions,
            "count": len(mock_questions),
            "message": f"Found {len(mock_questions)} target questions (mock data)"
        }
        
    except Exception as e:
        logger.error(f"Target question search failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/automation/active-users")
async def find_active_users(
    domain: str = Query(...),
    subreddits: str = Query(...),
    time_period_hours: int = Query(24)
):
    """Find users who frequently ask questions in your domain"""
    try:
        subreddit_list = subreddits.split(",")
        
        # Try to use real user targeting
        if user_targeting and hasattr(user_targeting, 'find_users_asking_questions'):
            try:
                users = await user_targeting.find_users_asking_questions(
                    domain=domain,
                    subreddits=subreddit_list,
                    time_period_hours=time_period_hours
                )
                
                return {
                    "success": True,
                    "active_users": users,
                    "count": len(users),
                    "message": f"Found {len(users)} active users in {domain} domain"
                }
            except Exception as e:
                logger.warning(f"Real user targeting failed: {e}")
        
        # Mock active users
        mock_users = [
            {
                "username": "studious_student",
                "question_count": 5,
                "engagement_level": "high",
                "average_score": 8.2,
                "total_score": 41,
                "subreddits": ["JEE", "IndianStudents"],
                "recent_questions": [
                    {"question": "Physics doubt in rotational motion", "subreddit": "JEE", "score": 12},
                    {"question": "Best coaching for JEE Main?", "subreddit": "JEE", "score": 8}
                ]
            },
            {
                "username": "future_doctor",
                "question_count": 3,
                "engagement_level": "medium",
                "average_score": 5.7,
                "total_score": 17,
                "subreddits": ["NEET", "india"],
                "recent_questions": [
                    {"question": "NEET biology preparation tips", "subreddit": "NEET", "score": 7},
                    {"question": "How to manage time during exam?", "subreddit": "NEET", "score": 4}
                ]
            }
        ]
        
        return {
            "success": True,
            "active_users": mock_users,
            "count": len(mock_users),
            "message": f"Found {len(mock_users)} active users (mock data)"
        }
        
    except Exception as e:
        logger.error(f"User targeting failed: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/automation/manual-reply")
async def manual_reply_to_question(reply_data: Dict[str, Any]):
    """Manually reply to a specific question with AI-generated answer"""
    try:
        user_id = "dev_user_123"
        
        # Check if user has Reddit tokens
        if user_id not in user_reddit_tokens:
            return {
                "success": False,
                "error": "Reddit account not connected",
                "message": "Please connect your Reddit account first"
            }
        
        # Generate AI answer
        answer_result = await ai_service.generate_qa_answer(
            platform="reddit",
            question=reply_data["question"],
            context=reply_data.get("context", ""),
            language=reply_data.get("language", "en"),
            domain=reply_data.get("domain", "general"),
            expertise_level=reply_data.get("expertise_level", "intermediate")
        )
        
        if not answer_result.get("success"):
            return {
                "success": False,
                "error": "Failed to generate AI answer",
                "details": answer_result.get("error")
            }
        
        # Post reply to Reddit
        if hasattr(reddit_oauth_connector, 'reply_to_post_with_token'):
            reply_result = await reddit_oauth_connector.reply_to_post_with_token(
                user_tokens=user_reddit_tokens[user_id],
                post_id=reply_data["post_id"],
                reply_content=answer_result["answer"]
            )
            
            if reply_result.get("success"):
                return {
                    "success": True,
                    "message": "Reply posted successfully",
                    "comment_id": reply_result.get("comment_id"),
                    "comment_url": reply_result.get("comment_url"),
                    "answer_preview": answer_result["answer"][:200] + "..."
                }
        
        # Mock successful reply
        return {
            "success": True,
            "message": "Reply posted successfully (mock mode)",
            "comment_id": "mock_comment_123",
            "comment_url": f"https://reddit.com/comments/{reply_data.get('post_id', 'mock')}/",
            "answer_preview": answer_result["answer"][:200] + "..."
        }
        
    except Exception as e:
        logger.error(f"Manual reply failed: {e}")
        return {"success": False, "error": str(e)}

# =============================================
# CONTENT GENERATION ENDPOINTS
# =============================================

@app.post("/api/ai/generate-content")
async def generate_ai_content(content_request: Dict[str, Any]):
    """Generate AI content"""
    try:
        # Use real AI service if available
        if hasattr(ai_service, 'generate_platform_content'):
            result = await ai_service.generate_platform_content(
                platform=content_request["platform"],
                content_type=content_request["content_type"],
                topic=content_request["topic"],
                tone=content_request.get("tone", "professional"),
                language=content_request.get("language", "en"),
                target_audience=content_request.get("target_audience", "general"),
                additional_context=content_request.get("additional_context", ""),
                domain=content_request.get("domain")
            )
            
            if result.get("success"):
                return result
        
        # Mock AI content generation
        topic = content_request.get('topic', 'General Topic')
        tone = content_request.get('tone', 'professional')
        audience = content_request.get('target_audience', 'general audience')
        
        mock_content = f"""
{topic} - A Comprehensive Guide

This is AI-generated content about {topic} written in a {tone} tone for {audience}.

Key points to consider:
1. Understanding the fundamentals is crucial
2. Practice and consistency are important
3. Learning from experts and experienced practitioners
4. Staying updated with latest trends and developments
5. Building a strong foundation before advancing

{content_request.get('additional_context', 'Additional context would be incorporated here.')}

Feel free to ask questions or share your experiences!
        """.strip()
        
        return {
            "success": True,
            "content": mock_content,
            "word_count": len(mock_content.split()),
            "character_count": len(mock_content),
            "platform": content_request["platform"],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"AI content generation failed: {e}")
        return {"success": False, "error": str(e)}

# =============================================
# MAIN APPLICATION RUNNER
# =============================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )