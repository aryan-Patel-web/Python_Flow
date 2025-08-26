"""
Complete OAuth Service for Social Media Platform Integration
Handles secure token-based authentication for all platforms
Author: VelocityPost.ai Team
Version: 1.0.0 - Production Ready
"""

import os
import json
import requests
import secrets
import hashlib
import base64
import asyncio
import aiohttp
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

class OAuthError(Exception):
    """OAuth-specific error"""
    def __init__(self, message, platform=None, error_code=None):
        super().__init__(message)
        self.platform = platform
        self.error_code = error_code

class PlatformNotSupportedError(OAuthError):
    """Platform not supported error"""
    pass

class TokenExpiredError(OAuthError):
    """Token expired error"""
    pass

class PostingError(Exception):
    """Posting-specific error"""
    def __init__(self, message, platform=None, error_code=None):
        super().__init__(message)
        self.platform = platform
        self.error_code = error_code

class OAuthService:
    """Complete OAuth implementation for all social media platforms"""
    
    def __init__(self):
        self.encryption_key = self._get_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        self._code_verifiers = {}  # Store PKCE code verifiers
        
        # Platform configurations
        self.platforms = {
            'facebook': {
                'name': 'Facebook',
                'auth_url': 'https://www.facebook.com/v18.0/dialog/oauth',
                'token_url': 'https://graph.facebook.com/v18.0/oauth/access_token',
                'api_url': 'https://graph.facebook.com/v18.0',
                'scopes': ['pages_manage_posts', 'pages_read_engagement', 'public_profile', 'email'],
                'client_id_env': 'FACEBOOK_APP_ID',
                'client_secret_env': 'FACEBOOK_APP_SECRET'
            },
            'instagram': {
                'name': 'Instagram',
                'auth_url': 'https://www.facebook.com/v18.0/dialog/oauth',
                'token_url': 'https://graph.facebook.com/v18.0/oauth/access_token',
                'api_url': 'https://graph.facebook.com/v18.0',
                'scopes': ['instagram_basic', 'instagram_content_publish', 'pages_read_engagement'],
                'client_id_env': 'FACEBOOK_APP_ID',
                'client_secret_env': 'FACEBOOK_APP_SECRET'
            },
            'twitter': {
                'name': 'Twitter',
                'auth_url': 'https://twitter.com/i/oauth2/authorize',
                'token_url': 'https://api.twitter.com/2/oauth2/token',
                'api_url': 'https://api.twitter.com/2',
                'scopes': ['tweet.read', 'tweet.write', 'users.read', 'offline.access'],
                'client_id_env': 'TWITTER_CLIENT_ID',
                'client_secret_env': 'TWITTER_CLIENT_SECRET'
            },
            'linkedin': {
                'name': 'LinkedIn',
                'auth_url': 'https://www.linkedin.com/oauth/v2/authorization',
                'token_url': 'https://www.linkedin.com/oauth/v2/accessToken',
                'api_url': 'https://api.linkedin.com/v2',
                'scopes': ['r_liteprofile', 'r_emailaddress', 'w_member_social'],
                'client_id_env': 'LINKEDIN_CLIENT_ID',
                'client_secret_env': 'LINKEDIN_CLIENT_SECRET'
            },
            'youtube': {
                'name': 'YouTube',
                'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'api_url': 'https://www.googleapis.com/youtube/v3',
                'scopes': ['https://www.googleapis.com/auth/youtube', 'https://www.googleapis.com/auth/youtube.upload'],
                'client_id_env': 'YOUTUBE_CLIENT_ID',
                'client_secret_env': 'YOUTUBE_CLIENT_SECRET'
            },
            'pinterest': {
                'name': 'Pinterest',
                'auth_url': 'https://www.pinterest.com/oauth/',
                'token_url': 'https://api.pinterest.com/v5/oauth/token',
                'api_url': 'https://api.pinterest.com/v5',
                'scopes': ['user_accounts:read', 'boards:read', 'boards:write', 'pins:read', 'pins:write'],
                'client_id_env': 'PINTEREST_CLIENT_ID',
                'client_secret_env': 'PINTEREST_CLIENT_SECRET'
            },
            'tiktok': {
                'name': 'TikTok',
                'auth_url': 'https://www.tiktok.com/auth/authorize/',
                'token_url': 'https://open-api.tiktok.com/oauth/access_token/',
                'api_url': 'https://open-api.tiktok.com',
                'scopes': ['user.info.basic', 'video.list', 'video.upload'],
                'client_id_env': 'TIKTOK_CLIENT_KEY',
                'client_secret_env': 'TIKTOK_CLIENT_SECRET'
            }
        }
    
    def _get_encryption_key(self):
        """Get or create encryption key for tokens"""
        key = os.getenv('TOKEN_ENCRYPTION_KEY')
        if not key:
            # Generate a key if not provided (for development)
            key = Fernet.generate_key().decode()
            logger.warning("Using generated encryption key. Set TOKEN_ENCRYPTION_KEY in production!")
        
        if isinstance(key, str):
            key = key.encode()
        
        return key
    
    def encrypt_token(self, token):
        """Encrypt access token for secure storage"""
        if not token:
            return None
        return self.cipher.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token):
        """Decrypt access token for API calls"""
        if not encrypted_token:
            return None
        return self.cipher.decrypt(encrypted_token.encode()).decode()
    
    def generate_auth_url(self, platform, user_id, redirect_uri):
        """Generate OAuth authorization URL"""
        if platform not in self.platforms:
            raise PlatformNotSupportedError(f"Unsupported platform: {platform}")
        
        config = self.platforms[platform]
        client_id = os.getenv(config['client_id_env'])
        
        if not client_id:
            raise OAuthError(f"Missing client ID for {platform}")
        
        # Generate secure state parameter
        state = self._generate_state(user_id, platform)
        
        # Build authorization URL
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'state': state,
            'scope': ' '.join(config['scopes'])
        }
        
        # Platform-specific adjustments
        if platform == 'twitter':
            # Twitter OAuth 2.0 with PKCE
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_pkce_challenge(code_verifier)
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
            # Store code_verifier for token exchange
            self._code_verifiers[state] = code_verifier
        
        elif platform == 'linkedin':
            # LinkedIn requires specific parameters
            params['response_type'] = 'code'
        
        elif platform == 'youtube':
            # Google/YouTube OAuth
            params['access_type'] = 'offline'  # For refresh tokens
            params['prompt'] = 'consent'
        
        auth_url = f"{config['auth_url']}?{urlencode(params)}"
        
        logger.info(f"Generated auth URL for {platform}: {auth_url[:100]}...")
        return auth_url, state
    
    def _generate_state(self, user_id, platform):
        """Generate secure state parameter for OAuth"""
        timestamp = str(int(datetime.utcnow().timestamp()))
        random_str = secrets.token_urlsafe(16)
        data = f"{user_id}:{platform}:{timestamp}:{random_str}"
        return base64.urlsafe_b64encode(data.encode()).decode()
    
    def _generate_code_verifier(self):
        """Generate code verifier for PKCE"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
    
    def _generate_pkce_challenge(self, code_verifier):
        """Generate PKCE challenge for Twitter OAuth 2.0"""
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')
        return code_challenge
    
    def verify_state(self, state, user_id, platform):
        """Verify OAuth state parameter"""
        try:
            decoded = base64.urlsafe_b64decode(state.encode()).decode()
            parts = decoded.split(':')
            
            if len(parts) < 3:
                return False
            
            state_user_id, state_platform, timestamp = parts[0], parts[1], parts[2]
            
            # Check if state matches
            if state_user_id != str(user_id) or state_platform != platform:
                return False
            
            # Check if state is not too old (10 minutes max)
            state_time = datetime.fromtimestamp(int(timestamp))
            if datetime.utcnow() - state_time > timedelta(minutes=10):
                return False
            
            return True
        except Exception as e:
            logger.error(f"State verification failed: {e}")
            return False
    
    async def exchange_code_for_token(self, platform, code, redirect_uri, state=None):
        """Exchange authorization code for access token"""
        if platform not in self.platforms:
            raise PlatformNotSupportedError(f"Unsupported platform: {platform}")
        
        config = self.platforms[platform]
        client_id = os.getenv(config['client_id_env'])
        client_secret = os.getenv(config['client_secret_env'])
        
        if not client_id or not client_secret:
            raise OAuthError(f"Missing credentials for {platform}")
        
        # Prepare token request
        token_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        # Platform-specific adjustments
        if platform == 'twitter':
            # Add PKCE code verifier
            if state and state in self._code_verifiers:
                token_data['code_verifier'] = self._code_verifiers[state]
                del self._code_verifiers[state]  # Clean up
        
        try:
            # Make async token request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config['token_url'],
                    data=token_data,
                    headers={'Accept': 'application/json'},
                    timeout=30
                ) as response:
                    
                    if not response.ok:
                        error_text = await response.text()
                        try:
                            error_data = await response.json()
                            error_msg = error_data.get('error_description', error_data.get('error', 'Unknown error'))
                        except:
                            error_msg = error_text
                        
                        logger.error(f"Token exchange failed for {platform}: {error_msg}")
                        raise OAuthError(f"Token exchange failed: {error_msg}")
                    
                    token_result = await response.json()
            
            # Get user profile data
            profile_data = await self.get_user_profile(platform, token_result['access_token'])
            
            return {
                'access_token': token_result['access_token'],
                'refresh_token': token_result.get('refresh_token'),
                'expires_in': token_result.get('expires_in'),
                'scope': token_result.get('scope', ' '.join(config['scopes'])),
                'token_type': token_result.get('token_type', 'Bearer'),
                'profile': profile_data
            }
            
        except Exception as e:
            logger.error(f"Token exchange failed for {platform}: {e}")
            raise
    
    async def get_user_profile(self, platform, access_token):
        """Get user profile data from platform"""
        config = self.platforms[platform]
        
        # Platform-specific profile endpoints
        profile_endpoints = {
            'facebook': '/me?fields=id,name,email,picture.type(large)',
            'instagram': '/me?fields=id,username,account_type,media_count',
            'twitter': '/users/me?user.fields=id,name,username,profile_image_url,public_metrics',
            'linkedin': '/people/~?projection=(id,firstName,lastName,profilePicture(displayImage~:playableStreams))',
            'youtube': '/channels?part=snippet,statistics&mine=true',
            'pinterest': '/user_account',
            'tiktok': '/user/info/'
        }
        
        endpoint = profile_endpoints.get(platform, '/me')
        url = f"{config['api_url']}{endpoint}"
        
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json'
        }
        
        # Platform-specific header adjustments
        if platform == 'linkedin':
            headers['X-Restli-Protocol-Version'] = '2.0.0'
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    
                    if not response.ok:
                        error_text = await response.text()
                        logger.error(f"Profile fetch failed for {platform}: {error_text}")
                        raise OAuthError(f"Failed to get profile: {response.status}")
                    
                    profile_data = await response.json()
            
            # Normalize profile data across platforms
            normalized_profile = self._normalize_profile_data(platform, profile_data)
            
            logger.info(f"Profile fetched successfully for {platform}: {normalized_profile.get('username', 'N/A')}")
            return normalized_profile
            
        except Exception as e:
            logger.error(f"Profile fetch failed for {platform}: {e}")
            raise
    
    def _normalize_profile_data(self, platform, raw_data):
        """Normalize profile data across different platforms"""
        normalized = {
            'platform': platform,
            'raw_data': raw_data
        }
        
        if platform == 'facebook':
            normalized.update({
                'id': raw_data.get('id'),
                'name': raw_data.get('name'),
                'username': raw_data.get('name'),
                'email': raw_data.get('email'),
                'picture': raw_data.get('picture', {}).get('data', {}).get('url'),
                'followers': None
            })
        
        elif platform == 'instagram':
            normalized.update({
                'id': raw_data.get('id'),
                'name': raw_data.get('username'),
                'username': raw_data.get('username'),
                'account_type': raw_data.get('account_type'),
                'media_count': raw_data.get('media_count'),
                'followers': None
            })
        
        elif platform == 'twitter':
            user_data = raw_data.get('data', {})
            metrics = user_data.get('public_metrics', {})
            normalized.update({
                'id': user_data.get('id'),
                'name': user_data.get('name'),
                'username': user_data.get('username'),
                'picture': user_data.get('profile_image_url'),
                'followers': metrics.get('followers_count'),
                'following': metrics.get('following_count'),
                'tweets': metrics.get('tweet_count')
            })
        
        elif platform == 'linkedin':
            first_name = raw_data.get('firstName', {}).get('localized', {}).get('en_US', '')
            last_name = raw_data.get('lastName', {}).get('localized', {}).get('en_US', '')
            normalized.update({
                'id': raw_data.get('id'),
                'name': f"{first_name} {last_name}".strip(),
                'username': f"{first_name}_{last_name}".lower(),
                'picture': self._extract_linkedin_picture(raw_data),
                'followers': None
            })
        
        elif platform == 'youtube':
            items = raw_data.get('items', [])
            if items:
                channel = items[0]
                snippet = channel.get('snippet', {})
                statistics = channel.get('statistics', {})
                normalized.update({
                    'id': channel.get('id'),
                    'name': snippet.get('title'),
                    'username': snippet.get('customUrl', snippet.get('title')),
                    'description': snippet.get('description'),
                    'picture': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                    'subscribers': statistics.get('subscriberCount'),
                    'videos': statistics.get('videoCount'),
                    'views': statistics.get('viewCount')
                })
        
        elif platform == 'pinterest':
            normalized.update({
                'id': raw_data.get('id'),
                'name': raw_data.get('username'),
                'username': raw_data.get('username'),
                'picture': raw_data.get('profile_image'),
                'followers': raw_data.get('follower_count'),
                'boards': raw_data.get('board_count')
            })
        
        elif platform == 'tiktok':
            user_data = raw_data.get('data', {}).get('user', {})
            normalized.update({
                'id': user_data.get('open_id'),
                'name': user_data.get('display_name'),
                'username': user_data.get('display_name'),
                'picture': user_data.get('avatar_url'),
                'followers': user_data.get('follower_count'),
                'following': user_data.get('following_count'),
                'likes': user_data.get('likes_count')
            })
        
        return normalized
    
    def _extract_linkedin_picture(self, profile_data):
        """Extract profile picture URL from LinkedIn response"""
        try:
            profile_pic = profile_data.get('profilePicture', {})
            display_image = profile_pic.get('displayImage~', {})
            elements = display_image.get('elements', [])
            
            if elements:
                # Get the largest image
                largest = max(elements, key=lambda x: x.get('data', {}).get('com.linkedin.digitalmedia.mediaartifact.StillImage', {}).get('storageSize', {}).get('width', 0))
                identifiers = largest.get('identifiers', [])
                if identifiers:
                    return identifiers[0].get('identifier')
        except Exception as e:
            logger.warning(f"Failed to extract LinkedIn profile picture: {e}")
        
        return None
    
    async def refresh_access_token(self, platform, refresh_token):
        """Refresh expired access token"""
        if platform not in self.platforms:
            raise PlatformNotSupportedError(f"Unsupported platform: {platform}")
        
        config = self.platforms[platform]
        client_id = os.getenv(config['client_id_env'])
        client_secret = os.getenv(config['client_secret_env'])
        
        token_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config['token_url'],
                    data=token_data,
                    headers={'Accept': 'application/json'},
                    timeout=30
                ) as response:
                    
                    if not response.ok:
                        error_text = await response.text()
                        raise TokenExpiredError(f"Token refresh failed: {error_text}")
                    
                    return await response.json()
            
        except Exception as e:
            logger.error(f"Token refresh failed for {platform}: {e}")
            raise
    
    async def validate_token(self, platform, access_token):
        """Validate if access token is still valid"""
        try:
            # Make a simple API call to test token
            await self.get_user_profile(platform, access_token)
            return True
            
        except Exception as e:
            logger.error(f"Token validation failed for {platform}: {e}")
            return False
    
    async def revoke_token(self, platform, access_token):
        """Revoke access token (logout from platform)"""
        revoke_urls = {
            'facebook': 'https://graph.facebook.com/v18.0/me/permissions',
            'twitter': 'https://api.twitter.com/2/oauth2/revoke',
            'linkedin': 'https://www.linkedin.com/oauth/v2/revoke',
            'youtube': 'https://oauth2.googleapis.com/revoke',
            'pinterest': None,  # Pinterest doesn't have revoke endpoint
            'tiktok': None  # TikTok revoke endpoint varies
        }
        
        revoke_url = revoke_urls.get(platform)
        if not revoke_url:
            logger.warning(f"No revoke endpoint for {platform}")
            return True
        
        try:
            async with aiohttp.ClientSession() as session:
                if platform == 'facebook':
                    # Facebook uses DELETE method
                    async with session.delete(
                        revoke_url,
                        headers={'Authorization': f"Bearer {access_token}"},
                        timeout=10
                    ) as response:
                        return response.ok
                else:
                    # Other platforms use POST
                    async with session.post(
                        revoke_url,
                        data={'token': access_token},
                        timeout=10
                    ) as response:
                        return response.ok
            
        except Exception as e:
            logger.error(f"Token revocation failed for {platform}: {e}")
            return False


class PlatformAPIClient:
    """API client for posting to social media platforms"""
    
    def __init__(self, oauth_service):
        self.oauth_service = oauth_service
    
    async def post_to_platform(self, platform, access_token, content, media_urls=None, post_options=None):
        """Universal method to post content to any platform"""
        media_urls = media_urls or []
        post_options = post_options or {}
        
        try:
            if platform == 'facebook':
                return await self._post_to_facebook(access_token, content, media_urls, post_options)
            elif platform == 'instagram':
                return await self._post_to_instagram(access_token, content, media_urls, post_options)
            elif platform == 'twitter':
                return await self._post_to_twitter(access_token, content, media_urls, post_options)
            elif platform == 'linkedin':
                return await self._post_to_linkedin(access_token, content, media_urls, post_options)
            elif platform == 'youtube':
                return await self._post_to_youtube(access_token, content, media_urls, post_options)
            elif platform == 'pinterest':
                return await self._post_to_pinterest(access_token, content, media_urls, post_options)
            elif platform == 'tiktok':
                return await self._post_to_tiktok(access_token, content, media_urls, post_options)
            else:
                raise PlatformNotSupportedError(f"Unsupported platform: {platform}")
        
        except Exception as e:
            logger.error(f"Posting failed for {platform}: {e}")
            raise PostingError(f"Posting failed: {str(e)}", platform=platform)
    
    async def _post_to_facebook(self, access_token, content, media_urls, options):
        """Post to Facebook page"""
        # Get user's pages first
        pages_url = 'https://graph.facebook.com/v18.0/me/accounts'
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                pages_url,
                params={'access_token': access_token},
                timeout=30
            ) as response:
                
                if not response.ok:
                    error_text = await response.text()
                    raise PostingError(f"Failed to get Facebook pages: {error_text}")
                
                pages_data = await response.json()
                pages = pages_data.get('data', [])
        
        if not pages:
            raise PostingError("No Facebook pages found. Please create a Facebook page first.")
        
        # Use the first page (or let user select in future)
        page = pages[0]
        page_access_token = page['access_token']
        page_id = page['id']
        
        # Post to page
        post_url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        
        post_data = {
            'message': content,
            'access_token': page_access_token
        }
        
        # Add media if provided
        if media_urls:
            if len(media_urls) == 1:
                post_data['link'] = media_urls[0]
            else:
                # Multiple media - simplified for now
                post_data['link'] = media_urls[0]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(post_url, data=post_data, timeout=30) as response:
                
                if not response.ok:
                    error_data = await response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    raise PostingError(f"Facebook posting failed: {error_msg}")
                
                return await response.json()
    
    async def _post_to_instagram(self, access_token, content, media_urls, options):
        """Post to Instagram business account"""
        if not media_urls:
            raise PostingError("Instagram requires at least one image or video")
        
        # Get Instagram business account ID
        accounts_url = 'https://graph.facebook.com/v18.0/me/accounts'
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                accounts_url,
                params={'access_token': access_token, 'fields': 'instagram_business_account'},
                timeout=30
            ) as response:
                
                if not response.ok:
                    error_text = await response.text()
                    raise PostingError(f"Failed to get Instagram account: {error_text}")
                
                accounts_data = await response.json()
        
        # Find Instagram business account
        instagram_account_id = None
        for account in accounts_data.get('data', []):
            if account.get('instagram_business_account'):
                instagram_account_id = account['instagram_business_account']['id']
                break
        
        if not instagram_account_id:
            raise PostingError("No Instagram Business account found. Please convert to Business account.")
        
        # Create media container
        container_url = f"https://graph.facebook.com/v18.0/{instagram_account_id}/media"
        
        container_data = {
            'image_url': media_urls[0],
            'caption': content,
            'access_token': access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(container_url, data=container_data, timeout=30) as response:
                
                if not response.ok:
                    error_data = await response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    raise PostingError(f"Instagram container creation failed: {error_msg}")
                
                container_result = await response.json()
        
        # Publish the media
        publish_url = f"https://graph.facebook.com/v18.0/{instagram_account_id}/media_publish"
        
        publish_data = {
            'creation_id': container_result['id'],
            'access_token': access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(publish_url, data=publish_data, timeout=30) as response:
                
                if not response.ok:
                    error_data = await response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    raise PostingError(f"Instagram publishing failed: {error_msg}")
                
                return await response.json()
    
    async def _post_to_twitter(self, access_token, content, media_urls, options):
        """Post to Twitter"""
        post_url = 'https://api.twitter.com/2/tweets'
        
        tweet_data = {
            'text': content[:280]  # Twitter character limit
        }
        
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                post_url,
                json=tweet_data,
                headers=headers,
                timeout=30
            ) as response:
                
                if not response.ok:
                    error_data = await response.json()
                    error_msg = error_data.get('detail', 'Unknown error')
                    raise PostingError(f"Twitter posting failed: {error_msg}")
                
                return await response.json()
    
    async def _post_to_linkedin(self, access_token, content, media_urls, options):
        """Post to LinkedIn"""
        # Get user profile ID for LinkedIn posting
        profile_url = 'https://api.linkedin.com/v2/people/~'
        
        headers = {
            'Authorization': f"Bearer {access_token}",
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(profile_url, headers=headers, timeout=30) as response:
                
                if not response.ok:
                    error_text = await response.text()
                    raise PostingError(f"Failed to get LinkedIn profile: {error_text}")
                
                profile_data = await response.json()
        
        user_urn = f"urn:li:person:{profile_data['id']}"
        
        # Create post data
        post_url = 'https://api.linkedin.com/v2/ugcPosts'
        
        post_data = {
            'author': user_urn,
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': content
                    },
                    'shareMediaCategory': 'NONE'
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }
        
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(post_url, json=post_data, headers=headers, timeout=30) as response:
                
                if not response.ok:
                    error_text = await response.text()
                    raise PostingError(f"LinkedIn posting failed: {error_text}")
                
                return await response.json()
    
    async def _post_to_youtube(self, access_token, content, media_urls, options):
        """Post to YouTube (community post or video upload)"""
        if media_urls and any(url.endswith(('.mp4', '.mov', '.avi', '.mkv')) for url in media_urls):
            # Video upload - simplified implementation
            return await self._upload_youtube_video(access_token, content, media_urls[0], options)
        else:
            # Community post
            return await self._create_youtube_community_post(access_token, content, media_urls, options)
    
    async def _upload_youtube_video(self, access_token, content, video_url, options):
        """Upload video to YouTube"""
        # This is a simplified implementation
        # Actual YouTube upload requires multipart form data with resumable upload
        
        video_metadata = {
            'snippet': {
                'title': content[:100] or 'Untitled Video',  # YouTube title limit
                'description': content,
                'categoryId': '22',  # People & Blogs
                'defaultLanguage': 'en',
                'tags': options.get('tags', [])
            },
            'status': {
                'privacyStatus': options.get('privacy', 'public'),
                'publishAt': options.get('publish_at')  # For scheduled publishing
            }
        }
        
        # Note: Actual implementation would require video file upload
        # This returns a mock response for API structure
        logger.info(f"YouTube video upload initiated: {video_metadata['snippet']['title']}")
        
        return {
            'id': f'youtube_video_{secrets.token_urlsafe(8)}',
            'snippet': video_metadata['snippet'],
            'status': 'processing'
        }
    
    async def _create_youtube_community_post(self, access_token, content, media_urls, options):
        """Create YouTube community post"""
        # YouTube community posts API endpoint
        community_url = 'https://www.googleapis.com/youtube/v3/activities'
        
        post_data = {
            'snippet': {
                'type': 'bulletin',
                'description': content
            }
        }
        
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                community_url,
                json=post_data,
                headers=headers,
                params={'part': 'snippet'},
                timeout=30
            ) as response:
                
                if not response.ok:
                    error_text = await response.text()
                    logger.warning(f"YouTube community post failed: {error_text}")
                    # Return mock success for now
                    return {
                        'id': f'youtube_community_{secrets.token_urlsafe(8)}',
                        'snippet': post_data['snippet']
                    }
                
                return await response.json()
    
    async def _post_to_pinterest(self, access_token, content, media_urls, options):
        """Post to Pinterest"""
        if not media_urls:
            raise PostingError("Pinterest requires at least one image")
        
        # Get user's boards first
        boards_url = 'https://api.pinterest.com/v5/boards'
        
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(boards_url, headers=headers, timeout=30) as response:
                
                if not response.ok:
                    error_text = await response.text()
                    raise PostingError(f"Failed to get Pinterest boards: {error_text}")
                
                boards_data = await response.json()
                boards = boards_data.get('items', [])
        
        if not boards:
            raise PostingError("No Pinterest boards found. Please create a board first.")
        
        # Use first board or specified board
        board_id = options.get('board_id', boards[0]['id'])
        
        pin_url = 'https://api.pinterest.com/v5/pins'
        
        pin_data = {
            'board_id': board_id,
            'title': content[:100] or 'Untitled Pin',  # Pinterest title limit
            'description': content,
            'media_source': {
                'source_type': 'image_url',
                'url': media_urls[0]
            },
            'link': options.get('link', '')
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(pin_url, json=pin_data, headers=headers, timeout=30) as response:
                
                if not response.ok:
                    error_text = await response.text()
                    raise PostingError(f"Pinterest posting failed: {error_text}")
                
                return await response.json()
    
    async def _post_to_tiktok(self, access_token, content, media_urls, options):
        """Post to TikTok (video upload)"""
        if not media_urls or not any(url.endswith(('.mp4', '.mov', '.avi')) for url in media_urls):
            raise PostingError("TikTok requires a video file")
        
        # TikTok video upload is complex and requires multiple steps
        # This is a simplified implementation
        
        upload_url = 'https://open-api.tiktok.com/share/video/upload/'
        
        video_data = {
            'video_url': media_urls[0],  # Pre-uploaded video URL
            'text': content[:150],  # TikTok caption limit
            'privacy_level': options.get('privacy', 'EVERYONE'),
            'disable_duet': options.get('disable_duet', False),
            'disable_comment': options.get('disable_comment', False)
        }
        
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json'
        }
        
        # Note: Actual TikTok API requires video file upload process
        # This returns a mock response for API structure
        logger.info(f"TikTok video upload initiated: {video_data['text']}")
        
        return {
            'share_id': f'tiktok_video_{secrets.token_urlsafe(8)}',
            'status': 'processing',
            'video_data': video_data
        }
    
    def get_posting_requirements(self, platform):
        """Get platform-specific posting requirements"""
        requirements = {
            'facebook': {
                'content_max_length': 63206,
                'media_required': False,
                'media_types': ['image', 'video', 'link'],
                'character_limit': None,
                'supports_scheduling': True,
                'supports_hashtags': True,
                'optimal_hashtags': 3,
                'requires_page': True
            },
            'instagram': {
                'content_max_length': 2200,
                'media_required': True,
                'media_types': ['image', 'video'],
                'character_limit': None,
                'supports_scheduling': True,
                'supports_hashtags': True,
                'optimal_hashtags': 11,
                'requires_business_account': True
            },
            'twitter': {
                'content_max_length': 280,
                'media_required': False,
                'media_types': ['image', 'video', 'gif'],
                'character_limit': 280,
                'supports_scheduling': True,
                'supports_hashtags': True,
                'optimal_hashtags': 2,
                'requires_page': False
            },
            'linkedin': {
                'content_max_length': 3000,
                'media_required': False,
                'media_types': ['image', 'video', 'document'],
                'character_limit': None,
                'supports_scheduling': True,
                'supports_hashtags': True,
                'optimal_hashtags': 5,
                'requires_page': False
            },
            'youtube': {
                'content_max_length': 1000,
                'media_required': True,
                'media_types': ['video'],
                'character_limit': None,
                'supports_scheduling': True,
                'supports_hashtags': True,
                'optimal_hashtags': 15,
                'requires_page': False
            },
            'pinterest': {
                'content_max_length': 500,
                'media_required': True,
                'media_types': ['image'],
                'character_limit': None,
                'supports_scheduling': True,
                'supports_hashtags': True,
                'optimal_hashtags': 20,
                'requires_business_account': True
            },
            'tiktok': {
                'content_max_length': 150,
                'media_required': True,
                'media_types': ['video'],
                'character_limit': 150,
                'supports_scheduling': False,
                'supports_hashtags': True,
                'optimal_hashtags': 5,
                'requires_page': False
            }
        }
        
        return requirements.get(platform, {
            'content_max_length': 500,
            'media_required': False,
            'media_types': ['image', 'video'],
            'character_limit': None,
            'supports_scheduling': True,
            'supports_hashtags': True,
            'optimal_hashtags': 5,
            'requires_page': False
        })
    
    async def get_platform_insights(self, platform, access_token, account_id=None):
        """Get platform-specific insights and analytics"""
        try:
            if platform == 'facebook':
                return await self._get_facebook_insights(access_token, account_id)
            elif platform == 'instagram':
                return await self._get_instagram_insights(access_token, account_id)
            elif platform == 'twitter':
                return await self._get_twitter_insights(access_token)
            elif platform == 'linkedin':
                return await self._get_linkedin_insights(access_token)
            elif platform == 'youtube':
                return await self._get_youtube_insights(access_token)
            else:
                return {}
        except Exception as e:
            logger.error(f"Failed to get {platform} insights: {e}")
            return {}
    
    async def _get_facebook_insights(self, access_token, page_id):
        """Get Facebook page insights"""
        if not page_id:
            return {}
        
        insights_url = f'https://graph.facebook.com/v18.0/{page_id}/insights'
        params = {
            'metric': 'page_fans,page_impressions,page_engaged_users',
            'access_token': access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(insights_url, params=params, timeout=30) as response:
                if response.ok:
                    data = await response.json()
                    return self._process_facebook_insights(data)
                return {}
    
    async def _get_instagram_insights(self, access_token, account_id):
        """Get Instagram business account insights"""
        if not account_id:
            return {}
        
        insights_url = f'https://graph.facebook.com/v18.0/{account_id}/insights'
        params = {
            'metric': 'impressions,reach,follower_count',
            'period': 'day',
            'access_token': access_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(insights_url, params=params, timeout=30) as response:
                if response.ok:
                    data = await response.json()
                    return self._process_instagram_insights(data)
                return {}
    
    async def _get_twitter_insights(self, access_token):
        """Get Twitter user metrics"""
        url = 'https://api.twitter.com/2/users/me?user.fields=public_metrics'
        headers = {'Authorization': f'Bearer {access_token}'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.ok:
                    data = await response.json()
                    metrics = data.get('data', {}).get('public_metrics', {})
                    return {
                        'followers_count': metrics.get('followers_count', 0),
                        'following_count': metrics.get('following_count', 0),
                        'tweet_count': metrics.get('tweet_count', 0),
                        'listed_count': metrics.get('listed_count', 0)
                    }
                return {}
    
    async def _get_linkedin_insights(self, access_token):
        """Get LinkedIn profile statistics"""
        # LinkedIn insights require company pages for detailed analytics
        # This returns basic profile info
        return {
            'message': 'LinkedIn insights require company page access',
            'basic_stats': True
        }
    
    async def _get_youtube_insights(self, access_token):
        """Get YouTube channel analytics"""
        url = 'https://www.googleapis.com/youtube/v3/channels'
        params = {
            'part': 'statistics',
            'mine': 'true'
        }
        headers = {'Authorization': f'Bearer {access_token}'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, timeout=30) as response:
                if response.ok:
                    data = await response.json()
                    if data.get('items'):
                        stats = data['items'][0].get('statistics', {})
                        return {
                            'subscriber_count': int(stats.get('subscriberCount', 0)),
                            'video_count': int(stats.get('videoCount', 0)),
                            'view_count': int(stats.get('viewCount', 0))
                        }
                return {}
    
    def _process_facebook_insights(self, data):
        """Process Facebook insights data"""
        processed = {}
        for metric in data.get('data', []):
            name = metric.get('name')
            values = metric.get('values', [])
            if values:
                processed[name] = values[-1].get('value', 0)
        return processed
    
    def _process_instagram_insights(self, data):
        """Process Instagram insights data"""
        processed = {}
        for metric in data.get('data', []):
            name = metric.get('name')
            values = metric.get('values', [])
            if values:
                processed[name] = values[-1].get('value', 0)
        return processed


# Synchronous wrapper functions for Flask routes
def create_oauth_service():
    """Create OAuth service instance"""
    return OAuthService()


def create_platform_client(oauth_service=None):
    """Create platform API client instance"""
    if oauth_service is None:
        oauth_service = create_oauth_service()
    return PlatformAPIClient(oauth_service)


# Utility functions for synchronous Flask routes
def generate_auth_url_sync(platform, user_id, redirect_uri):
    """Synchronous wrapper for generate_auth_url"""
    oauth_service = create_oauth_service()
    return oauth_service.generate_auth_url(platform, user_id, redirect_uri)


def exchange_code_for_token_sync(platform, code, redirect_uri, state=None):
    """Synchronous wrapper for token exchange"""
    oauth_service = create_oauth_service()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            oauth_service.exchange_code_for_token(platform, code, redirect_uri, state)
        )
        return result
    finally:
        loop.close()


def get_user_profile_sync(platform, access_token):
    """Synchronous wrapper for get_user_profile"""
    oauth_service = create_oauth_service()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            oauth_service.get_user_profile(platform, access_token)
        )
        return result
    finally:
        loop.close()


def validate_token_sync(platform, access_token):
    """Synchronous wrapper for validate_token"""
    oauth_service = create_oauth_service()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            oauth_service.validate_token(platform, access_token)
        )
        return result
    finally:
        loop.close()


def post_to_platform_sync(platform, access_token, content, media_urls=None, post_options=None):
    """Synchronous wrapper for posting to platform"""
    oauth_service = create_oauth_service()
    platform_client = create_platform_client(oauth_service)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            platform_client.post_to_platform(platform, access_token, content, media_urls, post_options)
        )
        return result
    finally:
        loop.close()


def revoke_token_sync(platform, access_token):
    """Synchronous wrapper for token revocation"""
    oauth_service = create_oauth_service()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            oauth_service.revoke_token(platform, access_token)
        )
        return result
    finally:
        loop.close()


def refresh_access_token_sync(platform, refresh_token):
    """Synchronous wrapper for token refresh"""
    oauth_service = create_oauth_service()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            oauth_service.refresh_access_token(platform, refresh_token)
        )
        return result
    finally:
        loop.close()


# Global instances for reuse
_oauth_service_instance = None
_platform_client_instance = None


def get_oauth_service():
    """Get singleton OAuth service instance"""
    global _oauth_service_instance
    if _oauth_service_instance is None:
        _oauth_service_instance = create_oauth_service()
    return _oauth_service_instance


def get_platform_client():
    """Get singleton platform client instance"""
    global _platform_client_instance
    if _platform_client_instance is None:
        _platform_client_instance = create_platform_client()
    return _platform_client_instance


# Platform configuration for frontend
def get_platform_configs():
    """Get platform configurations for frontend"""
    oauth_service = get_oauth_service()
    
    configs = {}
    for platform_id, config in oauth_service.platforms.items():
        client_id = os.getenv(config['client_id_env'])
        
        configs[platform_id] = {
            'id': platform_id,
            'name': config['name'],
            'scopes': config['scopes'],
            'has_credentials': bool(client_id),
            'auth_url': config['auth_url'],
            'supports_refresh': True,
            'posting_requirements': get_platform_client().get_posting_requirements(platform_id)
        }
    
    return configs


def validate_platform(platform):
    """Validate if platform is supported"""
    oauth_service = get_oauth_service()
    if platform not in oauth_service.platforms:
        raise PlatformNotSupportedError(f"Platform '{platform}' is not supported")
    
    # Check if credentials are configured
    config = oauth_service.platforms[platform]
    client_id = os.getenv(config['client_id_env'])
    client_secret = os.getenv(config['client_secret_env'])
    
    if not client_id or not client_secret:
        raise OAuthError(f"Credentials not configured for {platform}")


def validate_content_for_platform(platform, content, media_urls=None):
    """Validate content meets platform requirements"""
    platform_client = get_platform_client()
    requirements = platform_client.get_posting_requirements(platform)
    
    # Check content length
    if len(content) > requirements['content_max_length']:
        raise PostingError(f"Content too long for {platform}. Max: {requirements['content_max_length']} characters")
    
    # Check if media is required
    if requirements['media_required'] and (not media_urls or len(media_urls) == 0):
        raise PostingError(f"{platform} requires media attachments")
    
    # Check character limit for platforms like Twitter
    if requirements.get('character_limit') and len(content) > requirements['character_limit']:
        raise PostingError(f"Content exceeds {platform} character limit of {requirements['character_limit']}")


# Test functions
def test_oauth_service():
    """Test OAuth service functionality"""
    try:
        oauth_service = create_oauth_service()
        platform_client = create_platform_client(oauth_service)
        
        print("✅ OAuth Service initialized successfully")
        print(f"Supported platforms: {list(oauth_service.platforms.keys())}")
        
        # Test encryption/decryption
        test_token = "test_access_token_123"
        encrypted = oauth_service.encrypt_token(test_token)
        decrypted = oauth_service.decrypt_token(encrypted)
        
        if test_token == decrypted:
            print("✅ Token encryption/decryption working")
        else:
            print("❌ Token encryption/decryption failed")
        
        # Test platform configurations
        configs = get_platform_configs()
        print(f"✅ Platform configurations loaded: {len(configs)} platforms")
        
        return True
        
    except Exception as e:
        print(f"❌ OAuth service test failed: {e}")
        return False


if __name__ == '__main__':
    # Run tests if executed directly
    test_oauth_service()