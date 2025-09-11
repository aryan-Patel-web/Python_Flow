"""
Reddit Integration Module for Multi-Platform Automation
Handles Reddit OAuth, content posting, Q&A monitoring, and engagement tracking
OAuth-only implementation for multi-user platform
"""

import requests
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import json
import secrets
from urllib.parse import urlencode
import base64
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RedditPost:
    """Data class for Reddit post information"""
    id: str
    title: str
    content: str
    subreddit: str
    score: int
    num_comments: int
    created_utc: float
    url: str
    author: str
    is_self: bool

@dataclass
class RedditComment:
    """Data class for Reddit comment information"""
    id: str
    body: str
    score: int
    created_utc: float
    parent_id: str
    post_id: str
    subreddit: str

class RedditOAuthConnector:
    """
    Production-ready Reddit OAuth connector for multi-user platform
    """
    
    def __init__(self, config: Dict[str, str]):
        """Initialize Reddit OAuth connector"""
        self.client_id = config.get('REDDIT_CLIENT_ID')
        self.client_secret = config.get('REDDIT_CLIENT_SECRET')
        self.redirect_uri = config.get('REDDIT_REDIRECT_URI', 'http://localhost:8000/api/oauth/reddit/callback')
        self.user_agent = config.get('REDDIT_USER_AGENT', 'IndianAutomationPlatform/1.0')
        
        # Validate required configuration
        if not self.client_id or not self.client_secret:
            logger.warning("Reddit OAuth credentials not configured properly")
            self.is_configured = False
        else:
            self.is_configured = True
            logger.info("Reddit OAuth connector initialized successfully")
        
        # OAuth URLs
        self.auth_url = "https://www.reddit.com/api/v1/authorize"
        self.token_url = "https://www.reddit.com/api/v1/access_token"
        self.api_base = "https://oauth.reddit.com"
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 2  # seconds between requests
        
        # Encryption for token storage
        self.encryption_key = config.get('TOKEN_ENCRYPTION_KEY')
        if self.encryption_key:
            try:
                self.cipher = Fernet(self.encryption_key.encode())
            except:
                # Generate a new key if the provided one is invalid
                self.cipher = Fernet(Fernet.generate_key())
        else:
            self.cipher = Fernet(Fernet.generate_key())
        
        # Domain-specific subreddit mapping
        self.domain_subreddits = {
            "education": ["india", "JEE", "NEET", "IndianStudents", "StudyTips", "AskIndia"],
            "restaurant": ["india", "bangalore", "mumbai", "delhi", "food", "IndianFood"],
            "tech": ["india", "bangalore", "developersIndia", "programming", "coding"],
            "health": ["india", "fitness", "HealthyFood", "mentalhealth", "AskDocs"],
            "business": ["india", "entrepreneur", "IndiaInvestments", "business"]
        }
        
        # Indian subreddits for targeted content
        self.indian_subreddits = [
            'india', 'indiaspeaks', 'indianews', 'mumbai', 'delhi', 'bangalore',
            'chennai', 'kolkata', 'pune', 'hyderabad', 'ahmedabad', 'jaipur',
            'IndianStudents', 'IndianAcademia', 'IndianFood', 'bollywood',
            'cricket', 'IndianGaming', 'IndianPersonalFinance'
        ]
        
        # Educational subreddits for Q&A
        self.educational_subreddits = [
            'AskReddit', 'explainlikeimfive', 'NoStupidQuestions', 'answers',
            'HomeworkHelp', 'learnpython', 'learnjavascript', 'EngineeringStudents',
            'AskScience', 'AskHistorians', 'math', 'physics', 'chemistry'
        ]
    
    def generate_oauth_url(self, state: str = None) -> Dict[str, str]:
        """
        Generate Reddit OAuth authorization URL
        
        Args:
            state: CSRF protection token
            
        Returns:
            Dictionary with authorization URL and state
        """
        if not self.is_configured:
            return {
                "success": False,
                "error": "Reddit OAuth not configured",
                "message": "Please configure Reddit OAuth credentials"
            }
        
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "state": state,
            "redirect_uri": self.redirect_uri,
            "duration": "permanent",
            "scope": "identity read submit edit vote save subscribe privatemessages"
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        
        return {
            "success": True,
            "authorization_url": auth_url,
            "state": state
        }
    
    async def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            authorization_code: Code from Reddit OAuth callback
            
        Returns:
            Token information or error
        """
        try:
            if not self.is_configured:
                return {
                    "success": False,
                    "error": "Reddit OAuth not configured",
                    "message": "Please configure Reddit OAuth credentials"
                }
            
            # Prepare token exchange request
            token_data = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": self.redirect_uri
            }
            
            # Basic authentication with client credentials
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                "Authorization": f"Basic {auth_b64}",
                "User-Agent": self.user_agent,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Exchange code for token
            response = requests.post(
                self.token_url,
                data=token_data,
                headers=headers
            )
            
            if response.status_code == 200:
                token_info = response.json()
                
                # Get user information
                user_info = await self.get_reddit_user_info(token_info["access_token"])
                
                return {
                    "success": True,
                    "access_token": token_info["access_token"],
                    "refresh_token": token_info.get("refresh_token"),
                    "expires_in": token_info.get("expires_in", 3600),
                    "scope": token_info.get("scope", ""),
                    "user_info": user_info,
                    "message": "OAuth token exchange successful"
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("error", "Token exchange failed"),
                    "error_description": error_data.get("error_description", ""),
                    "message": "Failed to exchange code for token"
                }
                
        except Exception as e:
            logger.error(f"OAuth token exchange failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "OAuth token exchange failed"
            }
    
    async def get_reddit_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get Reddit user information using access token
        
        Args:
            access_token: Reddit OAuth access token
            
        Returns:
            User information
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "User-Agent": self.user_agent
            }
            
            response = requests.get(
                f"{self.api_base}/api/v1/me",
                headers=headers
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "username": user_data.get("name"),
                    "user_id": user_data.get("id"),
                    "created_utc": user_data.get("created_utc"),
                    "comment_karma": user_data.get("comment_karma", 0),
                    "link_karma": user_data.get("link_karma", 0),
                    "is_verified": user_data.get("verified", False)
                }
            else:
                logger.error(f"Failed to get user info: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Get Reddit user info failed: {e}")
            return {}
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt token for secure storage"""
        if self.cipher and token:
            return self.cipher.encrypt(token.encode()).decode()
        return token
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt token for API usage"""
        if self.cipher and encrypted_token:
            try:
                return self.cipher.decrypt(encrypted_token.encode()).decode()
            except:
                return encrypted_token
        return encrypted_token
    
    async def post_content_with_token(
        self,
        access_token: str,
        subreddit_name: str,
        title: str,
        content: str,
        content_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Post content to Reddit using OAuth token
        
        Args:
            access_token: User's Reddit access token
            subreddit_name: Target subreddit
            title: Post title
            content: Post content
            content_type: Type of content (text, link)
            
        Returns:
            Post result
        """
        try:
            self._rate_limit_check("post_content")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "User-Agent": self.user_agent,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Prepare post data
            if content_type == "text":
                post_data = {
                    "sr": subreddit_name,
                    "kind": "self",
                    "title": title,
                    "text": content,
                    "api_type": "json"
                }
            elif content_type == "link":
                post_data = {
                    "sr": subreddit_name,
                    "kind": "link",
                    "title": title,
                    "url": content,
                    "api_type": "json"
                }
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Submit post
            response = requests.post(
                f"{self.api_base}/api/submit",
                data=post_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result_data = response.json()
                
                if result_data.get("json", {}).get("errors"):
                    errors = result_data["json"]["errors"]
                    return {
                        "success": False,
                        "error": f"Reddit API errors: {errors}",
                        "message": "Failed to post content"
                    }
                
                # Extract post information
                post_info = result_data.get("json", {}).get("data", {})
                post_url = post_info.get("url", "")
                
                return {
                    "success": True,
                    "post_id": post_info.get("id"),
                    "post_url": post_url,
                    "title": title,
                    "subreddit": subreddit_name,
                    "created_utc": datetime.now().timestamp(),
                    "platform": "reddit",
                    "message": "Content posted successfully to Reddit"
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "message": "Failed to post content to Reddit"
                }
                
        except Exception as e:
            logger.error(f"Reddit posting with token failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to post content to Reddit"
            }
    
    async def reply_to_post_with_token(
        self,
        access_token: str,
        post_id: str,
        reply_content: str
    ) -> Dict[str, Any]:
        """
        Reply to a Reddit post using OAuth token
        
        Args:
            access_token: User's Reddit access token
            post_id: Reddit post ID to reply to
            reply_content: Reply content
            
        Returns:
            Reply result
        """
        try:
            self._rate_limit_check("post_reply")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "User-Agent": self.user_agent,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            reply_data = {
                "thing_id": f"t3_{post_id}",  # t3_ prefix for posts
                "text": reply_content,
                "api_type": "json"
            }
            
            response = requests.post(
                f"{self.api_base}/api/comment",
                data=reply_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result_data = response.json()
                
                if result_data.get("json", {}).get("errors"):
                    errors = result_data["json"]["errors"]
                    return {
                        "success": False,
                        "error": f"Reddit API errors: {errors}",
                        "message": "Failed to post reply"
                    }
                
                comment_info = result_data.get("json", {}).get("data", {}).get("things", [{}])[0]
                comment_data = comment_info.get("data", {})
                
                return {
                    "success": True,
                    "comment_id": comment_data.get("id"),
                    "comment_url": f"https://reddit.com{comment_data.get('permalink', '')}",
                    "parent_post_id": post_id,
                    "content": reply_content,
                    "created_utc": datetime.now().timestamp(),
                    "platform": "reddit",
                    "message": "Reply posted successfully on Reddit"
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "message": "Failed to post reply on Reddit"
                }
                
        except Exception as e:
            logger.error(f"Reddit reply with token failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to post reply on Reddit"
            }
    
    async def monitor_questions(
        self, 
        subreddits: List[str] = None,
        keywords: List[str] = None,
        limit: int = 10
    ) -> List[RedditPost]:
        """
        Monitor Reddit for new questions and discussion opportunities
        
        Args:
            subreddits: List of subreddits to monitor
            keywords: Keywords to filter posts
            limit: Maximum number of posts to return
            
        Returns:
            List of RedditPost objects
        """
        try:
            self._rate_limit_check("monitor_questions")
            
            if subreddits is None:
                subreddits = self.educational_subreddits
            
            questions = []
            
            for subreddit_name in subreddits:
                try:
                    # Get recent posts from subreddit
                    response = requests.get(
                        f"https://www.reddit.com/r/{subreddit_name}/new.json",
                        headers={"User-Agent": self.user_agent},
                        params={"limit": limit}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get("data", {}).get("children", [])
                        
                        for post_data in posts:
                            post = post_data.get("data", {})
                            
                            # Check if it's a question
                            if self._is_question_post(post.get("title", ""), post.get("selftext", "")):
                                
                                # Filter by keywords if provided
                                if keywords:
                                    title_lower = post.get("title", "").lower()
                                    if not any(keyword.lower() in title_lower for keyword in keywords):
                                        continue
                                
                                question = RedditPost(
                                    id=post.get("id"),
                                    title=post.get("title"),
                                    content=post.get("selftext", ""),
                                    subreddit=post.get("subreddit"),
                                    score=post.get("score", 0),
                                    num_comments=post.get("num_comments", 0),
                                    created_utc=post.get("created_utc", 0),
                                    url=f"https://reddit.com{post.get('permalink', '')}",
                                    author=post.get("author", "[deleted]"),
                                    is_self=post.get("is_self", True)
                                )
                                questions.append(question)
                
                except Exception as e:
                    logger.warning(f"Error monitoring subreddit {subreddit_name}: {e}")
                    continue
            
            # Sort by creation time (newest first) and return limited results
            questions.sort(key=lambda x: x.created_utc, reverse=True)
            return questions[:limit]
            
        except Exception as e:
            logger.error(f"Monitor questions failed: {e}")
            return []
    
    def get_domain_subreddits(self, domain: str) -> List[str]:
        """
        Get recommended subreddits for a business domain
        
        Args:
            domain: Business domain (education, restaurant, tech, health, business)
            
        Returns:
            List of recommended subreddits
        """
        return self.domain_subreddits.get(domain, self.indian_subreddits[:5])
    
    def _is_question_post(self, title: str, content: str) -> bool:
        """
        Determine if a post is asking a question
        
        Args:
            title: Post title
            content: Post content
            
        Returns:
            Boolean indicating if post is a question
        """
        question_indicators = [
            '?', 'how', 'what', 'why', 'where', 'when', 'which', 'who',
            'help', 'need', 'please', 'advice', 'suggest', 'recommend',
            'explain', 'understand', 'confusion', 'doubt', 'problem'
        ]
        
        # Hindi question indicators
        hindi_indicators = [
            'कैसे', 'क्या', 'क्यों', 'कहाँ', 'कब', 'कौन', 'कौन सा',
            'मदद', 'सहायता', 'सुझाव', 'सलाह', 'समझाइए', 'बताइए'
        ]
        
        all_indicators = question_indicators + hindi_indicators
        text_to_check = (title + ' ' + content).lower()
        
        return any(indicator in text_to_check for indicator in all_indicators)
    
    def _rate_limit_check(self, endpoint: str) -> None:
        """Implement rate limiting to avoid Reddit API limits"""
        current_time = datetime.now()
        
        if endpoint in self.last_request_time:
            time_diff = (current_time - self.last_request_time[endpoint]).total_seconds()
            if time_diff < self.min_request_interval:
                import time
                sleep_time = self.min_request_interval - time_diff
                time.sleep(sleep_time)
        
        self.last_request_time[endpoint] = current_time
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check Reddit API connection health
        
        Returns:
            Dictionary containing health status
        """
        try:
            return {
                "success": True,
                "status": "healthy" if self.is_configured else "degraded",
                "message": "Reddit OAuth connector health check completed",
                "client_configured": bool(self.client_id and self.client_secret),
                "encryption_available": bool(self.cipher),
                "oauth_ready": self.is_configured
            }
            
        except Exception as e:
            logger.error(f"Reddit health check failed: {e}")
            return {
                "success": False,
                "status": "unhealthy",
                "error": str(e),
                "message": "Reddit OAuth connector health check failed"
            }

# Additional method to get user credentials (add to RedditOAuthConnector class)
async def get_user_reddit_credentials(self, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get stored Reddit credentials for a user
    This method should be implemented in your database manager
    """
    # This is a placeholder - implement in your database manager
    return None