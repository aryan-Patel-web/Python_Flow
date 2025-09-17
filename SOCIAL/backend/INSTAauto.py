"""
Instagram Automation Backend - Real API Integration
Multi-user system with OAuth, content generation, and posting
"""

import asyncio
import logging
import os
import json
import requests
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import uuid
import time

logger = logging.getLogger(__name__)

@dataclass
class InstagramPostConfig:
    user_id: str
    domain: str
    business_type: str
    business_description: str
    target_audience: str = "indian_users"
    language: str = "en"
    content_style: str = "engaging"
    posts_per_day: int = 2
    posting_times: List[str] = None
    hashtags: List[str] = None
    manual_time_entry: bool = False
    custom_post_count: bool = False

class InstagramOAuthConnector:
    """Real Instagram API OAuth and posting connector"""
    
    def __init__(self, config):
        self.config = config
        self.app_id = config.get('INSTAGRAM_APP_ID', '')
        self.app_secret = config.get('INSTAGRAM_APP_SECRET', '')
        self.redirect_uri = config.get('INSTAGRAM_REDIRECT_URI', '')
        self.is_configured = bool(self.app_id and self.app_secret)
        
    def generate_oauth_url(self, state=None):
        """Generate Instagram OAuth URL"""
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
        
        return {
            "success": True,
            "authorization_url": auth_url,
            "state": params['state']
        }
    
    async def exchange_code_for_token(self, code):
        """Exchange authorization code for access token"""
        try:
            # Step 1: Get short-lived token
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
                
                # Step 2: Exchange for long-lived token
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
                        "expires_in": long_data.get('expires_in', 5184000),  # 60 days
                        "user_info": user_info
                    }
                else:
                    return {"success": False, "error": f"Long-lived token failed: {long_response.text}"}
            else:
                return {"success": False, "error": f"Token exchange failed: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"OAuth error: {str(e)}"}
    
    async def post_content_with_token(self, **kwargs):
        """Post content to Instagram"""
        try:
            access_token = kwargs.get('access_token')
            user_id = kwargs.get('instagram_user_id')
            caption = kwargs.get('caption', '')
            image_url = kwargs.get('image_url')
            
            if not access_token or not user_id:
                return {"success": False, "error": "Missing access token or user ID"}
            
            if not image_url:
                return {"success": False, "error": "Instagram requires image/video for posts"}
            
            # Step 1: Create media container
            container_url = f"https://graph.facebook.com/v18.0/{user_id}/media"
            container_data = {
                'image_url': image_url,
                'caption': caption,
                'access_token': access_token
            }
            
            container_response = requests.post(container_url, data=container_data, timeout=30)
            
            if container_response.status_code == 200:
                container_result = container_response.json()
                creation_id = container_result.get('id')
                
                # Step 2: Publish media
                publish_url = f"https://graph.facebook.com/v18.0/{user_id}/media_publish"
                publish_data = {
                    'creation_id': creation_id,
                    'access_token': access_token
                }
                
                publish_response = requests.post(publish_url, data=publish_data, timeout=30)
                
                if publish_response.status_code == 200:
                    publish_result = publish_response.json()
                    post_id = publish_result.get('id')
                    
                    return {
                        "success": True,
                        "post_id": post_id,
                        "post_url": f"https://instagram.com/p/{post_id}",
                        "message": "Posted to Instagram successfully"
                    }
                else:
                    return {"success": False, "error": f"Publish failed: {publish_response.text}"}
            else:
                return {"success": False, "error": f"Container creation failed: {container_response.text}"}
                
        except Exception as e:
            return {"success": False, "error": f"Posting failed: {str(e)}"}

class InstagramAutomationScheduler:
    """Instagram automation scheduler for multiple users"""
    
    def __init__(self, instagram_connector, ai_service, database_manager, user_tokens):
        self.instagram_connector = instagram_connector
        self.ai_service = ai_service
        self.database_manager = database_manager
        self.user_tokens = user_tokens
        self.is_running = True
        self.active_configs = {}
        
    def start_scheduler(self):
        """Start the automation scheduler"""
        logger.info("Instagram automation scheduler started")
        # In production, implement actual scheduling logic
        
    async def setup_auto_posting(self, config: InstagramPostConfig):
        """Setup auto-posting for a user"""
        try:
            user_id = config.user_id
            
            # Store configuration
            self.active_configs[user_id] = {
                "auto_posting": {
                    "config": config.__dict__,
                    "enabled": True,
                    "created_at": datetime.now().isoformat()
                }
            }
            
            # Test AI content generation
            test_content = await self.ai_service.generate_reddit_domain_content(
                domain=config.domain,
                business_type=config.business_type,
                business_description=config.business_description,
                target_audience=config.target_audience,
                content_style=config.content_style
            )
            
            if not test_content.get("success", True):
                return {"success": False, "error": "AI content generation failed"}
            
            logger.info(f"Instagram auto-posting configured for user {user_id}")
            
            return {
                "success": True,
                "message": "Instagram auto-posting configured successfully",
                "config": config.__dict__,
                "next_post_time": "Scheduling activated",
                "ai_service": test_content.get("ai_service", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Instagram auto-posting setup failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_automation_status(self, user_id):
        """Get automation status for user"""
        user_config = self.active_configs.get(user_id, {})
        instagram_connected = user_id in self.user_tokens
        
        return {
            "success": True,
            "user_id": user_id,
            "instagram_connected": instagram_connected,
            "auto_posting": {
                "enabled": "auto_posting" in user_config,
                "config": user_config.get("auto_posting", {}).get("config"),
                "stats": {"total_posts": 0, "successful_posts": 0, "failed_posts": 0}
            },
            "daily_stats": {"posts_today": 0, "total_engagement": 0},
            "scheduler_running": self.is_running,
            "last_updated": datetime.now().isoformat()
        }