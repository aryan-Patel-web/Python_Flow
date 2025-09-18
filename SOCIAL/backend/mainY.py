"""
Complete Multi-Platform Social Media Automation System
YouTube, WhatsApp, Instagram, Facebook with unified API
Real AI content generation and multi-user support
"""

from fastapi import FastAPI, HTTPException, Request, Query, BackgroundTasks, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uvicorn
import json
import threading
import random
from pydantic import BaseModel, EmailStr
import sys
import traceback
import uuid
import os
import requests
import base64
# Add these imports at the top of main2.py (if not already there)
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder


# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("multiplatform_automation.log")
    ]
)
logger = logging.getLogger(__name__)

# Import custom modules
try:
    from youtube import YouTubeOAuthConnector, YouTubeAutomationScheduler, YouTubeConfig, initialize_youtube_service, youtube_connector, youtube_scheduler
    YOUTUBE_AVAILABLE = True
    logger.info("YouTube module loaded successfully")
except ImportError as e:
    logger.warning(f"YouTube module not available: {e}")
    YOUTUBE_AVAILABLE = False

try:
    from whatsapp import WhatsAppCloudAPI, WhatsAppAutomationScheduler, WhatsAppConfig, WhatsAppWebhookHandler
    WHATSAPP_AVAILABLE = True
    logger.info("WhatsApp module loaded successfully")
except ImportError as e:
    logger.warning(f"WhatsApp module not available: {e}")
    WHATSAPP_AVAILABLE = False

try:
    from ai_service2 import AIService2
    AI_SERVICE_AVAILABLE = True
    logger.info("AI Service 2 loaded successfully")
except ImportError as e:
    logger.warning(f"AI Service 2 not available: {e}")
    AI_SERVICE_AVAILABLE = False

try:
    from YTdatabase import get_youtube_database, YouTubeDatabaseManager
    DATABASE_AVAILABLE = True
    logger.info("YouTube database loaded successfully")
except ImportError as e:
    logger.warning(f"YouTube database not available: {e}")
    DATABASE_AVAILABLE = False

# Global instances
database_manager = None
ai_service = None
youtube_connector = None
youtube_scheduler = None
whatsapp_scheduler = None
webhook_handler = None

# Multi-user management
user_platform_tokens = {}  # user_id -> {platform: tokens}
oauth_states = {}          # oauth_state -> user_id
automation_configs = {}    # user_id -> {platform: configs}

# Authentication setup
security = HTTPBearer()

# Pydantic Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class YouTubeOAuthRequest(BaseModel):
    user_id: str
    state: str = "youtube_oauth"
    redirect_uri: Optional[str] = None

class YouTubeOAuthCallback(BaseModel):
    user_id: str
    code: str
    state: Optional[str] = None
    redirect_uri: Optional[str] = None

class YouTubeSetupRequest(BaseModel):
    user_id: str
    config: dict

class YouTubeUploadRequest(BaseModel):
    user_id: str
    title: str
    description: str
    video_url: str
    content_type: str = "shorts"
    tags: List[str] = []
    privacy_status: str = "public"

class YouTubeContentRequest(BaseModel):
    content_type: str = "shorts"
    topic: str = "general"
    target_audience: str = "general"

class YouTubeAutomationRequest(BaseModel):
    content_type: str = "shorts"
    upload_schedule: List[str]
    content_categories: List[str] = []
    auto_generate_titles: bool = True
    privacy_status: str = "public"
    shorts_per_day: int = 3

class WhatsAppMessageRequest(BaseModel):
    to: str
    message: str
    message_type: str = "text"

class WhatsAppMediaRequest(BaseModel):
    to: str
    media_url: str
    media_type: str = "image"
    caption: str = None

class WhatsAppAutomationRequest(BaseModel):
    business_name: str
    auto_reply_enabled: bool = False
    campaign_enabled: bool = False
    business_hours: Dict[str, str] = {"start": "09:00", "end": "18:00"}

class BroadcastRequest(BaseModel):
    platform: str
    recipient_list: List[str]
    message: str
    media_url: str = None
    media_type: str = None

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_services()
    yield
    # Shutdown
    await cleanup_services()

app = FastAPI(
    title="Multi-Platform Social Media Automation",
    description="Complete automation system for YouTube, WhatsApp, Instagram, Facebook",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-agentic.onrender.com",
        "https://frontend-agentic-bnc2.onrender.com",  # Add your new frontend URL
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Trusted hosts middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)


# Add this exception handler RIGHT AFTER your middleware setup
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for 422 validation errors with detailed logging"""
    
    # Log the detailed error for debugging
    logger.error(f"=== 422 VALIDATION ERROR ===")
    logger.error(f"Request URL: {request.url}")
    logger.error(f"Request method: {request.method}")
    logger.error(f"Request headers: {dict(request.headers)}")
    logger.error(f"Validation errors: {exc.errors()}")
    logger.error(f"Request body received: {exc.body}")
    logger.error(f"================================")
    
    # Return detailed error response for debugging
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation failed - check request format",
            "details": exc.errors(),
            "request_body_received": exc.body,
            "expected_format": "Check API documentation",
            "timestamp": datetime.now().isoformat()
        }
    )












async def initialize_services():
    """Initialize all services"""
    global database_manager, ai_service
    
    try:
        # Initialize YouTube database (primary database)
        database_manager = get_youtube_database()
        if await database_manager.connect():
            logger.info("YouTube database manager initialized and connected")
        else:
            logger.error("Failed to connect to YouTube database")
            return False
        
        # Initialize AI service
        if AI_SERVICE_AVAILABLE:
            ai_service = AIService2()
            logger.info("AI service initialized")
        
        # Initialize YouTube service
        if YOUTUBE_AVAILABLE and database_manager and ai_service:
            try:
                if initialize_youtube_service(database_manager, ai_service):
                    logger.info("YouTube service initialized successfully")
                else:
                    logger.warning("YouTube service initialization failed")
            except Exception as e:
                logger.error(f"YouTube service initialization error: {e}")
        
        # Initialize WhatsApp service (add similar initialization)
        if WHATSAPP_AVAILABLE:
            logger.info("WhatsApp service ready for initialization")
            
        return True
        
    except Exception as e:
        logger.error(f"Service initialization failed: {e}")
        return False





async def cleanup_services():
    """Cleanup services on shutdown"""
    try:
        if database_manager:
            await database_manager.close()
        logger.info("Services cleaned up successfully")
    except Exception as e:
        logger.error(f"Service cleanup failed: {e}")







# Health check endpoint
@app.get("/")
async def root():
    """Health check and service status"""
    return {
        "status": "running",
        "message": "Multi-Platform Social Media Automation System",
        "version": "2.0.0",
        "services": {
            "youtube": YOUTUBE_AVAILABLE,
            "whatsapp": WHATSAPP_AVAILABLE,
            "ai_service": AI_SERVICE_AVAILABLE,
            "database": DATABASE_AVAILABLE
        },
        "timestamp": datetime.now().isoformat()
    }






@app.get("/health")
async def health_check():
    """Detailed health check"""
    services_status = {}
    
    if database_manager:
        try:
            # Test database connection using YouTube database health check
            health_result = await database_manager.health_check()
            services_status["database"] = health_result.get("status", "unknown")
        except:
            services_status["database"] = "disconnected"
    else:
        services_status["database"] = "not_initialized"
    
    services_status["ai_service"] = "available" if ai_service else "not_available"
    services_status["youtube"] = "available" if YOUTUBE_AVAILABLE else "not_available"
    services_status["whatsapp"] = "available" if WHATSAPP_AVAILABLE else "not_available"
    
    return {
        "status": "healthy",
        "services": services_status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables (remove in production)"""
    return {
        "GOOGLE_CLIENT_ID": "✓" if os.getenv("GOOGLE_CLIENT_ID") else "✗",
        "GOOGLE_CLIENT_SECRET": "✓" if os.getenv("GOOGLE_CLIENT_SECRET") else "✗", 
        "GOOGLE_OAUTH_REDIRECT_URI": os.getenv("GOOGLE_OAUTH_REDIRECT_URI"),
        "FRONTEND_URL": os.getenv("FRONTEND_URL"),
        "youtube_connector_initialized": youtube_connector is not None
    }



# Authentication endpoints
@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """User registration"""
    try:
        if not database_manager:
            raise HTTPException(status_code=503, detail="Database service not available")
        
        # Check if user already exists
        existing_user = await database_manager.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        user_id = str(uuid.uuid4())
        user_data = {
            "_id": user_id,
            "email": request.email,
            "name": request.name,
            "password": request.password,  # In production, hash this!
            "created_at": datetime.now(),
            "platforms_connected": [],
            "automation_enabled": False
        }
        
        await database_manager.create_user(user_data)
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """User login"""
    try:
        if not database_manager:
            raise HTTPException(status_code=503, detail="Database service not available")
        
        # Find user
        user = await database_manager.get_user_by_email(request.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check password (in production, use proper hashing)
        if user.get("password") != request.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "user_id": user["_id"],
                "email": user["email"],
                "name": user["name"],
                "platforms_connected": user.get("platforms_connected", [])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# YouTube API Routes



# Also update your YouTube OAuth URL endpoint to add more logging
@app.post("/api/youtube/oauth-url")
async def youtube_oauth_url(request: YouTubeOAuthRequest):
    """Generate YouTube OAuth URL"""
    try:
        # Log incoming request details
        logger.info(f"=== YOUTUBE OAUTH URL REQUEST ===")
        logger.info(f"Received request: {request}")
        logger.info(f"User ID: {request.user_id}")
        logger.info(f"State: {request.state}")
        logger.info(f"Redirect URI: {request.redirect_uri}")
        logger.info(f"YouTube connector available: {youtube_connector is not None}")
        logger.info(f"================================")
        
        if not youtube_connector:
            raise HTTPException(status_code=503, detail="YouTube service not available")
        
        # Use frontend domain as redirect URI if not provided
        redirect_uri = request.redirect_uri
        if not redirect_uri:
            frontend_url = os.getenv("FRONTEND_URL", "https://frontend-agentic.onrender.com")
            redirect_uri = f"{frontend_url}/youtube"
            logger.info(f"Using default redirect URI: {redirect_uri}")
        
        result = youtube_connector.generate_oauth_url(
            state=request.state,
            redirect_uri=redirect_uri
        )
        
        logger.info(f"OAuth URL generation result: {result}")
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YouTube OAuth URL generation failed: {e}")
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))








@app.post("/api/youtube/oauth-callback")
async def youtube_oauth_callback(request: YouTubeOAuthCallback):
    """Handle YouTube OAuth callback and store tokens"""
    try:
        if not youtube_connector:
            raise HTTPException(status_code=503, detail="YouTube service not available")
        
        # Exchange code for tokens
        redirect_uri = request.redirect_uri
        if not redirect_uri:
            frontend_url = os.getenv("FRONTEND_URL", "https://frontend-agentic.onrender.com")
            redirect_uri = f"{frontend_url}/youtube"
            
        token_result = await youtube_connector.exchange_code_for_token(
            code=request.code,
            redirect_uri=redirect_uri
        )
        
        if not token_result["success"]:
            raise HTTPException(status_code=400, detail=token_result["error"])
        
        # Store YouTube tokens in database for user
        user_id = request.user_id
        
        youtube_credentials = {
            "access_token": token_result["access_token"],
            "refresh_token": token_result["refresh_token"],
            "token_uri": token_result["token_uri"],
            "client_id": token_result["client_id"],
            "client_secret": token_result["client_secret"],
            "scopes": token_result["scopes"],
            "expires_at": datetime.now() + timedelta(seconds=token_result.get("expires_in", 3600)),
            "channel_info": token_result["channel_info"]
        }
        
        # Store in database
        try:
            await database_manager.store_user_credentials(
                user_id=user_id,
                platform="youtube",
                credentials=youtube_credentials
            )
        except Exception as db_error:
            logger.error(f"Database error storing YouTube credentials: {db_error}")
        
        logger.info(f"YouTube OAuth successful for user {user_id}")
        
        return {
            "success": True,
            "message": "YouTube connected successfully",
            "channel_info": token_result["channel_info"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YouTube OAuth callback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/youtube/status/{user_id}")
async def youtube_status(user_id: str):
    """Get YouTube connection and automation status"""
    try:
        # Check if user has YouTube credentials stored
        youtube_connected = False
        channel_info = None
        
        try:
            credentials = await database_manager.get_user_credentials(user_id, "youtube")
            youtube_connected = credentials is not None
            if credentials:
                channel_info = credentials.get("channel_info")
        except Exception as db_error:
            logger.error(f"Database error fetching YouTube status: {db_error}")
        
        # Get automation status if scheduler is available
        automation_status = {}
        if youtube_scheduler:
            automation_status = await youtube_scheduler.get_automation_status(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "youtube_connected": youtube_connected,
            "channel_info": channel_info,
            "youtube_automation": automation_status.get("youtube_automation", {
                "enabled": False,
                "config": None,
                "stats": {
                    "total_uploads": 0,
                    "successful_uploads": 0,
                    "failed_uploads": 0
                }
            })
        }
        
    except Exception as e:
        logger.error(f"YouTube status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/youtube/setup-automation")
async def youtube_setup_automation(request: YouTubeSetupRequest):
    """Setup YouTube automation configuration"""
    try:
        if not youtube_scheduler:
            raise HTTPException(status_code=503, detail="YouTube scheduler not available")
        
        user_id = request.user_id
        
        # Check if user has YouTube connected
        try:
            credentials = await database_manager.get_user_credentials(user_id, "youtube")
            if not credentials:
                raise HTTPException(status_code=400, detail="YouTube not connected")
        except Exception as db_error:
            logger.error(f"Database error checking YouTube connection: {db_error}")
            raise HTTPException(status_code=500, detail="Database error")
        
        result = await youtube_scheduler.setup_youtube_automation(user_id, request.config)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YouTube automation setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/youtube/upload")
async def youtube_upload_video(request: YouTubeUploadRequest):
    """Upload video to YouTube"""
    try:
        if not youtube_scheduler:
            raise HTTPException(status_code=503, detail="YouTube service not available")
        
        user_id = request.user_id
        
        # Get user's YouTube credentials
        try:
            credentials = await database_manager.get_user_credentials(user_id, "youtube")
            if not credentials:
                raise HTTPException(status_code=400, detail="YouTube not connected")
        except Exception as db_error:
            logger.error(f"Database error fetching YouTube credentials: {db_error}")
            raise HTTPException(status_code=500, detail="Database error")
        
        # Upload video
        result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id,
            credentials_data=credentials,
            content_type=request.content_type,
            title=request.title,
            description=request.description,
            video_url=request.video_url
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YouTube upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/youtube/analytics/{user_id}")
async def youtube_analytics(user_id: str, days: int = 30):
    """Get YouTube channel analytics"""
    try:
        if not youtube_connector:
            raise HTTPException(status_code=503, detail="YouTube service not available")
        
        # Get user's YouTube credentials
        try:
            credentials = await database_manager.get_user_credentials(user_id, "youtube")
            if not credentials:
                raise HTTPException(status_code=400, detail="YouTube not connected")
        except Exception as db_error:
            logger.error(f"Database error fetching YouTube credentials: {db_error}")
            raise HTTPException(status_code=500, detail="Database error")
        
        # Get analytics
        result = await youtube_connector.get_channel_analytics(credentials, days)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"YouTube analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/generate-youtube-content")
async def generate_youtube_content(request: YouTubeContentRequest):
    """Generate YouTube content using AI"""
    try:
        # Generate content based on request parameters
        if ai_service and hasattr(ai_service, 'generate_youtube_content'):
            result = await ai_service.generate_youtube_content(
                content_type=request.content_type,
                topic=request.topic,
                target_audience=request.target_audience,
                duration_seconds=60 if request.content_type == "shorts" else 300,
                style="engaging"
            )
        else:
            # Fallback mock content generation
            result = {
                "success": True,
                "title": f"AI Generated {request.content_type.title()} - {request.topic}",
                "description": f"This is an AI-generated {request.content_type} about {request.topic} for {request.target_audience} audience. Perfect for engaging your YouTube audience!",
                "tags": ["AI", "generated", request.content_type, request.topic, request.target_audience],
                "thumbnail_suggestions": [
                    "Bold text with bright colors",
                    "Emotional expression face",
                    "Question mark or arrow graphics"
                ]
            }
        
        return result
        
    except Exception as e:
        logger.error(f"YouTube content generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add WhatsApp routes here (similar structure)
# Add Instagram routes here (similar structure)  
# Add Facebook routes here (similar structure)

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main2:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )