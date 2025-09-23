# """
# Complete Multi-Platform Social Media Automation System
# Reddit + YouTube + WhatsApp + Instagram + Facebook
# Combined system with unified authentication and real AI content generation
# """

# from fastapi import FastAPI, HTTPException, Request, Query, BackgroundTasks, Header, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware
# from fastapi.responses import JSONResponse, RedirectResponse, Response
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from fastapi.exceptions import RequestValidationError
# from contextlib import asynccontextmanager
# import asyncio
# import logging
# from typing import Dict, List, Optional, Any
# from datetime import datetime, timedelta
# import uvicorn
# import json
# import threading
# import random
# from pydantic import BaseModel, EmailStr
# import sys
# import traceback
# import uuid
# import os
# import requests
# import base64
# import bcrypt
# import jwt

# # CRITICAL: Load environment variables FIRST
# from dotenv import load_dotenv
# load_dotenv()

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(sys.stdout),
#         logging.FileHandler("multiplatform_automation.log")
#     ]
# )
# logger = logging.getLogger(__name__)

# # =============================================================================
# # IMPORT ALL MODULES WITH SAFE ERROR HANDLING
# # =============================================================================

# def safe_import(module_name, class_name=None):
#     try:
#         if class_name:
#             module = __import__(module_name, fromlist=[class_name])
#             return getattr(module, class_name)
#         else:
#             return __import__(module_name)
#     except ImportError as e:
#         logger.warning(f"Could not import {module_name}: {e}")
#         return None
#     except Exception as e:
#         logger.error(f"Error importing {module_name}: {e}")
#         return None

# # Reddit imports
# RedditOAuthConnector = safe_import('reddit', 'RedditOAuthConnector')
# try:
#     from reddit_automation import (
#         RedditAutomationScheduler, 
#         AutoPostConfig, 
#         AutoReplyConfig
#     )
#     REDDIT_AUTOMATION_AVAILABLE = True
#     logger.info("Reddit automation components imported successfully")
# except ImportError as e:
#     logger.warning(f"Reddit automation not available: {e}")
#     REDDIT_AUTOMATION_AVAILABLE = False

# # YouTube imports
# try:
#     from youtube import (
#         initialize_youtube_service, 
#         get_youtube_connector, 
#         get_youtube_scheduler,
#         get_youtube_database
#     )
#     YOUTUBE_AVAILABLE = True
#     logger.info("YouTube module loaded successfully")
# except ImportError as e:
#     logger.warning(f"YouTube module not available: {e}")
#     YOUTUBE_AVAILABLE = False

# # WhatsApp imports
# try:
#     from whatsapp import WhatsAppCloudAPI, WhatsAppAutomationScheduler, WhatsAppConfig
#     WHATSAPP_AVAILABLE = True
#     logger.info("WhatsApp module loaded successfully")
# except ImportError as e:
#     logger.warning(f"WhatsApp module not available: {e}")
#     WHATSAPP_AVAILABLE = False

# # AI Service imports
# AIService = safe_import('ai_service', 'AIService')
# try:
#     from ai_service2 import AIService2
#     AI_SERVICE2_AVAILABLE = True
#     logger.info("AI Service 2 loaded successfully")
# except ImportError as e:
#     logger.warning(f"AI Service 2 not available: {e}")
#     AI_SERVICE2_AVAILABLE = False

# # Database imports
# try:
#     from database import MultiUserDatabaseManager as DatabaseManager
#     MULTIUSER_DB_AVAILABLE = True
#     logger.info("Multi-user database manager imported successfully")
# except ImportError:
#     logger.warning("Multi-user database not available, falling back to single-user")
#     DatabaseManager = safe_import('database', 'DatabaseManager')
#     MULTIUSER_DB_AVAILABLE = False

# try:
#     from YTdatabase import get_youtube_database, YouTubeDatabaseManager
#     YOUTUBE_DATABASE_AVAILABLE = True
#     logger.info("YouTube database loaded successfully")
# except ImportError as e:
#     logger.warning(f"YouTube database not available: {e}")
#     YOUTUBE_DATABASE_AVAILABLE = False

# # Settings import with fallback
# try:
#     from config import get_settings
# except ImportError:
#     def get_settings():
#         class MockSettings:
#             mongodb_uri = os.getenv("MONGODB_URI", "mongodb+srv://aryan:aryan@cluster0.7iquw6v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
#             reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
#             reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
#             reddit_redirect_uri = os.getenv("REDDIT_REDIRECT_URI", "https://agentic-u5lx.onrender.com/api/oauth/reddit/callback")
#             reddit_user_agent = "RedditAutomationPlatform/1.0"
#             token_encryption_key = os.getenv("TOKEN_ENCRYPTION_KEY")
#             mistral_api_key = os.getenv("MISTRAL_API_KEY")
#             groq_api_key = os.getenv("GROQ_API_KEY")
#             google_client_id = os.getenv("GOOGLE_CLIENT_ID")
#             google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
#             google_oauth_redirect_uri = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")
#         return MockSettings()

# # =============================================================================
# # PYDANTIC MODELS - COMBINED FROM BOTH FILES
# # =============================================================================

# # Authentication models
# class RegisterRequest(BaseModel):
#     email: EmailStr
#     password: str
#     name: str

# class LoginRequest(BaseModel):
#     email: EmailStr
#     password: str

# # Reddit models
# class AutoPostingRequest(BaseModel):
#     domain: str
#     business_type: str
#     business_description: str = ""
#     target_audience: str = "indian_users"
#     language: str = "en"
#     content_style: str = "engaging"
#     posts_per_day: int = 3
#     posting_times: List[str]
#     subreddits: List[str]
#     manual_time_entry: bool = False
#     custom_post_count: bool = False

# class AutoReplyRequest(BaseModel):
#     domain: str
#     expertise_level: str = "intermediate"
#     subreddits: List[str]
#     keywords: List[str]
#     max_replies_per_hour: int = 2
#     response_delay_minutes: int = 15

# class TestPostRequest(BaseModel):
#     domain: str
#     business_type: str
#     business_description: str = ""
#     target_audience: str = "indian_users"
#     language: str = "en"
#     subreddits: List[str]
#     content_style: str = "engaging"

# class ManualPostRequest(BaseModel):
#     title: str
#     content: str
#     subreddit: str
#     contentType: str = "text"

# class ScheduleUpdateRequest(BaseModel):
#     type: str
#     enabled: bool

# # YouTube models
# class YouTubeOAuthRequest(BaseModel):
#     user_id: str
#     state: str = "youtube_oauth"
#     redirect_uri: Optional[str] = None

# class YouTubeOAuthCallback(BaseModel):
#     user_id: str
#     code: str
#     state: Optional[str] = None
#     redirect_uri: Optional[str] = None

# class YouTubeSetupRequest(BaseModel):
#     user_id: str
#     config: dict

# class YouTubeUploadRequest(BaseModel):
#     user_id: str
#     title: str
#     description: str
#     video_url: str
#     content_type: str = "shorts"
#     tags: List[str] = []
#     privacy_status: str = "public"

# class YouTubeContentRequest(BaseModel):
#     content_type: str = "shorts"
#     topic: str = "general"
#     target_audience: str = "general"

# class YouTubeAutomationRequest(BaseModel):
#     content_type: str = "shorts"
#     upload_schedule: List[str]
#     content_categories: List[str] = []
#     auto_generate_titles: bool = True
#     privacy_status: str = "public"
#     shorts_per_day: int = 3

# # WhatsApp models
# class WhatsAppMessageRequest(BaseModel):
#     to: str
#     message: str
#     message_type: str = "text"

# class WhatsAppAutomationRequest(BaseModel):
#     business_name: str
#     auto_reply_enabled: bool = False
#     campaign_enabled: bool = False
#     business_hours: Dict[str, str] = {"start": "09:00", "end": "18:00"}

# # =============================================================================
# # GLOBAL VARIABLES AND INSTANCES
# # =============================================================================

# # Global settings
# settings = get_settings()

# # Global service instances
# database_manager = None
# youtube_database_manager = None
# ai_service = None
# ai_service2 = None
# reddit_oauth_connector = None
# reddit_automation_scheduler = None
# youtube_connector = None
# youtube_scheduler = None
# whatsapp_scheduler = None

# # Multi-user management
# user_reddit_tokens = {}  # user_id -> reddit tokens
# user_youtube_tokens = {}  # user_id -> youtube tokens
# user_platform_tokens = {}  # user_id -> {platform: tokens}
# oauth_states = {}          # oauth_state -> user_id
# automation_configs = {}    # user_id -> {platform: configs}

# # Authentication setup
# security = HTTPBearer()

# # =============================================================================
# # MOCK CLASSES FOR FALLBACK
# # =============================================================================

# class MockMultiUserDatabase:
#     """Mock database with real user data - unified for all platforms"""
#     def __init__(self):
#         self.users = {}
#         self.reddit_tokens = {}
#         self.youtube_tokens = {}
#         self.platform_tokens = {}
#         self.automation_configs = {}
#         self.user_sessions = {}
        
#     async def connect(self): 
#         logger.info("Mock unified database connected")
#         return True
    
#     async def disconnect(self): 
#         logger.info("Mock unified database disconnected")
#         return True
    
#     async def register_user(self, email, password, name):
#         user_id = f"user_{uuid.uuid4().hex[:12]}"
        
#         password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
#         user_data = {
#             "id": user_id,
#             "email": email,
#             "name": name,
#             "password_hash": password_hash,
#             "created_at": datetime.utcnow(),
#             "platforms_connected": []
#         }
        
#         self.users[user_id] = user_data
#         self.user_sessions[email] = user_data
        
#         token_payload = {
#             "user_id": user_id,
#             "email": email,
#             "name": name,
#             "exp": datetime.utcnow() + timedelta(days=30)
#         }
        
#         token = jwt.encode(token_payload, "your_secret_key", algorithm="HS256")
        
#         logger.info(f"User registered: {email} -> {name}")
        
#         return {
#             "success": True,
#             "user_id": user_id,
#             "email": email,
#             "name": name,
#             "token": token,
#             "message": f"User {name} registered successfully"
#         }
    
#     async def login_user(self, email, password):
#         user_data = self.user_sessions.get(email)
        
#         if not user_data:
#             user_id = f"user_{uuid.uuid4().hex[:12]}"
#             name = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
            
#             user_data = {
#                 "id": user_id,
#                 "email": email,
#                 "name": name,
#                 "created_at": datetime.utcnow(),
#                 "platforms_connected": []
#             }
            
#             self.users[user_id] = user_data
#             self.user_sessions[email] = user_data
            
#             logger.info(f"New user auto-created: {email} -> {name}")
        
#         token_payload = {
#             "user_id": user_data["id"],
#             "email": user_data["email"],
#             "name": user_data["name"],
#             "exp": datetime.utcnow() + timedelta(days=30)
#         }
        
#         token = jwt.encode(token_payload, "your_secret_key", algorithm="HS256")
        
#         # Check all platform connections
#         platforms_connected = []
#         if user_data["id"] in self.reddit_tokens:
#             platforms_connected.append("reddit")
#         if user_data["id"] in self.youtube_tokens:
#             platforms_connected.append("youtube")
        
#         return {
#             "success": True,
#             "user_id": user_data["id"],
#             "email": user_data["email"],
#             "name": user_data["name"],
#             "token": token,
#             "platforms_connected": platforms_connected,
#             "message": f"Welcome back, {user_data['name']}!"
#         }
    
#     async def get_user_by_token(self, token):
#         try:
#             payload = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
#             user_id = payload.get("user_id")
            
#             if user_id and user_id in self.users:
#                 user_data = self.users[user_id]
                
#                 platforms_connected = []
#                 if user_id in self.reddit_tokens:
#                     platforms_connected.append("reddit")
#                 if user_id in self.youtube_tokens:
#                     platforms_connected.append("youtube")
                
#                 return {
#                     "id": user_id,
#                     "email": user_data["email"],
#                     "name": user_data["name"],
#                     "platforms_connected": platforms_connected
#                 }
                
#         except jwt.ExpiredSignatureError:
#             logger.warning("Expired token provided")
#         except jwt.InvalidTokenError:
#             logger.warning("Invalid token provided")
#         except Exception as e:
#             logger.error(f"Token validation error: {e}")
            
#         return None
    
#     # Reddit-specific methods
#     async def store_reddit_tokens(self, user_id, token_data):
#         self.reddit_tokens[user_id] = {
#             "access_token": token_data["access_token"],
#             "refresh_token": token_data.get("refresh_token", ""),
#             "reddit_username": token_data["reddit_username"],
#             "reddit_user_id": token_data.get("reddit_user_id", ""),
#             "expires_in": token_data.get("expires_in", 3600),
#             "created_at": datetime.utcnow(),
#             "is_active": True
#         }
        
#         if user_id in self.users:
#             platforms = self.users[user_id].get("platforms_connected", [])
#             if "reddit" not in platforms:
#                 platforms.append("reddit")
#                 self.users[user_id]["platforms_connected"] = platforms
        
#         logger.info(f"Reddit tokens stored for user {user_id}: {token_data['reddit_username']}")
#         return {"success": True, "message": f"Reddit tokens stored for {token_data['reddit_username']}"}
    
#     # YouTube-specific methods
#     async def store_youtube_credentials(self, user_id, credentials):
#         self.youtube_tokens[user_id] = {
#             "access_token": credentials["access_token"],
#             "refresh_token": credentials.get("refresh_token", ""),
#             "channel_info": credentials.get("channel_info", {}),
#             "expires_at": credentials.get("expires_at"),
#             "created_at": datetime.utcnow(),
#             "is_active": True
#         }
        
#         if user_id in self.users:
#             platforms = self.users[user_id].get("platforms_connected", [])
#             if "youtube" not in platforms:
#                 platforms.append("youtube")
#                 self.users[user_id]["platforms_connected"] = platforms
        
#         logger.info(f"YouTube credentials stored for user {user_id}")
#         return True
    
#     # OAuth state management methods
#     async def store_oauth_state(self, state: str, user_id: str, expires_at: datetime) -> Dict[str, Any]:
#         if not hasattr(self, 'oauth_states'):
#             self.oauth_states = {}
        
#         self.oauth_states[state] = {
#             "user_id": user_id,
#             "expires_at": expires_at,
#             "created_at": datetime.utcnow()
#         }
#         logger.info(f"OAuth state stored: {state} for user {user_id}")
#         return {"success": True}

#     async def get_oauth_state(self, state: str) -> Optional[Dict[str, Any]]:
#         if not hasattr(self, 'oauth_states'):
#             self.oauth_states = {}
        
#         state_data = self.oauth_states.get(state)
#         if not state_data:
#             return None
        
#         if state_data["expires_at"] <= datetime.utcnow():
#             del self.oauth_states[state]
#             return None
        
#         return state_data

#     async def health_check(self):
#         return {
#             "status": "healthy",
#             "users_count": len(self.users),
#             "reddit_connections": len(self.reddit_tokens),
#             "youtube_connections": len(self.youtube_tokens),
#             "automation_configs": len(self.automation_configs)
#         }

# class MockAIService:
#     def __init__(self):
#         self.is_mock = True
#         logger.warning("MockAIService initialized - Configure AI API keys for real AI")
    
#     async def generate_reddit_domain_content(self, **kwargs):
#         return {
#             "success": False,
#             "error": "Mock AI Service Active",
#             "title": f"Mock Title for {kwargs.get('domain', 'general')}",
#             "content": f"Mock content for {kwargs.get('business_type', 'business')}",
#             "ai_service": "mock"
#         }
    
#     async def generate_youtube_content(self, **kwargs):
#         return {
#             "success": True,
#             "title": f"Mock YouTube {kwargs.get('content_type', 'video')}",
#             "description": f"Mock description for {kwargs.get('topic', 'general')}",
#             "tags": ["mock", "ai", "generated"],
#             "ai_service": "mock"
#         }
    
#     async def test_ai_connection(self):
#         return {"success": False, "error": "Mock AI", "primary_service": "mock"}

# # =============================================================================
# # AUTHENTICATION DEPENDENCY
# # =============================================================================

# async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     """Get current authenticated user from JWT token"""
#     try:
#         token = credentials.credentials
#         if not database_manager or not hasattr(database_manager, 'get_user_by_token'):
#             raise HTTPException(status_code=500, detail="Authentication system not available")
        
#         user = await database_manager.get_user_by_token(token)
#         if not user:
#             raise HTTPException(status_code=401, detail="Invalid or expired token")
        
#         return user
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Authentication failed: {e}")
#         raise HTTPException(status_code=401, detail="Authentication failed")

# # =============================================================================
# # SERVICE INITIALIZATION
# # =============================================================================

# async def initialize_all_services():
#     """Initialize all platform services"""
#     global database_manager, youtube_database_manager, ai_service, ai_service2
#     global reddit_oauth_connector, reddit_automation_scheduler
#     global youtube_connector, youtube_scheduler
    
#     logger.info("Starting Multi-Platform Social Media Automation System...")
    
#     # Verify environment variables
#     required_vars = {
#         'MISTRAL_API_KEY': os.getenv('MISTRAL_API_KEY'),
#         'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
#         'REDDIT_CLIENT_ID': os.getenv('REDDIT_CLIENT_ID'),
#         'REDDIT_CLIENT_SECRET': os.getenv('REDDIT_CLIENT_SECRET'),
#         'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
#         'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
#         'MONGODB_URI': os.getenv('MONGODB_URI')
#     }
    
#     logger.info("Environment Variables Status:")
#     for var_name, var_value in required_vars.items():
#         status = "FOUND" if var_value else "MISSING"
#         logger.info(f"  {var_name}: {status}")
    
#     # Initialize Primary Database (Reddit + General)
#     try:
#         if DatabaseManager and MULTIUSER_DB_AVAILABLE:
#             database_manager = DatabaseManager(settings.mongodb_uri)
#             await database_manager.connect()
#             logger.info("Multi-User MongoDB Atlas connected successfully")
#         else:
#             raise ImportError("Multi-User DatabaseManager not available")
#     except Exception as e:
#         logger.warning(f"Primary database initialization failed: {e}")
#         database_manager = MockMultiUserDatabase()
#         await database_manager.connect()
    
#     # Initialize YouTube Database (if separate)
#     if YOUTUBE_DATABASE_AVAILABLE:
#         try:
#             youtube_database_manager = get_youtube_database()
#             logger.info("YouTube database initialized successfully")
#         except Exception as e:
#             logger.warning(f"YouTube database initialization failed: {e}")
    
#     # Initialize AI Services
#     try:
#         if AIService and (os.getenv("MISTRAL_API_KEY") or os.getenv("GROQ_API_KEY")):
#             ai_service = AIService()
#             test_result = await ai_service.test_ai_connection()
            
#             if test_result.get("success") and test_result.get('primary_service') != 'mock':
#                 logger.info(f"AI service 1 initialized successfully: {test_result.get('primary_service')}")
#             else:
#                 raise Exception("AI service test failed")
#         else:
#             raise Exception("AI service not available or no API keys")
#     except Exception as e:
#         logger.warning(f"AI service 1 initialization failed: {e}")
#         ai_service = MockAIService()
    
#     # Initialize AI Service 2 (YouTube specific)
#     if AI_SERVICE2_AVAILABLE:
#         try:
#             ai_service2 = AIService2()
#             logger.info("AI service 2 initialized successfully")
#         except Exception as e:
#             logger.warning(f"AI service 2 initialization failed: {e}")
#             ai_service2 = None
    
#     # Initialize Reddit OAuth Connector
#     try:
#         if RedditOAuthConnector and os.getenv('REDDIT_CLIENT_ID') and os.getenv('REDDIT_CLIENT_SECRET'):
#             reddit_oauth_connector = RedditOAuthConnector(settings)
#             logger.info("Reddit OAuth connector initialized successfully")
#         else:
#             raise Exception("Reddit credentials missing")
#     except Exception as e:
#         logger.warning(f"Reddit OAuth initialization failed: {e}")
#         reddit_oauth_connector = None
    
#     # Initialize Reddit Automation Scheduler
#     if (REDDIT_AUTOMATION_AVAILABLE and RedditAutomationScheduler and 
#         reddit_oauth_connector and not isinstance(ai_service, MockAIService)):
#         try:
#             reddit_automation_scheduler = RedditAutomationScheduler(
#                 reddit_oauth_connector, ai_service, database_manager, user_reddit_tokens
#             )
#             reddit_automation_scheduler.start_scheduler()
#             logger.info("Reddit automation scheduler initialized successfully")
#         except Exception as e:
#             logger.warning(f"Reddit automation scheduler failed: {e}")
#             reddit_automation_scheduler = None
    
#     # Initialize YouTube Services
#     if YOUTUBE_AVAILABLE:
#         try:
#             success = await initialize_youtube_service(ai_service=ai_service2 or ai_service)
#             if success:
#                 youtube_connector = get_youtube_connector()
#                 youtube_scheduler = get_youtube_scheduler()
#                 logger.info("YouTube services initialized successfully")
#             else:
#                 logger.warning("YouTube service initialization failed")
#         except Exception as e:
#             logger.warning(f"YouTube services initialization failed: {e}")
    
#     logger.info("Multi-platform service initialization completed")
#     return True

# async def cleanup_all_services():
#     """Cleanup all services on shutdown"""
#     try:
#         if database_manager and hasattr(database_manager, 'disconnect'):
#             await database_manager.disconnect()
#         if youtube_database_manager and hasattr(youtube_database_manager, 'close'):
#             await youtube_database_manager.close()
#         logger.info("All services cleaned up successfully")
#     except Exception as e:
#         logger.error(f"Service cleanup failed: {e}")

# # =============================================================================
# # FASTAPI APP INITIALIZATION
# # =============================================================================

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     await initialize_all_services()
#     yield
#     # Shutdown
#     await cleanup_all_services()

# app = FastAPI(
#     title="Complete Multi-Platform Social Media Automation",
#     description="Unified automation system for Reddit, YouTube, WhatsApp, Instagram, Facebook",
#     version="3.0.0",
#     docs_url="/docs",
#     redoc_url="/redoc",
#     lifespan=lifespan
# )

# # CORS Configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",
#         "http://localhost:5173", 
#         "http://localhost:8080",
#         "https://frontend-agentic-bnc2.onrender.com",
#         "https://frontend-agentic.onrender.com",
#         "https://agentic-u5lx.onrender.com"
#     ],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
#     allow_headers=[
#         "Content-Type", 
#         "Authorization", 
#         "X-User-Token",
#         "Accept",
#         "Origin",
#         "X-Requested-With",
#         "Access-Control-Request-Method",
#         "Access-Control-Request-Headers"
#     ],
#     expose_headers=["*"],
#     max_age=3600
# )

# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["*"]
# )

# # Exception handlers
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     logger.error(f"Validation error on {request.url}: {exc.errors()}")
#     return JSONResponse(
#         status_code=422,
#         content={
#             "success": False,
#             "error": "Validation failed",
#             "details": exc.errors(),
#             "timestamp": datetime.now().isoformat()
#         }
#     )

# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     logger.error(f"Global exception on {request.url}: {exc}")
#     logger.error(traceback.format_exc())
#     return JSONResponse(
#         status_code=500,
#         content={
#             "success": False,
#             "error": str(exc),
#             "message": "An unexpected error occurred.",
#             "timestamp": datetime.now().isoformat()
#         }
#     )

# # =============================================================================
# # MAIN ENDPOINTS
# # =============================================================================

# @app.get("/")
# async def root():
#     """Main health check and service status"""
#     ai_status = "real" if not isinstance(ai_service, MockAIService) else "mock"
#     reddit_status = "real" if reddit_oauth_connector else "mock"
#     youtube_status = "real" if youtube_connector else "mock"
#     db_status = "real" if MULTIUSER_DB_AVAILABLE and not isinstance(database_manager, MockMultiUserDatabase) else "mock"
    
#     return {
#         "success": True,
#         "message": "Complete Multi-Platform Social Media Automation System",
#         "version": "3.0.0",
#         "timestamp": datetime.now().isoformat(),
#         "status": "running",
#         "platforms_enabled": {
#             "reddit": REDDIT_AUTOMATION_AVAILABLE and reddit_oauth_connector is not None,
#             "youtube": YOUTUBE_AVAILABLE and youtube_connector is not None,
#             "whatsapp": WHATSAPP_AVAILABLE,
#             "instagram": False,  # TODO: Implement
#             "facebook": False    # TODO: Implement
#         },
#         "services_status": {
#             "reddit": f"{reddit_status}",
#             "youtube": f"{youtube_status}",
#             "ai_service": f"{ai_status}",
#             "database": f"{db_status}"
#         },
#         "real_services_active": {
#             "ai_content_generation": ai_status == "real",
#             "reddit_posting": reddit_status == "real",
#             "youtube_upload": youtube_status == "real",
#             "persistent_database": db_status == "real"
#         }
#     }

# @app.get("/health")
# async def health_check():
#     """Comprehensive health check for all services"""
#     try:
#         services_status = {}
        
#         # Database health
#         if database_manager and hasattr(database_manager, 'health_check'):
#             try:
#                 db_health = await database_manager.health_check()
#                 services_status["database"] = db_health.get("status", "unknown")
#             except:
#                 services_status["database"] = "error"
#         else:
#             services_status["database"] = "mock"
        
#         # AI service health
#         if ai_service and hasattr(ai_service, 'test_ai_connection'):
#             try:
#                 ai_test = await ai_service.test_ai_connection()
#                 services_status["ai_service"] = "connected" if ai_test.get("success") else "error"
#             except:
#                 services_status["ai_service"] = "error"
#         else:
#             services_status["ai_service"] = "mock"
        
#         # Platform-specific health
#         services_status["reddit"] = "connected" if reddit_oauth_connector else "disconnected"
#         services_status["youtube"] = "connected" if youtube_connector else "disconnected"
#         services_status["whatsapp"] = "available" if WHATSAPP_AVAILABLE else "unavailable"
        
#         return {
#             "status": "healthy",
#             "services": services_status,
#             "active_users": {
#                 "reddit_connections": len(user_reddit_tokens),
#                 "youtube_connections": len(user_youtube_tokens),
#                 "total_automations": len(automation_configs)
#             },
#             "timestamp": datetime.now().isoformat()
#         }
        
#     except Exception as e:
#         logger.error(f"Health check failed: {e}")
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "status": "unhealthy",
#                 "error": str(e),
#                 "timestamp": datetime.now().isoformat()
#             }
#         )

# # =============================================================================
# # AUTHENTICATION ENDPOINTS
# # =============================================================================

# # =============================================================================
# # AUTHENTICATION ENDPOINTS
# # =============================================================================

# @app.post("/api/auth/register")
# async def register_user(user_data: RegisterRequest):
#     """Register new user with email and password"""
#     try:
#         result = await database_manager.register_user(
#             email=user_data.email,
#             password=user_data.password,
#             name=user_data.name
#         )
        
#         if result["success"]:
#             logger.info(f"New user registered: {user_data.email}")
        
#         return result
        
#     except Exception as e:
#         logger.error(f"User registration failed: {e}")
#         raise HTTPException(status_code=400, detail=str(e))

# @app.post("/api/auth/login")
# async def login_user(login_data: LoginRequest):
#     """Login user and return JWT token"""
#     try:
#         result = await database_manager.login_user(
#             email=login_data.email,
#             password=login_data.password
#         )
        
#         if result["success"]:
#             logger.info(f"User logged in: {login_data.email}")
        
#         return result
        
#     except Exception as e:
#         logger.error(f"User login failed: {e}")
#         raise HTTPException(status_code=401, detail="Invalid credentials")

# @app.get("/api/auth/me")
# async def get_current_user_info(current_user: dict = Depends(get_current_user)):
#     """Get current user information"""
#     return {
#         "success": True,
#         "user": current_user
#     }

# # =============================================================================
# # REDDIT AUTOMATION ENDPOINTS
# # =============================================================================

# @app.get("/api/oauth/reddit/authorize")
# async def reddit_oauth_authorize(current_user: dict = Depends(get_current_user)):
#     """Start Reddit OAuth flow for authenticated user"""
#     try:
#         user_id = current_user["id"]
        
#         # Generate OAuth state
#         state = f"oauth_{user_id}_{uuid.uuid4().hex[:12]}"
        
#         # Store in database with expiration
#         expires_at = datetime.utcnow() + timedelta(minutes=15)
#         await database_manager.store_oauth_state(state, user_id, expires_at)
        
#         reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
#         reddit_redirect_uri = os.getenv("REDDIT_REDIRECT_URI", "https://agentic-u5lx.onrender.com/api/oauth/reddit/callback")
        
#         if not reddit_client_id:
#             raise HTTPException(status_code=500, detail="Reddit credentials not configured")
        
#         oauth_url = f"https://www.reddit.com/api/v1/authorize?client_id={reddit_client_id}&response_type=code&state={state}&redirect_uri={reddit_redirect_uri}&duration=permanent&scope=identity,submit,edit,read"
        
#         logger.info(f"Starting Reddit OAuth for user {user_id} - state: {state}")
        
#         return {
#             "success": True,
#             "redirect_url": oauth_url,
#             "state": state,
#             "user_id": user_id
#         }
        
#     except Exception as e:
#         logger.error(f"Reddit OAuth authorize failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/oauth/reddit/callback")
# async def reddit_oauth_callback(code: str, state: str):
#     """Handle Reddit OAuth callback for authenticated user"""
#     try:
#         # Get user_id from database
#         state_data = await database_manager.get_oauth_state(state)
#         if not state_data:
#             logger.error(f"Invalid OAuth state: {state}")
#             return RedirectResponse(
#                 url="https://frontend-agentic-bnc2.onrender.com/?error=invalid_oauth_state",
#                 status_code=302
#             )
        
#         user_id = state_data["user_id"]
#         logger.info(f"Processing Reddit OAuth callback for user {user_id}")
        
#         # Exchange code for token
#         reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
#         reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
#         reddit_redirect_uri = os.getenv("REDDIT_REDIRECT_URI")
        
#         if not reddit_client_id or not reddit_client_secret:
#             logger.error("Reddit credentials missing from environment")
#             return RedirectResponse(
#                 url="https://frontend-agentic-bnc2.onrender.com/?error=missing_credentials",
#                 status_code=302
#             )
        
#         # Token exchange request
#         auth_string = f"{reddit_client_id}:{reddit_client_secret}"
#         auth_bytes = auth_string.encode('ascii')
#         auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
#         headers = {
#             'Authorization': f'Basic {auth_b64}',
#             'User-Agent': 'CompleteAutomationPlatform/3.0'
#         }
        
#         data = {
#             'grant_type': 'authorization_code',
#             'code': code,
#             'redirect_uri': reddit_redirect_uri
#         }
        
#         logger.info("Exchanging code for access token...")
        
#         response = requests.post(
#             'https://www.reddit.com/api/v1/access_token',
#             headers=headers,
#             data=data,
#             timeout=30
#         )
        
#         if response.status_code == 200:
#             token_data = response.json()
#             access_token = token_data.get('access_token')
            
#             if access_token:
#                 # Get Reddit user info
#                 user_headers = {
#                     'Authorization': f'Bearer {access_token}',
#                     'User-Agent': 'CompleteAutomationPlatform/3.0'
#                 }
                
#                 username = None
#                 reddit_user_id = ""
#                 user_info = {}
                
#                 try:
#                     user_response = requests.get(
#                         'https://oauth.reddit.com/api/v1/me',
#                         headers=user_headers,
#                         timeout=15
#                     )
                    
#                     if user_response.status_code == 200:
#                         user_info = user_response.json()
#                         username = user_info.get('name')
#                         reddit_user_id = user_info.get('id', '')
                        
#                         if not username:
#                             username = f"User_{reddit_user_id[:8]}" if reddit_user_id else f"User_{uuid.uuid4().hex[:8]}"
#                     else:
#                         username = f"User_{uuid.uuid4().hex[:8]}"
#                         user_info = {"name": username, "id": reddit_user_id}
                        
#                 except Exception as e:
#                     logger.error(f"User info request failed: {e}")
#                     username = f"User_{uuid.uuid4().hex[:8]}"
#                     user_info = {"name": username, "id": reddit_user_id}
                
#                 if not username:
#                     username = f"User_{uuid.uuid4().hex[:8]}"
                
#                 logger.info(f"Reddit OAuth successful for user: {username}")
                
#                 # Store tokens in database
#                 db_token_data = {
#                     "access_token": access_token,
#                     "refresh_token": token_data.get("refresh_token", ""),
#                     "expires_in": token_data.get("expires_in", 3600),
#                     "reddit_username": username,
#                     "reddit_user_id": reddit_user_id,
#                     "token_type": "bearer",
#                     "scope": "submit,edit,read"
#                 }
                
#                 if database_manager and hasattr(database_manager, 'store_reddit_tokens'):
#                     try:
#                         await database_manager.store_reddit_tokens(user_id, db_token_data)
#                         logger.info(f"Reddit tokens stored for user {user_id} as {username}")
#                     except Exception as e:
#                         logger.error(f"Database storage error: {e}")
                
#                 # Store in memory for immediate use
#                 user_reddit_tokens[user_id] = {
#                     "access_token": access_token,
#                     "refresh_token": token_data.get("refresh_token", ""),
#                     "reddit_username": username,
#                     "connected_at": datetime.now().isoformat(),
#                     "user_info": user_info or {"name": username, "id": reddit_user_id}
#                 }
                
#                 return RedirectResponse(
#                     url=f"https://frontend-agentic-bnc2.onrender.com/?reddit_connected=true&username={username}",
#                     status_code=302
#                 )
#             else:
#                 logger.error("No access token in Reddit response")
#                 return RedirectResponse(
#                     url="https://frontend-agentic-bnc2.onrender.com/?error=no_access_token",
#                     status_code=302
#                 )
#         else:
#             logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
#             return RedirectResponse(
#                 url="https://frontend-agentic-bnc2.onrender.com/?error=token_exchange_failed",
#                 status_code=302
#             )
        
#     except Exception as e:
#         logger.error(f"Reddit OAuth callback failed: {e}")
#         return RedirectResponse(
#             url="https://frontend-agentic-bnc2.onrender.com/?error=oauth_failed",
#             status_code=302
#         )

# @app.get("/api/reddit/connection-status")
# async def get_reddit_connection_status(current_user: dict = Depends(get_current_user)):
#     """Get Reddit connection status for current user"""
#     try:
#         user_id = current_user["id"]
        
#         # Check database for user's Reddit connection
#         if database_manager and hasattr(database_manager, 'check_reddit_connection'):
#             db_status = await database_manager.check_reddit_connection(user_id)
            
#             if db_status.get("connected"):
#                 # Load token into memory if not already there
#                 if user_id not in user_reddit_tokens:
#                     tokens = await database_manager.get_reddit_tokens(user_id)
#                     if tokens and tokens.get("is_valid"):
#                         user_reddit_tokens[user_id] = {
#                             "access_token": tokens["access_token"],
#                             "refresh_token": tokens.get("refresh_token", ""),
#                             "reddit_username": tokens["reddit_username"],
#                             "connected_at": datetime.now().isoformat()
#                         }
                
#                 return {
#                     "success": True,
#                     "connected": True,
#                     "user_id": user_id,
#                     "reddit_username": db_status.get("reddit_username"),
#                     "expires_at": db_status.get("expires_at"),
#                     "message": f"Reddit connected as {db_status.get('reddit_username')}",
#                     "source": "database"
#                 }
        
#         # Fallback to memory check
#         if user_id in user_reddit_tokens:
#             creds = user_reddit_tokens[user_id]
#             username = creds.get("reddit_username")
#             return {
#                 "success": True,
#                 "connected": True,
#                 "user_id": user_id,
#                 "reddit_username": username,
#                 "connected_at": creds.get("connected_at"),
#                 "message": f"Reddit connected as {username}",
#                 "source": "memory"
#             }
        
#         return {
#             "success": True,
#             "connected": False,
#             "user_id": user_id,
#             "message": "No Reddit connection found"
#         }
        
#     except Exception as e:
#         logger.error(f"Connection status check failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.post("/api/reddit/disconnect")
# async def disconnect_reddit(current_user: dict = Depends(get_current_user)):
#     """Disconnect Reddit account for current user"""
#     try:
#         user_id = current_user["id"]
        
#         # Remove from memory
#         if user_id in user_reddit_tokens:
#             reddit_username = user_reddit_tokens[user_id].get("reddit_username", "Unknown")
#             del user_reddit_tokens[user_id]
#             logger.info(f"Removed Reddit tokens from memory for user {user_id}")
        
#         # Revoke in database
#         if database_manager and hasattr(database_manager, 'revoke_reddit_connection'):
#             await database_manager.revoke_reddit_connection(user_id)
        
#         return {
#             "success": True,
#             "message": "Reddit account disconnected successfully"
#         }
        
#     except Exception as e:
#         logger.error(f"Reddit disconnect failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.post("/api/reddit/post")
# async def manual_reddit_post(
#     post_data: ManualPostRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Manual Reddit posting for authenticated user"""
#     try:
#         user_id = current_user["id"]
        
#         # Check Reddit connection
#         if user_id not in user_reddit_tokens:
#             return {
#                 "success": False, 
#                 "error": "Reddit not connected",
#                 "message": "Please connect your Reddit account first"
#             }
        
#         if not reddit_oauth_connector:
#             return {
#                 "success": False,
#                 "error": "Reddit connector not available",
#                 "message": "Reddit service not configured"
#             }
        
#         reddit_username = user_reddit_tokens[user_id].get("reddit_username", "Unknown")
#         access_token = user_reddit_tokens[user_id]["access_token"]
        
#         logger.info(f"Manual post: {reddit_username} posting to r/{post_data.subreddit}")
        
#         # Post using Reddit API
#         result = await reddit_oauth_connector.post_content_with_token(
#             access_token=access_token,
#             subreddit_name=post_data.subreddit,
#             title=post_data.title,
#             content=post_data.content,
#             content_type=post_data.contentType
#         )
        
#         return result
        
#     except Exception as e:
#         logger.error(f"Manual Reddit post failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.post("/api/automation/test-auto-post")
# async def test_reddit_auto_post(
#     test_data: TestPostRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Test auto-post generation with AI for authenticated user"""
#     try:
#         user_id = current_user["id"]
        
#         if isinstance(ai_service, MockAIService):
#             return {
#                 "success": False,
#                 "error": "Mock AI service active",
#                 "message": "Configure MISTRAL_API_KEY or GROQ_API_KEY environment variables"
#             }
        
#         logger.info(f"Generating AI content for user {user_id}: {test_data.domain}")
        
#         # Generate content using AI service
#         content_result = await ai_service.generate_reddit_domain_content(
#             domain=test_data.domain,
#             business_type=test_data.business_type,
#             business_description=test_data.business_description,
#             target_audience=test_data.target_audience,
#             language=test_data.language,
#             content_style=test_data.content_style,
#             test_mode=False
#         )
        
#         if not content_result.get("success", True):
#             return {
#                 "success": False,
#                 "error": f"AI content generation failed: {content_result.get('error')}"
#             }
        
#         return {
#             "success": True,
#             "message": "AI content generated successfully",
#             "post_details": {
#                 "title": content_result.get("title", "AI Generated Title"),
#                 "subreddit": test_data.subreddits[0] if test_data.subreddits else "test",
#                 "user_id": user_id
#             },
#             "content_preview": content_result.get("content", ""),
#             "ai_service": content_result.get("ai_service", "unknown"),
#             "timestamp": datetime.now().isoformat()
#         }
#     except Exception as e:
#         logger.error(f"Test auto-post failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.post("/api/automation/setup-auto-posting")
# async def setup_reddit_auto_posting(
#     config_data: AutoPostingRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Setup Reddit automatic posting for authenticated user"""
#     try:
#         user_id = current_user["id"]
#         logger.info(f"Setting up Reddit auto-posting for user {user_id}")
        
#         # Validate posting times
#         if not config_data.posting_times:
#             return {
#                 "success": False,
#                 "error": "No posting times provided"
#             }
        
#         validated_times = []
#         for time_str in config_data.posting_times:
#             try:
#                 datetime.strptime(time_str, "%H:%M")
#                 validated_times.append(time_str)
#             except ValueError:
#                 logger.warning(f"Invalid time format: {time_str}")
        
#         if not validated_times:
#             return {
#                 "success": False,
#                 "error": "No valid posting times provided"
#             }
        
#         # Check Reddit connection
#         if user_id not in user_reddit_tokens:
#             return {
#                 "success": False,
#                 "error": "Reddit account not connected"
#             }
        
#         reddit_username = user_reddit_tokens[user_id].get("reddit_username", "Unknown")
        
#         # Store configuration
#         if user_id not in automation_configs:
#             automation_configs[user_id] = {}
        
#         automation_configs[user_id]["reddit_auto_posting"] = {
#             "config": config_data.dict(),
#             "enabled": True,
#             "created_at": datetime.now().isoformat(),
#             "reddit_username": reddit_username
#         }
        
#         # Store in database
#         if database_manager and hasattr(database_manager, 'store_automation_config'):
#             await database_manager.store_automation_config(
#                 user_id=user_id,
#                 config_type='auto_posting',
#                 config_data=config_data.dict()
#             )
        
#         # Setup with Reddit automation scheduler
#         if reddit_automation_scheduler:
#             try:
#                 from reddit_automation import AutoPostConfig
#                 auto_config = AutoPostConfig(
#                     user_id=user_id,
#                     domain=config_data.domain,
#                     business_type=config_data.business_type,
#                     business_description=config_data.business_description,
#                     target_audience=config_data.target_audience,
#                     language=config_data.language,
#                     subreddits=config_data.subreddits,
#                     posts_per_day=config_data.posts_per_day,
#                     posting_times=validated_times,
#                     content_style=config_data.content_style
#                 )
                
#                 result = await reddit_automation_scheduler.setup_auto_posting(auto_config)
#                 result["user_id"] = user_id
#                 result["reddit_username"] = reddit_username
#                 return result
                
#             except Exception as e:
#                 logger.error(f"Reddit automation scheduler failed: {e}")
#                 return {"success": False, "error": str(e)}
        
#         return {
#             "success": True,
#             "message": "Reddit automation configured successfully",
#             "user_id": user_id,
#             "reddit_username": reddit_username,
#             "posting_times": validated_times
#         }
        
#     except Exception as e:
#         logger.error(f"Reddit automation setup failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.get("/api/automation/status")
# async def get_reddit_automation_status(current_user: dict = Depends(get_current_user)):
#     """Get Reddit automation status for current user"""
#     try:
#         user_id = current_user["id"]
        
#         if reddit_automation_scheduler and hasattr(reddit_automation_scheduler, 'get_automation_status'):
#             result = await reddit_automation_scheduler.get_automation_status(user_id)
#             return result
        
#         # Fallback status
#         user_config = automation_configs.get(user_id, {})
        
#         return {
#             "success": True,
#             "user_id": user_id,
#             "reddit_connected": user_id in user_reddit_tokens,
#             "reddit_username": user_reddit_tokens.get(user_id, {}).get("reddit_username", ""),
#             "auto_posting": {
#                 "enabled": "reddit_auto_posting" in user_config,
#                 "config": user_config.get("reddit_auto_posting", {}).get("config")
#             }
#         }
        
#     except Exception as e:
#         logger.error(f"Reddit automation status check failed: {e}")
#         return {"success": False, "error": str(e)}

# # =============================================================================
# # YOUTUBE AUTOMATION ENDPOINTS
# # =============================================================================

# @app.post("/api/youtube/oauth-url")
# async def youtube_oauth_url(request: YouTubeOAuthRequest):
#     """Generate YouTube OAuth URL"""
#     try:
#         logger.info(f"YouTube OAuth request for user_id: {request.user_id}")
        
#         if not youtube_connector:
#             raise HTTPException(
#                 status_code=503, 
#                 detail="YouTube service not initialized"
#             )
        
#         redirect_uri = request.redirect_uri
#         if not redirect_uri:
#             frontend_url = os.getenv("FRONTEND_URL", "https://frontend-agentic-bnc2.onrender.com")
#             redirect_uri = f"{frontend_url}/youtube"
        
#         result = youtube_connector.generate_oauth_url(
#             state=request.state,
#             redirect_uri=redirect_uri
#         )
        
#         if result["success"]:
#             return result
#         else:
#             raise HTTPException(status_code=400, detail=result["error"])
            
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"YouTube OAuth URL generation failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/youtube/oauth-callback")
# async def youtube_oauth_callback(request: YouTubeOAuthCallback):
#     """Handle YouTube OAuth callback and store tokens"""
#     try:
#         logger.info(f"YouTube OAuth callback for user_id: {request.user_id}")
        
#         if not youtube_connector:
#             raise HTTPException(status_code=503, detail="YouTube service not available")
        
#         redirect_uri = request.redirect_uri
#         if not redirect_uri:
#             frontend_url = os.getenv("FRONTEND_URL", "https://frontend-agentic-bnc2.onrender.com")
#             redirect_uri = f"{frontend_url}/youtube"
            
#         token_result = await youtube_connector.exchange_code_for_token(
#             code=request.code,
#             redirect_uri=redirect_uri
#         )
        
#         if not token_result["success"]:
#             raise HTTPException(status_code=400, detail=token_result["error"])
        
#         user_id = request.user_id
        
#         youtube_credentials = {
#             "access_token": token_result["access_token"],
#             "refresh_token": token_result["refresh_token"],
#             "token_uri": token_result["token_uri"],
#             "client_id": token_result["client_id"],
#             "client_secret": token_result["client_secret"],
#             "scopes": token_result["scopes"],
#             "expires_at": datetime.now() + timedelta(seconds=token_result.get("expires_in", 3600)),
#             "channel_info": token_result["channel_info"]
#         }
        
#         # Store in database
#         if database_manager and hasattr(database_manager, 'store_youtube_credentials'):
#             await database_manager.store_youtube_credentials(
#                 user_id=user_id,
#                 credentials=youtube_credentials
#             )
#         elif youtube_database_manager:
#             await youtube_database_manager.store_youtube_credentials(
#                 user_id=user_id,
#                 credentials=youtube_credentials
#             )
        
#         # Store in memory
#         user_youtube_tokens[user_id] = youtube_credentials
        
#         logger.info(f"YouTube OAuth successful for user {user_id}")
        
#         return {
#             "success": True,
#             "message": "YouTube connected successfully",
#             "channel_info": token_result["channel_info"]
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"YouTube OAuth callback failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/youtube/status/{user_id}")
# async def youtube_status(user_id: str):
#     """Get YouTube connection and automation status"""
#     try:
#         logger.info(f"Checking YouTube status for user: {user_id}")
        
#         youtube_connected = False
#         channel_info = None
        
#         # Check database first
#         if database_manager and hasattr(database_manager, 'get_youtube_credentials'):
#             credentials = await database_manager.get_youtube_credentials(user_id)
#         elif youtube_database_manager:
#             credentials = await youtube_database_manager.get_youtube_credentials(user_id)
#         else:
#             credentials = None
        
#         if credentials and credentials.get("is_active"):
#             youtube_connected = True
#             channel_info = credentials.get("channel_info")
            
#             # Load into memory if not already there
#             if user_id not in user_youtube_tokens:
#                 user_youtube_tokens[user_id] = credentials
        
#         # Get automation status
#         automation_status = {}
#         if youtube_scheduler and youtube_connected:
#             automation_status = await youtube_scheduler.get_automation_status(user_id)
        
#         return {
#             "success": True,
#             "user_id": user_id,
#             "youtube_connected": youtube_connected,
#             "channel_info": channel_info,
#             "youtube_automation": automation_status.get("youtube_automation", {
#                 "enabled": False,
#                 "config": None,
#                 "stats": {"total_uploads": 0, "successful_uploads": 0, "failed_uploads": 0}
#             })
#         }
        
#     except Exception as e:
#         logger.error(f"YouTube status check failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/youtube/disconnect/{user_id}")
# async def youtube_disconnect(user_id: str):
#     """Disconnect YouTube and remove stored credentials"""
#     try:
#         # Remove from memory
#         if user_id in user_youtube_tokens:
#             del user_youtube_tokens[user_id]
        
#         # Remove from database
#         if database_manager and hasattr(database_manager, 'revoke_youtube_access'):
#             success = await database_manager.revoke_youtube_access(user_id)
#         elif youtube_database_manager:
#             success = await youtube_database_manager.revoke_youtube_access(user_id)
#         else:
#             success = True
        
#         if success:
#             return {
#                 "success": True,
#                 "message": "YouTube disconnected successfully"
#             }
#         else:
#             raise HTTPException(status_code=400, detail="Failed to disconnect YouTube")
            
#     except Exception as e:
#         logger.error(f"YouTube disconnect failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/youtube/setup-automation")
# async def youtube_setup_automation(request: YouTubeSetupRequest):
#     """Setup YouTube automation configuration"""
#     try:
#         if not youtube_scheduler:
#             raise HTTPException(status_code=503, detail="YouTube scheduler not available")
        
#         user_id = request.user_id
        
#         # Check if user has YouTube connected
#         if user_id not in user_youtube_tokens:
#             # Try to load from database
#             if database_manager and hasattr(database_manager, 'get_youtube_credentials'):
#                 credentials = await database_manager.get_youtube_credentials(user_id)
#             elif youtube_database_manager:
#                 credentials = await youtube_database_manager.get_youtube_credentials(user_id)
#             else:
#                 credentials = None
                
#             if not credentials:
#                 raise HTTPException(status_code=400, detail="YouTube not connected")
            
#             user_youtube_tokens[user_id] = credentials
        
#         result = await youtube_scheduler.setup_youtube_automation(user_id, request.config)
        
#         if result["success"]:
#             # Store automation config
#             if user_id not in automation_configs:
#                 automation_configs[user_id] = {}
#             automation_configs[user_id]["youtube_automation"] = {
#                 "config": request.config,
#                 "enabled": True,
#                 "created_at": datetime.now().isoformat()
#             }
            
#             return result
#         else:
#             raise HTTPException(status_code=400, detail=result["error"])
            
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"YouTube automation setup failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/youtube/upload")
# async def youtube_upload_video(request: YouTubeUploadRequest):
#     """Upload video to YouTube"""
#     try:
#         if not youtube_scheduler:
#             raise HTTPException(status_code=503, detail="YouTube service not available")
        
#         user_id = request.user_id
        
#         # Get user's YouTube credentials
#         if user_id not in user_youtube_tokens:
#             if database_manager and hasattr(database_manager, 'get_youtube_credentials'):
#                 credentials = await database_manager.get_youtube_credentials(user_id)
#             elif youtube_database_manager:
#                 credentials = await youtube_database_manager.get_youtube_credentials(user_id)
#             else:
#                 credentials = None
                
#             if not credentials:
#                 raise HTTPException(status_code=400, detail="YouTube not connected")
            
#             user_youtube_tokens[user_id] = credentials
        
#         credentials = user_youtube_tokens[user_id]
        
#         # Upload video
#         result = await youtube_scheduler.generate_and_upload_content(
#             user_id=user_id,
#             credentials_data=credentials,
#             content_type=request.content_type,
#             title=request.title,
#             description=request.description,
#             video_url=request.video_url
#         )
        
#         if result["success"]:
#             return result
#         else:
#             raise HTTPException(status_code=400, detail=result["error"])
            
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"YouTube upload failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))




# @app.post("/api/ai/generate-youtube-content")
# async def generate_youtube_content(request: YouTubeContentRequest):
#     """Generate YouTube content using AI"""
#     try:
#         if ai_service2 and hasattr(ai_service2, 'generate_youtube_content'):
#             result = await ai_service2.generate_youtube_content(
#                 content_type=request.content_type,
#                 topic=request.topic,
#                 target_audience=request.target_audience,
#                 duration_seconds=60 if request.content_type == "shorts" else 300,
#                 style="engaging"
#             )
#         elif ai_service and hasattr(ai_service, 'generate_youtube_content'):
#             result = await ai_service.generate_youtube_content(
#                 content_type=request.content_type,
#                 topic=request.topic,
#                 target_audience=request.target_audience
#             )
#         else:
#             # Fallback mock content generation
#             result = {
#                 "success": True,
#                 "title": f"AI Generated {request.content_type.title()} - {request.topic}",
#                 "description": f"This is an AI-generated {request.content_type} about {request.topic} for {request.target_audience} audience. Perfect for engaging your YouTube audience!",
#                 "tags": ["AI", "generated", request.content_type, request.topic, request.target_audience],
#                 "thumbnail_suggestions": [
#                     "Bold text with bright colors",
#                     "Emotional expression face",
#                     "Question mark or arrow graphics"
#                 ],
#                 "ai_service": "fallback"
#             }
        
#         return result
        
#     except Exception as e:
#         logger.error(f"YouTube content generation failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/youtube/analytics/{user_id}")
# async def youtube_analytics(user_id: str, days: int = 30):
#     """Get YouTube channel analytics"""
#     try:
#         if not youtube_connector:
#             raise HTTPException(status_code=503, detail="YouTube service not available")
        
#         # Get user's YouTube credentials
#         if user_id not in user_youtube_tokens:
#             if database_manager and hasattr(database_manager, 'get_youtube_credentials'):
#                 credentials = await database_manager.get_youtube_credentials(user_id)
#             elif youtube_database_manager:
#                 credentials = await youtube_database_manager.get_youtube_credentials(user_id)
#             else:
#                 credentials = None
                
#             if not credentials:
#                 raise HTTPException(status_code=400, detail="YouTube not connected")
            
#             user_youtube_tokens[user_id] = credentials
        
#         credentials = user_youtube_tokens[user_id]
        
#         # Get analytics
#         result = await youtube_connector.get_channel_analytics(credentials, days)
        
#         if result["success"]:
#             return result
#         else:
#             raise HTTPException(status_code=400, detail=result["error"])
            
#     except Exception as e:
#         logger.error(f"YouTube analytics failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# # =============================================================================
# # WHATSAPP AUTOMATION ENDPOINTS
# # =============================================================================

# @app.post("/api/whatsapp/setup")
# async def setup_whatsapp(
#     config: WhatsAppAutomationRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Setup WhatsApp automation for user"""
#     try:
#         user_id = current_user["id"]
        
#         if not WHATSAPP_AVAILABLE:
#             return {
#                 "success": False,
#                 "error": "WhatsApp service not available",
#                 "message": "WhatsApp module not configured"
#             }
        
#         # Store WhatsApp config
#         if user_id not in automation_configs:
#             automation_configs[user_id] = {}
        
#         automation_configs[user_id]["whatsapp"] = {
#             "config": config.dict(),
#             "enabled": True,
#             "created_at": datetime.now().isoformat()
#         }
        
#         logger.info(f"WhatsApp automation configured for user {user_id}")
        
#         return {
#             "success": True,
#             "message": "WhatsApp automation configured successfully",
#             "user_id": user_id,
#             "config": config.dict()
#         }
        
#     except Exception as e:
#         logger.error(f"WhatsApp setup failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.post("/api/whatsapp/send-message")
# async def send_whatsapp_message(
#     message_data: WhatsAppMessageRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Send WhatsApp message"""
#     try:
#         user_id = current_user["id"]
        
#         if not WHATSAPP_AVAILABLE:
#             return {
#                 "success": False,
#                 "error": "WhatsApp service not available"
#             }
        
#         # TODO: Implement actual WhatsApp message sending
#         logger.info(f"WhatsApp message sent by user {user_id} to {message_data.to}")
        
#         return {
#             "success": True,
#             "message": "WhatsApp message sent successfully",
#             "to": message_data.to,
#             "message_id": f"wa_msg_{uuid.uuid4().hex[:12]}"
#         }
        
#     except Exception as e:
#         logger.error(f"WhatsApp message sending failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.get("/api/whatsapp/status/{user_id}")
# async def whatsapp_status(user_id: str):
#     """Get WhatsApp automation status"""
#     try:
#         user_config = automation_configs.get(user_id, {}).get("whatsapp", {})
        
#         return {
#             "success": True,
#             "user_id": user_id,
#             "whatsapp_configured": bool(user_config),
#             "config": user_config.get("config", {}),
#             "enabled": user_config.get("enabled", False),
#             "stats": {
#                 "messages_sent": 0,
#                 "auto_replies": 0,
#                 "campaigns_sent": 0
#             }
#         }
        
#     except Exception as e:
#         logger.error(f"WhatsApp status check failed: {e}")
#         return {"success": False, "error": str(e)}

# # =============================================================================
# # MULTI-PLATFORM ENDPOINTS
# # =============================================================================

# @app.get("/api/platforms/status")
# async def get_all_platforms_status(current_user: dict = Depends(get_current_user)):
#     """Get status of all connected platforms for user"""
#     try:
#         user_id = current_user["id"]
        
#         platforms_status = {
#             "reddit": {
#                 "connected": user_id in user_reddit_tokens,
#                 "username": user_reddit_tokens.get(user_id, {}).get("reddit_username"),
#                 "automation_enabled": user_id in automation_configs and "reddit_auto_posting" in automation_configs[user_id]
#             },
#             "youtube": {
#                 "connected": user_id in user_youtube_tokens,
#                 "channel_info": user_youtube_tokens.get(user_id, {}).get("channel_info"),
#                 "automation_enabled": user_id in automation_configs and "youtube_automation" in automation_configs[user_id]
#             },
#             "whatsapp": {
#                 "connected": user_id in automation_configs and "whatsapp" in automation_configs[user_id],
#                 "automation_enabled": automation_configs.get(user_id, {}).get("whatsapp", {}).get("enabled", False)
#             },
#             "instagram": {
#                 "connected": False,  # TODO: Implement
#                 "automation_enabled": False
#             },
#             "facebook": {
#                 "connected": False,  # TODO: Implement
#                 "automation_enabled": False
#             }
#         }
        
#         return {
#             "success": True,
#             "user_id": user_id,
#             "platforms": platforms_status,
#             "total_connected": sum(1 for p in platforms_status.values() if p["connected"]),
#             "total_automated": sum(1 for p in platforms_status.values() if p["automation_enabled"])
#         }
        
#     except Exception as e:
#         logger.error(f"Platforms status check failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.get("/api/user/dashboard")
# async def get_user_dashboard(current_user: dict = Depends(get_current_user)):
#     """Get comprehensive dashboard data for current user"""
#     try:
#         user_id = current_user["id"]
        
#         # Get platform connections count
#         reddit_connected = user_id in user_reddit_tokens
#         youtube_connected = user_id in user_youtube_tokens
#         whatsapp_configured = user_id in automation_configs and "whatsapp" in automation_configs[user_id]
        
#         # Get automation counts
#         active_automations = 0
#         if user_id in automation_configs:
#             for platform, config in automation_configs[user_id].items():
#                 if config.get("enabled", False):
#                     active_automations += 1
        
#         # Calculate today's activity (mock data for now)
#         today_posts = 0  # TODO: Get from database
#         total_engagement = 0  # TODO: Calculate from all platforms
        
#         dashboard_data = {
#             "user_info": {
#                 "name": current_user.get("name", ""),
#                 "email": current_user.get("email", ""),
#                 "joined_date": "2024-01-01"  # TODO: Get from user creation date
#             },
#             "platforms_connected": {
#                 "reddit": reddit_connected,
#                 "youtube": youtube_connected,
#                 "whatsapp": whatsapp_configured,
#                 "total": sum([reddit_connected, youtube_connected, whatsapp_configured])
#             },
#             "automation_summary": {
#                 "active_automations": active_automations,
#                 "reddit_auto_posting": reddit_connected and "reddit_auto_posting" in automation_configs.get(user_id, {}),
#                 "youtube_automation": youtube_connected and "youtube_automation" in automation_configs.get(user_id, {}),
#                 "whatsapp_automation": whatsapp_configured
#             },
#             "today_stats": {
#                 "posts_created": today_posts,
#                 "total_engagement": total_engagement,
#                 "platforms_active": sum([reddit_connected, youtube_connected, whatsapp_configured])
#             },
#             "recent_activity": [
#                 # TODO: Get from activity log
#             ]
#         }
        
#         return {
#             "success": True,
#             "dashboard": dashboard_data,
#             "user": current_user
#         }
        
#     except Exception as e:
#         logger.error(f"Dashboard data fetch failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.get("/api/user/activity")
# async def get_user_activity(
#     current_user: dict = Depends(get_current_user),
#     days: int = Query(7, description="Number of days to fetch activity for")
# ):
#     """Get user's activity across all platforms"""
#     try:
#         user_id = current_user["id"]
        
#         # TODO: Implement actual activity fetching from database
#         activity_data = {
#             "reddit": {
#                 "posts": [],
#                 "replies": [],
#                 "total_karma": 0
#             },
#             "youtube": {
#                 "uploads": [],
#                 "total_views": 0,
#                 "total_subscribers": 0
#             },
#             "whatsapp": {
#                 "messages_sent": 0,
#                 "campaigns": []
#             }
#         }
        
#         return {
#             "success": True,
#             "activity": activity_data,
#             "user_id": user_id,
#             "period_days": days
#         }
        
#     except Exception as e:
#         logger.error(f"User activity fetch failed: {e}")
#         return {"success": False, "error": str(e)}

# # =============================================================================
# # DEBUG ENDPOINTS
# # =============================================================================

# @app.get("/api/debug/services")
# async def debug_services_status():
#     """Debug endpoint to check all service status"""
#     return {
#         "services": {
#             "reddit": {
#                 "oauth_connector": reddit_oauth_connector is not None,
#                 "automation_scheduler": reddit_automation_scheduler is not None,
#                 "automation_available": REDDIT_AUTOMATION_AVAILABLE
#             },
#             "youtube": {
#                 "connector": youtube_connector is not None,
#                 "scheduler": youtube_scheduler is not None,
#                 "available": YOUTUBE_AVAILABLE
#             },
#             "whatsapp": {
#                 "available": WHATSAPP_AVAILABLE
#             },
#             "ai": {
#                 "service1": ai_service is not None and not isinstance(ai_service, MockAIService),
#                 "service2": ai_service2 is not None,
#                 "ai_service2_available": AI_SERVICE2_AVAILABLE
#             },
#             "database": {
#                 "primary": database_manager is not None and not isinstance(database_manager, MockMultiUserDatabase),
#                 "youtube": youtube_database_manager is not None,
#                 "multiuser_available": MULTIUSER_DB_AVAILABLE,
#                 "youtube_db_available": YOUTUBE_DATABASE_AVAILABLE
#             }
#         },
#         "environment_vars": {
#             "REDDIT_CLIENT_ID": "✓" if os.getenv("REDDIT_CLIENT_ID") else "✗",
#             "REDDIT_CLIENT_SECRET": "✓" if os.getenv("REDDIT_CLIENT_SECRET") else "✗",
#             "GOOGLE_CLIENT_ID": "✓" if os.getenv("GOOGLE_CLIENT_ID") else "✗",
#             "GOOGLE_CLIENT_SECRET": "✓" if os.getenv("GOOGLE_CLIENT_SECRET") else "✗",
#             "MISTRAL_API_KEY": "✓" if os.getenv("MISTRAL_API_KEY") else "✗",
#             "GROQ_API_KEY": "✓" if os.getenv("GROQ_API_KEY") else "✗",
#             "MONGODB_URI": "✓" if os.getenv("MONGODB_URI") else "✗"
#         },
#         "active_connections": {
#             "reddit_tokens": len(user_reddit_tokens),
#             "youtube_tokens": len(user_youtube_tokens),
#             "automation_configs": len(automation_configs),
#             "oauth_states": len(oauth_states)
#         },
#         "timestamp": datetime.now().isoformat()
#     }

# @app.get("/api/debug/user-tokens")
# async def debug_user_tokens(current_user: dict = Depends(get_current_user)):
#     """Debug user's tokens and connections"""
#     try:
#         user_id = current_user["id"]
        
#         return {
#             "success": True,
#             "user_id": user_id,
#             "tokens": {
#                 "reddit": {
#                     "exists": user_id in user_reddit_tokens,
#                     "username": user_reddit_tokens.get(user_id, {}).get("reddit_username"),
#                     "connected_at": user_reddit_tokens.get(user_id, {}).get("connected_at")
#                 },
#                 "youtube": {
#                     "exists": user_id in user_youtube_tokens,
#                     "channel_info": user_youtube_tokens.get(user_id, {}).get("channel_info", {}).get("title"),
#                     "expires_at": str(user_youtube_tokens.get(user_id, {}).get("expires_at"))
#                 }
#             },
#             "automations": automation_configs.get(user_id, {}),
#             "all_users_with_tokens": {
#                 "reddit": list(user_reddit_tokens.keys()),
#                 "youtube": list(user_youtube_tokens.keys())
#             }
#         }
        
#     except Exception as e:
#         return {"success": False, "error": str(e)}

# @app.get("/api/debug/database")
# async def debug_database_status():
#     """Debug database connections and health"""
#     try:
#         results = {}
        
#         # Primary database health
#         if database_manager and hasattr(database_manager, 'health_check'):
#             try:
#                 results["primary_db"] = await database_manager.health_check()
#             except Exception as e:
#                 results["primary_db"] = {"error": str(e)}
#         else:
#             results["primary_db"] = {"status": "not_available"}
        
#         # YouTube database health
#         if youtube_database_manager and hasattr(youtube_database_manager, 'health_check'):
#             try:
#                 results["youtube_db"] = await youtube_database_manager.health_check()
#             except Exception as e:
#                 results["youtube_db"] = {"error": str(e)}
#         else:
#             results["youtube_db"] = {"status": "not_available"}
        
#         results["database_types"] = {
#             "primary": type(database_manager).__name__ if database_manager else None,
#             "youtube": type(youtube_database_manager).__name__ if youtube_database_manager else None
#         }
        
#         return results
        
#     except Exception as e:
#         return {"success": False, "error": str(e)}

# # =============================================================================
# # LEGACY ENDPOINTS (For backward compatibility)
# # =============================================================================

# @app.post("/api/auth/create-session")
# async def create_session_fallback():
#     """Create session for backward compatibility (deprecated)"""
#     try:
#         session_id = f"temp_{uuid.uuid4().hex[:16]}"
#         user_id = f"user_{uuid.uuid4().hex[:12]}"
        
#         logger.warning(f"Creating temporary session for backward compatibility: {session_id}")
        
#         return {
#             "success": True,
#             "session_id": session_id,
#             "user_id": user_id,
#             "message": "Temporary session created - please register/login for full features",
#             "deprecated": True,
#             "multiplatform_available": True
#         }
#     except Exception as e:
#         logger.error(f"Create fallback session failed: {e}")
#         return {"success": False, "error": str(e)}

# @app.get("/api/auth/check-existing-connection")
# async def check_existing_connection_fallback(session_id: str = Header(None, alias="x-session-id")):
#     """Check existing connection for backward compatibility"""
#     return {
#         "success": True,
#         "session_id": session_id or "none",
#         "user_id": "temp_user",
#         "platforms_connected": [],
#         "message": "Please register/login for full multi-platform features",
#         "multiplatform_available": True,
#         "deprecated": True,
#         "auth_endpoints": {
#             "register": "/api/auth/register",
#             "login": "/api/auth/login",
#             "me": "/api/auth/me"
#         }
#     }

# # =============================================================================
# # SYSTEM INFORMATION ENDPOINTS
# # =============================================================================

# @app.get("/api/system/info")
# async def get_system_info():
#     """Get comprehensive system information and capabilities"""
#     return {
#         "success": True,
#         "system": {
#             "name": "Complete Multi-Platform Social Media Automation System",
#             "version": "3.0.0",
#             "platforms": {
#                 "reddit": {
#                     "available": REDDIT_AUTOMATION_AVAILABLE and reddit_oauth_connector is not None,
#                     "features": ["auto_posting", "auto_replies", "manual_posting", "analytics"]
#                 },
#                 "youtube": {
#                     "available": YOUTUBE_AVAILABLE and youtube_connector is not None,
#                     "features": ["auto_upload", "shorts_generation", "analytics", "channel_management"]
#                 },
#                 "whatsapp": {
#                     "available": WHATSAPP_AVAILABLE,
#                     "features": ["messaging", "auto_replies", "campaigns", "business_hours"]
#                 },
#                 "instagram": {
#                     "available": False,  # TODO: Implement
#                     "features": ["coming_soon"]
#                 },
#                 "facebook": {
#                     "available": False,  # TODO: Implement
#                     "features": ["coming_soon"]
#                 }
#             },
#             "features": {
#                 "multi_user_auth": True,
#                 "individual_platform_connections": True,
#                 "per_user_automation": True,
#                 "real_ai_content": not isinstance(ai_service, MockAIService),
#                 "cross_platform_analytics": True,
#                 "unified_dashboard": True,
#                 "persistent_database": MULTIUSER_DB_AVAILABLE and not isinstance(database_manager, MockMultiUserDatabase)
#             },
#             "services": {
#                 "ai_primary": {
#                     "type": type(ai_service).__name__ if ai_service else None,
#                     "real": not isinstance(ai_service, MockAIService) if ai_service else False
#                 },
#                 "ai_secondary": {
#                     "type": type(ai_service2).__name__ if ai_service2 else None,
#                     "available": AI_SERVICE2_AVAILABLE
#                 },
#                 "database_primary": {
#                     "type": type(database_manager).__name__ if database_manager else None,
#                     "real": MULTIUSER_DB_AVAILABLE and not isinstance(database_manager, MockMultiUserDatabase)
#                 },
#                 "database_youtube": {
#                     "type": type(youtube_database_manager).__name__ if youtube_database_manager else None,
#                     "available": YOUTUBE_DATABASE_AVAILABLE
#                 }
#             }
#         },
#         "timestamp": datetime.now().isoformat()
#     }

# # =============================================================================
# # OPTIONS HANDLER FOR CORS
# # =============================================================================

# @app.options("/{path:path}")
# async def options_handler(request: Request):
#     """Handle preflight OPTIONS requests"""
#     return Response(
#         content="",
#         status_code=200,
#         headers={
#             "Access-Control-Allow-Origin": "*",
#             "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
#             "Access-Control-Allow-Headers": "Content-Type, Authorization, X-User-Token",
#             "Access-Control-Max-Age": "3600"
#         }
#     )

# # =============================================================================
# # APPLICATION STARTUP
# # =============================================================================

# if __name__ == "__main__":
#     PORT = int(os.getenv("PORT", 10000))
#     logger.info(f"Starting Complete Multi-Platform Social Media Automation System on port {PORT}")
    
#     uvicorn.run(
#         "mainALL:app",
#         host="0.0.0.0",
#         port=PORT,
#         reload=False,  # Set to True for development
#         log_level="info"
#     )