"""
OAuth Social Media Integration Routes
Handles secure OAuth 2.0 authentication for all social media platforms
"""

import os
import secrets
import requests
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, redirect, current_app, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from urllib.parse import urlencode, parse_qs

from app.utils.database import PlatformConnection, serialize_doc
from app.services.oauth_handlers import (
    FacebookOAuthHandler,
    InstagramOAuthHandler,
    TwitterOAuthHandler,
    LinkedInOAuthHandler,
    YouTubeOAuthHandler,
    TikTokOAuthHandler,
    PinterestOAuthHandler
)

oauth_bp = Blueprint('oauth', __name__)

# OAuth handlers mapping
OAUTH_HANDLERS = {
    'facebook': FacebookOAuthHandler,
    'instagram': InstagramOAuthHandler,
    'twitter': TwitterOAuthHandler,
    'linkedin': LinkedInOAuthHandler,
    'youtube': YouTubeOAuthHandler,
    'tiktok': TikTokOAuthHandler,
    'pinterest': PinterestOAuthHandler
}

@oauth_bp.route('/auth-url/<platform>', methods=['GET'])
@jwt_required()
def get_auth_url(platform):
    """Get OAuth authorization URL for a platform"""
    try:
        user_id = get_jwt_identity()
        
        if platform not in OAUTH_HANDLERS:
            return jsonify({'error': 'Unsupported platform'}), 400
        
        # Generate state parameter for security
        state = secrets.token_urlsafe(32)
        session[f'{platform}_oauth_state'] = state
        session[f'{platform}_user_id'] = user_id
        
        # Get handler and authorization URL
        handler = OAUTH_HANDLERS[platform]()
        auth_url = handler.get_authorization_url(state)
        
        return jsonify({
            'auth_url': auth_url,
            'state': state,
            'platform': platform
        })
        
    except Exception as e:
        current_app.logger.error(f'OAuth auth URL error for {platform}: {str(e)}')
        return jsonify({'error': 'Failed to generate authorization URL'}), 500

@oauth_bp.route('/callback/<platform>', methods=['GET'])
def oauth_callback(platform):
    """Handle OAuth callback from platform"""
    try:
        if platform not in OAUTH_HANDLERS:
            return jsonify({'error': 'Unsupported platform'}), 400
        
        # Verify state parameter
        state = request.args.get('state')
        stored_state = session.get(f'{platform}_oauth_state')
        user_id = session.get(f'{platform}_user_id')
        
        if not state or not stored_state or state != stored_state:
            return jsonify({'error': 'Invalid state parameter'}), 400
            
        if not user_id:
            return jsonify({'error': 'User session not found'}), 400
        
        # Get authorization code
        code = request.args.get('code')
        if not code:
            error = request.args.get('error')
            return jsonify({'error': f'Authorization failed: {error}'}), 400
        
        # Exchange code for access token
        handler = OAUTH_HANDLERS[platform]()
        token_data = handler.exchange_code_for_token(code)
        
        if not token_data:
            return jsonify({'error': 'Failed to exchange code for token'}), 400
        
        # Get user profile information
        profile_info = handler.get_user_profile(token_data['access_token'])
        
        # Store connection in database
        connection = PlatformConnection.create(
            user_id=user_id,
            platform=platform,
            access_token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token'),
            expires_at=datetime.utcnow() + timedelta(seconds=token_data.get('expires_in', 3600)),
            platform_user_id=profile_info.get('id'),
            platform_username=profile_info.get('username'),
            profile_info=profile_info,
            permissions=token_data.get('scope', '').split(',')
        )
        
        # Clean up session
        session.pop(f'{platform}_oauth_state', None)
        session.pop(f'{platform}_user_id', None)
        
        # Redirect to frontend with success message
        redirect_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/platforms?connected={platform}"
        return redirect(redirect_url)
        
    except Exception as e:
        current_app.logger.error(f'OAuth callback error for {platform}: {str(e)}')
        redirect_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/platforms?error={platform}_failed"
        return redirect(redirect_url)

@oauth_bp.route('/connected-platforms', methods=['GET'])
@jwt_required()
def get_connected_platforms():
    """Get all connected platforms for the user"""
    try:
        user_id = get_jwt_identity()
        connections = PlatformConnection.get_user_connections(user_id)
        
        # Format response without sensitive tokens
        platforms = []
        for conn in connections:
            platforms.append({
                'platform': conn['platform'],
                'platform_username': conn.get('platform_username'),
                'profile_info': conn.get('profile_info', {}),
                'connected_at': conn['created_at'].isoformat(),
                'is_active': conn['is_active'],
                'permissions': conn.get('permissions', []),
                'last_used_at': conn['last_used_at'].isoformat() if conn.get('last_used_at') else None
            })
        
        return jsonify({
            'platforms': platforms,
            'total_connected': len(platforms)
        })
        
    except Exception as e:
        current_app.logger.error(f'Get connected platforms error: {str(e)}')
        return jsonify({'error': 'Failed to fetch connected platforms'}), 500

@oauth_bp.route('/disconnect/<platform>', methods=['DELETE'])
@jwt_required()
def disconnect_platform(platform):
    """Disconnect a platform"""
    try:
        user_id = get_jwt_identity()
        
        if platform not in OAUTH_HANDLERS:
            return jsonify({'error': 'Unsupported platform'}), 400
        
        # Revoke tokens with platform if possible
        connection = PlatformConnection.get_connection(user_id, platform)
        if connection:
            try:
                handler = OAUTH_HANDLERS[platform]()
                handler.revoke_token(connection['access_token'])
            except Exception as e:
                current_app.logger.warning(f'Failed to revoke token for {platform}: {str(e)}')
        
        # Remove from database
        success = PlatformConnection.disconnect(user_id, platform)
        
        if success:
            return jsonify({'message': f'{platform.title()} disconnected successfully'})
        else:
            return jsonify({'error': 'Platform not found or already disconnected'}), 404
            
    except Exception as e:
        current_app.logger.error(f'Disconnect platform error for {platform}: {str(e)}')
        return jsonify({'error': 'Failed to disconnect platform'}), 500

@oauth_bp.route('/test-connection/<platform>', methods=['POST'])
@jwt_required()
def test_connection(platform):
    """Test if platform connection is working"""
    try:
        user_id = get_jwt_identity()
        
        if platform not in OAUTH_HANDLERS:
            return jsonify({'error': 'Unsupported platform'}), 400
        
        connection = PlatformConnection.get_connection(user_id, platform)
        if not connection:
            return jsonify({'error': 'Platform not connected'}), 404
        
        # Test connection with platform API
        handler = OAUTH_HANDLERS[platform]()
        is_valid = handler.test_connection(connection['access_token'])
        
        if is_valid:
            # Update last used timestamp
            PlatformConnection.update_tokens(
                user_id, 
                platform, 
                connection['access_token'],
                connection.get('refresh_token')
            )
            
            return jsonify({
                'status': 'connected',
                'message': f'{platform.title()} connection is active'
            })
        else:
            return jsonify({
                'status': 'disconnected',
                'message': f'{platform.title()} connection failed. Please reconnect.'
            }), 401
            
    except Exception as e:
        current_app.logger.error(f'Test connection error for {platform}: {str(e)}')
        return jsonify({'error': 'Failed to test connection'}), 500

@oauth_bp.route('/refresh-token/<platform>', methods=['POST'])
@jwt_required()
def refresh_platform_token(platform):
    """Refresh access token for a platform"""
    try:
        user_id = get_jwt_identity()
        
        if platform not in OAUTH_HANDLERS:
            return jsonify({'error': 'Unsupported platform'}), 400
        
        connection = PlatformConnection.get_connection(user_id, platform)
        if not connection or not connection.get('refresh_token'):
            return jsonify({'error': 'No refresh token available'}), 404
        
        # Refresh token with platform
        handler = OAUTH_HANDLERS[platform]()
        new_token_data = handler.refresh_access_token(connection['refresh_token'])
        
        if new_token_data:
            # Update tokens in database
            PlatformConnection.update_tokens(
                user_id,
                platform,
                new_token_data['access_token'],
                new_token_data.get('refresh_token'),
                datetime.utcnow() + timedelta(seconds=new_token_data.get('expires_in', 3600))
            )
            
            return jsonify({
                'message': f'{platform.title()} token refreshed successfully',
                'expires_at': (datetime.utcnow() + timedelta(seconds=new_token_data.get('expires_in', 3600))).isoformat()
            })
        else:
            return jsonify({'error': 'Failed to refresh token'}), 400
            
    except Exception as e:
        current_app.logger.error(f'Refresh token error for {platform}: {str(e)}')
        return jsonify({'error': 'Failed to refresh token'}), 500

@oauth_bp.route('/platform-info/<platform>', methods=['GET'])
@jwt_required()
def get_platform_info(platform):
    """Get platform-specific information and capabilities"""
    try:
        user_id = get_jwt_identity()
        
        if platform not in OAUTH_HANDLERS:
            return jsonify({'error': 'Unsupported platform'}), 400
        
        handler = OAUTH_HANDLERS[platform]()
        platform_info = handler.get_platform_info()
        
        # Check if user has this platform connected
        connection = PlatformConnection.get_connection(user_id, platform)
        platform_info['is_connected'] = connection is not None
        
        if connection:
            platform_info['connected_username'] = connection.get('platform_username')
            platform_info['connected_at'] = connection['created_at'].isoformat()
            platform_info['permissions'] = connection.get('permissions', [])
        
        return jsonify(platform_info)
        
    except Exception as e:
        current_app.logger.error(f'Get platform info error for {platform}: {str(e)}')
        return jsonify({'error': 'Failed to get platform information'}), 500

@oauth_bp.route('/supported-platforms', methods=['GET'])
def get_supported_platforms():
    """Get list of all supported platforms"""
    try:
        platforms = []
        
        for platform_name, handler_class in OAUTH_HANDLERS.items():
            handler = handler_class()
            platform_info = handler.get_platform_info()
            platforms.append({
                'name': platform_name,
                'display_name': platform_info.get('display_name', platform_name.title()),
                'description': platform_info.get('description', ''),
                'features': platform_info.get('features', []),
                'content_types': platform_info.get('content_types', []),
                'api_version': platform_info.get('api_version', ''),
                'rate_limits': platform_info.get('rate_limits', {}),
                'max_post_length': platform_info.get('max_post_length', 0),
                'supports_images': platform_info.get('supports_images', False),
                'supports_videos': platform_info.get('supports_videos', False),
                'supports_scheduling': platform_info.get('supports_scheduling', False)
            })
        
        return jsonify({
            'platforms': platforms,
            'total_supported': len(platforms)
        })
        
    except Exception as e:
        current_app.logger.error(f'Get supported platforms error: {str(e)}')
        return jsonify({'error': 'Failed to get supported platforms'}), 500