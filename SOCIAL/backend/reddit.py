"""
Simple Reddit OAuth Connector for main.py compatibility
"""
import os
import requests
import base64
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RedditOAuthConnector:
    """Simple Reddit OAuth connector compatible with main.py"""
    
    def __init__(self, config: Dict[str, str] = None):
        self.config = config or {}
        self.is_configured = True
        
    def generate_oauth_url(self, state: str = None) -> Dict[str, Any]:
        """Generate Reddit OAuth URL"""
        reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
        reddit_redirect_uri = os.getenv("REDDIT_REDIRECT_URI", "https://agentic-u5lx.onrender.com/api/oauth/reddit/callback")
        
        if not reddit_client_id:
            return {"success": False, "error": "Reddit client ID not configured"}
        
        oauth_url = f"https://www.reddit.com/api/v1/authorize?client_id={reddit_client_id}&response_type=code&state={state}&redirect_uri={reddit_redirect_uri}&duration=permanent&scope=identity,submit,edit,read"
        
        return {
            "success": True,
            "authorization_url": oauth_url,
            "state": state
        }
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
            reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
            reddit_redirect_uri = os.getenv("REDDIT_REDIRECT_URI")
            
            auth_string = f"{reddit_client_id}:{reddit_client_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'User-Agent': 'RedditAutomationPlatform/1.0'
            }
            
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': reddit_redirect_uri
            }
            
            response = requests.post(
                'https://www.reddit.com/api/v1/access_token',
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return {
                    "success": True,
                    "access_token": token_data.get('access_token'),
                    "refresh_token": token_data.get('refresh_token'),
                    "expires_in": token_data.get('expires_in', 3600)
                }
            else:
                return {"success": False, "error": f"Token exchange failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def post_content_with_token(self, **kwargs) -> Dict[str, Any]:
        """Post content to Reddit using access token"""
        try:
            access_token = kwargs.get('access_token')
            subreddit_name = kwargs.get('subreddit_name')
            title = kwargs.get('title')
            content = kwargs.get('content')
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'User-Agent': 'RedditAutomationPlatform/1.0'
            }
            
            data = {
                'kind': 'self',
                'title': title,
                'text': content,
                'sr': subreddit_name
            }
            
            response = requests.post(
                'https://oauth.reddit.com/api/submit',
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "post_id": "reddit_post_id",
                    "post_url": f"https://reddit.com/r/{subreddit_name}/comments/post_id"
                }
            else:
                return {
                    "success": False,
                    "error": f"Reddit API error: {response.status_code}",
                    "message": response.text[:200]
                }
                
        except Exception as e:
            logger.error(f"Reddit posting failed: {e}")
            return {"success": False, "error": str(e)}