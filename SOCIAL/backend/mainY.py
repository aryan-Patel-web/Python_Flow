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
    from youtube import (
        initialize_youtube_service, 
        get_youtube_connector, 
        get_youtube_scheduler,
        get_youtube_database
    )
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












# Updated service initialization
async def initialize_services():
    """Initialize all services with robust error handling"""
    global database_manager, ai_service
    
    try:
        logger.info("Starting service initialization...")
        
        # Check required environment variables
        required_env_vars = [
            'GOOGLE_CLIENT_ID',
            'GOOGLE_CLIENT_SECRET', 
            'GOOGLE_OAUTH_REDIRECT_URI',
            'MONGODB_URI'
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            return False
            
        logger.info("Environment variables check passed")
        
        # Initialize AI service
        if AI_SERVICE_AVAILABLE:
            try:
                ai_service = AIService2()
                logger.info("AI service initialized")
            except Exception as e:
                logger.error(f"AI service initialization error: {e}")
                ai_service = None
        else:
            logger.warning("AI service not available")
            ai_service = None
        
        # Initialize YouTube service with its own database
        if YOUTUBE_AVAILABLE:
            try:
                logger.info("Initializing YouTube service...")
                success = await initialize_youtube_service(ai_service=ai_service)
                
                if success:
                    database_manager = get_youtube_database()
                    logger.info("YouTube service initialization completed successfully")
                else:
                    logger.error("YouTube service initialization failed")
                    return False
                    
            except Exception as e:
                logger.error(f"YouTube service initialization failed: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return False
        else:
            logger.error("YouTube module not available - check imports")
            return False
            
        logger.info("All services initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Critical service initialization failure: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
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






# Add debug endpoints
@app.get("/debug/services")
async def debug_services():
    """Debug endpoint to check service status"""
    youtube_connector = get_youtube_connector()
    youtube_scheduler = get_youtube_scheduler()
    
    return {
        "youtube_connector": youtube_connector is not None,
        "youtube_scheduler": youtube_scheduler is not None,
        "database_manager": database_manager is not None,
        "ai_service": ai_service is not None,
        "YOUTUBE_AVAILABLE": YOUTUBE_AVAILABLE,
        "AI_SERVICE_AVAILABLE": AI_SERVICE_AVAILABLE,
        "DATABASE_AVAILABLE": DATABASE_AVAILABLE,
        "env_vars": {
            "GOOGLE_CLIENT_ID": "✓" if os.getenv("GOOGLE_CLIENT_ID") else "✗",
            "GOOGLE_CLIENT_SECRET": "✓" if os.getenv("GOOGLE_CLIENT_SECRET") else "✗",
            "GOOGLE_OAUTH_REDIRECT_URI": os.getenv("GOOGLE_OAUTH_REDIRECT_URI"),
            "MONGODB_URI": "✓" if os.getenv("MONGODB_URI") else "✗",
            "FRONTEND_URL": os.getenv("FRONTEND_URL")
        }
    }





@app.get("/debug/user/{email}")
async def debug_user(email: str):
    """Debug endpoint to check user data (REMOVE IN PRODUCTION)"""
    try:
        if not database_manager:
            return {"error": "Database not available"}
        
        user = await database_manager.get_user_by_email(email)
        if user:
            # Return user data without password for security
            return {
                "found": True,
                "user_id": user.get("_id"),
                "email": user.get("email"),
                "name": user.get("name"),
                "has_password": "password" in user,
                "password_length": len(user.get("password", "")) if user.get("password") else 0,
                "created_at": user.get("created_at"),
                "platforms_connected": user.get("platforms_connected", [])
            }
        else:
            return {"found": False}
            
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


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




@app.get("/debug/users")
async def debug_users():
    """Debug endpoint to list recent users"""
    try:
        if not database_manager:
            return {"error": "Database not available"}
        
        # Get recent users (last 10)
        users_cursor = database_manager.users_collection.find({}).sort("created_at", -1).limit(10)
        users = []
        
        async for user in users_cursor:
            users.append({
                "user_id": user.get("_id"),
                "email": user.get("email"),
                "name": user.get("name"),
                "created_at": str(user.get("created_at")),
                "has_password": "password" in user
            })
        
        return {"users": users, "count": len(users)}
        
    except Exception as e:
        return {"error": str(e)}




# Authentication endpoints


@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """User registration that returns user data for auto-login"""
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
            "password": request.password,
            "created_at": datetime.now(),
            "platforms_connected": [],
            "automation_enabled": False
        }
        
        success = await database_manager.create_user(user_data)
        
        if success:
            # Return user data like login does for auto-authentication
            return {
                "success": True,
                "message": "User registered successfully",
                "user": {
                    "user_id": user_id,
                    "email": request.email,
                    "name": request.name,
                    "platforms_connected": []
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Registration failed")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))





@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """User login with detailed debugging"""
    try:
        logger.info(f"Login attempt for email: {request.email}")
        
        if not database_manager:
            raise HTTPException(status_code=503, detail="Database service not available")
        
        # Find user with detailed logging
        user = await database_manager.get_user_by_email(request.email)
        logger.info(f"User lookup result: {'Found' if user else 'Not found'}")
        
        if not user:
            logger.warning(f"No user found with email: {request.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Log user data structure (without password)
        user_info = {k: v for k, v in user.items() if k != 'password'}
        logger.info(f"User data: {user_info}")
        
        # Check if password field exists
        stored_password = user.get("password")
        if not stored_password:
            logger.error(f"No password stored for user: {request.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Compare passwords (add detailed logging)
        logger.info(f"Password comparison - Provided length: {len(request.password)}, Stored length: {len(stored_password)}")
        
        if stored_password != request.password:
            logger.warning(f"Password mismatch for user: {request.email}")
            logger.info(f"Provided password: '{request.password}'")
            logger.info(f"Stored password: '{stored_password}'")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        logger.info(f"Login successful for user: {request.email}")
        
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
        logger.error(f"Login failed with exception: {e}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


# YouTube API Routes







# =============================================================================
# YOUTUBE OAUTH FIX - UPDATE THESE ENDPOINTS IN YOUR mainALL.py
# =============================================================================

@app.post("/api/youtube/oauth-url")
async def youtube_oauth_url(request: YouTubeOAuthRequest):
    """Generate YouTube OAuth URL - FIXED VERSION"""
    try:
        logger.info(f"YouTube OAuth request for user_id: {request.user_id}")
        
        if not youtube_connector:
            raise HTTPException(
                status_code=503, 
                detail="YouTube service not initialized"
            )
        
        # FIXED: Use BACKEND redirect URI, not frontend
        redirect_uri = request.redirect_uri
        if not redirect_uri:
            # Point to BACKEND callback endpoint
            backend_url = os.getenv("BACKEND_URL", "https://agentic-u5lx.onrender.com")
            redirect_uri = f"{backend_url}/api/youtube/oauth-callback"
            logger.info(f"Using backend redirect URI: {redirect_uri}")
        
        result = youtube_connector.generate_oauth_url(
            state=f"{request.state}_{request.user_id}",  # Include user_id in state
            redirect_uri=redirect_uri
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YouTube OAuth URL generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/youtube/oauth-callback")
async def youtube_oauth_callback_get(code: str, state: str):
    """Handle YouTube OAuth callback - GET version for Google redirect"""
    try:
        logger.info(f"YouTube OAuth callback received - state: {state}, code: {code[:20]}...")
        
        # Extract user_id from state
        if "_" in state:
            state_parts = state.split("_")
            if len(state_parts) >= 2:
                user_id = state_parts[1]  # Extract user_id from state
            else:
                logger.error(f"Invalid state format: {state}")
                return RedirectResponse(
                    url="https://frontend-agentic-bnc2.onrender.com/?error=invalid_state",
                    status_code=302
                )
        else:
            logger.error(f"State missing user_id: {state}")
            return RedirectResponse(
                url="https://frontend-agentic-bnc2.onrender.com/?error=missing_user_id",
                status_code=302
            )
        
        if not youtube_connector:
            logger.error("YouTube connector not available")
            return RedirectResponse(
                url="https://frontend-agentic-bnc2.onrender.com/?error=service_unavailable",
                status_code=302
            )
        
        # Use backend URL for token exchange
        backend_url = os.getenv("BACKEND_URL", "https://agentic-u5lx.onrender.com")
        redirect_uri = f"{backend_url}/api/youtube/oauth-callback"
            
        token_result = await youtube_connector.exchange_code_for_token(
            code=code,
            redirect_uri=redirect_uri
        )
        
        if not token_result["success"]:
            logger.error(f"Token exchange failed: {token_result.get('error')}")
            return RedirectResponse(
                url=f"https://frontend-agentic-bnc2.onrender.com/?error=token_exchange_failed&details={token_result.get('error')}",
                status_code=302
            )
        
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
            if database_manager and hasattr(database_manager, 'store_youtube_credentials'):
                await database_manager.store_youtube_credentials(
                    user_id=user_id,
                    credentials=youtube_credentials
                )
                logger.info(f"YouTube credentials stored in primary database for user {user_id}")
            elif youtube_database_manager:
                await youtube_database_manager.store_youtube_credentials(
                    user_id=user_id,
                    credentials=youtube_credentials
                )
                logger.info(f"YouTube credentials stored in YouTube database for user {user_id}")
            else:
                logger.warning("No database available to store YouTube credentials")
        except Exception as db_error:
            logger.error(f"Database storage failed: {db_error}")
        
        # Store in memory
        user_youtube_tokens[user_id] = youtube_credentials
        
        channel_title = token_result["channel_info"].get("title", "Unknown Channel")
        logger.info(f"YouTube OAuth successful for user {user_id} - Channel: {channel_title}")
        
        # Redirect to frontend with success
        return RedirectResponse(
            url=f"https://frontend-agentic-bnc2.onrender.com/youtube?youtube_connected=true&channel={channel_title}&user_id={user_id}",
            status_code=302
        )
        
    except Exception as e:
        logger.error(f"YouTube OAuth callback failed: {e}")
        logger.error(traceback.format_exc())
        return RedirectResponse(
            url="https://frontend-agentic-bnc2.onrender.com/?error=oauth_callback_failed",
            status_code=302
        )


# ALSO ADD THIS ENVIRONMENT VARIABLE CHECK
@app.get("/api/debug/youtube-oauth-config")
async def debug_youtube_oauth_config():
    """Debug YouTube OAuth configuration"""
    return {
        "google_client_id": "✓" if os.getenv("GOOGLE_CLIENT_ID") else "✗",
        "google_client_secret": "✓" if os.getenv("GOOGLE_CLIENT_SECRET") else "✗",
        "backend_url": os.getenv("BACKEND_URL", "https://agentic-u5lx.onrender.com"),
        "frontend_url": os.getenv("FRONTEND_URL", "https://frontend-agentic-bnc2.onrender.com"),
        "expected_redirect_uri": f"{os.getenv('BACKEND_URL', 'https://agentic-u5lx.onrender.com')}/api/youtube/oauth-callback",
        "youtube_connector_available": youtube_connector is not None
    }










@app.get("/api/youtube/status/{user_id}")
async def youtube_status(user_id: str):
    """Get YouTube connection and automation status with persistent token check"""
    try:
        logger.info(f"Checking YouTube status for user: {user_id}")
        
        # Check if user has YouTube credentials stored
        youtube_connected = False
        channel_info = None
        credentials_valid = False
        
        try:
            credentials = await database_manager.get_youtube_credentials(user_id)
            if credentials and credentials.get("is_active"):
                youtube_connected = True
                channel_info = credentials.get("channel_info")
                
                # Check if token is still valid
                expires_at = credentials.get("expires_at")
                if expires_at and isinstance(expires_at, datetime):
                    credentials_valid = datetime.now() < expires_at
                else:
                    credentials_valid = True  # Assume valid if no expiry
                
                logger.info(f"YouTube credentials found for user {user_id}, valid: {credentials_valid}")
            else:
                logger.info(f"No active YouTube credentials found for user {user_id}")
        except Exception as db_error:
            logger.error(f"Database error fetching YouTube status: {db_error}")
        
        # Get automation status if scheduler is available
        automation_status = {}
        youtube_scheduler = get_youtube_scheduler()
        if youtube_scheduler and youtube_connected:
            automation_status = await youtube_scheduler.get_automation_status(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "youtube_connected": youtube_connected and credentials_valid,
            "channel_info": channel_info,
            "connected_at": credentials.get("created_at") if credentials else None,
            "last_updated": credentials.get("updated_at") if credentials else None,
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

@app.post("/api/youtube/disconnect/{user_id}")
async def youtube_disconnect(user_id: str):
    """Disconnect YouTube and remove stored credentials"""
    try:
        success = await database_manager.revoke_youtube_access(user_id)
        
        if success:
            return {
                "success": True,
                "message": "YouTube disconnected successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to disconnect YouTube")
            
    except Exception as e:
        logger.error(f"YouTube disconnect failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


from youtube import get_youtube_scheduler

@app.post("/api/youtube/setup-automation")
async def youtube_setup_automation(request: YouTubeSetupRequest):
    """Setup YouTube automation configuration"""
    try:
        # Get the initialized scheduler
        youtube_scheduler = get_youtube_scheduler()
        
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


@app.get("/debug/mongodb")
async def test_mongodb():
    """Test MongoDB connection"""
    try:
        if database_manager:
            health = await database_manager.health_check()
            return {
                "status": "success",
                "database_health": health,
                "mongodb_uri_set": "✓" if os.getenv("MONGODB_URI") else "✗"
            }
        else:
            return {"status": "failed", "error": "Database manager not initialized"}
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "type": type(e).__name__
        }



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