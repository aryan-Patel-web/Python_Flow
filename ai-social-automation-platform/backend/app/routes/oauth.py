#!/usr/bin/env python3
"""
OAuth Routes for Social Media Platform Integration
Handles secure OAuth 2.0 flow for all supported platforms with Redis caching
"""

import os
import json
import redis
import base64
import asyncio
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, redirect
from bson.objectid import ObjectId

# Try to import auth decorator
try:
    from app.routes.auth import require_auth
except ImportError:
    def require_auth(f):
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper

from app.utils.database import get_collection, PlatformConnectionModel, check_user_limits

logger = logging.getLogger(__name__)

# Create Blueprint
oauth_bp = Blueprint('oauth', __name__)

# Redis connection for caching OAuth states and tokens
redis_client = None
try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 1)),  # Use DB 1 for OAuth
        decode_responses=True
    )
    redis_client.ping()
    logger.info("Redis connected successfully for OAuth")
except Exception as e:
    logger.warning(f"Redis connection failed for OAuth: {e}")
    redis_client = None

# Platform Configuration
PLATFORM_CONFIGS = {
    'facebook': {
        'name': 'Facebook',
        'client_id': os.getenv('FACEBOOK_CLIENT_ID'),
        'client_secret': os.getenv('FACEBOOK_CLIENT_SECRET'),
        'auth_url': 'https://www.facebook.com/v18.0/dialog/oauth',
        'token_url': 'https://graph.facebook.com/v18.0/oauth/access_token',
        'profile_url': 'https://graph.facebook.com/v18.0/me',
        'scope': 'pages_manage_posts,pages_read_engagement,pages_show_list,publish_to_groups',
        'icon': 'facebook',
        'color': '#1877F2',
        'requires_page': True,
        'supported_content': ['text', 'images', 'links', 'videos']
    },
    'instagram': {
        'name': 'Instagram',
        'client_id': os.getenv('INSTAGRAM_CLIENT_ID'),
        'client_secret': os.getenv('INSTAGRAM_CLIENT_SECRET'),
        'auth_url': 'https://api.instagram.com/oauth/authorize',
        'token_url': 'https://api.instagram.com/oauth/access_token',
        'profile_url': 'https://graph.instagram.com/v18.0/me',
        'scope': 'user_profile,user_media',
        'icon': 'instagram',
        'color': '#E4405F',
        'requires_business_account': True,
        'supported_content': ['images', 'videos', 'stories']
    },
    'twitter': {
        'name': 'Twitter/X',
        'client_id': os.getenv('TWITTER_CLIENT_ID'),
        'client_secret': os.getenv('TWITTER_CLIENT_SECRET'),
        'auth_url': 'https://twitter.com/i/oauth2/authorize',
        'token_url': 'https://api.twitter.com/2/oauth2/token',
        'profile_url': 'https://api.twitter.com/2/users/me',
        'scope': 'tweet.read,tweet.write,users.read,offline.access',
        'icon': 'twitter',
        'color': '#000000',
        'requires_page': False,
        'supported_content': ['text', 'images', 'videos', 'threads']
    },
    'linkedin': {
        'name': 'LinkedIn',
        'client_id': os.getenv('LINKEDIN_CLIENT_ID'),
        'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET'),
        'auth_url': 'https://www.linkedin.com/oauth/v2/authorization',
        'token_url': 'https://www.linkedin.com/oauth/v2/accessToken',
        'profile_url': 'https://api.linkedin.com/v2/people/~',
        'scope': 'r_liteprofile,w_member_social',
        'icon': 'linkedin',
        'color': '#0A66C2',
        'requires_page': False,
        'supported_content': ['text', 'images', 'videos', 'articles']
    },
    'youtube': {
        'name': 'YouTube',
        'client_id': os.getenv('YOUTUBE_CLIENT_ID'),
        'client_secret': os.getenv('YOUTUBE_CLIENT_SECRET'),
        'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
        'token_url': 'https://oauth2.googleapis.com/token',
        'profile_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
        'scope': 'https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube',
        'icon': 'youtube',
        'color': '#FF0000',
        'requires_page': False,
        'supported_content': ['videos', 'community_posts', 'shorts']
    },
    'pinterest': {
        'name': 'Pinterest',
        'client_id': os.getenv('PINTEREST_CLIENT_ID'),
        'client_secret': os.getenv('PINTEREST_CLIENT_SECRET'),
        'auth_url': 'https://www.pinterest.com/oauth/',
        'token_url': 'https://api.pinterest.com/v5/oauth/token',
        'profile_url': 'https://api.pinterest.com/v5/user_account',
        'scope': 'boards:read,pins:read,pins:write',
        'icon': 'pinterest',
        'color': '#BD081C',
        'requires_business_account': True,
        'supported_content': ['images', 'idea_pins']
    }
}

@oauth_bp.route('/platforms', methods=['GET'])
def get_supported_platforms():
    """Get list of supported social media platforms"""
    try:
        platforms = []
        for platform_id, config in PLATFORM_CONFIGS.items():
            platforms.append({
                'id': platform_id,
                'name': config['name'],
                'description': f"Connect your {config['name']} account to automatically post content",
                'icon': config['icon'],
                'color': config['color'],
                'available': bool(config['client_id'] and config['client_secret']),
                'scope': config['scope'],
                'requires_page': config.get('requires_page', False),
                'requires_business_account': config.get('requires_business_account', False),
                'supported_content': config['supported_content']
            })
        
        return jsonify({
            'success': True,
            'platforms': platforms,
            'total_count': len(platforms)
        }), 200
        
    except Exception as e:
        logger.error(f"Get platforms error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get platforms',
            'error': str(e)
        }), 500

@oauth_bp.route('/auth-url/<platform>', methods=['POST'])
@require_auth
def generate_auth_url(platform):
    """Generate OAuth authorization URL for platform"""
    try:
        user_id = request.user_id
        
        if platform not in PLATFORM_CONFIGS:
            return jsonify({
                'success': False,
                'message': 'Platform not supported',
                'error': f'Platform {platform} is not supported'
            }), 400
        
        config = PLATFORM_CONFIGS[platform]
        
        # Check if credentials are configured
        if not config['client_id'] or not config['client_secret']:
            return jsonify({
                'success': False,
                'message': 'Platform not configured',
                'error': f'{platform} OAuth credentials not configured'
            }), 400
        
        # Check user's plan limits
        can_connect, limit_message = check_user_limits(user_id, 'connect_platform', platform)
        if not can_connect:
            return jsonify({
                'success': False,
                'message': 'Plan limit reached',
                'error': limit_message,
                'upgrade_required': True
            }), 403
        
        # Generate state for security
        state_data = f"{user_id}:{platform}:{int(datetime.utcnow().timestamp())}"
        state = base64.urlsafe_b64encode(state_data.encode()).decode()
        
        # Store state in Redis with 10 minute expiry
        if redis_client:
            try:
                redis_client.setex(f"oauth_state:{state}", 600, json.dumps({
                    'user_id': user_id,
                    'platform': platform,
                    'created_at': datetime.utcnow().isoformat()
                }))
            except Exception as e:
                logger.warning(f"Failed to store OAuth state in Redis: {e}")
        
        # Generate redirect URI
        redirect_uri = f"{os.getenv('BACKEND_URL', 'http://localhost:5000')}/api/oauth/callback/{platform}"
        
        # Build authorization URL
        auth_params = {
            'client_id': config['client_id'],
            'redirect_uri': redirect_uri,
            'scope': config['scope'],
            'response_type': 'code',
            'state': state
        }
        
        # Platform-specific parameters
        if platform == 'facebook':
            auth_params['display'] = 'popup'
        elif platform == 'linkedin':
            auth_params['response_type'] = 'code'
        elif platform == 'youtube':
            auth_params['access_type'] = 'offline'
            auth_params['prompt'] = 'consent'
        
        from urllib.parse import urlencode
        auth_url = config['auth_url'] + '?' + urlencode(auth_params)
        
        logger.info(f"Generated OAuth URL for {platform}, user: {user_id}")
        
        return jsonify({
            'success': True,
            'auth_url': auth_url,
            'state': state,
            'platform': platform,
            'expires_in': 600  # 10 minutes
        }), 200
        
    except Exception as e:
        logger.error(f"Generate auth URL error for {platform}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to generate auth URL',
            'error': str(e)
        }), 500

@oauth_bp.route('/callback/<platform>', methods=['GET'])
def oauth_callback(platform):
    """Handle OAuth callback from social media platforms"""
    try:
        # Get authorization code and state from query parameters
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        
        # Handle OAuth errors
        if error:
            error_description = request.args.get('error_description', 'Unknown error')
            logger.error(f"OAuth error for {platform}: {error} - {error_description}")
            return redirect(f"{frontend_url}/platforms?error={error}&description={error_description}")
        
        # Validate required parameters
        if not code or not state:
            logger.error(f"Missing OAuth parameters for {platform}: code={bool(code)}, state={bool(state)}")
            return redirect(f"{frontend_url}/platforms?error=missing_parameters")
        
        # Verify state from Redis if available
        state_user_id = None
        if redis_client:
            try:
                redis_key = f"oauth_state:{state}"
                stored_state = redis_client.get(redis_key)
                if stored_state:
                    state_data = json.loads(stored_state)
                    state_user_id = state_data['user_id']
                    # Delete used state
                    redis_client.delete(redis_key)
                else:
                    logger.error(f"Invalid or expired state for {platform}")
                    return redirect(f"{frontend_url}/platforms?error=invalid_state")
            except Exception as e:
                logger.error(f"Redis state verification failed: {e}")
                # Fall back to decoding state directly
        
        # Fallback: Extract user_id from state if Redis failed
        if not state_user_id:
            try:
                decoded_state = base64.urlsafe_b64decode(state.encode()).decode()
                state_user_id, state_platform, timestamp = decoded_state.split(':')
                
                if state_platform != platform:
                    raise ValueError("Platform mismatch in state")
                
                # Check if state is not too old (10 minutes)
                state_time = datetime.fromtimestamp(int(timestamp))
                if (datetime.utcnow() - state_time).total_seconds() > 600:
                    raise ValueError("State expired")
                    
            except Exception as e:
                logger.error(f"State validation failed for {platform}: {e}")
                return redirect(f"{frontend_url}/platforms?error=invalid_state")
        
        # Generate redirect URI (same as in auth_url)
        redirect_uri = f"{os.getenv('BACKEND_URL', 'http://localhost:5000')}/api/oauth/callback/{platform}"
        
        # Exchange code for token
        config = PLATFORM_CONFIGS[platform]
        token_data = exchange_code_for_token(platform, code, config, redirect_uri)
        
        if not token_data:
            logger.error(f"Token exchange failed for {platform}")
            return redirect(f"{frontend_url}/platforms?error=token_exchange_failed")
        
        # Get user profile from platform
        profile_data = get_user_profile(platform, token_data['access_token'], config)
        
        if not profile_data:
            logger.error(f"Profile fetch failed for {platform}")
            return redirect(f"{frontend_url}/platforms?error=profile_fetch_failed")
        
        # Save connection to database
        try:
            connection_result = PlatformConnectionModel.save_connection(
                state_user_id, platform, token_data, profile_data
            )
            
            if not connection_result:
                raise Exception("Database save failed")
            
            logger.info(f"Successfully connected {platform} for user {state_user_id}")
            
            # Cache connection status in Redis
            if redis_client:
                try:
                    cache_key = f"platform_connection:{state_user_id}:{platform}"
                    cache_data = {
                        'platform': platform,
                        'username': profile_data.get('username', ''),
                        'connected_at': datetime.utcnow().isoformat(),
                        'is_active': True
                    }
                    redis_client.setex(cache_key, 3600, json.dumps(cache_data))  # 1 hour cache
                except Exception as e:
                    logger.warning(f"Failed to cache connection in Redis: {e}")
            
        except Exception as e:
            logger.error(f"Failed to save social account for {platform}: {e}")
            return redirect(f"{frontend_url}/platforms?error=save_failed")
        
        # Redirect to frontend with success
        return redirect(f"{frontend_url}/platforms?connected={platform}&success=true")
        
    except Exception as e:
        logger.error(f"OAuth callback failed for {platform}: {e}")
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return redirect(f"{frontend_url}/platforms?error=callback_failed")

@oauth_bp.route('/callback/<platform>', methods=['POST'])
@require_auth
def handle_oauth_callback_post(platform):
    """Handle OAuth callback via POST (alternative method)"""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided',
                'error': 'Authorization code and state required'
            }), 400
        
        code = data.get('code')
        state = data.get('state')
        
        if not code:
            return jsonify({
                'success': False,
                'message': 'Authorization code required',
                'error': 'No authorization code provided'
            }), 400
        
        # Verify state if provided
        if state and redis_client:
            try:
                redis_key = f"oauth_state:{state}"
                stored_state = redis_client.get(redis_key)
                if stored_state:
                    state_data = json.loads(stored_state)
                    if state_data['user_id'] != user_id:
                        return jsonify({
                            'success': False,
                            'message': 'State validation failed',
                            'error': 'Invalid state parameter'
                        }), 400
                    redis_client.delete(redis_key)
            except Exception as e:
                logger.warning(f"State validation warning: {e}")
        
        # Exchange code for access token
        config = PLATFORM_CONFIGS[platform]
        redirect_uri = f"{os.getenv('BACKEND_URL', 'http://localhost:5000')}/api/oauth/callback/{platform}"
        
        token_data = exchange_code_for_token(platform, code, config, redirect_uri)
        
        if not token_data:
            return jsonify({
                'success': False,
                'message': 'Token exchange failed',
                'error': 'Failed to exchange authorization code for access token'
            }), 400
        
        # Get user profile from platform
        profile_data = get_user_profile(platform, token_data['access_token'], config)
        
        if not profile_data:
            return jsonify({
                'success': False,
                'message': 'Profile fetch failed',
                'error': 'Failed to fetch user profile from platform'
            }), 400
        
        # Save connection to database
        connection_result = PlatformConnectionModel.save_connection(
            user_id, platform, token_data, profile_data
        )
        
        if not connection_result:
            return jsonify({
                'success': False,
                'message': 'Failed to save connection',
                'error': 'Database error while saving connection'
            }), 500
        
        logger.info(f"OAuth connection successful: {platform} for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': f'{platform.title()} connected successfully',
            'platform': platform,
            'profile': {
                'id': profile_data.get('id'),
                'username': profile_data.get('username', ''),
                'name': profile_data.get('name', ''),
                'picture': profile_data.get('picture', '')
            }
        }), 200
        
    except Exception as e:
        logger.error(f"OAuth callback POST error for {platform}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'OAuth callback failed',
            'error': str(e)
        }), 500

@oauth_bp.route('/connected-accounts', methods=['GET'])
@require_auth
def get_connected_accounts():
    """Get user's connected social media accounts"""
    try:
        user_id = request.user_id
        
        # Try to get from Redis cache first
        cached_accounts = []
        if redis_client:
            try:
                for platform in PLATFORM_CONFIGS.keys():
                    cache_key = f"platform_connection:{user_id}:{platform}"
                    cached_data = redis_client.get(cache_key)
                    if cached_data:
                        cached_accounts.append(json.loads(cached_data))
            except Exception as e:
                logger.warning(f"Redis cache read failed: {e}")
        
        # Get from database (always do this to ensure accuracy)
        connections = PlatformConnectionModel.get_connections_by_user(user_id)
        
        # Add platform-specific information and status
        enriched_accounts = []
        for account in connections:
            platform_config = PLATFORM_CONFIGS.get(account['platform'])
            
            enriched_account = {
                **account,
                'platform_name': platform_config['name'] if platform_config else account['platform'].title(),
                'icon': platform_config.get('icon', account['platform']) if platform_config else account['platform'],
                'color': platform_config.get('color', '#000000') if platform_config else '#000000',
                'connection_status': 'active' if account['is_active'] else 'inactive',
                'requires_reauth': False,
                'last_used': account.get('last_used_at'),
                'permissions': account.get('permissions', []),
                'profile_data': {
                    'username': account.get('username', ''),
                    'display_name': account.get('display_name', ''),
                    'profile_picture': account.get('profile_picture', ''),
                    'followers': account.get('profile_data', {}).get('followers'),
                    'account_type': account.get('profile_data', {}).get('account_type')
                }
            }
            
            # Check if token needs refresh
            if account.get('token_expires_at'):
                if datetime.utcnow() > account['token_expires_at']:
                    enriched_account['requires_reauth'] = True
                    enriched_account['connection_status'] = 'expired'
            
            enriched_accounts.append(enriched_account)
        
        return jsonify({
            'success': True,
            'accounts': enriched_accounts,
            'total_count': len(enriched_accounts),
            'active_count': len([acc for acc in enriched_accounts if acc['connection_status'] == 'active'])
        }), 200
        
    except Exception as e:
        logger.error(f"Get connected accounts error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get connected accounts',
            'error': str(e)
        }), 500

@oauth_bp.route('/disconnect/<platform>', methods=['DELETE'])
@require_auth
def disconnect_platform(platform):
    """Disconnect a social media platform"""
    try:
        user_id = request.user_id
        
        # Get the account to disconnect
        connection = PlatformConnectionModel.get_connection_by_platform(user_id, platform)
        if not connection:
            return jsonify({
                'success': False,
                'message': 'Platform not connected',
                'error': f'No connected {platform} account found'
            }), 404
        
        # Update connection status in database
        connections_collection = get_collection('platform_connections')
        if not connections_collection:
            return jsonify({
                'success': False,
                'message': 'Database unavailable',
                'error': 'Please try again later'
            }), 503
        
        result = connections_collection.update_one(
            {'user_id': ObjectId(user_id), 'platform': platform},
            {'$set': {
                'is_active': False,
                'disconnected_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }}
        )
        
        if result.matched_count == 0:
            return jsonify({
                'success': False,
                'message': 'Platform not connected',
                'error': f'{platform} is not connected to your account'
            }), 404
        
        # Remove from Redis cache
        if redis_client:
            try:
                cache_key = f"platform_connection:{user_id}:{platform}"
                redis_client.delete(cache_key)
            except Exception as e:
                logger.warning(f"Failed to remove from Redis cache: {e}")
        
        logger.info(f"Platform disconnected: {platform} for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': f'{platform.title()} disconnected successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Disconnect platform error for {platform}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to disconnect platform',
            'error': str(e)
        }), 500

def exchange_code_for_token(platform, code, config, redirect_uri):
    """Exchange authorization code for access token"""
    try:
        import requests
        
        token_data = {
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        # Platform-specific token exchange
        if platform == 'twitter':
            # Twitter requires PKCE
            token_data['code_verifier'] = 'challenge'
        
        response = requests.post(config['token_url'], data=token_data, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Token exchange failed for {platform}: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Token exchange error for {platform}: {str(e)}")
        return None

def get_user_profile(platform, access_token, config):
    """Get user profile from platform API"""
    try:
        import requests
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Platform-specific profile requests
        params = {}
        if platform == 'facebook':
            params = {'fields': 'id,name,email,picture'}
        elif platform == 'instagram':
            params = {'fields': 'id,username,account_type,media_count'}
        elif platform == 'twitter':
            params = {'user.fields': 'id,name,username,profile_image_url'}
        
        response = requests.get(config['profile_url'], headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            profile_data = response.json()
            
            # Normalize profile data across platforms
            if platform == 'twitter' and 'data' in profile_data:
                profile_data = profile_data['data']
            
            return profile_data
        else:
            logger.error(f"Profile fetch failed for {platform}: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Profile fetch error for {platform}: {str(e)}")
        return None

# Error handlers specific to oauth blueprint
@oauth_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'message': 'Bad request',
        'error': 'Invalid request parameters'
    }), 400

@oauth_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'message': 'Forbidden',
        'error': 'Plan upgrade required for this feature'
    }), 403

@oauth_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Not found',
        'error': 'Platform or account not found'
    }), 404