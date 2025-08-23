"""
Secure OAuth Service for Backend Token Exchange
Handles server-side OAuth flows and token management
"""

import requests
import os
import logging
import hashlib
import base64
from datetime import datetime, timedelta
from urllib.parse import urlencode

class OAuthService:
    def __init__(self):
        self.facebook_app_id = os.getenv('FACEBOOK_APP_ID')
        self.facebook_app_secret = os.getenv('FACEBOOK_APP_SECRET')
        self.instagram_client_id = os.getenv('INSTAGRAM_CLIENT_ID')
        self.instagram_client_secret = os.getenv('INSTAGRAM_CLIENT_SECRET')
        self.twitter_client_id = os.getenv('TWITTER_CLIENT_ID')
        self.twitter_client_secret = os.getenv('TWITTER_CLIENT_SECRET')
        self.linkedin_client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.linkedin_client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.tiktok_client_key = os.getenv('TIKTOK_CLIENT_KEY')
        self.tiktok_client_secret = os.getenv('TIKTOK_CLIENT_SECRET')
        self.pinterest_client_id = os.getenv('PINTEREST_CLIENT_ID')
        self.pinterest_client_secret = os.getenv('PINTEREST_CLIENT_SECRET')
        
        self.frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')

    def exchange_code_for_token(self, platform, code, state=None, code_verifier=None):
        """
        Exchange authorization code for access token
        This is the secure server-side token exchange
        """
        try:
            if platform == 'facebook':
                return self._exchange_facebook_token(code)
            elif platform == 'instagram':
                return self._exchange_instagram_token(code)
            elif platform == 'twitter':
                return self._exchange_twitter_token(code, code_verifier)
            elif platform == 'linkedin':
                return self._exchange_linkedin_token(code)
            elif platform == 'youtube':
                return self._exchange_google_token(code)
            elif platform == 'tiktok':
                return self._exchange_tiktok_token(code)
            elif platform == 'pinterest':
                return self._exchange_pinterest_token(code)
            else:
                raise ValueError(f"Unsupported platform: {platform}")
                
        except Exception as e:
            logging.error(f"Token exchange failed for {platform}: {str(e)}")
            raise

    def _exchange_facebook_token(self, code):
        """Exchange Facebook authorization code for access token"""
        url = 'https://graph.facebook.com/v18.0/oauth/access_token'
        
        params = {
            'client_id': self.facebook_app_id,
            'client_secret': self.facebook_app_secret,
            'redirect_uri': f'{self.frontend_url}/auth/callback/facebook',
            'code': code
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Get long-lived token
        long_lived_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
        long_lived_params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.facebook_app_id,
            'client_secret': self.facebook_app_secret,
            'fb_exchange_token': data['access_token']
        }
        
        long_lived_response = requests.get(long_lived_url, params=long_lived_params)
        if long_lived_response.ok:
            long_lived_data = long_lived_response.json()
            return {
                'access_token': long_lived_data['access_token'],
                'token_type': 'Bearer',
                'expires_in': long_lived_data.get('expires_in', 3600)
            }
        
        return {
            'access_token': data['access_token'],
            'token_type': 'Bearer',
            'expires_in': data.get('expires_in', 3600)
        }

    def _exchange_instagram_token(self, code):
        """Exchange Instagram authorization code for access token"""
        url = 'https://api.instagram.com/oauth/access_token'
        
        data = {
            'client_id': self.instagram_client_id,
            'client_secret': self.instagram_client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': f'{self.frontend_url}/auth/callback/instagram',
            'code': code
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        return response.json()

    def _exchange_twitter_token(self, code, code_verifier):
        """Exchange Twitter authorization code for access token (OAuth 2.0 with PKCE)"""
        url = 'https://api.twitter.com/2/oauth2/token'
        
        # Basic auth with client credentials
        auth = (self.twitter_client_id, self.twitter_client_secret)
        
        data = {
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': self.twitter_client_id,
            'redirect_uri': f'{self.frontend_url}/auth/callback/twitter',
            'code_verifier': code_verifier
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(url, data=data, headers=headers, auth=auth)
        response.raise_for_status()
        
        return response.json()

    def _exchange_linkedin_token(self, code):
        """Exchange LinkedIn authorization code for access token"""
        url = 'https://www.linkedin.com/oauth/v2/accessToken'
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.linkedin_client_id,
            'client_secret': self.linkedin_client_secret,
            'redirect_uri': f'{self.frontend_url}/auth/callback/linkedin'
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        
        return response.json()

    def _exchange_google_token(self, code):
        """Exchange Google/YouTube authorization code for access token"""
        url = 'https://oauth2.googleapis.com/token'
        
        data = {
            'code': code,
            'client_id': self.google_client_id,
            'client_secret': self.google_client_secret,
            'redirect_uri': f'{self.frontend_url}/auth/callback/youtube',
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        return response.json()

    def _exchange_tiktok_token(self, code):
        """Exchange TikTok authorization code for access token"""
        url = 'https://open-api.tiktok.com/oauth/access_token/'
        
        data = {
            'client_key': self.tiktok_client_key,
            'client_secret': self.tiktok_client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': f'{self.frontend_url}/auth/callback/tiktok'
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        if result.get('data'):
            return result['data']
        return result

    def _exchange_pinterest_token(self, code):
        """Exchange Pinterest authorization code for access token"""
        url = 'https://api.pinterest.com/v5/oauth/token'
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': f'{self.frontend_url}/auth/callback/pinterest'
        }
        
        # Basic auth with client credentials
        auth = (self.pinterest_client_id, self.pinterest_client_secret)
        
        response = requests.post(url, data=data, auth=auth)
        response.raise_for_status()
        
        return response.json()

    def get_platform_user_info(self, platform, access_token):
        """Get user information from platform using access token"""
        try:
            if platform == 'facebook':
                return self._get_facebook_user_info(access_token)
            elif platform == 'instagram':
                return self._get_instagram_user_info(access_token)
            elif platform == 'twitter':
                return self._get_twitter_user_info(access_token)
            elif platform == 'linkedin':
                return self._get_linkedin_user_info(access_token)
            elif platform == 'youtube':
                return self._get_google_user_info(access_token)
            elif platform == 'tiktok':
                return self._get_tiktok_user_info(access_token)
            elif platform == 'pinterest':
                return self._get_pinterest_user_info(access_token)
            else:
                return {'id': 'unknown', 'username': 'unknown'}
                
        except Exception as e:
            logging.error(f"Failed to get user info for {platform}: {str(e)}")
            return {'id': 'unknown', 'username': 'unknown'}

    def _get_facebook_user_info(self, access_token):
        """Get Facebook user information"""
        url = f'https://graph.facebook.com/me?fields=id,name,email&access_token={access_token}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {'id': data.get('id'), 'username': data.get('name')}

    def _get_instagram_user_info(self, access_token):
        """Get Instagram user information"""
        url = f'https://graph.instagram.com/me?fields=id,username&access_token={access_token}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {'id': data.get('id'), 'username': data.get('username')}

    def _get_twitter_user_info(self, access_token):
        """Get Twitter user information"""
        url = 'https://api.twitter.com/2/users/me'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        user_data = data.get('data', {})
        return {'id': user_data.get('id'), 'username': user_data.get('username')}

    def _get_linkedin_user_info(self, access_token):
        """Get LinkedIn user information"""
        url = 'https://api.linkedin.com/v2/people/~'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return {'id': data.get('id'), 'username': f"{data.get('firstName', {}).get('localized', {}).get('en_US', '')} {data.get('lastName', {}).get('localized', {}).get('en_US', '')}"}

    def _get_google_user_info(self, access_token):
        """Get Google user information"""
        url = f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {'id': data.get('id'), 'username': data.get('name')}

    def _get_tiktok_user_info(self, access_token):
        """Get TikTok user information"""
        url = 'https://open-api.tiktok.com/oauth/userinfo/'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        user_data = data.get('data', {}).get('user', {})
        return {'id': user_data.get('open_id'), 'username': user_data.get('display_name')}

    def _get_pinterest_user_info(self, access_token):
        """Get Pinterest user information"""
        url = 'https://api.pinterest.com/v5/user_account'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return {'id': data.get('id'), 'username': data.get('username')}

    def test_token(self, platform, access_token):
        """Test if access token is still valid"""
        try:
            user_info = self.get_platform_user_info(platform, access_token)
            return user_info.get('id') != 'unknown'
        except Exception:
            return False

    def is_token_valid(self, connection):
        """Check if stored token is still valid"""
        if not connection or not connection.expires_at:
            return False
            
        # Check if token has expired
        if connection.expires_at <= datetime.utcnow():
            return False
            
        return True

    def refresh_access_token(self, platform, refresh_token):
        """Refresh access token using refresh token"""
        try:
            if platform == 'google':
                return self._refresh_google_token(refresh_token)
            elif platform == 'facebook':
                # Facebook tokens don't typically need refresh
                return None
            elif platform == 'twitter':
                # Twitter OAuth 2.0 tokens don't expire
                return None
            elif platform == 'linkedin':
                return self._refresh_linkedin_token(refresh_token)
            else:
                return None
                
        except Exception as e:
            logging.error(f"Token refresh failed for {platform}: {str(e)}")
            return None

    def _refresh_google_token(self, refresh_token):
        """Refresh Google access token"""
        url = 'https://oauth2.googleapis.com/token'
        
        data = {
            'client_id': self.google_client_id,
            'client_secret': self.google_client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        return response.json()

    def _refresh_linkedin_token(self, refresh_token):
        """Refresh LinkedIn access token"""
        url = 'https://www.linkedin.com/oauth/v2/accessToken'
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.linkedin_client_id,
            'client_secret': self.linkedin_client_secret
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        return response.json()

    def revoke_token(self, platform, access_token):
        """Revoke access token on platform"""
        try:
            if platform == 'google':
                url = f'https://oauth2.googleapis.com/revoke?token={access_token}'
                requests.post(url)
            elif platform == 'facebook':
                url = f'https://graph.facebook.com/me/permissions?access_token={access_token}'
                requests.delete(url)
            elif platform == 'linkedin':
                # LinkedIn doesn't have a revoke endpoint
                pass
            elif platform == 'twitter':
                url = 'https://api.twitter.com/2/oauth2/revoke'
                data = {'token': access_token}
                auth = (self.twitter_client_id, self.twitter_client_secret)
                requests.post(url, data=data, auth=auth)
            # Add other platforms as needed
            
        except Exception as e:
            logging.warning(f"Failed to revoke token for {platform}: {str(e)}")

    def get_posting_permissions(self, platform, access_token):
        """Check what posting permissions are available for the platform"""
        try:
            if platform == 'facebook':
                url = f'https://graph.facebook.com/me/permissions?access_token={access_token}'
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                permissions = [p['permission'] for p in data.get('data', []) if p.get('status') == 'granted']
                return permissions
            elif platform == 'instagram':
                # Instagram permissions are checked differently
                return ['user_profile', 'user_media']
            elif platform == 'twitter':
                # Check Twitter API scopes
                url = 'https://api.twitter.com/2/users/me'
                headers = {'Authorization': f'Bearer {access_token}'}
                response = requests.get(url, headers=headers)
                if response.ok:
                    return ['tweet.write', 'tweet.read']
                return []
            # Add other platforms
            return []
            
        except Exception as e:
            logging.error(f"Failed to get permissions for {platform}: {str(e)}")
            return []