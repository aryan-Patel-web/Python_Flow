"""
Secure OAuth Authentication Routes for VelocityPost.ai
Handles OAuth token exchange and platform connections
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import os
from datetime import datetime, timedelta
import logging
from ..services.oauth_service import OAuthService
from ..services.encryption_service import EncryptionService
from ..models.platform_connection import PlatformConnection
from ..models.user import User

auth_bp = Blueprint('auth', __name__)
oauth_service = OAuthService()
encryption_service = EncryptionService()

@auth_bp.route('/oauth/callback', methods=['POST'])
@jwt_required()
def oauth_callback():
    """
    Handle OAuth callback and exchange authorization code for access token
    This is the secure server-side token exchange
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        platform = data.get('platform')
        code = data.get('code')
        state = data.get('state')
        code_verifier = data.get('code_verifier')  # For PKCE (Twitter)
        
        if not platform or not code:
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Validate platform
        supported_platforms = ['facebook', 'instagram', 'twitter', 'linkedin', 'youtube', 'tiktok', 'pinterest']
        if platform not in supported_platforms:
            return jsonify({'error': 'Unsupported platform'}), 400
            
        # Exchange authorization code for access token
        token_data = oauth_service.exchange_code_for_token(
            platform=platform,
            code=code,
            state=state,
            code_verifier=code_verifier
        )
        
        if not token_data.get('access_token'):
            return jsonify({'error': 'Failed to obtain access token'}), 400
            
        # Get platform user info
        user_info = oauth_service.get_platform_user_info(platform, token_data['access_token'])
        
        # Encrypt and store tokens
        encrypted_access_token = encryption_service.encrypt(token_data['access_token'])
        encrypted_refresh_token = None
        if token_data.get('refresh_token'):
            encrypted_refresh_token = encryption_service.encrypt(token_data['refresh_token'])
            
        # Save or update platform connection
        connection = PlatformConnection.query.filter_by(
            user_id=user_id,
            platform=platform
        ).first()
        
        if connection:
            # Update existing connection
            connection.access_token = encrypted_access_token
            connection.refresh_token = encrypted_refresh_token
            connection.expires_at = datetime.utcnow() + timedelta(seconds=token_data.get('expires_in', 3600))
            connection.platform_user_id = user_info.get('id')
            connection.platform_username = user_info.get('username')
            connection.is_active = True
            connection.last_connected = datetime.utcnow()
        else:
            # Create new connection
            connection = PlatformConnection(
                user_id=user_id,
                platform=platform,
                access_token=encrypted_access_token,
                refresh_token=encrypted_refresh_token,
                expires_at=datetime.utcnow() + timedelta(seconds=token_data.get('expires_in', 3600)),
                platform_user_id=user_info.get('id'),
                platform_username=user_info.get('username'),
                is_active=True,
                scopes=token_data.get('scope', ''),
                last_connected=datetime.utcnow()
            )
            
        connection.save()
        
        # Log successful connection
        logging.info(f"User {user_id} successfully connected {platform}")
        
        return jsonify({
            'success': True,
            'platform': platform,
            'username': user_info.get('username'),
            'connected_at': connection.last_connected.isoformat()
        })
        
    except Exception as e:
        logging.error(f"OAuth callback error: {str(e)}")
        return jsonify({'error': 'OAuth callback failed'}), 500

@auth_bp.route('/platforms/connected', methods=['GET'])
@jwt_required()
def get_connected_platforms():
    """Get list of connected platforms for the user"""
    try:
        user_id = get_jwt_identity()
        
        connections = PlatformConnection.query.filter_by(
            user_id=user_id,
            is_active=True
        ).all()
        
        platforms = []
        for conn in connections:
            platforms.append({
                'platform': conn.platform,
                'username': conn.platform_username,
                'connected_at': conn.last_connected.isoformat(),
                'expires_at': conn.expires_at.isoformat() if conn.expires_at else None,
                'is_token_valid': oauth_service.is_token_valid(conn)
            })
            
        return jsonify({
            'platforms': platforms,
            'total': len(platforms)
        })
        
    except Exception as e:
        logging.error(f"Error fetching connected platforms: {str(e)}")
        return jsonify({'error': 'Failed to fetch platforms'}), 500

@auth_bp.route('/platforms/disconnect', methods=['POST'])
@jwt_required()
def disconnect_platform():
    """Disconnect a platform"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        platform = data.get('platform')
        
        if not platform:
            return jsonify({'error': 'Platform is required'}), 400
            
        connection = PlatformConnection.query.filter_by(
            user_id=user_id,
            platform=platform
        ).first()
        
        if not connection:
            return jsonify({'error': 'Platform not connected'}), 404
            
        # Revoke token on platform (if supported)
        try:
            decrypted_token = encryption_service.decrypt(connection.access_token)
            oauth_service.revoke_token(platform, decrypted_token)
        except Exception as e:
            logging.warning(f"Failed to revoke token for {platform}: {str(e)}")
            
        # Mark as inactive instead of deleting (for audit purposes)
        connection.is_active = False
        connection.disconnected_at = datetime.utcnow()
        connection.save()
        
        logging.info(f"User {user_id} disconnected {platform}")
        
        return jsonify({
            'success': True,
            'platform': platform,
            'disconnected_at': connection.disconnected_at.isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error disconnecting platform: {str(e)}")
        return jsonify({'error': 'Failed to disconnect platform'}), 500

@auth_bp.route('/platforms/<platform>/test', methods=['POST'])
@jwt_required()
def test_platform_connection(platform):
    """Test if platform connection is working"""
    try:
        user_id = get_jwt_identity()
        
        connection = PlatformConnection.query.filter_by(
            user_id=user_id,
            platform=platform,
            is_active=True
        ).first()
        
        if not connection:
            return jsonify({'error': 'Platform not connected'}), 404
            
        # Decrypt token and test
        decrypted_token = encryption_service.decrypt(connection.access_token)
        is_valid = oauth_service.test_token(platform, decrypted_token)
        
        if is_valid:
            return jsonify({
                'success': True,
                'platform': platform,
                'status': 'Token is valid'
            })
        else:
            # Try to refresh token if available
            if connection.refresh_token:
                try:
                    new_tokens = oauth_service.refresh_access_token(platform, connection.refresh_token)
                    if new_tokens:
                        # Update with new tokens
                        connection.access_token = encryption_service.encrypt(new_tokens['access_token'])
                        if new_tokens.get('refresh_token'):
                            connection.refresh_token = encryption_service.encrypt(new_tokens['refresh_token'])
                        connection.expires_at = datetime.utcnow() + timedelta(seconds=new_tokens.get('expires_in', 3600))
                        connection.save()
                        
                        return jsonify({
                            'success': True,
                            'platform': platform,
                            'status': 'Token refreshed'
                        })
                except Exception:
                    pass
                    
            return jsonify({
                'success': False,
                'platform': platform,
                'status': 'Token expired or invalid'
            }), 401
            
    except Exception as e:
        logging.error(f"Error testing platform connection: {str(e)}")
        return jsonify({'error': 'Failed to test connection'}), 500

@auth_bp.route('/platforms/status', methods=['GET'])
@jwt_required()
def get_platforms_status():
    """Get status of all supported platforms"""
    try:
        user_id = get_jwt_identity()
        
        supported_platforms = ['facebook', 'instagram', 'twitter', 'linkedin', 'youtube', 'tiktok', 'pinterest']
        connections = PlatformConnection.query.filter_by(
            user_id=user_id,
            is_active=True
        ).all()
        
        connected_platforms = {conn.platform: conn for conn in connections}
        
        status = []
        for platform in supported_platforms:
            platform_status = {
                'platform': platform,
                'connected': platform in connected_platforms,
                'username': None,
                'connected_at': None,
                'token_valid': False
            }
            
            if platform in connected_platforms:
                conn = connected_platforms[platform]
                platform_status.update({
                    'username': conn.platform_username,
                    'connected_at': conn.last_connected.isoformat(),
                    'token_valid': oauth_service.is_token_valid(conn)
                })
                
            status.append(platform_status)
            
        return jsonify({
            'platforms': status,
            'total_connected': len(connected_platforms)
        })
        
    except Exception as e:
        logging.error(f"Error getting platforms status: {str(e)}")
        return jsonify({'error': 'Failed to get platforms status'}), 500