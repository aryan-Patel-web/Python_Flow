"""
OAuth Handlers for Social Media Platforms
Implements OAuth 2.0 flow for each supported platform
"""

import os
import requests
from abc import ABC, abstractmethod
from typing import Dict, Optional
from urllib.parse import urlencode
from flask import current_app



class BaseOAuthHandler(ABC):
    """Base class for OAuth handlers"""
    
    def __init__(self):
        self.client_id = None
        self.client_secret = None
        self.redirect_uri = f"{os.getenv('BACKEND_URL', 'http://localhost:5000')}/api/oauth/callback/{self.platform}"
    
    @property
    @abstractmethod
    def platform(self) -> str:
        pass
    
    @property
    @abstractmethod
    def auth_url(self) -> str:
        pass
    
    @property
    @abstractmethod
    def token_url(self) -> str:
        pass
    
    @property
    @abstractmethod
    def scope(self) -> str:
        pass
    
    @abstractmethod
    def get_user_profile(self, access_token: str) -> Dict:
        pass
    
    def get_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'state': state,
            'response_type': 'code'
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            current_app.logger.error(f'Token exchange failed for {self.platform}: {str(e)}')
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh access token using refresh token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            current_app.logger.error(f'Token refresh failed for {self.platform}: {str(e)}')
            return None
    
    def test_connection(self, access_token: str) -> bool:
        """Test if the access token is valid"""
        try:
            profile = self.get_user_profile(access_token)
            return profile is not None
        except Exception:
            return False

class FacebookOAuthHandler(BaseOAuthHandler):
    """Facebook OAuth handler"""
    
    def __init__(self):
        super().__init__()
        self.client_id = os.getenv('FACEBOOK_APP_ID')
        self.client_secret = os.getenv('FACEBOOK_APP_SECRET')
    
    @property
    def platform(self) -> str:
        return 'facebook'
    
    @property
    def auth_url(self) -> str:
        return 'https://www.facebook.com/v18.0/dialog/oauth'
    
    @property
    def token_url(self) -> str:
        return 'https://graph.facebook.com/v18.0/oauth/access_token'
    
    @property
    def scope(self) -> str:
        return 'pages_manage_posts,pages_read_engagement,pages_show_list,publish_video'
    
    def get_user_profile(self, access_token: str) -> Dict:
        """Get Facebook user profile"""
        try:
            # Get user info
            user_url = f'https://graph.facebook.com/v18.0/me?fields=id,name,email&access_token={access_token}'
            user_response = requests.get(user_url)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Get pages managed by user
            pages_url = f'https://graph.facebook.com/v18.0/me/accounts?access_token={access_token}'
            pages_response = requests.get(pages_url)
            pages_response.raise_for_status()
            pages_data = pages_response.json()
            
            return {
                'id': user_data.get('id'),
                'username': user_data.get('name'),
                'email': user_data.get('email'),
                'profile_image': f"https://graph.facebook.com/v18.0/{user_data.get('id')}/picture",
                'pages': pages_data.get('data', [])
            }
        except Exception as e:
            current_app.logger.error(f'Facebook profile fetch failed: {str(e)}')
            return {}

class InstagramOAuthHandler(BaseOAuthHandler):
    """Instagram Business OAuth handler"""
    
    def __init__(self):
        super().__init__()
        self.client_id = os.getenv('INSTAGRAM_APP_ID') or os.getenv('FACEBOOK_APP_ID')
        self.client_secret = os.getenv('INSTAGRAM_APP_SECRET') or os.getenv('FACEBOOK_APP_SECRET')
    
    @property
    def platform(self) -> str:
        return 'instagram'
    
    @property
    def auth_url(self) -> str:
        return 'https://www.facebook.com/v18.0/dialog/oauth'
    
    @property
    def token_url(self) -> str:
        return 'https://graph.facebook.com/v18.0/oauth/access_token'
    
    @property
    def scope(self) -> str:
        return 'instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement'
    
    def get_user_profile(self, access_token: str) -> Dict:
        """Get Instagram Business account profile"""
        try:
            # Get Facebook pages first
            pages_url = f'https://graph.facebook.com/v18.0/me/accounts?access_token={access_token}'
            pages_response = requests.get(pages_url)
            pages_response.raise_for_status()
            pages_data = pages_response.json()
            
            instagram_accounts = []
            
            # Get Instagram accounts linked to pages
            for page in pages_data.get('data', []):
                page_token = page.get('access_token')
                ig_url = f'https://graph.facebook.com/v18.0/{page["id"]}?fields=instagram_business_account&access_token={page_token}'
                ig_response = requests.get(ig_url)
                
                if ig_response.status_code == 200:
                    ig_data = ig_response.json()
                    if 'instagram_business_account' in ig_data:
                        ig_account_id = ig_data['instagram_business_account']['id']
                        
                        # Get Instagram account details
                        ig_details_url = f'https://graph.facebook.com/v18.0/{ig_account_id}?fields=id,username,profile_picture_url&access_token={page_token}'
                        ig_details_response = requests.get(ig_details_url)
                        
                        if ig_details_response.status_code == 200:
                            ig_details = ig_details_response.json()
                            instagram_accounts.append({
                                'id': ig_details.get('id'),
                                'username': ig_details.get('username'),
                                'profile_picture': ig_details.get('profile_picture_url'),
                                'page_id': page['id'],
                                'page_token': page_token
                            })
            
            return {
                'id': instagram_accounts[0]['id'] if instagram_accounts else None,
                'username': instagram_accounts[0]['username'] if instagram_accounts else None,
                'profile_image': instagram_accounts[0]['profile_picture'] if instagram_accounts else None,
                'accounts': instagram_accounts
            }
        except Exception as e:
            current_app.logger.error(f'Instagram profile fetch failed: {str(e)}')
            return {}

class TwitterOAuthHandler(BaseOAuthHandler):
    """Twitter/X OAuth 2.0 handler"""
    
    def __init__(self):
        super().__init__()
        self.client_id = os.getenv('TWITTER_CLIENT_ID')
        self.client_secret = os.getenv('TWITTER_CLIENT_SECRET')
    
    @property
    def platform(self) -> str:
        return 'twitter'
    
    @property
    def auth_url(self) -> str:
        return 'https://twitter.com/i/oauth2/authorize'
    
    @property
    def token_url(self) -> str:
        return 'https://api.twitter.com/2/oauth2/token'
    
    @property
    def scope(self) -> str:
        return 'tweet.read tweet.write users.read offline.access'
    
    def get_authorization_url(self, state: str) -> str:
        """Generate Twitter OAuth 2.0 authorization URL"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'state': state,
            'code_challenge': 'challenge',  # For PKCE - implement properly in production
            'code_challenge_method': 'plain'
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    def get_user_profile(self, access_token: str) -> Dict:
        """Get Twitter user profile"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = 'https://api.twitter.com/2/users/me?user.fields=id,name,username,profile_image_url,public_metrics'
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            user_data = data.get('data', {})
            
            return {
                'id': user_data.get('id'),
                'username': user_data.get('username'),
                'display_name': user_data.get('name'),
                'profile_image': user_data.get('profile_image_url'),
                'followers_count': user_data.get('public_metrics', {}).get('followers_count', 0),
                'following_count': user_data.get('public_metrics', {}).get('following_count', 0)
            }
        except Exception as e:
            current_app.logger.error(f'Twitter profile fetch failed: {str(e)}')
            return {}

class LinkedInOAuthHandler(BaseOAuthHandler):
    """LinkedIn OAuth handler"""
    
    def __init__(self):
        super().__init__()
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    
    @property
    def platform(self) -> str:
        return 'linkedin'
    
    @property
    def auth_url(self) -> str:
        return 'https://www.linkedin.com/oauth/v2/authorization'
    
    @property
    def token_url(self) -> str:
        return 'https://www.linkedin.com/oauth/v2/accessToken'
    
    @property
    def scope(self) -> str:
        return 'r_liteprofile r_emailaddress w_member_social'
    
    def get_user_profile(self, access_token: str) -> Dict:
        """Get LinkedIn user profile"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get profile info
            profile_url = 'https://api.linkedin.com/v2/people/~?projection=(id,firstName,lastName,profilePicture(displayImage~:playableStreams))'
            profile_response = requests.get(profile_url, headers=headers)
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            
            # Get email
            email_url = 'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))'
            email_response = requests.get(email_url, headers=headers)
            email_data = email_response.json() if email_response.status_code == 200 else {}
            
            email = None
            if 'elements' in email_data and email_data['elements']:
                email = email_data['elements'][0]['handle~']['emailAddress']
            
            return {
                'id': profile_data.get('id'),
                'username': f"{profile_data.get('firstName', {}).get('localized', {}).get('en_US', '')} {profile_data.get('lastName', {}).get('localized', {}).get('en_US', '')}".strip(),
                'email': email,
                'profile_image': self._extract_profile_image(profile_data),
                'first_name': profile_data.get('firstName', {}).get('localized', {}).get('en_US', ''),
                'last_name': profile_data.get('lastName', {}).get('localized', {}).get('en_US', '')
            }
        except Exception as e:
            current_app.logger.error(f'LinkedIn profile fetch failed: {str(e)}')
            return {}
    
    def _extract_profile_image(self, profile_data: Dict) -> str:
        """Extract profile image URL from LinkedIn response"""
        try:
            profile_picture = profile_data.get('profilePicture', {})
            display_image = profile_picture.get('displayImage~', {})
            elements = display_image.get('elements', [])
            
            for element in elements:
                identifiers = element.get('identifiers', [])
                if identifiers:
                    return identifiers[0].get('identifier', '')
        except Exception:
            pass
        return ''

class YouTubeOAuthHandler(BaseOAuthHandler):
    """YouTube Data API OAuth handler"""
    
    def __init__(self):
        super().__init__()
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    @property
    def platform(self) -> str:
        return 'youtube'
    
    @property
    def auth_url(self) -> str:
        return 'https://accounts.google.com/o/oauth2/auth'
    
    @property
    def token_url(self) -> str:
        return 'https://oauth2.googleapis.com/token'
    
    @property
    def scope(self) -> str:
        return 'https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube'
    
    def get_user_profile(self, access_token: str) -> Dict:
        """Get YouTube channel information"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = 'https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&mine=true'
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if 'items' in data and data['items']:
                channel = data['items'][0]
                snippet = channel.get('snippet', {})
                statistics = channel.get('statistics', {})
                
                return {
                    'id': channel.get('id'),
                    'username': snippet.get('title'),
                    'display_name': snippet.get('title'),
                    'profile_image': snippet.get('thumbnails', {}).get('default', {}).get('url'),
                    'subscriber_count': statistics.get('subscriberCount', 0),
                    'video_count': statistics.get('videoCount', 0),
                    'view_count': statistics.get('viewCount', 0)
                }
            return {}
        except Exception as e:
            current_app.logger.error(f'YouTube profile fetch failed: {str(e)}')
            return {}

class TikTokOAuthHandler(BaseOAuthHandler):
    """TikTok for Business OAuth handler"""
    
    def __init__(self):
        super().__init__()
        self.client_id = os.getenv('TIKTOK_CLIENT_ID')
        self.client_secret = os.getenv('TIKTOK_CLIENT_SECRET')
    
    @property
    def platform(self) -> str:
        return 'tiktok'
    
    @property
    def auth_url(self) -> str:
        return 'https://www.tiktok.com/auth/authorize/'
    
    @property
    def token_url(self) -> str:
        return 'https://open-api.tiktok.com/oauth/access_token/'
    
    @property
    def scope(self) -> str:
        return 'user.info.basic,video.list,video.upload'
    
    def get_user_profile(self, access_token: str) -> Dict:
        """Get TikTok user profile"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = 'https://open-api.tiktok.com/user/info/'
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            user_data = data.get('data', {}).get('user', {})
            
            return {
                'id': user_data.get('open_id'),
                'username': user_data.get('display_name'),
                'profile_image': user_data.get('avatar_url'),
                'follower_count': user_data.get('follower_count', 0),
                'following_count': user_data.get('following_count', 0),
                'likes_count': user_data.get('likes_count', 0)
            }
        except Exception as e:
            current_app.logger.error(f'TikTok profile fetch failed: {str(e)}')
            return {}

class PinterestOAuthHandler(BaseOAuthHandler):
    """Pinterest OAuth handler"""
    
    def __init__(self):
        super().__init__()
        self.client_id = os.getenv('PINTEREST_CLIENT_ID')
        self.client_secret = os.getenv('PINTEREST_CLIENT_SECRET')
    
    @property
    def platform(self) -> str:
        return 'pinterest'
    
    @property
    def auth_url(self) -> str:
        return 'https://www.pinterest.com/oauth/'
    
    @property
    def token_url(self) -> str:
        return 'https://api.pinterest.com/v5/oauth/token'
    
    @property
    def scope(self) -> str:
        return 'user_accounts:read,boards:read,boards:write,pins:read,pins:write'
    
    def get_user_profile(self, access_token: str) -> Dict:
        """Get Pinterest user profile"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = 'https://api.pinterest.com/v5/user_account'
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'id': data.get('id'),
                'username': data.get('username'),
                'profile_image': data.get('profile_image'),
                'follower_count': data.get('follower_count', 0),
                'following_count': data.get('following_count', 0),
                'board_count': data.get('board_count', 0)
            }
        except Exception as e:
            current_app.logger.error(f'Pinterest profile fetch failed: {str(e)}')
            return {}

# OAuth Handler Registry
OAUTH_HANDLERS = {
    'facebook': FacebookOAuthHandler,
    'instagram': InstagramOAuthHandler,
    'twitter': TwitterOAuthHandler,
    'linkedin': LinkedInOAuthHandler,
    'youtube': YouTubeOAuthHandler,
    'tiktok': TikTokOAuthHandler,
    'pinterest': PinterestOAuthHandler
}

def get_oauth_handler(platform: str) -> BaseOAuthHandler:
    """Get OAuth handler for platform"""
    handler_class = OAUTH_HANDLERS.get(platform.lower())
    if not handler_class:
        raise ValueError(f"Unsupported platform: {platform}")
    return handler_class()

def get_supported_platforms() -> Dict:
    """Get list of supported platforms"""
    platforms = {}
    for platform_name, handler_class in OAUTH_HANDLERS.items():
        handler = handler_class()
        platforms[platform_name] = {
            'name': platform_name,
            'display_name': platform_name.title(),
            'auth_url': handler.auth_url,
            'supports_refresh': True
        }
    return platforms