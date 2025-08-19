# app/routes/credentials.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.credentials.credential_manager import CredentialManager
from app.automation.platforms.instagram_automator import InstagramAutomator
from app.automation.platforms.facebook_automator import FacebookAutomator
import logging

logger = logging.getLogger(__name__)
credentials_bp = Blueprint('credentials', __name__)

@credentials_bp.route('/', methods=['POST'])
@jwt_required()
def save_credentials():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        platform = data.get('platform', '').lower()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        additional_data = data.get('additional_data', {})
        
        if not all([platform, username, password]):
            return jsonify({'error': 'Platform, username, and password are required'}), 400
        
        if platform not in current_app.config['SUPPORTED_PLATFORMS']:
            return jsonify({'error': f'Platform {platform} is not supported'}), 400
        
        credential_manager = CredentialManager(
            current_app.db, 
            current_app.config['ENCRYPTION_KEY']
        )
        
        result = credential_manager.save_credentials(
            user_id, platform, username, password, additional_data
        )
        
        if result['success']:
            logger.info(f"Credentials saved for user {user_id} on platform {platform}")
            return jsonify(result), 201
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Save credentials error: {str(e)}")
        return jsonify({'error': 'Failed to save credentials'}), 500

@credentials_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_credentials():
    try:
        user_id = get_jwt_identity()
        
        credential_manager = CredentialManager(
            current_app.db, 
            current_app.config['ENCRYPTION_KEY']
        )
        
        result = credential_manager.get_all_user_credentials(user_id)
        
        if result['success']:
            # Don't return actual passwords, just platform status
            platforms_status = {}
            for platform, creds in result['credentials'].items():
                platforms_status[platform] = {
                    'connected': True,
                    'username': creds['username'],
                    'verified': creds.get('verified', False),
                    'last_verified': creds.get('last_verified')
                }
            
            return jsonify({
                'success': True,
                'platforms': platforms_status
            }), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Get credentials error: {str(e)}")
        return jsonify({'error': 'Failed to fetch credentials'}), 500

@credentials_bp.route('/<platform>', methods=['GET'])
@jwt_required()
def get_platform_credentials(platform):
    try:
        user_id = get_jwt_identity()
        
        credential_manager = CredentialManager(
            current_app.db, 
            current_app.config['ENCRYPTION_KEY']
        )
        
        result = credential_manager.get_credentials(user_id, platform)
        
        if result['success']:
            # Don't return password in response
            return jsonify({
                'success': True,
                'platform': platform,
                'username': result['username'],
                'verified': result.get('verified', False),
                'last_verified': result.get('last_verified')
            }), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Get platform credentials error: {str(e)}")
        return jsonify({'error': 'Failed to fetch credentials'}), 500

@credentials_bp.route('/<platform>/test', methods=['POST'])
@jwt_required()
def test_credentials(platform):
    try:
        user_id = get_jwt_identity()
        
        credential_manager = CredentialManager(
            current_app.db, 
            current_app.config['ENCRYPTION_KEY']
        )
        
        # Get credentials
        creds_result = credential_manager.get_credentials(user_id, platform)
        
        if not creds_result['success']:
            return jsonify({'error': f'No {platform} credentials found'}), 404
        
        username = creds_result['username']
        password = creds_result['password']
        
        # Test login based on platform
        if platform == 'instagram':
            automator = InstagramAutomator(current_app.config['CHROME_OPTIONS'])
            login_success = automator.login(username, password)
            automator.close()
        elif platform == 'facebook':
            automator = FacebookAutomator(current_app.config['CHROME_OPTIONS'])
            login_success = automator.login(username, password)
            automator.close()
        else:
            return jsonify({'error': f'Testing not implemented for {platform}'}), 400
        
        # Update verification status
        credential_manager.verify_credentials(user_id, platform, login_success)
        
        if login_success:
            logger.info(f"Credentials verified for user {user_id} on platform {platform}")
            return jsonify({
                'success': True,
                'message': f'{platform} credentials verified successfully',
                'verified': True
            }), 200
        else:
            logger.warning(f"Credentials verification failed for user {user_id} on platform {platform}")
            return jsonify({
                'success': False,
                'message': f'{platform} credentials verification failed',
                'verified': False
            }), 400
            
    except Exception as e:
        logger.error(f"Test credentials error: {str(e)}")
        return jsonify({'error': 'Failed to test credentials'}), 500

@credentials_bp.route('/<platform>', methods=['PUT'])
@jwt_required()
def update_credentials(platform):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        additional_data = data.get('additional_data', {})
        
        if not all([username, password]):
            return jsonify({'error': 'Username and password are required'}), 400
        
        credential_manager = CredentialManager(
            current_app.db, 
            current_app.config['ENCRYPTION_KEY']
        )
        
        result = credential_manager.save_credentials(
            user_id, platform, username, password, additional_data
        )
        
        if result['success']:
            logger.info(f"Credentials updated for user {user_id} on platform {platform}")
            return jsonify({
                'success': True,
                'message': f'{platform} credentials updated successfully'
            }), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Update credentials error: {str(e)}")
        return jsonify({'error': 'Failed to update credentials'}), 500

@credentials_bp.route('/<platform>', methods=['DELETE'])
@jwt_required()
def delete_credentials(platform):
    try:
        user_id = get_jwt_identity()
        
        credential_manager = CredentialManager(
            current_app.db, 
            current_app.config['ENCRYPTION_KEY']
        )
        
        result = credential_manager.delete_credentials(user_id, platform)
        
        if result['success']:
            logger.info(f"Credentials deleted for user {user_id} on platform {platform}")
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Delete credentials error: {str(e)}")
        return jsonify({'error': 'Failed to delete credentials'}), 500