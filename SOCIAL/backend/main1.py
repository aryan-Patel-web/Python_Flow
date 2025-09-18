"""
Complete Facebook & Instagram Automation Backend - All Reddit Features Implemented
Real OAuth, AI content generation, scheduling, manual posting, automation
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
import bcrypt
import jwt
import schedule
import time

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import modules with error handling
try:
    from ai_service import AIService
    from database import MultiUserDatabaseManager
    AI_AVAILABLE = True
    DB_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Import failed: {e}")
    AI_AVAILABLE = False
    DB_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("social_automation.log")
    ]
)
logger = logging.getLogger(__name__)

# Global instances
database_manager = None
ai_service = None
facebook_connector = None
instagram_connector = None
automation_scheduler = None

# Multi-user management
user_facebook_tokens = {}
user_instagram_tokens = {}
oauth_states = {}
automation_configs = {}

# Authentication setup
security = HTTPBearer()

# Request Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AutoPostingRequest(BaseModel):
    platform: str  # 'facebook' or 'instagram'
    domain: str
    business_type: str
    business_description: str = ""
    target_audience: str = "indian_users"
    language: str = "en"
    content_style: str = "engaging"
    posts_per_day: int = 3
    posting_times: List[str]
    pages: List[str] = []  # For Facebook
    hashtags: List[str] = []  # For Instagram
    manual_time_entry: bool = False
    custom_post_count: bool = False

class TestPostRequest(BaseModel):
    platform: str
    domain: str
    business_type: str
    business_description: str = ""
    target_audience: str = "indian_users"
    language: str = "en"
    content_style: str = "engaging"

class ManualPostRequest(BaseModel):
    platform: str  # 'facebook' or 'instagram'
    title: str
    content: str
    page_id: str = ""
    image_url: str = ""
    hashtags: List[str] = []

class ScheduleUpdateRequest(BaseModel):
    platform: str
    type: str
    enabled: bool

# Facebook OAuth Connector
class FacebookOAuthConnector:
    def __init__(self, config):
        self.config = config
        self.app_id = config.get('FB_APP_ID', '')
        self.app_secret = config.get('FB_APP_SECRET', '')
        self.redirect_uri = config.get('FB_REDIRECT_URI', '')
        self.is_configured = bool(self.app_id and self.app_secret)
        
    def generate_oauth_url(self, state=None):
        if not self.is_configured:
            return {"success": False, "error": "Facebook credentials not configured"}
        
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'state': state or f"fb_{uuid.uuid4().hex[:12]}",
            'scope': 'pages_manage_posts,pages_read_engagement,public_profile,email',
            'response_type': 'code'
        }
        
        auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        return {"success": True, "authorization_url": auth_url, "state": params['state']}
    
    async def exchange_code_for_token(self, code):
        try:
            token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            params = {'client_id': self.app_id, 'client_secret': self.app_secret, 'redirect_uri': self.redirect_uri, 'code': code}
            
            response = requests.post(token_url, data=params, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                
                # Get user info
                user_response = requests.get(f"https://graph.facebook.com/v18.0/me?fields=id,name,email&access_token={access_token}", timeout=15)
                user_info = user_response.json() if user_response.status_code == 200 else {}
                
                # Get user pages
                pages_response = requests.get(f"https://graph.facebook.com/v18.0/me/accounts?fields=id,name,access_token&access_token={access_token}", timeout=15)
                pages = pages_response.json().get('data', []) if pages_response.status_code == 200 else []
                
                return {"success": True, "access_token": access_token, "expires_in": token_data.get('expires_in', 3600), "user_info": user_info, "pages": pages}
            else:
                return {"success": False, "error": f"Token exchange failed: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"OAuth error: {str(e)}"}
    
    async def post_content_with_token(self, **kwargs):
        try:
            access_token = kwargs.get('access_token')
            page_id = kwargs.get('page_id')
            title = kwargs.get('title', '')
            content = kwargs.get('content', '')
            image_url = kwargs.get('image_url')
            
            if not access_token or not page_id:
                return {"success": False, "error": "Missing access token or page ID"}
            
            post_data = {'message': f"{title}\n\n{content}", 'access_token': access_token}
            
            if image_url:
                post_data['link'] = image_url
            
            url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
            response = requests.post(url, data=post_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get('id', '')
                
                return {"success": True, "post_id": post_id, "post_url": f"https://facebook.com/{post_id}", "message": "Posted to Facebook successfully"}
            else:
                return {"success": False, "error": f"Facebook API error: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"Posting failed: {str(e)}"}

# Instagram OAuth Connector
class InstagramOAuthConnector:
    def __init__(self, config):
        self.config = config
        self.app_id = config.get('INSTAGRAM_APP_ID', '')
        self.app_secret = config.get('INSTAGRAM_APP_SECRET', '')
        self.redirect_uri = config.get('INSTAGRAM_REDIRECT_URI', '')
        self.is_configured = bool(self.app_id and self.app_secret)
        
    def generate_oauth_url(self, state=None):
        if not self.is_configured:
            return {"success": False, "error": "Instagram credentials not configured"}
        
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'user_profile,user_media',
            'response_type': 'code',
            'state': state or f"ig_{uuid.uuid4().hex[:12]}"
        }
        
        auth_url = f"https://api.instagram.com/oauth/authorize?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        return {"success": True, "authorization_url": auth_url, "state": params['state']}
    
    async def exchange_code_for_token(self, code):
        try:
            token_url = "https://api.instagram.com/oauth/access_token"
            data = {'client_id': self.app_id, 'client_secret': self.app_secret, 'grant_type': 'authorization_code', 'redirect_uri': self.redirect_uri, 'code': code}
            
            response = requests.post(token_url, data=data, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                short_token = token_data.get('access_token')
                
                # Get long-lived token
                long_token_url = "https://graph.instagram.com/access_token"
                long_params = {'grant_type': 'ig_exchange_token', 'client_secret': self.app_secret, 'access_token': short_token}
                
                long_response = requests.get(long_token_url, params=long_params, timeout=30)
                
                if long_response.status_code == 200:
                    long_data = long_response.json()
                    access_token = long_data.get('access_token')
                    
                    # Get user info
                    user_response = requests.get(f"https://graph.instagram.com/me?fields=id,username,account_type&access_token={access_token}", timeout=15)
                    user_info = user_response.json() if user_response.status_code == 200 else {}
                    
                    return {"success": True, "access_token": access_token, "expires_in": long_data.get('expires_in', 5184000), "user_info": user_info}
                else:
                    return {"success": False, "error": f"Long-lived token failed: {long_response.text}"}
            else:
                return {"success": False, "error": f"Token exchange failed: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"OAuth error: {str(e)}"}
    
    async def post_content_with_token(self, **kwargs):
        try:
            access_token = kwargs.get('access_token')
            user_id = kwargs.get('instagram_user_id')
            caption = kwargs.get('caption', '')
            image_url = kwargs.get('image_url')
            
            if not access_token or not user_id:
                return {"success": False, "error": "Missing access token or user ID"}
            
            if not image_url:
                return {"success": False, "error": "Instagram requires image/video for posts"}
            
            # Create media container
            container_url = f"https://graph.facebook.com/v18.0/{user_id}/media"
            container_data = {'image_url': image_url, 'caption': caption, 'access_token': access_token}
            
            container_response = requests.post(container_url, data=container_data, timeout=30)
            
            if container_response.status_code == 200:
                container_result = container_response.json()
                creation_id = container_result.get('id')
                
                # Publish media
                publish_url = f"https://graph.facebook.com/v18.0/{user_id}/media_publish"
                publish_data = {'creation_id': creation_id, 'access_token': access_token}
                
                publish_response = requests.post(publish_url, data=publish_data, timeout=30)
                
                if publish_response.status_code == 200:
                    publish_result = publish_response.json()
                    post_id = publish_result.get('id')
                    
                    return {"success": True, "post_id": post_id, "post_url": f"https://instagram.com/p/{post_id}", "message": "Posted to Instagram successfully"}
                else:
                    return {"success": False, "error": f"Publish failed: {publish_response.text}"}
            else:
                return {"success": False, "error": f"Container creation failed: {container_response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"Posting failed: {str(e)}"}

# Automation Scheduler (Like Reddit)
class SocialMediaAutomationScheduler:
    def __init__(self, facebook_connector, instagram_connector, ai_service, database_manager, user_fb_tokens, user_ig_tokens):
        self.facebook_connector = facebook_connector
        self.instagram_connector = instagram_connector
        self.ai_service = ai_service
        self.database_manager = database_manager
        self.user_fb_tokens = user_fb_tokens
        self.user_ig_tokens = user_ig_tokens
        self.is_running = True
        self.active_configs = {}
        self.scheduler_thread = None
        
    def start_scheduler(self):
        logger.info("Social Media automation scheduler started")
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
    def _run_scheduler(self):
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                
    async def setup_auto_posting(self, config):
        try:
            user_id = config.get('user_id')
            platform = config.get('platform')
            
            # Store configuration
            if user_id not in self.active_configs:
                self.active_configs[user_id] = {}
            self.active_configs[user_id][f"{platform}_auto_posting"] = {"config": config, "enabled": True, "created_at": datetime.now().isoformat()}
            
            # Test AI content generation
            test_content = await self.ai_service.generate_reddit_domain_content(
                domain=config.get('domain'),
                business_type=config.get('business_type'),
                business_description=config.get('business_description'),
                target_audience=config.get('target_audience'),
                content_style=config.get('content_style')
            )
            
            if not test_content.get("success", True):
                return {"success": False, "error": "AI content generation failed"}
            
            # Schedule posts
            posting_times = config.get('posting_times', [])
            for post_time in posting_times:
                schedule.every().day.at(post_time).do(self._execute_scheduled_post, user_id, platform, config)
            
            logger.info(f"{platform} auto-posting configured for user {user_id}")
            
            return {"success": True, "message": f"{platform} auto-posting configured successfully", "config": config, "next_post_time": "Scheduling activated", "ai_service": test_content.get("ai_service", "unknown")}
            
        except Exception as e:
            logger.error(f"{platform} auto-posting setup failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_scheduled_post(self, user_id, platform, config):
        try:
            # Generate AI content
            content = await self.ai_service.generate_reddit_domain_content(
                domain=config.get('domain'),
                business_type=config.get('business_type'),
                business_description=config.get('business_description'),
                target_audience=config.get('target_audience'),
                content_style=config.get('content_style')
            )
            
            if not content.get("success", True):
                logger.error(f"AI content generation failed for user {user_id}")
                return
            
            title = content.get("title", "Automated Post")
            post_content = content.get("content", "")
            
            # Post to platform
            if platform == "facebook":
                tokens = self.user_fb_tokens.get(user_id)
                if tokens and tokens.get("pages"):
                    page = tokens["pages"][0]  # Use first page
                    result = await self.facebook_connector.post_content_with_token(
                        access_token=page.get("access_token", tokens["access_token"]),
                        page_id=page.get("id"),
                        title=title,
                        content=post_content
                    )
                    
            elif platform == "instagram":
                tokens = self.user_ig_tokens.get(user_id)
                if tokens:
                    # Instagram requires image - use placeholder
                    image_url = "https://via.placeholder.com/1080x1080/4267B2/FFFFFF?text=Auto+Post"
                    result = await self.instagram_connector.post_content_with_token(
                        access_token=tokens["access_token"],
                        instagram_user_id=tokens["instagram_user_id"],
                        caption=f"{title}\n\n{post_content}",
                        image_url=image_url
                    )
            
            # Log activity
            if self.database_manager:
                await self.database_manager.log_social_activity(
                    user_id=user_id,
                    platform=platform,
                    activity_type="post",
                    activity_data={"success": result.get("success"), "title": title, "post_id": result.get("post_id"), "automated": True}
                )
            
            logger.info(f"Scheduled {platform} post executed for user {user_id}: {result.get('success')}")
            
        except Exception as e:
            logger.error(f"Scheduled post execution failed: {e}")
    
    async def get_automation_status(self, user_id):
        user_config = self.active_configs.get(user_id, {})
        facebook_connected = user_id in self.user_fb_tokens
        instagram_connected = user_id in self.user_ig_tokens
        
        return {
            "success": True,
            "user_id": user_id,
            "facebook_connected": facebook_connected,
            "instagram_connected": instagram_connected,
            "facebook_username": self.user_fb_tokens.get(user_id, {}).get("facebook_username", ""),
            "instagram_username": self.user_ig_tokens.get(user_id, {}).get("instagram_username", ""),
            "auto_posting": {
                "facebook": {"enabled": "facebook_auto_posting" in user_config, "config": user_config.get("facebook_auto_posting", {}).get("config"), "stats": {"total_posts": 0, "successful_posts": 0, "failed_posts": 0}},
                "instagram": {"enabled": "instagram_auto_posting" in user_config, "config": user_config.get("instagram_auto_posting", {}).get("config"), "stats": {"total_posts": 0, "successful_posts": 0, "failed_posts": 0}}
            },
            "daily_stats": {"posts_today": 0, "total_engagement": 0},
            "scheduler_running": self.is_running,
            "last_updated": datetime.now().isoformat()
        }

# Mock implementations for development
class MockAIService:
    async def generate_reddit_domain_content(self, **kwargs):
        return {"success": False, "error": "Mock AI Service", "title": f"Mock Title for {kwargs.get('domain', 'general')}", "content": "Configure MISTRAL_API_KEY or GROQ_API_KEY for real AI content", "ai_service": "mock"}
    
    async def test_ai_connection(self):
        return {"success": False, "error": "Mock AI", "primary_service": "mock"}

class MockDatabaseManager:
    def __init__(self):
        self.users = {}
        self.social_tokens = {}
        
    async def connect(self):
        return True
    
    async def disconnect(self):
        return True
    
    async def register_user(self, email, password, name):
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        self.users[user_id] = {"id": user_id, "email": email, "name": name}
        token = jwt.encode({"user_id": user_id, "email": email, "name": name, "exp": datetime.utcnow() + timedelta(days=30)}, "secret", algorithm="HS256")
        return {"success": True, "user_id": user_id, "email": email, "name": name, "token": token}
    
    async def login_user(self, email, password):
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        token = jwt.encode({"user_id": user_id, "email": email, "name": email.split('@')[0], "exp": datetime.utcnow() + timedelta(days=30)}, "secret", algorithm="HS256")
        return {"success": True, "user_id": user_id, "email": email, "name": email.split('@')[0], "token": token}
    
    async def get_user_by_token(self, token):
        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
            return {"id": payload["user_id"], "email": payload["email"], "name": payload["name"]}
        except:
            return None
    
    async def store_social_tokens(self, user_id, platform, token_data):
        if user_id not in self.social_tokens:
            self.social_tokens[user_id] = {}
        self.social_tokens[user_id][platform] = token_data
        return {"success": True}
    
    async def log_social_activity(self, user_id, platform, activity_type, activity_data):
        return {"success": True}

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        user = await database_manager.get_user_by_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    global database_manager, ai_service, facebook_connector, instagram_connector, automation_scheduler
    
    logger.info("Starting Complete Social Media Automation System...")
    
    # Initialize database
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
    
    # Initialize AI service
    try:
        if AI_AVAILABLE:
            ai_service = AIService()
            test_result = await ai_service.test_ai_connection()
            if test_result.get("success"):
                logger.info(f"Real AI service ready: {test_result.get('primary_service')}")
            else:
                ai_service = MockAIService()
                logger.info("AI service not configured, using mock")
        else:
            ai_service = MockAIService()
            logger.info("AI service not available, using mock")
    except Exception as e:
        logger.error(f"AI service failed: {e}")
        ai_service = MockAIService()
    
    # Initialize connectors
    fb_config = {'FB_APP_ID': os.getenv('FB_APP_ID', '1802724037303404'), 'FB_APP_SECRET': os.getenv('FB_APP_SECRET', '88015121b7360d1f7f074f630a54a485'), 'FB_REDIRECT_URI': os.getenv('FB_REDIRECT_URI', 'https://agentic-u5lx.onrender.com/api/oauth/facebook/callback')}
    facebook_connector = FacebookOAuthConnector(fb_config)
    
    ig_config = {'INSTAGRAM_APP_ID': os.getenv('INSTAGRAM_APP_ID', '1802724037303404'), 'INSTAGRAM_APP_SECRET': os.getenv('INSTAGRAM_APP_SECRET', 'instagram_secret_here'), 'INSTAGRAM_REDIRECT_URI': os.getenv('INSTAGRAM_REDIRECT_URI', 'https://agentic-u5lx.onrender.com/api/oauth/instagram/callback')}
    instagram_connector = InstagramOAuthConnector(ig_config)
    
    # Initialize scheduler
    automation_scheduler = SocialMediaAutomationScheduler(facebook_connector, instagram_connector, ai_service, database_manager, user_facebook_tokens, user_instagram_tokens)
    automation_scheduler.start_scheduler()
    
    logger.info("Application startup completed")
    yield
    
    # Cleanup
    if automation_scheduler:
        automation_scheduler.is_running = False
    if database_manager:
        await database_manager.disconnect()

# Create app
app = FastAPI(title="Complete Social Media Automation", version="1.0.0", lifespan=lifespan)

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Routes
@app.get("/")
async def root():
    return {"success": True, "message": "Complete Social Media Automation API", "platforms": ["facebook", "instagram"], "features": ["oauth", "ai_content", "manual_posting", "scheduling", "automation"], "version": "1.0.0", "timestamp": datetime.now().isoformat()}

@app.post("/api/auth/register")
async def register_user(user_data: RegisterRequest):
    result = await database_manager.register_user(email=user_data.email, password=user_data.password, name=user_data.name)
    return result

@app.post("/api/auth/login")
async def login_user(login_data: LoginRequest):
    result = await database_manager.login_user(email=login_data.email, password=login_data.password)
    return result

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {"success": True, "user": current_user}

# OAuth endpoints
@app.get("/api/oauth/{platform}/authorize")
async def oauth_authorize(platform: str, current_user: dict = Depends(get_current_user)):
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

@app.get("/api/oauth/{platform}/callback")
async def oauth_callback(platform: str, code: str, state: str):
    user_id = oauth_states.get(state)
    if not user_id:
        return RedirectResponse(url="https://frontend-agentic-bnc2.onrender.com/?error=invalid_state", status_code=302)
    
    if platform == "facebook":
        result = await facebook_connector.exchange_code_for_token(code)
        if result["success"]:
            token_data = {"access_token": result["access_token"], "expires_in": result["expires_in"], "facebook_username": result["user_info"].get("name", "Unknown"), "facebook_user_id": result["user_info"].get("id", ""), "pages": result.get("pages", [])}
            await database_manager.store_social_tokens(user_id, "facebook", token_data)
            user_facebook_tokens[user_id] = token_data
    elif platform == "instagram":
        result = await instagram_connector.exchange_code_for_token(code)
        if result["success"]:
            token_data = {"access_token": result["access_token"], "expires_in": result["expires_in"], "instagram_username": result["user_info"].get("username", "Unknown"), "instagram_user_id": result["user_info"].get("id", "")}
            await database_manager.store_social_tokens(user_id, "instagram", token_data)
            user_instagram_tokens[user_id] = token_data
    
    oauth_states.pop(state, None)
    
    if result["success"]:
        username = result["user_info"].get("name" if platform == "facebook" else "username", "User")
        return RedirectResponse(url=f"https://frontend-agentic-bnc2.onrender.com/?{platform}_connected=true&username={username}", status_code=302)
    else:
        return RedirectResponse(url=f"https://frontend-agentic-bnc2.onrender.com/?error={platform}_auth_failed", status_code=302)

# Connection status
@app.get("/api/{platform}/connection-status")
async def get_connection_status(platform: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    if platform == "facebook":
        tokens = user_facebook_tokens.get(user_id)
        if tokens:
            return {"success": True, "connected": True, "username": tokens.get("facebook_username"), "pages": tokens.get("pages", [])}
    elif platform == "instagram":
        tokens = user_instagram_tokens.get(user_id)
        if tokens:
            return {"success": True, "connected": True, "username": tokens.get("instagram_username")}
    
    return {"success": True, "connected": False}

# Manual posting
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
            page_token = next((p.get("access_token") for p in tokens.get("pages", []) if p.get("id") == page_id), tokens.get("access_token"))
            
            result = await facebook_connector.post_content_with_token(access_token=page_token, page_id=page_id, title=post_data.title, content=post_data.content, image_url=post_data.image_url)
        
        elif platform == "instagram":
            tokens = user_instagram_tokens.get(user_id)
            if not tokens:
                return {"success": False, "error": "Instagram not connected"}
            
            if not post_data.image_url:
                return {"success": False, "error": "Instagram requires image URL"}
            
            caption = f"{post_data.title}\n\n{post_data.content}"
            if post_data.hashtags:
                caption += "\n\n" + " ".join(post_data.hashtags)
            
            result = await instagram_connector.post_content_with_token(access_token=tokens["access_token"], instagram_user_id=tokens["instagram_user_id"], caption=caption, image_url=post_data.image_url)
        else:
            return {"success": False, "error": "Invalid platform"}
        
        # Log activity
        await database_manager.log_social_activity(user_id, platform, "post", {"success": result.get("success"), "title": post_data.title, "post_id": result.get("post_id"), "manual": True})
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

# AI content generation
@app.post("/api/automation/test-auto-post")
async def test_auto_post(test_data: TestPostRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        if isinstance(ai_service, MockAIService):
            return {"success": False, "error": "Mock AI service active", "message": "Configure MISTRAL_API_KEY or GROQ_API_KEY environment variables", "mock_warning": True}
        
        content_result = await ai_service.generate_reddit_domain_content(domain=test_data.domain, business_type=test_data.business_type, business_description=test_data.business_description, target_audience=test_data.target_audience, language=test_data.language, content_style=test_data.content_style, test_mode=False)
        
        if content_result.get("ai_service") == "mock":
            return {"success": False, "error": "AI service returned mock content", "message": "Check your API keys configuration"}
        
        if not content_result.get("success", True):
            return {"success": False, "error": f"AI content generation failed: {content_result.get('error')}", "message": "Check your AI API keys and service availability"}
        
        return {"success": True, "message": f"Real AI content generated using {content_result.get('ai_service')}!", "post_details": {"title": content_result.get("title"), "platform": test_data.platform, "user_id": user_id, "real_ai": True}, "content_preview": content_result.get("content"), "ai_service": content_result.get("ai_service"), "word_count": content_result.get("word_count"), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Automation setup
@app.post("/api/automation/setup-auto-posting")
async def setup_auto_posting(config_data: AutoPostingRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        platform = config_data.platform
        
        # Check connections
        if platform == "facebook" and user_id not in user_facebook_tokens:
            return {"success": False, "error": "Facebook account not connected", "message": "Please connect your Facebook account first"}
        elif platform == "instagram" and user_id not in user_instagram_tokens:
            return {"success": False, "error": "Instagram account not connected", "message": "Please connect your Instagram account first"}
        
        if isinstance(ai_service, MockAIService):
            return {"success": False, "error": "AI service not configured", "message": "Configure MISTRAL_API_KEY or GROQ_API_KEY for real AI content generation"}
        
        # Test AI service
        test_content = await ai_service.generate_reddit_domain_content(domain=config_data.domain, business_type=config_data.business_type, business_description=config_data.business_description, target_audience=config_data.target_audience, test_mode=False)
        
        if not test_content.get("success", True) or test_content.get("ai_service") == "mock":
            return {"success": False, "error": "AI service not working properly", "message": "AI service returned mock content. Check your API key configuration"}
        
        # Setup automation
        config_dict = config_data.dict()
        config_dict['user_id'] = user_id
        
        result = await automation_scheduler.setup_auto_posting(config_dict)
        
        if result.get("success"):
            username = user_facebook_tokens.get(user_id, {}).get("facebook_username") if platform == "facebook" else user_instagram_tokens.get(user_id, {}).get("instagram_username")
            result["user_id"] = user_id
            result["username"] = username
            result["real_posting"] = True
            result["real_ai"] = True
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

# Status endpoints
@app.get("/api/automation/status")
async def get_automation_status(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        result = await automation_scheduler.get_automation_status(user_id)
        result["real_posting"] = not isinstance(automation_scheduler, type(None))
        result["real_ai"] = not isinstance(ai_service, MockAIService)
        result["ai_service"] = type(ai_service).__name__
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/automation/update-schedule")
async def update_automation_schedule(update_data: ScheduleUpdateRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        platform = update_data.platform
        
        # Update stored config
        if user_id in automation_configs:
            config_key = f"{platform}_{update_data.type}"
            if config_key in automation_configs[user_id]:
                automation_configs[user_id][config_key]["enabled"] = update_data.enabled
        
        return {"success": True, "message": f"{platform} {update_data.type.replace('_', ' ').title()} {'enabled' if update_data.enabled else 'disabled'}", "user_id": user_id, "platform": platform, "type": update_data.type, "enabled": update_data.enabled}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Dashboard
@app.get("/api/user/dashboard")
async def get_user_dashboard(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        facebook_connected = user_id in user_facebook_tokens
        instagram_connected = user_id in user_instagram_tokens
        
        return {"success": True, "dashboard": {"posts_today": 0, "total_engagement": 0, "active_platforms": int(facebook_connected) + int(instagram_connected), "facebook_connected": facebook_connected, "instagram_connected": instagram_connected, "facebook_username": user_facebook_tokens.get(user_id, {}).get("facebook_username", ""), "instagram_username": user_instagram_tokens.get(user_id, {}).get("instagram_username", ""), "user_name": current_user.get("name", ""), "user_email": current_user.get("email", "")}, "user": current_user}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Disconnect
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

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 10000))
    uvicorn.run("main1:app", host="0.0.0.0", port=PORT, reload=False)