#!/usr/bin/env python3
"""
OAuth Routes for VelocityPost.ai
Handles social media platform OAuth integration
"""

import os
import secrets
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

# Import database functions
from app.utils.database import get_collection

# Create blueprint
oauth_bp = Blueprint('oauth', __name__)

logger = logging.getLogger(__name__)

# Platform configurations
PLATFORM_CONFIGS = {
    'instagram': {
        'name': 'Instagram',
        'client_id': os.getenv('INSTAGRAM_CLIENT_ID'),
        'client_secret': os.getenv('INSTAGRAM_CLIENT_SECRET'),
        'available': bool(os.getenv('INSTAGRAM_CLIENT_ID')),
        'scope': 'user_profile,user_media',
        'icon': 'instagram',
        'color': '#E4405F'
    },
    'facebook': {
        'name': 'Facebook', 
        'client_id': os.getenv('FACEBOOK_APP_ID'),
        'client_secret': os.getenv('FACEBOOK_APP_SECRET'),
        'available': bool(os.getenv('FACEBOOK_APP_ID')),
        'scope': 'pages_manage_posts,pages_read_engagement',
        'icon': 'facebook',
        'color': '#1877F2'
    },
    'twitter': {
        'name': 'Twitter',
        'client_id': os.getenv('TWITTER_CLIENT_ID'), 
        'client_secret': os.getenv('TWITTER_CLIENT_SECRET'),
        'available': bool(os.getenv('TWITTER_CLIENT_ID')),
        'scope': 'tweet.read,tweet.write,users.read',
        'icon': 'twitter',
        'color': '#1DA1F2'
    },
    'linkedin': {
        'name': 'LinkedIn',
        'client_id': os.getenv('LINKEDIN_CLIENT_ID'),
        'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET'), 
        'available': bool(os.getenv('LINKEDIN_CLIENT_ID')),
        'scope': 'w_member_social,r_liteprofile',
        'icon': 'linkedin',
        'color': '#0A66C2'
    }
}

@oauth_bp.route('/platforms', methods=['GET'])
def get_supported_platforms():
    """Get list of supported social media platforms"""
    try:
        platforms = []
        
        for platform_id, config in PLATFORM_CONFIGS.items():
            platform_info = {
                'id': platform_id,
                'name': config['name'],
                'description': f"Connect your {config['name']} account to automatically post content",
                'icon': config['icon'],
                'color': config['color'],
                'available': config['available'],
                'scope': config['scope'],
                'supported_content': ['text', 'images', 'links']
            }
            platforms.append(platform_info)
        
        return jsonify({
            'success': True,
            'platforms': platforms,
            'total_count': len(platforms)
        })
        
    except Exception as e:
        logger.error(f"Error fetching platforms: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch platforms',
            'error': str(e)
        }), 500

@oauth_bp.route('/auth-url/<platform>', methods=['POST'])
@jwt_required()
def generate_auth_url(platform):
    """Generate OAuth authorization URL for platform"""
    try:
        user_id = get_jwt_identity()
        
        if platform not in PLATFORM_CONFIGS:
            return jsonify({
                'success': False,
                'message': 'Platform not supported'
            }), 400
        
        config = PLATFORM_CONFIGS[platform]
        
        if not config.get('client_id'):
            return jsonify({
                'success': False,
                'message': f'{config["name"]} is not configured'
            }), 503
        
        # Generate state for security
        state = secrets.token_urlsafe(32)
        
        # Store state temporarily (in production use Redis)
        oauth_states = get_collection('oauth_states')
        if oauth_states:
            oauth_states.insert_one({
                'state': state,
                'user_id': user_id,
                'platform': platform,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(minutes=10)
            })
        
        # Build authorization URL (simplified)
        auth_url = f"https://example.com/oauth/{platform}?state={state}"
        
        return jsonify({
            'success': True,
            'auth_url': auth_url,
            'state': state,
            'platform': platform,
            'expires_in': 600
        })
        
    except Exception as e:
        logger.error(f"Error generating auth URL for {platform}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to generate authorization URL',
            'error': str(e)
        }), 500

@oauth_bp.route('/connected-accounts', methods=['GET'])
@jwt_required()
def get_connected_accounts():
    """Get user's connected social media accounts"""
    try:
        user_id = get_jwt_identity()
        
        social_accounts = get_collection('social_accounts')
        if not social_accounts:
            return jsonify({
                'success': True,
                'accounts': [],
                'total_count': 0,
                'active_count': 0
            })
        
        accounts = list(social_accounts.find({
            'user_id': user_id,
            'is_active': True
        }))
        
        formatted_accounts = []
        for account in accounts:
            platform_config = PLATFORM_CONFIGS.get(account['platform'], {})
            
            formatted_account = {
                'platform': account['platform'],
                'platform_name': platform_config.get('name', account['platform'].title()),
                'icon': account['platform'],
                'color': platform_config.get('color', '#6B7280'),
                'connection_status': 'active',
                'connected_at': account.get('connected_at'),
                'profile_data': {
                    'username': account.get('username', ''),
                    'display_name': account.get('display_name', ''),
                    'profile_picture': account.get('profile_picture', ''),
                }
            }
            formatted_accounts.append(formatted_account)
        
        return jsonify({
            'success': True,
            'accounts': formatted_accounts,
            'total_count': len(formatted_accounts),
            'active_count': len(formatted_accounts)
        })
        
    except Exception as e:
        logger.error(f"Error fetching connected accounts: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch connected accounts',
            'error': str(e)
        }), 500

@oauth_bp.route('/disconnect/<platform>', methods=['DELETE'])
@jwt_required()
def disconnect_platform(platform):
    """Disconnect a social media platform"""
    try:
        user_id = get_jwt_identity()
        
        social_accounts = get_collection('social_accounts')
        if not social_accounts:
            return jsonify({
                'success': False,
                'message': 'Database unavailable'
            }), 503
        
        result = social_accounts.update_one(
            {'user_id': user_id, 'platform': platform},
            {'$set': {'is_active': False, 'disconnected_at': datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            return jsonify({
                'success': False,
                'message': 'Platform connection not found'
            }), 404
        
        platform_name = PLATFORM_CONFIGS.get(platform, {}).get('name', platform.title())
        
        return jsonify({
            'success': True,
            'message': f'{platform_name} disconnected successfully'
        })
        
    except Exception as e:
        logger.error(f"Error disconnecting {platform}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to disconnect platform',
            'error': str(e)
        }), 500