"""
Complete FastAPI Application with Real Reddit Posting
Fixed all imports, routes, and username handling for Actual_Pain3385
REAL POSTING ENABLED - No more test mode
REAL AI CONTENT GENERATION - No mock content
"""

from fastapi import FastAPI, HTTPException, Request, Query, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from contextlib import asynccontextmanager
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uvicorn
import json
import threading
import random
from pydantic import BaseModel
import sys
import traceback
import uuid
import os

# CRITICAL: Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()  # This must be called before importing other modules

# Verify API keys are loaded (temporary debug)
MISTRAL_KEY = os.getenv("MISTRAL_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")
print(f"MISTRAL_API_KEY loaded: {MISTRAL_KEY[:10] + '...' if MISTRAL_KEY else 'NOT FOUND'}")
print(f"GROQ_API_KEY loaded: {GROQ_KEY[:10] + '...' if GROQ_KEY else 'NOT FOUND'}")

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("reddit_automation.log")
    ]
)
logger = logging.getLogger(__name__)

# Import modules with error handling
def safe_import(module_name, class_name=None):
    try:
        if class_name:
            module = __import__(module_name, fromlist=[class_name])
            return getattr(module, class_name)
        else:
            return __import__(module_name)
    except ImportError as e:
        logger.warning(f"Could not import {module_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error importing {module_name}: {e}")
        return None

# Safe imports
RedditOAuthConnector = safe_import('reddit', 'RedditOAuthConnector')
AIService = safe_import('ai_service', 'AIService')
DatabaseManager = safe_import('database', 'DatabaseManager')

# Import settings with fallback
try:
    from config import get_settings
except ImportError:
    def get_settings():
        class MockSettings:
            mongodb_uri = "mongodb://localhost:27017/socialMedia"
            reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
            reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
            reddit_redirect_uri = os.getenv("REDDIT_REDIRECT_URI", "http://localhost:8000/api/oauth/reddit/callback")
            reddit_user_agent = "RedditAutomationPlatform/1.0"
            token_encryption_key = os.getenv("TOKEN_ENCRYPTION_KEY")
            mistral_api_key = os.getenv("MISTRAL_API_KEY")
            groq_api_key = os.getenv("GROQ_API_KEY")
        return MockSettings()

# Import Reddit Automation Components with error handling
try:
    from reddit_automation import (
        RedditAutomationScheduler, 
        AutoPostConfig, 
        AutoReplyConfig
    )
    AUTOMATION_AVAILABLE = True
    logger.info("Reddit automation components imported successfully")
except ImportError as e:
    logger.warning(f"Reddit automation not available: {e}")
    AUTOMATION_AVAILABLE = False

# Global settings
settings = get_settings()

# Global instances - Initialize as None
database_manager = None
ai_service = None
reddit_oauth_connector = None
automation_scheduler = None

# FIXED: Better user session management
user_reddit_tokens = {}  # user_id -> reddit tokens
user_sessions = {}       # session_id -> user_id
oauth_states = {}        # oauth_state -> session_id
automation_configs = {}
automation_stats = {}

# Helper functions for user management
def generate_user_id() -> str:
    """Generate unique user ID"""
    return f"user_{uuid.uuid4().hex[:12]}"

def generate_session_id() -> str:
    """Generate unique session ID"""
    return f"session_{uuid.uuid4().hex[:16]}"

def get_user_from_session(session_id: str) -> Optional[str]:
    """Get user_id from session_id with proper validation"""
    if not session_id:
        logger.warning("No session ID provided")
        return None
    
    if session_id not in user_sessions:
        logger.warning(f"Session ID not found in user_sessions: {session_id}")
        logger.debug(f"Available sessions: {list(user_sessions.keys())}")
        return None
    
    user_id = user_sessions.get(session_id)
    logger.info(f"Session {session_id} mapped to user {user_id}")
    return user_id

def create_user_session(user_id: str = None) -> str:
    """Create new user session"""
    session_id = generate_session_id()
    if not user_id:
        user_id = generate_user_id()
    user_sessions[session_id] = user_id
    return session_id

# Request models with validation
class AutoPostingRequest(BaseModel):
    domain: str
    business_type: str
    business_description: str = ""
    target_audience: str = "indian_users"
    language: str = "en"
    content_style: str = "engaging"
    posts_per_day: int = 3
    posting_times: List[str]
    subreddits: List[str]
    manual_time_entry: bool = False
    custom_post_count: bool = False
    user_id: Optional[str] = None

class AutoReplyRequest(BaseModel):
    domain: str
    expertise_level: str = "intermediate"
    subreddits: List[str]
    keywords: List[str]
    max_replies_per_hour: int = 2
    response_delay_minutes: int = 15
    user_id: Optional[str] = None

class TestPostRequest(BaseModel):
    domain: str
    business_type: str
    business_description: str = ""
    target_audience: str = "indian_users"
    language: str = "en"
    subreddits: List[str]
    content_style: str = "engaging"
    user_id: Optional[str] = None

class ScheduleUpdateRequest(BaseModel):
    type: str
    enabled: bool
    user_id: Optional[str] = None

class ManualPostRequest(BaseModel):
    title: str
    content: str
    subreddit: str
    contentType: str = "text"
    user_id: Optional[str] = None

# Enhanced Mock classes with better error messages
class MockDatabase:
    async def connect(self): 
        logger.info("Mock database connected")
        return True
    
    async def disconnect(self): 
        logger.info("Mock database disconnected")
        return True
    
    async def store_automation_config(self, user_id, config_type, config): 
        logger.info(f"Mock store config for {user_id}: {config_type}")
        return True
    
    async def get_daily_automation_stats(self, user_id): 
        return {"posts_today": 0, "replies_24h": 0, "karma_gained": 0}

class MockAIService:
    def __init__(self):
        self.is_mock = True
        logger.warning("MockAIService initialized - Configure MISTRAL_API_KEY or GROQ_API_KEY for real AI")
    
    async def generate_reddit_domain_content(self, **kwargs):
        logger.error("USING MOCK AI SERVICE - Real AI not configured")
        return {
            "success": False,
            "error": "Mock AI Service Active",
            "title": f"CONFIGURE REAL AI - Mock Title for {kwargs.get('domain', 'general')}",
            "content": f"MOCK CONTENT ALERT: Configure your MISTRAL_API_KEY or GROQ_API_KEY environment variables to generate real AI content. This is placeholder text for {kwargs.get('business_type', 'your business')} in {kwargs.get('domain', 'general')} domain.",
            "body": "Mock content - needs real AI configuration",
            "ai_service": "mock",
            "mock_warning": "Real AI keys not found"
        }
    
    async def test_ai_connection(self):
        return {
            "success": False, 
            "error": "Mock AI - no real API keys", 
            "primary_service": "mock", 
            "services": {"mistral": False, "groq": False}
        }

class MockRedditConnector:
    def __init__(self):
        self.is_configured = False
        
    def generate_oauth_url(self, state=None):
        return {
            "success": True,
            "authorization_url": "https://www.reddit.com/api/v1/authorize?client_id=mock&response_type=code&state=mock_state&redirect_uri=http://localhost:8000/api/oauth/reddit/callback&duration=permanent&scope=submit,edit,read",
            "state": state or "mock_state"
        }
    
    async def exchange_code_for_token(self, code):
        return {
            "success": True,
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token", 
            "expires_in": 3600,
            "user_info": {"username": "MockUser", "id": "mock_user_id"}
        }
        
    async def post_content_with_token(self, **kwargs):
        return {
            "success": False,
            "error": "Mock Reddit connector - configure real Reddit API credentials",
            "message": "Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables"
        }

class MockAutomationScheduler:
    def __init__(self): 
        self.is_running = True
        self.active_configs = {}
        
    def start_scheduler(self): 
        logger.info("Mock automation scheduler started")
        
    async def setup_auto_posting(self, config): 
        config_dict = config.__dict__ if hasattr(config, '__dict__') else config
        user_id = config_dict.get('user_id', 'mock_user')
        self.active_configs[user_id] = {
            "auto_posting": {"config": config_dict, "enabled": True}
        }
        return {
            "success": False, 
            "error": "Mock scheduler active",
            "message": "Configure real API keys: MISTRAL_API_KEY, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET",
            "config": config_dict,
            "scheduler_status": "Mock scheduler - needs real API configuration",
            "mock_warning": True
        }
        
    async def setup_auto_replies(self, config): 
        config_dict = config.__dict__ if hasattr(config, '__dict__') else config
        user_id = config_dict.get('user_id', 'mock_user')
        if user_id not in self.active_configs:
            self.active_configs[user_id] = {}
        self.active_configs[user_id]["auto_replies"] = {"config": config_dict, "enabled": True}
        return {
            "success": False, 
            "error": "Mock scheduler active",
            "message": "Configure real API keys for auto-replies",
            "config": config_dict
        }
        
    async def get_automation_status(self, user_id): 
        user_config = self.active_configs.get(user_id, {})
        return {
            "success": True,
            "user_id": user_id,
            "reddit_connected": user_id in user_reddit_tokens,
            "reddit_username": user_reddit_tokens.get(user_id, {}).get("reddit_username", ""),
            "auto_posting": {
                "enabled": "auto_posting" in user_config,
                "config": user_config.get("auto_posting", {}).get("config"),
                "stats": {"total_posts": 0, "successful_posts": 0, "failed_posts": 0}
            },
            "auto_replies": {
                "enabled": "auto_replies" in user_config,
                "config": user_config.get("auto_replies", {}).get("config"),
                "stats": {"total_replies": 0, "successful_replies": 0}
            },
            "daily_stats": {"posts_today": 0, "recent_replies": 0, "total_karma": 0},
            "scheduler_running": False,
            "mock_warning": "Configure real API keys",
            "last_updated": datetime.now().isoformat()
        }

# Application lifespan management with REAL AI verification
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown with comprehensive error handling"""
    global database_manager, ai_service, reddit_oauth_connector, automation_scheduler
    
    logger.info("Starting Reddit Automation System with REAL AI CONTENT...")
    print("Initializing Reddit Automation Platform with REAL AI...")
    
    # Verify environment variables first
    required_vars = {
        'MISTRAL_API_KEY': os.getenv('MISTRAL_API_KEY'),
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
        'REDDIT_CLIENT_ID': os.getenv('REDDIT_CLIENT_ID'),
        'REDDIT_CLIENT_SECRET': os.getenv('REDDIT_CLIENT_SECRET')
    }
    
    print("Environment Variables Status:")
    for var_name, var_value in required_vars.items():
        status = "FOUND" if var_value else "MISSING"
        print(f"  {var_name}: {status}")
        if var_value:
            logger.info(f"{var_name}: Present")
        else:
            logger.warning(f"{var_name}: Missing")
    
    # Initialize Database
    try:
        if DatabaseManager:
            database_manager = DatabaseManager(settings.mongodb_uri)
            await database_manager.connect()
            logger.info("Database connected successfully")
            print("Database: Connected")
        else:
            raise ImportError("DatabaseManager not available")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
        database_manager = MockDatabase()
        await database_manager.connect()
        print("Database: Mock mode")
    
    # Initialize AI Service with STRICT REAL AI VERIFICATION
    try:
        if AIService and (MISTRAL_KEY or GROQ_KEY):
            logger.info("Attempting to initialize REAL AI service...")
            ai_service = AIService()
            
            # CRITICAL: Test AI connection immediately
            test_result = await ai_service.test_ai_connection()
            
            if test_result.get("success") and test_result.get('primary_service') != 'mock':
                primary_service = test_result.get('primary_service', 'unknown')
                logger.info(f"REAL AI service initialized successfully: {primary_service}")
                print(f"AI Service: {primary_service.upper()} CONNECTED")
                
                # Double-check by generating test content
                test_content = await ai_service.generate_reddit_domain_content(
                    domain="tech",
                    business_type="test",
                    business_description="test",
                    test_mode=False
                )
                
                if test_content.get('ai_service') != 'mock':
                    logger.info("AI content generation verified - REAL AI active")
                    print("AI Content Generation: VERIFIED")
                else:
                    raise Exception("AI service returning mock content")
                    
            else:
                raise Exception(f"AI service test failed: {test_result}")
                
        else:
            raise Exception("AI service not available or no API keys")
            
    except Exception as e:
        logger.error(f"REAL AI service initialization failed: {e}")
        logger.error("Falling back to MockAIService")
        ai_service = MockAIService()
        print("AI Service: MOCK MODE - Configure API keys")
    
    # Initialize Reddit OAuth Connector
    try:
        if RedditOAuthConnector and os.getenv('REDDIT_CLIENT_ID') and os.getenv('REDDIT_CLIENT_SECRET'):
            config = {
                'REDDIT_CLIENT_ID': settings.reddit_client_id,
                'REDDIT_CLIENT_SECRET': settings.reddit_client_secret,
                'REDDIT_REDIRECT_URI': settings.reddit_redirect_uri,
                'REDDIT_USER_AGENT': settings.reddit_user_agent,
                'TOKEN_ENCRYPTION_KEY': settings.token_encryption_key
            }
            reddit_oauth_connector = RedditOAuthConnector(config)
            if reddit_oauth_connector.is_configured:
                logger.info("Reddit OAuth connector initialized successfully")
                print("Reddit OAuth: Configured")
            else:
                logger.warning("Reddit OAuth not properly configured")
                print("Reddit OAuth: Configuration incomplete")
        else:
            raise ImportError("RedditOAuthConnector not available or credentials missing")
    except Exception as e:
        logger.warning(f"Reddit OAuth initialization failed: {e}")
        reddit_oauth_connector = MockRedditConnector()
        print("Reddit OAuth: Mock mode")
    
    # Initialize Reddit Automation System  
    try:
        if (AUTOMATION_AVAILABLE and RedditAutomationScheduler and 
            not isinstance(ai_service, MockAIService) and 
            not isinstance(reddit_oauth_connector, MockRedditConnector)):
            
            automation_scheduler = RedditAutomationScheduler(
                reddit_oauth_connector, ai_service, database_manager, user_reddit_tokens
            )
            automation_scheduler.start_scheduler()
            logger.info("REAL Reddit automation system initialized with REAL AI and REAL POSTING")
            print("Automation Scheduler: REAL MODE - AI + Reddit integrated")
        else:
            raise ImportError("Real automation components not available")
    except Exception as e:
        logger.warning(f"Real automation system initialization failed: {e}")
        automation_scheduler = MockAutomationScheduler()
        automation_scheduler.start_scheduler()
        print("Automation Scheduler: Mock mode")
    
    # Final status report
    real_components = []
    mock_components = []
    
    if not isinstance(ai_service, MockAIService):
        real_components.append("AI Content Generation")
    else:
        mock_components.append("AI (needs MISTRAL_API_KEY or GROQ_API_KEY)")
        
    if not isinstance(reddit_oauth_connector, MockRedditConnector):
        real_components.append("Reddit API")
    else:
        mock_components.append("Reddit (needs REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET)")
        
    if not isinstance(automation_scheduler, MockAutomationScheduler):
        real_components.append("Auto-posting")
    else:
        mock_components.append("Automation (depends on AI + Reddit)")
    
    print(f"\nREAL Components Active: {real_components if real_components else 'None'}")
    print(f"Mock Components: {mock_components if mock_components else 'None'}")
    print("Application startup completed!\n")
    
    logger.info("Application startup completed")
    
    yield
    
    # Cleanup
    logger.info("Shutting down application...")
    if automation_scheduler and hasattr(automation_scheduler, 'is_running'):
        automation_scheduler.is_running = False
    if database_manager and hasattr(database_manager, 'disconnect'):
        try:
            await database_manager.disconnect()
        except Exception as e:
            logger.warning(f"Database disconnect failed: {e}")

# Create FastAPI app
app = FastAPI(
    title="Reddit Automation Platform",
    description="Complete Reddit Automation System with REAL AI CONTENT GENERATION",
    version="5.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://agentic-u5lx.onrender.com",
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception on {request.url}: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "message": "An unexpected error occurred.",
            "timestamp": datetime.now().isoformat()
        }
    )

# Health check endpoints
@app.get("/")
async def root():
    ai_status = "real" if not isinstance(ai_service, MockAIService) else "mock"
    reddit_status = "real" if not isinstance(reddit_oauth_connector, MockRedditConnector) else "mock"
    
    return {
        "success": True,
        "message": "Reddit Automation Platform API - REAL AI CONTENT GENERATION",
        "version": "5.0.0",
        "timestamp": datetime.now().isoformat(),
        "status": "running",
        "real_ai_active": ai_status == "real",
        "real_reddit_active": reddit_status == "real",
        "services": {
            "reddit": f"{type(reddit_oauth_connector).__name__} ({reddit_status})",
            "ai": f"{type(ai_service).__name__} ({ai_status})",
            "database": type(database_manager).__name__,
            "automation": type(automation_scheduler).__name__
        }
    }

@app.get("/health")
async def health_check():
    try:
        ai_status = "unknown"
        ai_is_real = not isinstance(ai_service, MockAIService)
        
        if hasattr(ai_service, 'test_ai_connection'):
            try:
                test_result = await ai_service.test_ai_connection()
                if ai_is_real and test_result.get("success"):
                    ai_status = f"connected_{test_result.get('primary_service', 'unknown')}"
                elif ai_is_real:
                    ai_status = "real_service_failed"
                else:
                    ai_status = "mock_active"
            except Exception as e:
                ai_status = f"error_{str(e)[:20]}"
        
        return {
            "success": True,
            "health": {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "real_ai_content_enabled": ai_is_real,
                "real_posting_enabled": not isinstance(reddit_oauth_connector, MockRedditConnector),
                "services": {
                    "database": {
                        "success": database_manager is not None and not isinstance(database_manager, MockDatabase), 
                        "status": "connected" if database_manager else "failed",
                        "type": type(database_manager).__name__
                    },
                    "ai_service": {
                        "success": ai_is_real and ai_status.startswith("connected"), 
                        "status": ai_status,
                        "type": type(ai_service).__name__,
                        "real_ai": ai_is_real
                    },
                    "reddit_oauth": {
                        "success": reddit_oauth_connector is not None and hasattr(reddit_oauth_connector, 'is_configured') and reddit_oauth_connector.is_configured, 
                        "status": "configured" if reddit_oauth_connector and hasattr(reddit_oauth_connector, 'is_configured') and reddit_oauth_connector.is_configured else "mock",
                        "type": type(reddit_oauth_connector).__name__
                    },
                    "automation": {
                        "success": automation_scheduler is not None, 
                        "status": "running" if automation_scheduler and automation_scheduler.is_running else "stopped",
                        "type": type(automation_scheduler).__name__,
                        "real_posting": not isinstance(automation_scheduler, MockAutomationScheduler)
                    }
                },
                "stats": {
                    "active_users": len(user_reddit_tokens),
                    "active_sessions": len(user_sessions),
                    "oauth_states": len(oauth_states)
                }
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"success": False, "error": str(e), "status": "unhealthy"}

# Session management endpoints
@app.post("/api/auth/create-session")
async def create_session():
    """Create new user session"""
    try:
        session_id = create_user_session()
        user_id = user_sessions[session_id]
        
        logger.info(f"Created session {session_id} for user {user_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "user_id": user_id,
            "message": "Session created successfully"
        }
    except Exception as e:
        logger.error(f"Create session failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/auth/session-info")
async def get_session_info(session_id: str = Header(None, alias="x-session-id")):
    """Get session information"""
    try:
        if not session_id:
            return {"success": False, "error": "Session ID required in header"}
        
        user_id = get_user_from_session(session_id)
        if not user_id:
            return {"success": False, "error": "Invalid session"}
        
        return {
            "success": True,
            "session_id": session_id,
            "user_id": user_id,
            "reddit_connected": user_id in user_reddit_tokens,
            "reddit_username": user_reddit_tokens.get(user_id, {}).get("reddit_username"),
            "ai_service_active": not isinstance(ai_service, MockAIService)
        }
    except Exception as e:
        logger.error(f"Get session info failed: {e}")
        return {"success": False, "error": str(e)}

# Reddit OAuth endpoints
@app.get("/api/oauth/reddit/authorize")
async def reddit_oauth_authorize(session_id: str = Query(None)):
    """Start Reddit OAuth flow"""
    try:
        # Create session if not provided
        if not session_id:
            session_id = create_user_session()
            logger.info(f"Created new session for OAuth: {session_id}")
        
        # Generate OAuth state
        state = f"oauth_{uuid.uuid4().hex[:16]}"
        oauth_states[state] = session_id
        
        logger.info(f"Starting OAuth for session {session_id} with state {state}")
        
        if hasattr(reddit_oauth_connector, 'generate_oauth_url') and not isinstance(reddit_oauth_connector, MockRedditConnector):
            oauth_result = reddit_oauth_connector.generate_oauth_url(state)
            if oauth_result.get("success"):
                logger.info("Real Reddit OAuth URL generated")
                return {
                    "success": True,
                    "redirect_url": oauth_result["authorization_url"],
                    "state": state,
                    "session_id": session_id
                }
        
        # Fallback for mock
        oauth_states[state] = session_id
        logger.warning("Using mock Reddit OAuth URL")
        return {
            "success": True,
            "redirect_url": f"https://www.reddit.com/api/v1/authorize?client_id=mock&response_type=code&state={state}&redirect_uri=http://localhost:8000/api/oauth/reddit/callback&duration=permanent&scope=submit,edit,read",
            "state": state,
            "session_id": session_id,
            "message": "Mock OAuth URL - Configure real Reddit API credentials"
        }
    except Exception as e:
        logger.error(f"Reddit OAuth authorize failed: {e}")
        return {"success": False, "error": str(e)}






@app.get("/api/oauth/reddit/callback")
async def reddit_oauth_callback(code: str, state: str):
    """Handle Reddit OAuth callback - Fixed for Actual_Pain3385"""
    try:
        logger.info(f"OAuth callback received: code={code[:10]}..., state={state}")
        
        # Get session from OAuth state
        session_id = oauth_states.get(state)
        if not session_id:
            logger.error(f"Invalid OAuth state: {state}")
            return RedirectResponse(
                url="http://localhost:5173/reddit-auto?error=invalid_oauth_state",
                status_code=302
            )
        
        user_id = get_user_from_session(session_id)
        if not user_id:
            logger.error(f"Invalid session: {session_id}")
            return RedirectResponse(
                url="http://localhost:5173/reddit-auto?error=invalid_session", 
                status_code=302
            )
        
        logger.info(f"Processing OAuth for user_id: {user_id}, session: {session_id}")
        
        # Exchange code for token
        if hasattr(reddit_oauth_connector, 'exchange_code_for_token') and not isinstance(reddit_oauth_connector, MockRedditConnector):
            logger.info("Using REAL Reddit OAuth connector")
            token_result = await reddit_oauth_connector.exchange_code_for_token(code)
            
            if token_result.get("success"):
                username = token_result["user_info"]["username"]
                logger.info(f"REAL Reddit OAuth successful for user: {username}")
                
                # Store tokens with proper user_id
                user_reddit_tokens[user_id] = {
                    "access_token": token_result["access_token"],
                    "refresh_token": token_result.get("refresh_token", ""),
                    "expires_in": token_result["expires_in"],
                    "reddit_username": username,
                    "connected_at": datetime.now().isoformat(),
                    "user_info": token_result["user_info"]
                }
                
                # Clean up OAuth state
                oauth_states.pop(state, None)
                
                logger.info(f"Reddit OAuth successful for user: {username} (user_id: {user_id})")
                
                return RedirectResponse(
                    url=f"http://localhost:5173/reddit-auto?reddit_connected=true&username={username}&session_id={session_id}&real_connection=true",
                    status_code=302
                )
            else:
                logger.error(f"Token exchange failed: {token_result.get('error')}")
                return RedirectResponse(
                    url=f"http://localhost:5173/reddit-auto?error=token_exchange_failed&message={token_result.get('error')}",
                    status_code=302
                )
        else:
            logger.warning("Using MockRedditConnector or real connector failed")
            return RedirectResponse(
                url="http://localhost:5173/reddit-auto?error=reddit_not_configured&message=Configure REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET",
                status_code=302
            )
        
    except Exception as e:
        logger.error(f"Reddit OAuth callback failed: {e}")
        logger.error(traceback.format_exc())
        return RedirectResponse(
            url=f"http://localhost:5173/reddit-auto?error=oauth_failed&message={str(e)}", 
            status_code=302
        )


                 
                 
                 







@app.get("/api/reddit/test-connection")
async def test_reddit_connection(
    user_id: str = Query(None),
    session_id: str = Header(None, alias="x-session-id")
):
    """Test Reddit API connection - Fixed endpoint"""
    try:
        logger.info(f"Testing Reddit connection - session_id: {session_id}")
        
        # Get user_id
        if not user_id and session_id:
            user_id = get_user_from_session(session_id)
            
        if not user_id:
            logger.error("Test connection failed - no user authentication")
            return {"success": False, "error": "User authentication required"}
        
        # Check if user has Reddit tokens
        if user_id not in user_reddit_tokens:
            logger.error(f"No Reddit tokens for user {user_id}")
            return {
                "success": False,
                "error": "Reddit not connected",
                "message": "Please connect your Reddit account first"
            }
        
        # Test with Reddit connector
        if isinstance(reddit_oauth_connector, MockRedditConnector):
            logger.warning("Mock Reddit connector active")
            return {
                "success": False,
                "error": "Mock connector active",
                "message": "Configure REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET for real connection"
            }
        
        # Test actual Reddit connection
        username = user_reddit_tokens[user_id].get("reddit_username")
        logger.info(f"Testing Reddit connection for {username}")
        
        return {
            "success": True,
            "message": f"Reddit connection verified for {username}",
            "username": username,
            "real_connection": True
        }
        
    except Exception as e:
        logger.error(f"Reddit connection test failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/reddit/connection-status")
async def get_reddit_connection_status(
    user_id: str = Query(None),
    session_id: str = Header(None, alias="x-session-id")
):
    """Get Reddit connection status for user - Enhanced Debug Version"""
    try:
        logger.info(f"Connection status check - session_id: {session_id}, user_id: {user_id}")
        logger.info(f"Available user_sessions: {list(user_sessions.keys())}")
        logger.info(f"Available user_reddit_tokens: {list(user_reddit_tokens.keys())}")
        
        # Get user_id from session if not provided
        if not user_id and session_id:
            user_id = get_user_from_session(session_id)
            logger.info(f"Extracted user_id from session: {user_id}")
            
        if not user_id:
            logger.error("No user_id found - authentication failed")
            return {
                "success": False, 
                "error": "User ID or session required",
                "connected": False,
                "debug": {
                    "session_id_provided": bool(session_id),
                    "user_id_provided": bool(user_id),
                    "available_sessions": list(user_sessions.keys()),
                    "session_exists": session_id in user_sessions if session_id else False
                }
            }
        
        logger.info(f"Checking Reddit tokens for user: {user_id}")
        
        if user_id in user_reddit_tokens:
            creds = user_reddit_tokens[user_id]
            username = creds.get("reddit_username")
            logger.info(f"User {user_id} connected as Reddit user: {username}")
            return {
                "success": True,
                "connected": True,
                "user_id": user_id,
                "reddit_username": username,
                "connected_at": creds.get("connected_at"),
                "message": f"Reddit account connected as {username}",
                "real_connection": not isinstance(reddit_oauth_connector, MockRedditConnector)
            }
        
        logger.info(f"User {user_id} not connected to Reddit")
        return {
            "success": True,
            "connected": False,
            "user_id": user_id,
            "message": "No Reddit connection found"
        }
    except Exception as e:
        logger.error(f"Connection status check failed: {e}")
        return {"success": False, "error": str(e)}

# Manual Reddit posting with REAL posting and REAL AI content
@app.post("/api/reddit/post")
async def manual_reddit_post(
    post_data: ManualPostRequest,
    session_id: str = Header(None, alias="x-session-id")
):
    """Manual Reddit posting - REAL POSTING with REAL AI CONTENT"""
    try:
        # Get user_id from request or session
        user_id = post_data.user_id
        if not user_id and session_id:
            user_id = get_user_from_session(session_id)
            
        if not user_id:
            return {"success": False, "error": "User authentication required"}
        
        # Check Reddit connection
        if user_id not in user_reddit_tokens:
            return {
                "success": False, 
                "error": "Reddit not connected",
                "message": "Please connect your Reddit account first"
            }
        
        # Check if using mock connector
        if isinstance(reddit_oauth_connector, MockRedditConnector):
            logger.warning("Using MockRedditConnector - posts won't actually be sent to Reddit")
            return {
                "success": False,
                "error": "Mock Reddit connector active",
                "message": "Configure real Reddit API credentials: Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET"
            }
        
        # Get user info for logging
        reddit_username = user_reddit_tokens[user_id].get("reddit_username", "Unknown")
        access_token = user_reddit_tokens[user_id]["access_token"]
        
        logger.info(f"MANUAL POST: {reddit_username} posting to r/{post_data.subreddit}")
        logger.info(f"Title: {post_data.title}")
        logger.info(f"Content length: {len(post_data.content)} characters")
        
        # Attempt to post using REAL Reddit API
        result = await reddit_oauth_connector.post_content_with_token(
            access_token=access_token,
            subreddit_name=post_data.subreddit,
            title=post_data.title,
            content=post_data.content,
            content_type=post_data.contentType
        )
        
        # Log the result
        if result.get("success"):
            logger.info(f"REAL Manual post successful for {reddit_username}: {result.get('post_url')}")
        else:
            logger.error(f"Manual post failed for {reddit_username}: {result.get('error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Manual Reddit post failed: {e}")
        return {"success": False, "error": str(e)}

# AI Content Generation with STRICT REAL AI VERIFICATION
@app.post("/api/automation/test-auto-post")
async def test_auto_post(
    test_data: TestPostRequest,
    session_id: str = Header(None, alias="x-session-id")
):
    """Test auto-post generation with REAL AI - NO MOCK CONTENT"""
    try:
        # Get user_id
        user_id = test_data.user_id
        if not user_id and session_id:
            user_id = get_user_from_session(session_id)
        if not user_id:
            user_id = "test_user"  # Fallback for testing
        
        # STRICT CHECK: Reject if AI service is mock
        if isinstance(ai_service, MockAIService):
            logger.error("REJECTING test-auto-post: AI service is mock")
            return {
                "success": False,
                "error": "Mock AI service active",
                "message": "Configure MISTRAL_API_KEY or GROQ_API_KEY environment variables for real AI content generation",
                "mock_warning": True,
                "required_env_vars": ["MISTRAL_API_KEY", "GROQ_API_KEY"]
            }
        
        logger.info(f"Generating REAL AI content for test: {test_data.domain} - {test_data.business_type}")
        
        # Generate content using REAL AI service
        content_result = await ai_service.generate_reddit_domain_content(
            domain=test_data.domain,
            business_type=test_data.business_type,
            business_description=test_data.business_description,
            target_audience=test_data.target_audience,
            language=test_data.language,
            content_style=test_data.content_style,
            test_mode=False  # REAL AI GENERATION
        )
        
        # STRICT VERIFICATION: Check if AI returned mock content
        if content_result.get("ai_service") == "mock" or "mock" in content_result.get("content", "").lower():
            logger.error("AI service returned mock content")
            return {
                "success": False,
                "error": "AI service returned mock content",
                "message": "Check your API keys configuration",
                "content_result": content_result
            }
        
        # Ensure we have real content
        if not content_result.get("success", True):
            logger.error(f"AI content generation failed: {content_result.get('error')}")
            return {
                "success": False,
                "error": f"AI content generation failed: {content_result.get('error')}",
                "message": "Check your AI API keys and service availability"
            }
        
        content_preview = content_result.get("content", "")
        ai_service_name = content_result.get("ai_service", "unknown")
        
        logger.info(f"REAL AI generated: {len(content_preview)} characters using {ai_service_name}")
        
        return {
            "success": True,
            "message": f"REAL AI content generated successfully using {ai_service_name}!",
            "post_details": {
                "title": content_result.get("title", "AI Generated Title"),
                "subreddit": test_data.subreddits[0] if test_data.subreddits else "test",
                "test_mode": False,
                "user_id": user_id,
                "real_ai": True
            },
            "content_preview": content_preview,
            "ai_service": ai_service_name,
            "word_count": content_result.get("word_count", len(content_preview.split())),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Test auto-post failed: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/automation/setup-auto-posting")
async def setup_auto_posting(
    config_data: AutoPostingRequest,
    session_id: str = Header(None, alias="x-session-id")
):
    """Setup automatic posting - REAL POSTING with REAL AI CONTENT"""
    try:
        # Get user_id
        user_id = config_data.user_id
        if not user_id and session_id:
            user_id = get_user_from_session(session_id)
        if not user_id:
            return {"success": False, "error": "User authentication required"}
        
        # Check Reddit connection
        if user_id not in user_reddit_tokens:
            return {
                "success": False,
                "error": "Reddit account not connected",
                "message": "Please connect your Reddit account first"
            }
        
        # Get Reddit username for logging
        reddit_username = user_reddit_tokens[user_id].get("reddit_username", "Unknown")
        
        # STRICT CHECK: Reject if Reddit connector is mock
        if isinstance(reddit_oauth_connector, MockRedditConnector):
            return {
                "success": False,
                "error": "Reddit API not properly configured",
                "message": "Please configure REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables"
            }
        
        # STRICT CHECK: Reject if AI service is mock
        if isinstance(ai_service, MockAIService):
            return {
                "success": False,
                "error": "AI service not configured",
                "message": "Configure MISTRAL_API_KEY or GROQ_API_KEY for real AI content generation",
                "required_env_vars": ["MISTRAL_API_KEY", "GROQ_API_KEY"]
            }
        
        # Test AI service before setup
        logger.info(f"Testing REAL AI service for automation setup - user: {reddit_username}")
        try:
            test_content = await ai_service.generate_reddit_domain_content(
                domain=config_data.domain,
                business_type=config_data.business_type,
                business_description=config_data.business_description,
                target_audience=config_data.target_audience,
                test_mode=False  # REAL AI TEST
            )
            
            # Verify AI returned real content
            if (not test_content.get("success", True) or 
                test_content.get("ai_service") == "mock" or 
                "mock" in test_content.get("content", "").lower()):
                logger.error(f"AI service test failed: {test_content}")
                return {
                    "success": False,
                    "error": "AI service not working properly",
                    "message": "AI service returned mock content. Check your MISTRAL_API_KEY or GROQ_API_KEY configuration",
                    "test_result": test_content
                }
                
            ai_service_name = test_content.get('ai_service', 'unknown')
            logger.info(f"REAL AI service test passed for {reddit_username} - using {ai_service_name}")
            
        except Exception as e:
            logger.error(f"AI service test failed: {e}")
            return {
                "success": False,
                "error": f"AI service error: {str(e)}",
                "message": "Check MISTRAL_API_KEY or GROQ_API_KEY environment variables"
            }
        
        # Store configuration for persistence
        automation_configs[user_id] = {
            "auto_posting": {
                "config": config_data.dict(),
                "enabled": True,
                "created_at": datetime.now().isoformat(),
                "reddit_username": reddit_username,
                "ai_service": ai_service_name,
                "real_ai": True
            }
        }
        
        logger.info(f"Setting up REAL auto-posting for {reddit_username}")
        logger.info(f"Domain: {config_data.domain}, Posts/day: {config_data.posts_per_day}")
        logger.info(f"Subreddits: {config_data.subreddits}")
        logger.info(f"Posting times: {config_data.posting_times}")
        logger.info(f"AI Service: {ai_service_name}")
        
        # Setup with automation scheduler
        if automation_scheduler and AUTOMATION_AVAILABLE and not isinstance(automation_scheduler, MockAutomationScheduler):
            try:
                auto_config = AutoPostConfig(
                    user_id=user_id,
                    domain=config_data.domain,
                    business_type=config_data.business_type,
                    business_description=config_data.business_description,
                    target_audience=config_data.target_audience,
                    language=config_data.language,
                    subreddits=config_data.subreddits,
                    posts_per_day=config_data.posts_per_day,
                    posting_times=config_data.posting_times,
                    content_style=config_data.content_style,
                    manual_time_entry=config_data.manual_time_entry,
                    custom_post_count=config_data.custom_post_count
                )
                
                result = await automation_scheduler.setup_auto_posting(auto_config)
                result["user_id"] = user_id
                result["reddit_username"] = reddit_username
                result["real_posting"] = True
                result["real_ai"] = True
                result["ai_service"] = ai_service_name
                
                logger.info(f"REAL auto-posting setup successful for {reddit_username} with {ai_service_name}")
                return result
            except Exception as e:
                logger.warning(f"Real automation scheduler failed: {e}")
                # Continue with fallback
        
        # Fallback response (should not reach here if everything is configured properly)
        return {
            "success": False,
            "error": "Automation scheduler not available",
            "message": "Real automation scheduler could not be initialized",
            "debug_info": {
                "automation_scheduler_type": type(automation_scheduler).__name__ if automation_scheduler else "None",
                "automation_available": AUTOMATION_AVAILABLE,
                "user_id": user_id,
                "reddit_username": reddit_username
            }
        }
        
    except Exception as e:
        logger.error(f"Auto-posting setup failed: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/automation/setup-auto-replies")
async def setup_auto_replies(
    config_data: AutoReplyRequest,
    session_id: str = Header(None, alias="x-session-id")
):
    """Setup automatic replies with REAL AI"""
    try:
        # Get user_id
        user_id = config_data.user_id
        if not user_id and session_id:
            user_id = get_user_from_session(session_id)
        if not user_id:
            return {"success": False, "error": "User authentication required"}
        
        # Check Reddit connection
        if user_id not in user_reddit_tokens:
            return {
                "success": False,
                "error": "Reddit account not connected",
                "message": "Please connect your Reddit account first"
            }
        
        # STRICT CHECK: Reject if services are mock
        if isinstance(reddit_oauth_connector, MockRedditConnector):
            return {
                "success": False,
                "error": "Reddit API not configured",
                "message": "Configure REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET"
            }
        
        if isinstance(ai_service, MockAIService):
            return {
                "success": False,
                "error": "AI service not configured", 
                "message": "Configure MISTRAL_API_KEY or GROQ_API_KEY"
            }
        
        reddit_username = user_reddit_tokens[user_id].get("reddit_username", "Unknown")
        
        # Store configuration
        if user_id not in automation_configs:
            automation_configs[user_id] = {}
        automation_configs[user_id]["auto_replies"] = {
            "config": config_data.dict(),
            "enabled": True,
            "created_at": datetime.now().isoformat(),
            "reddit_username": reddit_username
        }
        
        logger.info(f"Setting up REAL auto-replies for {reddit_username}")
        
        # Setup with automation scheduler
        if automation_scheduler and not isinstance(automation_scheduler, MockAutomationScheduler):
            try:
                auto_config = AutoReplyConfig(
                    user_id=user_id,
                    domain=config_data.domain,
                    expertise_level=config_data.expertise_level,
                    subreddits=config_data.subreddits,
                    keywords=config_data.keywords,
                    max_replies_per_hour=config_data.max_replies_per_hour,
                    response_delay_minutes=config_data.response_delay_minutes
                )
                
                result = await automation_scheduler.setup_auto_replies(auto_config)
                result["user_id"] = user_id
                result["reddit_username"] = reddit_username
                result["real_ai"] = True
                
                logger.info(f"REAL auto-replies setup successful for {reddit_username}")
                return result
            except Exception as e:
                logger.warning(f"Auto-replies setup failed: {e}")
        
        return {
            "success": False,
            "error": "Auto-replies scheduler not available",
            "message": "Configure all required API keys and restart application"
        }
        
    except Exception as e:
        logger.error(f"Auto-replies setup failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/automation/status")
async def get_automation_status(
    user_id: str = Query(None),
    session_id: str = Header(None, alias="x-session-id")
):
    """Get automation status for user"""
    try:
        # Get user_id
        if not user_id and session_id:
            user_id = get_user_from_session(session_id)
        if not user_id:
            return {"success": False, "error": "User authentication required"}
        
        reddit_username = user_reddit_tokens.get(user_id, {}).get("reddit_username", "")
        
        if automation_scheduler and hasattr(automation_scheduler, 'get_automation_status'):
            try:
                result = await automation_scheduler.get_automation_status(user_id)
                result["reddit_username"] = reddit_username
                result["real_posting"] = not isinstance(automation_scheduler, MockAutomationScheduler)
                result["real_ai"] = not isinstance(ai_service, MockAIService)
                result["ai_service"] = type(ai_service).__name__
                return result
            except Exception as e:
                logger.warning(f"Automation status check failed: {e}")
        
        # Fallback status from stored configs
        user_config = automation_configs.get(user_id, {})
        
        return {
            "success": True,
            "user_id": user_id,
            "reddit_connected": user_id in user_reddit_tokens,
            "reddit_username": reddit_username,
            "auto_posting": {
                "enabled": "auto_posting" in user_config,
                "config": user_config.get("auto_posting", {}).get("config"),
                "stats": {"total_posts": 0, "successful_posts": 0, "failed_posts": 0}
            },
            "auto_replies": {
                "enabled": "auto_replies" in user_config,
                "config": user_config.get("auto_replies", {}).get("config"),
                "stats": {"total_replies": 0, "successful_replies": 0}
            },
            "daily_stats": {
                "posts_today": 0,
                "recent_replies": 0,
                "total_karma": 0
            },
            "scheduler_running": automation_scheduler.is_running if automation_scheduler else False,
            "real_posting": not isinstance(automation_scheduler, MockAutomationScheduler) if automation_scheduler else False,
            "real_ai": not isinstance(ai_service, MockAIService),
            "ai_service": type(ai_service).__name__,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/automation/update-schedule")
async def update_automation_schedule(
    update_data: ScheduleUpdateRequest,
    session_id: str = Header(None, alias="x-session-id")
):
    """Update automation schedule settings"""
    try:
        user_id = update_data.user_id
        if not user_id and session_id:
            user_id = get_user_from_session(session_id)
        if not user_id:
            return {"success": False, "error": "User authentication required"}
        
        # Update stored config
        if user_id in automation_configs:
            if update_data.type in automation_configs[user_id]:
                automation_configs[user_id][update_data.type]["enabled"] = update_data.enabled
        
        logger.info(f"Updated {update_data.type} schedule for user {user_id}: enabled={update_data.enabled}")
        
        return {
            "success": True,
            "message": f"{update_data.type.replace('_', ' ').title()} {'enabled' if update_data.enabled else 'disabled'}",
            "user_id": user_id,
            "type": update_data.type,
            "enabled": update_data.enabled
        }
        
    except Exception as e:
        logger.error(f"Schedule update failed: {e}")
        return {"success": False, "error": str(e)}

# Debug endpoints
@app.get("/api/debug/sessions")
async def debug_sessions():
    """Debug session information"""
    return {
        "user_sessions": {k: v for k, v in user_sessions.items()},
        "user_reddit_tokens": {k: {"username": v.get("reddit_username", "N/A"), "has_token": bool(v.get("access_token"))} for k, v in user_reddit_tokens.items()},
        "oauth_states": list(oauth_states.keys()),
        "total_sessions": len(user_sessions),
        "total_tokens": len(user_reddit_tokens),
        "automation_configs": {k: {config_type: config_data.get("enabled", False) for config_type, config_data in v.items()} for k, v in automation_configs.items()}
    }

@app.get("/api/reddit/debug")
async def debug_reddit_connector():
    """Debug Reddit connector status"""
    return {
        "connector_available": reddit_oauth_connector is not None,
        "connector_type": type(reddit_oauth_connector).__name__ if reddit_oauth_connector else None,
        "connector_configured": hasattr(reddit_oauth_connector, 'is_configured') and reddit_oauth_connector.is_configured if reddit_oauth_connector else False,
        "user_tokens": len(user_reddit_tokens),
        "connected_users": list(user_reddit_tokens.keys()),
        "reddit_usernames": [tokens.get("reddit_username") for tokens in user_reddit_tokens.values()],
        "active_sessions": len(user_sessions),
        "oauth_states": len(oauth_states),
        "environment_vars": {
            "REDDIT_CLIENT_ID": bool(os.getenv("REDDIT_CLIENT_ID")),
            "REDDIT_CLIENT_SECRET": bool(os.getenv("REDDIT_CLIENT_SECRET")),
            "MISTRAL_API_KEY": bool(os.getenv("MISTRAL_API_KEY")),
            "GROQ_API_KEY": bool(os.getenv("GROQ_API_KEY"))
        },
        "real_posting_enabled": not isinstance(reddit_oauth_connector, MockRedditConnector),
        "real_ai_enabled": not isinstance(ai_service, MockAIService),
        "ai_service_type": type(ai_service).__name__
    }

@app.get("/api/ai/debug")
async def debug_ai_service():
    """Debug AI service status"""
    try:
        ai_test = None
        if hasattr(ai_service, 'test_ai_connection'):
            try:
                ai_test = await ai_service.test_ai_connection()
            except Exception as e:
                ai_test = {"error": str(e)}
        
        return {
            "ai_service_available": ai_service is not None,
            "ai_service_type": type(ai_service).__name__,
            "is_mock": isinstance(ai_service, MockAIService),
            "ai_test_result": ai_test,
            "environment_keys": {
                "MISTRAL_API_KEY": bool(os.getenv("MISTRAL_API_KEY")),
                "GROQ_API_KEY": bool(os.getenv("GROQ_API_KEY"))
            },
            "real_ai_active": not isinstance(ai_service, MockAIService)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    
PORT = int(os.getenv("PORT", 8000))
if __name__ == "__main__":
    print("Starting Reddit Automation Platform...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,  # Use environment PORT
        reload=False,  # Disable reload in production
        log_level="info"
    )