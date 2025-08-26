"""
OAuth Routes for Social Media Platform Integration
Handles secure OAuth 2.0 flow for all supported platforms
"""

import os
import asyncio
from datetime import datetime
from flask import Blueprint, request, jsonify, redirect, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from app.services.oauth_service import OAuthService, PlatformAPIClient
from app.utils.database import get_db, SocialAccountModel, check_user_limits

logger = logging.getLogger(__name__)

# Create Blueprint
oauth_bp = Blueprint('oauth', __name__)

# Initialize OAuth service
oauth_service = OAuthService()
api_client = PlatformAPIClient(oauth_service)

@oauth_bp.route('/platforms', methods=['GET'])
def get_supported_platforms():
    """Get list of supported social media platforms"""
    try:
        platforms = [
            {
                'id': 'facebook',
                'name': 'Facebook',
                'description': 'Connect your Facebook page to automatically post content',
                'icon': 'facebook',
                'color': '#1877F2',
                'requires_page': True,
                'supported_content': ['text', 'images', 'links', 'videos']
            },
            {
                'id': 'instagram',
                'name': 'Instagram',
                'description': 'Connect your Instagram business account for automatic posting',
                'icon': 'instagram',
                'color': '#E4405F',
                'requires_business_account': True,
                'supported_content': ['images', 'videos', 'stories']
            },
            {
                'id': 'twitter',
                'name': 'Twitter/X',
                'description': 'Automatically post tweets and engage with your audience',
                'icon': 'twitter',
                'color': '#000000',
                'requires_page': False,
                'supported_content': ['text', 'images', 'videos', 'threads']
            },
            {
                'id': 'linkedin',
                'name': 'LinkedIn',
                'description': 'Share professional content and build your network',
                'icon': 'linkedin',
                'color': '#0A66C2',
                'requires_page': False,
                'supported_content': ['text', 'images', 'videos', 'articles']
            },
            {
                'id': 'youtube',
                'name': 'YouTube',
                'description': 'Upload videos and manage your YouTube channel',
                'icon': 'youtube',
                'color': '#FF0000',
                'requires_page': False,
                'supported_content': ['videos', 'community_posts', 'shorts']
            },
            {
                'id': 'pinterest',
                'name': 'Pinterest',
                'description': 'Create pins and manage your Pinterest boards',
                'icon': 'pinterest',
                'color': '#BD081C',
                'requires_business_account': True,
                'supported_content': ['images', 'idea_pins']
            }
        ]
        
        return jsonify({
            'platforms': platforms,
            'total_count': len(platforms)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get supported platforms: {e}")
        return jsonify({
            'error': 'Failed to get platforms',
            'message': 'Unable to retrieve supported platforms'
        }), 500

@oauth_bp.route('/auth-url/<platform>', methods=['POST'])
@jwt_required()
def get_auth_url(platform):
    """Generate OAuth authorization URL for a platform"""
    try:
        current_user_id = get_jwt_identity()
        
        # Validate platform
        if platform not in oauth_service.platforms:
            return jsonify({
                'error': 'Unsupported platform',
                'message': f'Platform {platform} is not supported'
            }), 400
        
        # Check user's plan limits
        can_connect, message = check_user_limits(current_user_id, 'connect_platform', platform)
        if not can_connect:
            return jsonify({
                'error': 'Plan limit reached',
                'message': message,
                'upgrade_required': True
            }), 403
        
        # Generate redirect URI
        redirect_uri = f"{os.getenv('BACKEND_URL', 'http://localhost:5000')}/api/oauth/callback/{platform}"
        
        # Generate authorization URL
        auth_url, state = oauth_service.generate_auth_url(
            platform=platform,
            user_id=current_user_id,
            redirect_uri=redirect_uri
        )
        
        # Store state in session/cache for verification
        # In production, use Redis or database
        # For now, we'll include it in the response for client-side storage
        
        logger.info(f"Generated OAuth URL for {platform}, user: {current_user_id}")
        
        return jsonify({
            'auth_url': auth_url,
            'state': state,
            'platform': platform,
            'expires_in': 600  # 10 minutes
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to generate auth URL for {platform}: {e}")
        return jsonify({
            'error': 'Auth URL generation failed',
            'message': 'Unable to generate authorization URL. Please try again.'
        }), 500

@oauth_bp.route('/callback/<platform>', methods=['GET'])
def oauth_callback(platform):
    """Handle OAuth callback from social media platforms"""
    try:
        # Get authorization code and state from query parameters
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        # Handle OAuth errors
        if error:
            error_description = request.args.get('error_description', 'Unknown error')
            logger.error(f"OAuth error for {platform}: {error} - {error_description}")
            
            # Redirect to frontend with error
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            return redirect(f"{frontend_url}/platforms?error={error}&description={error_description}")
        
        # Validate required parameters
        if not code or not state:
            logger.error(f"Missing OAuth parameters for {platform}: code={bool(code)}, state={bool(state)}")
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            return redirect(f"{frontend_url}/platforms?error=missing_parameters")
        
        # Extract user_id from state
        try:
            import base64
            decoded_state = base64.urlsafe_b64decode(state.encode()).decode()
            state_user_id, state_platform, timestamp = decoded_state.split(':')
            
            if state_platform != platform:
                raise ValueError("Platform mismatch in state")
                
        except Exception as e:
            logger.error(f"Invalid state parameter for {platform}: {e}")
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            return redirect(f"{frontend_url}/platforms?error=invalid_state")
        
        # Verify state is not too old (10 minutes)
        try:
            from datetime import datetime
            state_time = datetime.fromtimestamp(int(timestamp))
            if (datetime.utcnow() - state_time).total_seconds() > 600:
                raise ValueError("State expired")
        except:
            logger.error(f"Expired state for {platform}")
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            return redirect(f"{frontend_url}/platforms?error=state_expired")
        
        # Generate redirect URI (same as in auth_url)
        redirect_uri = f"{os.getenv('BACKEND_URL', 'http://localhost:5000')}/api/oauth/callback/{platform}"
        
        # Exchange code for token
        try:
            # Use asyncio to run the async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            token_data = loop.run_until_complete(
                oauth_service.exchange_code_for_token(
                    platform=platform,
                    code=code,
                    redirect_uri=redirect_uri,
                    state=state
                )
            )
            
            loop.close()
            
        except Exception as e:
            logger.error(f"Token exchange failed for {platform}: {e}")
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            return redirect(f"{frontend_url}/platforms?error=token_exchange_failed&message={str(e)}")
        
        # Save social account to database
        try:
            account_id = SocialAccountModel.save_social_account(
                user_id=state_user_id,
                platform=platform,
                token_data={
                    'access_token': oauth_service.encrypt_token(token_data['access_token']),
                    'refresh_token': oauth_service.encrypt_token(token_data.get('refresh_token', '')),
                    'expires_in': token_data.get('expires_in'),
                    'scope': token_data.get('scope', '')
                },
                profile_data=token_data['profile']
            )
            
            logger.info(f"Successfully connected {platform} for user {state_user_id}")
            
        except Exception as e:
            logger.error(f"Failed to save social account for {platform}: {e}")
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            return redirect(f"{frontend_url}/platforms?error=save_failed")
        
        # Redirect to frontend with success
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return redirect(f"{frontend_url}/platforms?connected={platform}&success=true")
        
    except Exception as e:
        logger.error(f"OAuth callback failed for {platform}: {e}")
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return redirect(f"{frontend_url}/platforms?error=callback_failed")

@oauth_bp.route('/connected-accounts', methods=['GET'])
@jwt_required()
def get_connected_accounts():
    """Get user's connected social media accounts"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get connected accounts
        accounts = SocialAccountModel.get_connected_accounts(current_user_id)
        
        # Add platform-specific information and status
        enriched_accounts = []
        for account in accounts:
            platform_config = oauth_service.platforms.get(account['platform'])
            
            enriched_account = {
                **account,
                'platform_name': platform_config['name'] if platform_config else account['platform'].title(),
                'connection_status': 'active' if account['is_active'] else 'inactive',
                'requires_reauth': False,  # Check if token is expired/invalid
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
            
            # Check if token needs refresh (if expires_at exists and is past)
            if account.get('token_expires_at'):
                if datetime.utcnow() > account['token_expires_at']:
                    enriched_account['requires_reauth'] = True
                    enriched_account['connection_status'] = 'expired'
            
            enriched_accounts.append(enriched_account)
        
        return jsonify({
            'accounts': enriched_accounts,
            'total_count': len(enriched_accounts),
            'active_count': len([acc for acc in enriched_accounts if acc['connection_status'] == 'active'])
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get connected accounts: {e}")
        return jsonify({
            'error': 'Failed to get accounts',
            'message': 'Unable to retrieve connected accounts'
        }), 500

@oauth_bp.route('/disconnect/<platform>', methods=['DELETE'])
@jwt_required()
def disconnect_account(platform):
    """Disconnect a social media account"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get the account to disconnect
        account = SocialAccountModel.get_account_by_platform(current_user_id, platform)
        if not account:
            return jsonify({
                'error': 'Account not found',
                'message': f'No connected {platform} account found'
            }), 404
        
        # Decrypt token for revocation
        try:
            access_token = oauth_service.decrypt_token(account['access_token'])
            
            # Attempt to revoke token on the platform
            revoke_success = oauth_service.revoke_token(platform, access_token)
            if not revoke_success:
                logger.warning(f"Failed to revoke token on {platform} - proceeding with local disconnect")
                
        except Exception as e:
            logger.warning(f"Token revocation failed for {platform}: {e} - proceeding with local disconnect")
        
        # Remove account from database
        db = get_db()
        from bson import ObjectId
        
        result = db.social_accounts.update_one(
            {
                'user_id': ObjectId(current_user_id),
                'platform': platform
            },
            {
                '$set': {
                    'is_active': False,
                    'disconnected_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            return jsonify({
                'error': 'Disconnect failed',
                'message': 'Failed to disconnect account'
            }), 500
        
        logger.info(f"Disconnected {platform} account for user {current_user_id}")
        
        return jsonify({
            'message': f'{platform.title()} account disconnected successfully',
            'platform': platform
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to disconnect {platform} account: {e}")
        return jsonify({
            'error': 'Disconnect failed',
            'message': f'Unable to disconnect {platform} account. Please try again.'
        }), 500

@oauth_bp.route('/test-connection/<platform>', methods=['POST'])
@jwt_required()
def test_connection(platform):
    """Test if a connected account's token is still valid"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get the account
        account = SocialAccountModel.get_account_by_platform(current_user_id, platform)
        if not account:
            return jsonify({
                'error': 'Account not found',
                'message': f'No connected {platform} account found'
            }), 404
        
        # Decrypt and validate token
        try:
            access_token = oauth_service.decrypt_token(account['access_token'])
            is_valid = oauth_service.validate_token(platform, access_token)
            
            # Update last_used_at if valid
            if is_valid:
                db = get_db()
                from bson import ObjectId
                db.social_accounts.update_one(
                    {'_id': ObjectId(account['_id'])},
                    {'$set': {'last_used_at': datetime.utcnow()}}
                )
            
            return jsonify({
                'platform': platform,
                'is_valid': is_valid,
                'status': 'active' if is_valid else 'invalid',
                'tested_at': datetime.utcnow().isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"Token validation failed for {platform}: {e}")
            return jsonify({
                'platform': platform,
                'is_valid': False,
                'status': 'error',
                'error_message': str(e)
            }), 200
        
    except Exception as e:
        logger.error(f"Connection test failed for {platform}: {e}")
        return jsonify({
            'error': 'Test failed',
            'message': f'Unable to test {platform} connection'
        }), 500

@oauth_bp.route('/refresh-token/<platform>', methods=['POST'])
@jwt_required()
def refresh_token(platform):
    """Refresh expired access token for a platform"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get the account
        account = SocialAccountModel.get_account_by_platform(current_user_id, platform)
        if not account:
            return jsonify({
                'error': 'Account not found',
                'message': f'No connected {platform} account found'
            }), 404
        
        # Check if refresh token exists
        if not account.get('refresh_token'):
            return jsonify({
                'error': 'Refresh not available',
                'message': f'{platform} account needs to be reconnected',
                'requires_reauth': True
            }), 400
        
        try:
            # Decrypt refresh token
            refresh_token = oauth_service.decrypt_token(account['refresh_token'])
            
            # Refresh the token
            new_token_data = oauth_service.refresh_access_token(platform, refresh_token)
            
            # Update account with new token
            db = get_db()
            from bson import ObjectId
            from datetime import datetime, timedelta
            
            update_data = {
                'access_token': oauth_service.encrypt_token(new_token_data['access_token']),
                'updated_at': datetime.utcnow(),
                'last_used_at': datetime.utcnow()
            }
            
            # Update refresh token if provided
            if new_token_data.get('refresh_token'):
                update_data['refresh_token'] = oauth_service.encrypt_token(new_token_data['refresh_token'])
            
            # Update expiry if provided
            if new_token_data.get('expires_in'):
                update_data['token_expires_at'] = datetime.utcnow() + timedelta(seconds=int(new_token_data['expires_in']))
            
            result = db.social_accounts.update_one(
                {'_id': ObjectId(account['_id'])},
                {'$set': update_data}
            )
            
            if result.modified_count == 0:
                raise Exception("Failed to update token in database")
            
            logger.info(f"Token refreshed successfully for {platform}, user {current_user_id}")
            
            return jsonify({
                'message': f'{platform.title()} token refreshed successfully',
                'platform': platform,
                'refreshed_at': datetime.utcnow().isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"Token refresh failed for {platform}: {e}")
            
            # Mark account as requiring reauth
            db = get_db()
            from bson import ObjectId
            db.social_accounts.update_one(
                {'_id': ObjectId(account['_id'])},
                {'$set': {
                    'requires_reauth': True,
                    'updated_at': datetime.utcnow()
                }}
            )
            
            return jsonify({
                'error': 'Refresh failed',
                'message': f'{platform.title()} account needs to be reconnected',
                'requires_reauth': True
            }), 400
        
    except Exception as e:
        logger.error(f"Token refresh process failed for {platform}: {e}")
        return jsonify({
            'error': 'Refresh failed',
            'message': f'Unable to refresh {platform} token'
        }), 500

@oauth_bp.route('/account-info/<platform>', methods=['GET'])
@jwt_required()
def get_account_info(platform):
    """Get detailed information about a connected account"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get the account
        account = SocialAccountModel.get_account_by_platform(current_user_id, platform)
        if not account:
            return jsonify({
                'error': 'Account not found',
                'message': f'No connected {platform} account found'
            }), 404
        
        # Decrypt token to get fresh profile data
        try:
            access_token = oauth_service.decrypt_token(account['access_token'])
            
            # Get fresh profile data
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            fresh_profile = loop.run_until_complete(
                oauth_service.get_user_profile(platform, access_token)
            )
            
            loop.close()
            
            # Update profile data in database
            db = get_db()
            from bson import ObjectId
            db.social_accounts.update_one(
                {'_id': ObjectId(account['_id'])},
                {'$set': {
                    'profile_data': fresh_profile,
                    'last_used_at': datetime.utcnow()
                }}
            )
            
            # Return detailed account info
            account_info = {
                'platform': platform,
                'platform_name': oauth_service.platforms[platform]['name'],
                'connected_at': account['connected_at'].isoformat(),
                'last_used_at': account.get('last_used_at', account['connected_at']).isoformat(),
                'is_active': account['is_active'],
                'username': fresh_profile.get('username', ''),
                'display_name': fresh_profile.get('name', ''),
                'profile_picture': fresh_profile.get('picture', ''),
                'profile_url': f"https://{platform}.com/{fresh_profile.get('username', '')}",
                'permissions': account.get('permissions', []),
                'account_stats': {
                    'followers': fresh_profile.get('followers'),
                    'following': fresh_profile.get('following'),
                    'posts': fresh_profile.get('posts', fresh_profile.get('media_count', fresh_profile.get('tweets', fresh_profile.get('videos')))),
                    'account_type': fresh_profile.get('account_type', 'personal')
                },
                'token_status': {
                    'is_valid': True,
                    'expires_at': account.get('token_expires_at').isoformat() if account.get('token_expires_at') else None,
                    'requires_refresh': False
                }
            }
            
            return jsonify(account_info), 200
            
        except Exception as e:
            logger.warning(f"Failed to get fresh profile data for {platform}: {e}")
            
            # Return cached account info
            account_info = {
                'platform': platform,
                'platform_name': oauth_service.platforms[platform]['name'],
                'connected_at': account['connected_at'].isoformat(),
                'last_used_at': account.get('last_used_at', account['connected_at']).isoformat(),
                'is_active': account['is_active'],
                'username': account.get('username', ''),
                'display_name': account.get('display_name', ''),
                'profile_picture': account.get('profile_picture', ''),
                'permissions': account.get('permissions', []),
                'token_status': {
                    'is_valid': False,
                    'error': str(e),
                    'requires_refresh': True
                }
            }
            
            return jsonify(account_info), 200
        
    except Exception as e:
        logger.error(f"Failed to get account info for {platform}: {e}")
        return jsonify({
            'error': 'Account info failed',
            'message': f'Unable to get {platform} account information'
        }), 500

@oauth_bp.route('/platform-requirements/<platform>', methods=['GET'])
def get_platform_requirements(platform):
    """Get platform-specific requirements and posting guidelines"""
    try:
        if platform not in oauth_service.platforms:
            return jsonify({
                'error': 'Unsupported platform',
                'message': f'Platform {platform} is not supported'
            }), 400
        
        requirements = api_client.get_posting_requirements(platform)
        platform_config = oauth_service.platforms[platform]
        
        return jsonify({
            'platform': platform,
            'platform_name': platform_config['name'],
            'requirements': requirements,
            'scopes_required': platform_config['scopes'],
            'setup_instructions': {
                'facebook': 'You need a Facebook Page to post content. Personal profiles cannot be used for automated posting.',
                'instagram': 'You need an Instagram Business or Creator account connected to a Facebook Page.',
                'twitter': 'Personal Twitter accounts can be used for posting.',
                'linkedin': 'You can post to your LinkedIn profile or company pages you manage.',
                'youtube': 'You can upload videos to your YouTube channel.',
                'pinterest': 'You need a Pinterest Business account to use the API.'
            }.get(platform, f'Connect your {platform} account to start posting.')
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get platform requirements for {platform}: {e}")
        return jsonify({
            'error': 'Requirements fetch failed',
            'message': f'Unable to get {platform} requirements'
        }), 500

# Error handlers for OAuth blueprint
@oauth_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad request',
        'message': 'Invalid request parameters'
    }), 400

@oauth_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'error': 'Forbidden',
        'message': 'Plan upgrade required for this feature'
    }), 403

@oauth_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'Platform or account not found'
    }), 404

if __name__ == '__main__':
    # Test OAuth service initialization
    try:
        test_service = OAuthService()
        print("✅ OAuth service initialized successfully")
        print(f"Supported platforms: {list(test_service.platforms.keys())}")
        
        # Test auth URL generation
        test_url, test_state = test_service.generate_auth_url('twitter', 'test_user_123', 'http://localhost:5000/callback')
        print(f"✅ Test auth URL generated: {test_url[:100]}...")
        
    except Exception as e:
        print(f"❌ OAuth service test failed: {e}")