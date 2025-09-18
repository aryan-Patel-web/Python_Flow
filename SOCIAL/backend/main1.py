"""
Clean Facebook & Instagram Automation Backend
Properly organized with all imports, error-free implementation
"""

# Standard library imports
import asyncio
import json
import logging
import os
import sys
import threading
import time
import traceback
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Third-party imports
import bcrypt
import jwt
import requests
import schedule
import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Header, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

# Load environment variables first
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Try to import custom modules
try:
    from ai_service import AIService
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

try:
    from database import MultiUserDatabaseManager
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Pydantic Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AutoPostingRequest(BaseModel):
    platform: str
    domain: str
    business_type: str
    business_description: str = ""
    target_audience: str = "indian_users"
    language: str = "en"
    content_style: str = "engaging"
    posts_per_day: int = 3
    posting_times: List[str] = []

class ManualPostRequest(BaseModel):
    platform: str
    title: str
    content: str
    page_id: str = ""
    image_url: str = ""

class TestPostRequest(BaseModel):
    platform: str
    domain: str
    business_type: str
    business_description: str = ""
    target_audience: str = "indian_users"
    content_style: str = "engaging"

# Facebook OAuth Connector
class FacebookOAuthConnector:
    def __init__(self, app_id: str, app_secret: str, redirect_uri: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.is_configured = bool(app_id and app_secret)
        
    def generate_oauth_url(self, state: str) -> Dict[str, Any]:
        if not self.is_configured:
            return {"success": False, "error": "Facebook credentials not configured"}
        
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'scope': 'pages_manage_posts,pages_read_engagement,public_profile,email',
            'response_type': 'code'
        }
        
        auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?" + "&".join([f"{k}={v}" for k, v in params.items()])
        return {"success": True, "authorization_url": auth_url, "state": state}
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        try:
            token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'redirect_uri': self.redirect_uri,
                'code': code
            }
            
            response = requests.post(token_url, data=params, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                
                # Get user info
                user_response = requests.get(
                    f"https://graph.facebook.com/v18.0/me?fields=id,name,email&access_token={access_token}",
                    timeout=15
                )
                user_info = user_response.json() if user_response.status_code == 200 else {}
                
                # Get pages
                pages_response = requests.get(
                    f"https://graph.facebook.com/v18.0/me/accounts?fields=id,name,access_token&access_token={access_token}",
                    timeout=15
                )
                pages = pages_response.json().get('data', []) if pages_response.status_code == 200 else []
                
                return {
                    "success": True,
                    "access_token": access_token,
                    "expires_in": token_data.get('expires_in', 3600),
                    "user_info": user_info,
                    "pages": pages
                }
            else:
                return {"success": False, "error": f"Token exchange failed: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"OAuth error: {str(e)}"}
    
    async def post_content(self, access_token: str, page_id: str, title: str, content: str, image_url: str = "") -> Dict[str, Any]:
        try:
            post_data = {
                'message': f"{title}\n\n{content}",
                'access_token': access_token
            }
            
            if image_url:
                post_data['link'] = image_url
            
            url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
            response = requests.post(url, data=post_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "post_id": result.get('id', ''),
                    "post_url": f"https://facebook.com/{result.get('id', '')}",
                    "message": "Posted to Facebook successfully"
                }
            else:
                return {"success": False, "error": f"Facebook API error: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"Posting failed: {str(e)}"}

# Instagram OAuth Connector
class InstagramOAuthConnector:
    def __init__(self, app_id: str, app_secret: str, redirect_uri: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.is_configured = bool(app_id and app_secret)
        
    def generate_oauth_url(self, state: str) -> Dict[str, Any]:
        if not self.is_configured:
            return {"success": False, "error": "Instagram credentials not configured"}
        
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'user_profile,user_media',
            'response_type': 'code',
            'state': state
        }
        
        auth_url = f"https://api.instagram.com/oauth/authorize?" + "&".join([f"{k}={v}" for k, v in params.items()])
        return {"success": True, "authorization_url": auth_url, "state": state}
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        try:
            # Get short-lived token
            token_url = "https://api.instagram.com/oauth/access_token"
            data = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri,
                'code': code
            }
            
            response = requests.post(token_url, data=data, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                short_token = token_data.get('access_token')
                
                # Exchange for long-lived token
                long_token_url = "https://graph.instagram.com/access_token"
                long_params = {
                    'grant_type': 'ig_exchange_token',
                    'client_secret': self.app_secret,
                    'access_token': short_token
                }
                
                long_response = requests.get(long_token_url, params=long_params, timeout=30)
                
                if long_response.status_code == 200:
                    long_data = long_response.json()
                    access_token = long_data.get('access_token')
                    
                    # Get user info
                    user_response = requests.get(
                        f"https://graph.instagram.com/me?fields=id,username,account_type&access_token={access_token}",
                        timeout=15
                    )
                    user_info = user_response.json() if user_response.status_code == 200 else {}
                    
                    return {
                        "success": True,
                        "access_token": access_token,
                        "expires_in": long_data.get('expires_in', 5184000),
                        "user_info": user_info
                    }
                else:
                    return {"success": False, "error": f"Long-lived token failed: {long_response.text}"}
            else:
                return {"success": False, "error": f"Token exchange failed: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"OAuth error: {str(e)}"}

# Mock Classes for Development
class MockAIService:
    async def generate_reddit_domain_content(self, **kwargs):
        return {
            "success": False,
            "error": "Mock AI Service",
            "title": f"Mock Title for {kwargs.get('domain', 'general')}",
            "content": "Configure MISTRAL_API_KEY or GROQ_API_KEY for real AI content",
            "ai_service": "mock"
        }
    
    async def test_ai_connection(self):
        return {"success": False, "error": "Mock AI", "primary_service": "mock"}

class MockDatabaseManager:
    def __init__(self):
        self.users = {}
        self.tokens = {}
        
    async def connect(self):
        return True
    
    async def disconnect(self):
        return True
    
    async def register_user(self, email: str, password: str, name: str):
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        token = jwt.encode({
            "user_id": user_id,
            "email": email,
            "name": name,
            "exp": datetime.utcnow() + timedelta(days=30)
        }, "secret", algorithm="HS256")
        
        self.users[user_id] = {"id": user_id, "email": email, "name": name}
        
        return {
            "success": True,
            "user_id": user_id,
            "email": email,
            "name": name,
            "token": token
        }
    
    async def login_user(self, email: str, password: str):
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        name = email.split('@')[0].title()
        token = jwt.encode({
            "user_id": user_id,
            "email": email,
            "name": name,
            "exp": datetime.utcnow() + timedelta(days=30)
        }, "secret", algorithm="HS256")
        
        return {
            "success": True,
            "user_id": user_id,
            "email": email,
            "name": name,
            "token": token
        }
    
    async def get_user_by_token(self, token: str):
        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
            return {
                "id": payload["user_id"],
                "email": payload["email"],
                "name": payload["name"]
            }
        except:
            return None

# Global Variables
database_manager = None
ai_service = None
facebook_connector = None
instagram_connector = None
user_facebook_tokens = {}
user_instagram_tokens = {}
oauth_states = {}

# Authentication
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        user = await database_manager.get_user_by_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")

# Application Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    global database_manager, ai_service, facebook_connector, instagram_connector
    
    logger.info("Starting Social Media Automation System...")
    
    # Initialize Database
    try:
        if DB_AVAILABLE:
            mongodb_uri = os.getenv("MONGODB_URI", "mongodb+srv://aryan:aryan@cluster0.7iquw6v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
            database_manager = MultiUserDatabaseManager(mongodb_uri)
            await database_manager.connect()
            logger.info("Real database connected")
        else:
            database_manager = MockDatabaseManager()
            await database_manager.connect()
            logger.info("Mock database connected")
    except Exception as e:
        logger.error(f"Database failed: {e}")
        database_manager = MockDatabaseManager()
        await database_manager.connect()
    
    # Initialize AI Service
    try:
        if AI_AVAILABLE:
            ai_service = AIService()
            test_result = await ai_service.test_ai_connection()
            if test_result.get("success"):
                logger.info(f"Real AI service ready: {test_result.get('primary_service')}")
            else:
                ai_service = MockAIService()
        else:
            ai_service = MockAIService()
            logger.info("AI service not available, using mock")
    except Exception as e:
        logger.error(f"AI service failed: {e}")
        ai_service = MockAIService()
    
    # Initialize Connectors
    facebook_connector = FacebookOAuthConnector(
        app_id=os.getenv('FB_APP_ID', '1802724037303404'),
        app_secret=os.getenv('FB_APP_SECRET', '88015121b7360d1f7f074f630a54a485'),
        redirect_uri=os.getenv('FB_REDIRECT_URI', 'https://agentic-u5lx.onrender.com/api/oauth/facebook/callback')
    )
    
    instagram_connector = InstagramOAuthConnector(
        app_id=os.getenv('INSTAGRAM_APP_ID', '1802724037303404'),
        app_secret=os.getenv('INSTAGRAM_APP_SECRET', 'instagram_secret_here'),
        redirect_uri=os.getenv('INSTAGRAM_REDIRECT_URI', 'https://agentic-u5lx.onrender.com/api/oauth/instagram/callback')
    )
    
    logger.info("Application startup completed")
    yield
    
    # Cleanup
    if database_manager:
        await database_manager.disconnect()

# Create FastAPI App
app = FastAPI(
    title="Social Media Automation API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Routes
@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Social Media Automation API",
        "platforms": ["facebook", "instagram"],
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "success": True,
        "status": "healthy",
        "services": {
            "database": database_manager is not None,
            "ai": ai_service is not None and not isinstance(ai_service, MockAIService),
            "facebook": facebook_connector is not None and facebook_connector.is_configured,
            "instagram": instagram_connector is not None and instagram_connector.is_configured
        },
        "timestamp": datetime.now().isoformat()
    }

# Authentication Routes
@app.post("/api/auth/register")
async def register_user(user_data: RegisterRequest):
    try:
        result = await database_manager.register_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login")
async def login_user(login_data: LoginRequest):
    try:
        result = await database_manager.login_user(
            email=login_data.email,
            password=login_data.password
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {"success": True, "user": current_user}

# OAuth Routes
@app.get("/api/oauth/{platform}/authorize")
async def oauth_authorize(platform: str, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        state = f"{platform}_{user_id}_{uuid.uuid4().hex[:12]}"
        oauth_states[state] = user_id
        
        if platform == "facebook":
            result = facebook_connector.generate_oauth_url(state)
        elif platform == "instagram":
            result = instagram_connector.generate_oauth_url(state)
        else:
            raise HTTPException(status_code=400, detail="Invalid platform")
        
        if result["success"]:
            return {"success": True, "redirect_url": result["authorization_url"], "state": state}
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/oauth/{platform}/callback")
async def oauth_callback(platform: str, code: str, state: str):
    try:
        user_id = oauth_states.get(state)
        if not user_id:
            return RedirectResponse(
                url="https://frontend-agentic-bnc2.onrender.com/?error=invalid_state",
                status_code=302
            )
        
        if platform == "facebook":
            result = await facebook_connector.exchange_code_for_token(code)
            if result["success"]:
                user_facebook_tokens[user_id] = {
                    "access_token": result["access_token"],
                    "facebook_username": result["user_info"].get("name", "Unknown"),
                    "pages": result.get("pages", [])
                }
        elif platform == "instagram":
            result = await instagram_connector.exchange_code_for_token(code)
            if result["success"]:
                user_instagram_tokens[user_id] = {
                    "access_token": result["access_token"],
                    "instagram_username": result["user_info"].get("username", "Unknown"),
                    "instagram_user_id": result["user_info"].get("id", "")
                }
        
        oauth_states.pop(state, None)
        
        if result["success"]:
            username = result["user_info"].get("name" if platform == "facebook" else "username", "User")
            return RedirectResponse(
                url=f"https://frontend-agentic-bnc2.onrender.com/?{platform}_connected=true&username={username}",
                status_code=302
            )
        else:
            return RedirectResponse(
                url=f"https://frontend-agentic-bnc2.onrender.com/?error={platform}_auth_failed",
                status_code=302
            )
    except Exception as e:
        return RedirectResponse(
            url="https://frontend-agentic-bnc2.onrender.com/?error=oauth_failed",
            status_code=302
        )

# Connection Status Routes
@app.get("/api/{platform}/connection-status")
async def get_connection_status(platform: str, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        if platform == "facebook":
            tokens = user_facebook_tokens.get(user_id)
            if tokens:
                return {
                    "success": True,
                    "connected": True,
                    "username": tokens.get("facebook_username"),
                    "pages": tokens.get("pages", [])
                }
        elif platform == "instagram":
            tokens = user_instagram_tokens.get(user_id)
            if tokens:
                return {
                    "success": True,
                    "connected": True,
                    "username": tokens.get("instagram_username")
                }
        
        return {"success": True, "connected": False}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Manual Posting Routes
@app.post("/api/post/manual")
async def manual_post(post_data: ManualPostRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        platform = post_data.platform
        
        if platform == "facebook":
            tokens = user_facebook_tokens.get(user_id)
            if not tokens:
                return {"success": False, "error": "Facebook not connected"}
            
            page_id = post_data.page_id or (tokens.get("pages", [{}])[0].get("id", "") if tokens.get("pages") else "")
            page_token = next(
                (p.get("access_token") for p in tokens.get("pages", []) if p.get("id") == page_id),
                tokens.get("access_token")
            )
            
            result = await facebook_connector.post_content(
                access_token=page_token,
                page_id=page_id,
                title=post_data.title,
                content=post_data.content,
                image_url=post_data.image_url
            )
        else:
            return {"success": False, "error": "Platform not supported yet"}
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

# AI Content Generation Routes
@app.post("/api/automation/test-auto-post")
async def test_auto_post(test_data: TestPostRequest, current_user: dict = Depends(get_current_user)):
    try:
        if isinstance(ai_service, MockAIService):
            return {
                "success": False,
                "error": "Mock AI service active",
                "message": "Configure MISTRAL_API_KEY or GROQ_API_KEY environment variables"
            }
        
        content_result = await ai_service.generate_reddit_domain_content(
            domain=test_data.domain,
            business_type=test_data.business_type,
            business_description=test_data.business_description,
            target_audience=test_data.target_audience,
            content_style=test_data.content_style
        )
        
        if not content_result.get("success", True):
            return {
                "success": False,
                "error": f"AI content generation failed: {content_result.get('error')}"
            }
        
        return {
            "success": True,
            "message": f"Content generated using {content_result.get('ai_service')}!",
            "post_details": {
                "title": content_result.get("title"),
                "platform": test_data.platform
            },
            "content_preview": content_result.get("content"),
            "ai_service": content_result.get("ai_service"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Automation Setup Routes
@app.post("/api/automation/setup-auto-posting")
async def setup_auto_posting(config_data: AutoPostingRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        platform = config_data.platform
        
        # Check connections
        if platform == "facebook" and user_id not in user_facebook_tokens:
            return {"success": False, "error": "Facebook account not connected"}
        elif platform == "instagram" and user_id not in user_instagram_tokens:
            return {"success": False, "error": "Instagram account not connected"}
        
        if isinstance(ai_service, MockAIService):
            return {"success": False, "error": "AI service not configured"}
        
        # Test AI service
        test_content = await ai_service.generate_reddit_domain_content(
            domain=config_data.domain,
            business_type=config_data.business_type,
            business_description=config_data.business_description,
            target_audience=config_data.target_audience
        )
        
        if not test_content.get("success", True):
            return {"success": False, "error": "AI service not working properly"}
        
        return {
            "success": True,
            "message": f"{platform} auto-posting configured successfully",
            "config": config_data.dict(),
            "ai_service": test_content.get("ai_service", "unknown")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Status Routes
@app.get("/api/automation/status")
async def get_automation_status(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        return {
            "success": True,
            "user_id": user_id,
            "facebook_connected": user_id in user_facebook_tokens,
            "instagram_connected": user_id in user_instagram_tokens,
            "facebook_username": user_facebook_tokens.get(user_id, {}).get("facebook_username", ""),
            "instagram_username": user_instagram_tokens.get(user_id, {}).get("instagram_username", ""),
            "real_ai": not isinstance(ai_service, MockAIService),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Disconnect Routes
@app.post("/api/{platform}/disconnect")
async def disconnect_platform(platform: str, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        if platform == "facebook" and user_id in user_facebook_tokens:
            del user_facebook_tokens[user_id]
        elif platform == "instagram" and user_id in user_instagram_tokens:
            del user_instagram_tokens[user_id]
        
        return {"success": True, "message": f"{platform.title()} disconnected successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Main execution
if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 10000))
    uvicorn.run("main1:app", host="0.0.0.0", port=PORT, reload=False)