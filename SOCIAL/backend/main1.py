"""
Combined Social Media Automation Server - Facebook & Instagram
Multi-user FastAPI with real API integrations and AI content generation
"""

from fastapi import FastAPI, HTTPException, Request, Query, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import asyncio
import logging
import os
import sys
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, EmailStr
import uvicorn

# Environment variables
from dotenv import load_dotenv
load_dotenv()

# Import modules
try:
    from FBauto import FacebookOAuthConnector, FacebookAutomationScheduler, FacebookPostConfig
    from INSTAauto import InstagramOAuthConnector, InstagramAutomationScheduler, InstagramPostConfig
    from ai_service import AIService
    from database import MultiUserDatabaseManager
    FB_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Import failed: {e}")
    FB_AVAILABLE = False

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global instances
database_manager = None
ai_service = None
facebook_connector = None
instagram_connector = None
facebook_scheduler = None
instagram_scheduler = None
user_facebook_tokens = {}
user_instagram_tokens = {}
oauth_states = {}

# Authentication
security = HTTPBearer()

# Request Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class FacebookPostRequest(BaseModel):
    domain: str
    business_type: str
    business_description: str = ""
    target_audience: str = "indian_users"
    language: str = "en"
    content_style: str = "engaging"
    posts_per_day: int = 3
    posting_times: List[str] = []
    pages: List[str] = []

class InstagramPostRequest(BaseModel):
    domain: str
    business_type: str
    business_description: str = ""
    target_audience: str = "indian_users"
    language: str = "en"
    content_style: str = "engaging"
    posts_per_day: int = 2
    posting_times: List[str] = []
    hashtags: List[str] = []

class ManualPostRequest(BaseModel):
    platform: str  # 'facebook' or 'instagram'
    title: str
    content: str
    page_id: str = ""
    image_url: str = ""

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
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
    global database_manager, ai_service, facebook_connector, instagram_connector, facebook_scheduler, instagram_scheduler
    
    logger.info("Starting Multi-Platform Social Media Automation...")
    
    # Initialize database
    try:
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb+srv://aryan:aryan@cluster0.7iquw6v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        database_manager = MultiUserDatabaseManager(mongodb_uri)
        await database_manager.connect()
        logger.info("Database connected")
    except Exception as e:
        logger.error(f"Database failed: {e}")
    
    # Initialize AI service
    try:
        ai_service = AIService()
        test_result = await ai_service.test_ai_connection()
        if test_result.get("success"):
            logger.info(f"AI service ready: {test_result.get('primary_service')}")
        else:
            logger.warning("AI service not configured properly")
    except Exception as e:
        logger.error(f"AI service failed: {e}")
    
    # Initialize Facebook connector
    try:
        fb_config = {
            'FB_APP_ID': os.getenv('FB_APP_ID'),
            'FB_APP_SECRET': os.getenv('FB_APP_SECRET'),
            'FB_REDIRECT_URI': os.getenv('FB_REDIRECT_URI', 'https://agentic-u5lx.onrender.com/api/oauth/facebook/callback')
        }
        facebook_connector = FacebookOAuthConnector(fb_config)
        logger.info(f"Facebook connector ready: {facebook_connector.is_configured}")
    except Exception as e:
        logger.error(f"Facebook connector failed: {e}")
    
    # Initialize Instagram connector
    try:
        ig_config = {
            'INSTAGRAM_APP_ID': os.getenv('INSTAGRAM_APP_ID'),
            'INSTAGRAM_APP_SECRET': os.getenv('INSTAGRAM_APP_SECRET'),
            'INSTAGRAM_REDIRECT_URI': os.getenv('INSTAGRAM_REDIRECT_URI', 'https://agentic-u5lx.onrender.com/api/oauth/instagram/callback')
        }
        instagram_connector = InstagramOAuthConnector(ig_config)
        logger.info(f"Instagram connector ready: {instagram_connector.is_configured}")
    except Exception as e:
        logger.error(f"Instagram connector failed: {e}")
    
    # Initialize schedulers
    if facebook_connector and ai_service:
        facebook_scheduler = FacebookAutomationScheduler(facebook_connector, ai_service, database_manager, user_facebook_tokens)
        facebook_scheduler.start_scheduler()
    
    if instagram_connector and ai_service:
        instagram_scheduler = InstagramAutomationScheduler(instagram_connector, ai_service, database_manager, user_instagram_tokens)
        instagram_scheduler.start_scheduler()
    
    logger.info("Application startup completed")
    yield
    
    # Cleanup
    if database_manager:
        await database_manager.disconnect()

# Create app
app = FastAPI(title="Multi-Platform Social Media Automation", version="1.0.0", lifespan=lifespan)

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Routes
@app.get("/")
async def root():
    return {"success": True, "message": "Multi-Platform Social Media Automation API", "platforms": ["facebook", "instagram"], "version": "1.0.0", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_check():
    return {"success": True, "status": "healthy", "services": {"database": database_manager is not None, "ai": ai_service is not None, "facebook": facebook_connector is not None, "instagram": instagram_connector is not None}, "timestamp": datetime.now().isoformat()}

# Authentication endpoints
@app.post("/api/auth/register")
async def register_user(user_data: RegisterRequest):
    try:
        result = await database_manager.register_user(email=user_data.email, password=user_data.password, name=user_data.name)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login")
async def login_user(login_data: LoginRequest):
    try:
        result = await database_manager.login_user(email=login_data.email, password=login_data.password)
        return result
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {"success": True, "user": current_user}

# Facebook OAuth endpoints
@app.get("/api/oauth/facebook/authorize")
async def facebook_oauth_authorize(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        state = f"fb_{user_id}_{uuid.uuid4().hex[:12]}"
        oauth_states[state] = user_id
        
        result = facebook_connector.generate_oauth_url(state)
        if result["success"]:
            return {"success": True, "redirect_url": result["authorization_url"], "state": state}
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/oauth/facebook/callback")
async def facebook_oauth_callback(code: str, state: str):
    try:
        user_id = oauth_states.get(state)
        if not user_id:
            return RedirectResponse(url="https://frontend-agentic-bnc2.onrender.com/?error=invalid_state", status_code=302)
        
        result = await facebook_connector.exchange_code_for_token(code)
        
        if result["success"]:
            # Store tokens
            token_data = {"access_token": result["access_token"], "expires_in": result["expires_in"], "facebook_username": result["user_info"].get("name", "Unknown"), "facebook_user_id": result["user_info"].get("id", ""), "pages": result.get("pages", [])}
            
            await database_manager.store_social_tokens(user_id, "facebook", token_data)
            user_facebook_tokens[user_id] = token_data
            
            oauth_states.pop(state, None)
            
            return RedirectResponse(url=f"https://frontend-agentic-bnc2.onrender.com/?facebook_connected=true&username={result['user_info'].get('name', 'User')}", status_code=302)
        else:
            return RedirectResponse(url="https://frontend-agentic-bnc2.onrender.com/?error=facebook_auth_failed", status_code=302)
    except Exception as e:
        return RedirectResponse(url="https://frontend-agentic-bnc2.onrender.com/?error=oauth_failed", status_code=302)

# Instagram OAuth endpoints
@app.get("/api/oauth/instagram/authorize")
async def instagram_oauth_authorize(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        state = f"ig_{user_id}_{uuid.uuid4().hex[:12]}"
        oauth_states[state] = user_id
        
        result = instagram_connector.generate_oauth_url(state)
        if result["success"]:
            return {"success": True, "redirect_url": result["authorization_url"], "state": state}
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/oauth/instagram/callback")
async def instagram_oauth_callback(code: str, state: str):
    try:
        user_id = oauth_states.get(state)
        if not user_id:
            return RedirectResponse(url="https://frontend-agentic-bnc2.onrender.com/?error=invalid_state", status_code=302)
        
                    result = await instagram_connector.exchange_code_for_token(code)
        
        if result["success"]:
            # Store tokens
            token_data = {"access_token": result["access_token"], "expires_in": result["expires_in"], "instagram_username": result["user_info"].get("username", "Unknown"), "instagram_user_id": result["user_info"].get("id", "")}
            
            await database_manager.store_social_tokens(user_id, "instagram", token_data)
            user_instagram_tokens[user_id] = token_data
            
            oauth_states.pop(state, None)
            
            return RedirectResponse(url=f"https://frontend-agentic-bnc2.onrender.com/?instagram_connected=true&username={result['user_info'].get('username', 'User')}", status_code=302)
        else:
            return RedirectResponse(url="https://frontend-agentic-bnc2.onrender.com/?error=instagram_auth_failed", status_code=302)
    except Exception as e:
        return RedirectResponse(url="https://frontend-agentic-bnc2.onrender.com/?error=oauth_failed", status_code=302)

# Connection status endpoints
@app.get("/api/{platform}/connection-status")
async def get_connection_status(platform: str, current_user: dict = Depends(get_current_user)):
    try:
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
    except Exception as e:
        return {"success": False, "error": str(e)}

# Manual posting
@app.post("/api/post/manual")
async def manual_post(post_data: ManualPostRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        if post_data.platform == "facebook":
            tokens = user_facebook_tokens.get(user_id)
            if not tokens:
                return {"success": False, "error": "Facebook not connected"}
            
            result = await facebook_connector.post_content_with_token(
                access_token=tokens["access_token"],
                page_id=post_data.page_id or tokens.get("pages", [{}])[0].get("id", ""),
                title=post_data.title,
                content=post_data.content,
                media_urls=[post_data.image_url] if post_data.image_url else []
            )
        
        elif post_data.platform == "instagram":
            tokens = user_instagram_tokens.get(user_id)
            if not tokens:
                return {"success": False, "error": "Instagram not connected"}
            
            if not post_data.image_url:
                return {"success": False, "error": "Instagram requires image URL"}
            
            result = await instagram_connector.post_content_with_token(
                access_token=tokens["access_token"],
                instagram_user_id=tokens["instagram_user_id"],
                caption=f"{post_data.title}\n\n{post_data.content}",
                image_url=post_data.image_url
            )
        else:
            return {"success": False, "error": "Invalid platform"}
        
        # Log activity
        if database_manager:
            await database_manager.log_social_activity(user_id, post_data.platform, "post", {"success": result.get("success"), "title": post_data.title, "post_id": result.get("post_id"), "manual": True})
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

# AI content generation
@app.post("/api/content/generate")
async def generate_content(domain: str, business_type: str, business_description: str = "", target_audience: str = "indian_users", content_style: str = "engaging", current_user: dict = Depends(get_current_user)):
    try:
        if not ai_service:
            return {"success": False, "error": "AI service not available"}
        
        content = await ai_service.generate_reddit_domain_content(
            domain=domain,
            business_type=business_type,
            business_description=business_description,
            target_audience=target_audience,
            content_style=content_style
        )
        
        if content.get("success", True):
            return {"success": True, "title": content.get("title", ""), "content": content.get("content", ""), "ai_service": content.get("ai_service", "unknown")}
        else:
            return {"success": False, "error": content.get("error", "AI generation failed")}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Automation setup
@app.post("/api/automation/facebook/setup")
async def setup_facebook_automation(config_data: FacebookPostRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        if user_id not in user_facebook_tokens:
            return {"success": False, "error": "Facebook account not connected"}
        
        config = FacebookPostConfig(
            user_id=user_id,
            domain=config_data.domain,
            business_type=config_data.business_type,
            business_description=config_data.business_description,
            target_audience=config_data.target_audience,
            language=config_data.language,
            content_style=config_data.content_style,
            posts_per_day=config_data.posts_per_day,
            posting_times=config_data.posting_times,
            pages=config_data.pages
        )
        
        if facebook_scheduler:
            result = await facebook_scheduler.setup_auto_posting(config)
            if database_manager:
                await database_manager.store_automation_config(user_id, "facebook_auto_posting", config.__dict__)
            return result
        else:
            return {"success": False, "error": "Facebook scheduler not available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/automation/instagram/setup")
async def setup_instagram_automation(config_data: InstagramPostRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        if user_id not in user_instagram_tokens:
            return {"success": False, "error": "Instagram account not connected"}
        
        config = InstagramPostConfig(
            user_id=user_id,
            domain=config_data.domain,
            business_type=config_data.business_type,
            business_description=config_data.business_description,
            target_audience=config_data.target_audience,
            language=config_data.language,
            content_style=config_data.content_style,
            posts_per_day=config_data.posts_per_day,
            posting_times=config_data.posting_times,
            hashtags=config_data.hashtags
        )
        
        if instagram_scheduler:
            result = await instagram_scheduler.setup_auto_posting(config)
            if database_manager:
                await database_manager.store_automation_config(user_id, "instagram_auto_posting", config.__dict__)
            return result
        else:
            return {"success": False, "error": "Instagram scheduler not available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Status endpoints
@app.get("/api/automation/status")
async def get_automation_status(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        facebook_status = await facebook_scheduler.get_automation_status(user_id) if facebook_scheduler else {"success": False}
        instagram_status = await instagram_scheduler.get_automation_status(user_id) if instagram_scheduler else {"success": False}
        
        return {
            "success": True,
            "user_id": user_id,
            "facebook": facebook_status,
            "instagram": instagram_status,
            "connections": {
                "facebook": user_id in user_facebook_tokens,
                "instagram": user_id in user_instagram_tokens
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/user/dashboard")
async def get_user_dashboard(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        # Get basic stats
        facebook_connected = user_id in user_facebook_tokens
        instagram_connected = user_id in user_instagram_tokens
        
        return {
            "success": True,
            "dashboard": {
                "posts_today": 0,
                "total_engagement": 0,
                "active_platforms": int(facebook_connected) + int(instagram_connected),
                "facebook_connected": facebook_connected,
                "instagram_connected": instagram_connected,
                "facebook_username": user_facebook_tokens.get(user_id, {}).get("facebook_username", ""),
                "instagram_username": user_instagram_tokens.get(user_id, {}).get("instagram_username", ""),
                "user_name": current_user.get("name", ""),
                "user_email": current_user.get("email", "")
            },
            "user": current_user
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Disconnect endpoints
@app.post("/api/{platform}/disconnect")
async def disconnect_platform(platform: str, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        if platform == "facebook" and user_id in user_facebook_tokens:
            del user_facebook_tokens[user_id]
        elif platform == "instagram" and user_id in user_instagram_tokens:
            del user_instagram_tokens[user_id]
        
        if database_manager:
            await database_manager.revoke_social_connection(user_id, platform)
        
        return {"success": True, "message": f"{platform.title()} disconnected successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 10000))
    uvicorn.run("main1:app", host="0.0.0.0", port=PORT, reload=False)