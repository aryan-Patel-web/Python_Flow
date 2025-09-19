# """
# Facebook Automation Backend - Real API Integration
# Multi-user system with OAuth, content generation, and posting
# """

# import asyncio
# import logging
# import os
# import json
# import requests
# import base64
# from datetime import datetime, timedelta
# from typing import Dict, List, Optional, Any
# from dataclasses import dataclass
# import uuid
# import time

# logger = logging.getLogger(__name__)

# @dataclass
# class FacebookPostConfig:
#     user_id: str
#     domain: str
#     business_type: str
#     business_description: str
#     target_audience: str = "indian_users"
#     language: str = "en"
#     content_style: str = "engaging"
#     posts_per_day: int = 3
#     posting_times: List[str] = None
#     pages: List[str] = None
#     manual_time_entry: bool = False
#     custom_post_count: bool = False

# class FacebookOAuthConnector:
#     """Real Facebook API OAuth and posting connector"""
    
#     def __init__(self, config):
#         self.config = config
#         self.app_id = config.get('FB_APP_ID', '')
#         self.app_secret = config.get('FB_APP_SECRET', '')
#         self.redirect_uri = config.get('FB_REDIRECT_URI', '')
#         self.is_configured = bool(self.app_id and self.app_secret)
        
#     def generate_oauth_url(self, state=None):
#         """Generate Facebook OAuth URL"""
#         if not self.is_configured:
#             return {"success": False, "error": "Facebook credentials not configured"}
        
#         params = {
#             'client_id': self.app_id,
#             'redirect_uri': self.redirect_uri,
#             'state': state or f"fb_{uuid.uuid4().hex[:12]}",
#             'scope': 'pages_manage_posts,pages_read_engagement,public_profile,email',
#             'response_type': 'code'
#         }
        
#         auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
#         return {
#             "success": True,
#             "authorization_url": auth_url,
#             "state": params['state']
#         }
    
#     async def exchange_code_for_token(self, code):
#         """Exchange authorization code for access token"""
#         try:
#             token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
#             params = {
#                 'client_id': self.app_id,
#                 'client_secret': self.app_secret,
#                 'redirect_uri': self.redirect_uri,
#                 'code': code
#             }
            
#             response = requests.post(token_url, data=params, timeout=30)
            
#             if response.status_code == 200:
#                 token_data = response.json()
#                 access_token = token_data.get('access_token')
                
#                 # Get user info
#                 user_response = requests.get(
#                     f"https://graph.facebook.com/v18.0/me?fields=id,name,email&access_token={access_token}",
#                     timeout=15
#                 )
                
#                 user_info = user_response.json() if user_response.status_code == 200 else {}
                
#                 # Get user pages
#                 pages_response = requests.get(
#                     f"https://graph.facebook.com/v18.0/me/accounts?fields=id,name,access_token&access_token={access_token}",
#                     timeout=15
#                 )
                
#                 pages = pages_response.json().get('data', []) if pages_response.status_code == 200 else []
                
#                 return {
#                     "success": True,
#                     "access_token": access_token,
#                     "expires_in": token_data.get('expires_in', 3600),
#                     "user_info": user_info,
#                     "pages": pages
#                 }
#             else:
#                 return {"success": False, "error": f"Token exchange failed: {response.text}"}
                
#         except Exception as e:
#             return {"success": False, "error": f"OAuth error: {str(e)}"}
    
#     async def post_content_with_token(self, **kwargs):
#         """Post content to Facebook page"""
#         try:
#             access_token = kwargs.get('access_token')
#             page_id = kwargs.get('page_id')
#             title = kwargs.get('title', '')
#             content = kwargs.get('content', '')
#             media_urls = kwargs.get('media_urls', [])
            
#             if not access_token or not page_id:
#                 return {"success": False, "error": "Missing access token or page ID"}
            
#             # Prepare post data
#             post_data = {
#                 'message': f"{title}\n\n{content}",
#                 'access_token': access_token
#             }
            
#             # Add media if provided
#             if media_urls:
#                 post_data['link'] = media_urls[0]  # Facebook will auto-generate preview
            
#             # Post to Facebook Page
#             url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
#             response = requests.post(url, data=post_data, timeout=30)
            
#             if response.status_code == 200:
#                 result = response.json()
#                 post_id = result.get('id', '')
                
#                 return {
#                     "success": True,
#                     "post_id": post_id,
#                     "post_url": f"https://facebook.com/{post_id}",
#                     "message": "Posted to Facebook successfully"
#                 }
#             else:
#                 return {"success": False, "error": f"Facebook API error: {response.text}"}
                
#         except Exception as e:
#             return {"success": False, "error": f"Posting failed: {str(e)}"}

# class FacebookAutomationScheduler:
#     """Facebook automation scheduler for multiple users"""
    
#     def __init__(self, facebook_connector, ai_service, database_manager, user_tokens):
#         self.facebook_connector = facebook_connector
#         self.ai_service = ai_service
#         self.database_manager = database_manager
#         self.user_tokens = user_tokens
#         self.is_running = True
#         self.active_configs = {}
        
#     def start_scheduler(self):
#         """Start the automation scheduler"""
#         logger.info("Facebook automation scheduler started")
#         # In production, implement actual scheduling logic
        
#     async def setup_auto_posting(self, config: FacebookPostConfig):
#         """Setup auto-posting for a user"""
#         try:
#             user_id = config.user_id
            
#             # Store configuration
#             self.active_configs[user_id] = {
#                 "auto_posting": {
#                     "config": config.__dict__,
#                     "enabled": True,
#                     "created_at": datetime.now().isoformat()
#                 }
#             }
            
#             # Test AI content generation
#             test_content = await self.ai_service.generate_reddit_domain_content(
#                 domain=config.domain,
#                 business_type=config.business_type,
#                 business_description=config.business_description,
#                 target_audience=config.target_audience,
#                 content_style=config.content_style
#             )
            
#             if not test_content.get("success", True):
#                 return {"success": False, "error": "AI content generation failed"}
            
#             logger.info(f"Facebook auto-posting configured for user {user_id}")
            
#             return {
#                 "success": True,
#                 "message": "Facebook auto-posting configured successfully",
#                 "config": config.__dict__,
#                 "next_post_time": "Scheduling activated",
#                 "ai_service": test_content.get("ai_service", "unknown")
#             }
            
#         except Exception as e:
#             logger.error(f"Facebook auto-posting setup failed: {e}")
#             return {"success": False, "error": str(e)}
    
#     async def get_automation_status(self, user_id):
#         """Get automation status for user"""
#         user_config = self.active_configs.get(user_id, {})
#         facebook_connected = user_id in self.user_tokens
        
#         return {
#             "success": True,
#             "user_id": user_id,
#             "facebook_connected": facebook_connected,
#             "auto_posting": {
#                 "enabled": "auto_posting" in user_config,
#                 "config": user_config.get("auto_posting", {}).get("config"),
#                 "stats": {"total_posts": 0, "successful_posts": 0, "failed_posts": 0}
#             },
#             "daily_stats": {"posts_today": 0, "total_engagement": 0},
#             "scheduler_running": self.is_running,
#             "last_updated": datetime.now().isoformat()
#         }