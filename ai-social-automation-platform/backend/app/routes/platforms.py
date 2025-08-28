#!/usr/bin/env python3
"""
Platform Management Routes for VelocityPost.ai
Simplified version for testing
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from bson import ObjectId

# Import database with fallback
try:
    from app.utils.database import get_collection
except ImportError:
    def get_collection(name):
        return None

# Import auth with fallback
try:
    from app.routes.auth import require_auth
except ImportError:
    def require_auth(f):
        def decorated_function(*args, **kwargs):
            request.user_id = "dummy_user_id"
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function

logger = logging.getLogger(__name__)

# Create blueprint
platforms_bp = Blueprint('platforms', __name__)

@platforms_bp.route('/supported', methods=['GET'])
def get_supported_platforms():
    """Get list of supported platforms"""
    try:
        platforms = {
            'instagram': {
                'name': 'Instagram',
                'display_name': 'Instagram',
                'description': 'Connect your Instagram account for automated posting',
                'features': ['text_posts', 'image_posts'],
                'max_post_length': 2200,
                'supports_images': True,
                'supports_videos': True,
                'supports_scheduling': True
            },
            'facebook': {
                'name': 'Facebook',
                'display_name': 'Facebook',
                'description': 'Connect your Facebook account for automated posting',
                'features': ['text_posts', 'image_posts'],
                'max_post_length': 63206,
                'supports_images': True,
                'supports_videos': True,
                'supports_scheduling': True
            }
        }
        
        return jsonify({
            'success': True,
            'message': 'Supported platforms retrieved',
            'platforms': platforms
        }), 200
        
    except Exception as e:
        logger.error(f'Get supported platforms error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Failed to get supported platforms',
            'error': str(e)
        }), 500

@platforms_bp.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        'success': True,
        'message': 'Platforms blueprint is working!',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

print("✅ Platforms blueprint loaded successfully")