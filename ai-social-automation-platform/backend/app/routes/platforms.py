"""
Platform Management Routes for VelocityPost.ai
Handles OAuth connections, platform status, and management
"""

from flask import Blueprint, request, jsonify, current_app, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid
from bson import ObjectId

from app.utils.database import get_database
from app.utils.helpers import generate_response
from app.services.oauth_handlers import get_oauth_handler, get_supported_platforms, OAUTH_HANDLERS

platforms_bp = Blueprint('platforms', __name__)

@platforms_bp.route('/supported', methods=['GET'])
def get_supported_platforms_list():
    """Get list of supported platforms"""
    try:
        platforms = get_supported_platforms()
        
        # Add platform-specific information
        platform_details = {}
        for platform_name, handler_class in OAUTH_HANDLERS.items():
            handler = handler_class()
            platform_details[platform_name] = {
                'name': platform_name,
                'display_name': platform_name.title(),
                'description': f'Connect your {platform_name.title()} account for automated posting',
                'features': ['text_posts', 'image_posts'],
                'max_post_length': 280 if platform_name == 'twitter' else 2200,
                'supports_images': True,
                'supports_videos': platform_name in ['youtube', 'tiktok', 'instagram', 'facebook'],
                'supports_scheduling': platform_name != 'twitter'
            }
        
        return generate_response(
            True, 
            'Supported platforms retrieved', 
            data={'platforms': platform_details}
        )
        
    except Exception as e:
        current_app.logger.error(f'Get supported platforms error: {str(e)}')
        return generate_response(False, 'Failed to get supported platforms', status_code=500)

@platforms_bp.route('/connect/<platform>', methods=['POST'])
@jwt_required()
def initiate_oauth_connection(platform):
    """Initiate OAuth connection for a platform"""
    try:
        user_id = get_jwt_identity()
        
        # Check if platform is supported
        if platform.lower() not in OAUTH_HANDLERS:
            return generate_response(False, f'Platform {platform} is not supported', status_code=400)
        
        # Check user's plan limits
        db = get_database()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return generate_response(False, 'User not found', status_code=404)
        
        # Count current connections
        current_connections = db.platform_connections.find({
            'user_id': ObjectId(user_id),
            'is_active': True
        }).count()
        
        plan_limits = user.get('plan_limits', {})
        max_platforms = plan_limits.get('max_platforms', 2)
        
        if current_connections >= max_platforms:
            return generate_response(
                False, 
                f'Platform limit reached. Your {user.get("subscription_plan", "free")} plan allows {max_platforms} platforms. Upgrade to connect more.',
                status_code=403
            )
        
        # Check if platform already connected
        existing_connection = db.platform_connections.find_one({
            'user_id': ObjectId(user_id),
            'platform': platform.lower(),
            'is_active': True
        })
        
        if existing_connection:
            return generate_response(False, f'{platform.title()} is already connected', status_code=409)
        
        # Generate OAuth state for security
        oauth_state = str(uuid.uuid4())
        
        # Store OAuth state temporarily
        db.oauth_states.insert_one({
            'state': oauth_state,
            'user_id': ObjectId(user_id),
            'platform': platform.lower(),
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow().replace(minute=datetime.utcnow().minute + 15)  # 15 min expiry
        })
        
        # Get OAuth handler and generate authorization URL
        oauth_handler = get_oauth_handler(platform)
        auth_url = oauth_handler.get_authorization_url(oauth_state)
        
        return generate_response(
            True,
            'OAuth authorization URL generated',
            data={'auth_url': auth_url, 'state': oauth_state}
        )
        
    except ValueError as e:
        return generate_response(False, str(e), status_code=400)
    except Exception as e:
        current_app.logger.error(f'OAuth initiation error: {str(e)}')
        return generate_response(False, 'Failed to initiate OAuth connection', status_code=500)

@platforms_bp.route('/oauth/callback/<platform>', methods=['GET'])
def oauth_callback(platform):
    """Handle OAuth callback from platforms"""
    try:
        # Get authorization code and state from query params
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            current_app.logger.error(f'OAuth error for {platform}: {error}')
            # Redirect to frontend with error
            return redirect(f"{current_app.config['FRONTEND_URL']}/platforms?error=oauth_failed")
        
        if not code or not state:
            return redirect(f"{current_app.config['FRONTEND_URL']}/platforms?error=missing_params")
        
        db = get_database()
        
        # Verify OAuth state
        oauth_state_doc = db.oauth_states.find_one({
            'state': state,
            'platform': platform.lower(),
            'expires_at': {'$gt': datetime.utcnow()}
        })
        
        if not oauth_state_doc:
            return redirect(f"{current_app.config['FRONTEND_URL']}/platforms?error=invalid_state")
        
        user_id = oauth_state_doc['user_id']
        
        # Get OAuth handler and exchange code for token
        oauth_handler = get_oauth_handler(platform)
        token_data = oauth_handler.exchange_code_for_token(code)
        
        if not token_data:
            return redirect(f"{current_app.config['FRONTEND_URL']}/platforms?error=token_exchange_failed")
        
        # Get user profile from platform
        access_token = token_data.get('access_token')
        profile_data = oauth_handler.get_user_profile(access_token)
        
        if not profile_data:
            return redirect(f"{current_app.config['FRONTEND_URL']}/platforms?error=profile_fetch_failed")
        
        # Save platform connection
        connection_data = {
            'user_id': user_id,
            'platform': platform.lower(),
            'platform_user_id': profile_data.get('id'),
            'username': profile_data.get('username') or profile_data.get('display_name'),
            'email': profile_data.get('email'),
            'profile_image': profile_data.get('profile_image'),
            'access_token': access_token,
            'refresh_token': token_data.get('refresh_token'),
            'token_expires_at': datetime.utcnow().replace(second=datetime.utcnow().second + token_data.get('expires_in', 3600)),
            'platform_data': profile_data,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Remove existing connection if any (replace)
        db.platform_connections.delete_many({
            'user_id': user_id,
            'platform': platform.lower()
        })
        
        # Insert new connection
        db.platform_connections.insert_one(connection_data)
        
        # Clean up OAuth state
        db.oauth_states.delete_one({'_id': oauth_state_doc['_id']})
        
        # Redirect to frontend with success
        return redirect(f"{current_app.config['FRONTEND_URL']}/platforms?success={platform}_connected")
        
    except Exception as e:
        current_app.logger.error(f'OAuth callback error for {platform}: {str(e)}')
        return redirect(f"{current_app.config['FRONTEND_URL']}/platforms?error=callback_failed")

@platforms_bp.route('/connected', methods=['GET'])
@jwt_required()
def get_connected_platforms():
    """Get user's connected platforms"""
    try:
        user_id = get_jwt_identity()
        
        db = get_database()
        connections = list(db.platform_connections.find({
            'user_id': ObjectId(user_id),
            'is_active': True
        }))
        
        platforms_data = []
        for connection in connections:
            platforms_data.append({
                'platform': connection['platform'],
                'username': connection['username'],
                'profile_image': connection.get('profile_image'),
                'connected_at': connection['created_at'].isoformat(),
                'is_active': connection['is_active'],
                'platform_data': {
                    'followers_count': connection.get('platform_data', {}).get('followers_count', 0),
                    'following_count': connection.get('platform_data', {}).get('following_count', 0)
                }
            })
        
        return generate_response(
            True,
            'Connected platforms retrieved',
            data={'platforms': platforms_data}
        )
        
    except Exception as e:
        current_app.logger.error(f'Get connected platforms error: {str(e)}')
        return generate_response(False, 'Failed to get connected platforms', status_code=500)

@platforms_bp.route('/disconnect/<platform>', methods=['DELETE'])
@jwt_required()
def disconnect_platform(platform):
    """Disconnect a platform"""
    try:
        user_id = get_jwt_identity()
        
        db = get_database()
        
        # Find and deactivate connection
        result = db.platform_connections.update_one(
            {
                'user_id': ObjectId(user_id),
                'platform': platform.lower(),
                'is_active': True
            },
            {
                '$set': {
                    'is_active': False,
                    'disconnected_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            return generate_response(False, f'{platform.title()} connection not found', status_code=404)
        
        # TODO: Revoke tokens on platform side if supported
        
        return generate_response(True, f'{platform.title()} disconnected successfully')
        
    except Exception as e:
        current_app.logger.error(f'Disconnect platform error: {str(e)}')
        return generate_response(False, f'Failed to disconnect {platform}', status_code=500)

@platforms_bp.route('/test-connection/<platform>', methods=['POST'])
@jwt_required()
def test_platform_connection(platform):
    """Test platform connection validity"""
    try:
        user_id = get_jwt_identity()
        
        db = get_database()
        connection = db.platform_connections.find_one({
            'user_id': ObjectId(user_id),
            'platform': platform.lower(),
            'is_active': True
        })
        
        if not connection:
            return generate_response(False, f'{platform.title()} is not connected', status_code=404)
        
        # Test connection using OAuth handler
        oauth_handler = get_oauth_handler(platform)
        is_valid = oauth_handler.test_connection(connection['access_token'])
        
        if is_valid:
            # Update last tested timestamp
            db.platform_connections.update_one(
                {'_id': connection['_id']},
                {'$set': {'last_tested': datetime.utcnow()}}
            )
            return generate_response(True, f'{platform.title()} connection is working')
        else:
            # Try to refresh token if available
            if connection.get('refresh_token'):
                token_data = oauth_handler.refresh_access_token(connection['refresh_token'])
                
                if token_data:
                    # Update tokens
                    db.platform_connections.update_one(
                        {'_id': connection['_id']},
                        {
                            '$set': {
                                'access_token': token_data.get('access_token'),
                                'token_expires_at': datetime.utcnow().replace(
                                    second=datetime.utcnow().second + token_data.get('expires_in', 3600)
                                ),
                                'updated_at': datetime.utcnow()
                            }
                        }
                    )
                    return generate_response(True, f'{platform.title()} connection refreshed and working')
            
            # Connection is invalid
            return generate_response(False, f'{platform.title()} connection is invalid. Please reconnect.', status_code=400)
        
    except Exception as e:
        current_app.logger.error(f'Test connection error for {platform}: {str(e)}')
        return generate_response(False, f'Failed to test {platform} connection', status_code=500)

@platforms_bp.route('/refresh-token/<platform>', methods=['POST'])
@jwt_required()
def refresh_platform_token(platform):
    """Manually refresh platform token"""
    try:
        user_id = get_jwt_identity()
        
        db = get_database()
        connection = db.platform_connections.find_one({
            'user_id': ObjectId(user_id),
            'platform': platform.lower(),
            'is_active': True
        })
        
        if not connection:
            return generate_response(False, f'{platform.title()} is not connected', status_code=404)
        
        if not connection.get('refresh_token'):
            return generate_response(False, f'{platform.title()} does not support token refresh', status_code=400)
        
        # Refresh token
        oauth_handler = get_oauth_handler(platform)
        token_data = oauth_handler.refresh_access_token(connection['refresh_token'])
        
        if not token_data:
            return generate_response(False, f'Failed to refresh {platform.title()} token', status_code=400)
        
        # Update connection with new tokens
        update_data = {
            'access_token': token_data.get('access_token'),
            'token_expires_at': datetime.utcnow().replace(
                second=datetime.utcnow().second + token_data.get('expires_in', 3600)
            ),
            'updated_at': datetime.utcnow()
        }
        
        # Update refresh token if provided
        if 'refresh_token' in token_data:
            update_data['refresh_token'] = token_data['refresh_token']
        
        db.platform_connections.update_one(
            {'_id': connection['_id']},
            {'$set': update_data}
        )
        
        return generate_response(True, f'{platform.title()} token refreshed successfully')
        
    except Exception as e:
        current_app.logger.error(f'Refresh token error for {platform}: {str(e)}')
        return generate_response(False, f'Failed to refresh {platform} token', status_code=500)