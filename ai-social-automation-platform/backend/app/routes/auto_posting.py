"""
Auto-Posting Management Routes for VelocityPost.ai
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.database import get_db
from app.models.user import User
from app.models.platform_connection import PlatformConnection
import logging

logger = logging.getLogger(__name__)
auto_posting_bp = Blueprint('auto_posting', __name__)

@auto_posting_bp.route('/status', methods=['GET'])
@jwt_required()
def get_automation_status():
    """Get auto-posting automation status"""
    try:
        current_user_id = get_jwt_identity()
        db = get_db()
        user = User.find_by_id(db, current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get connected platforms
        connected_platforms = PlatformConnection.find_by_user(db, current_user_id)
        
        # Mock status for now - implement actual automation logic
        status_data = {
            'status': 'stopped',
            'is_active': False,
            'posts_today': 0,
            'posts_scheduled': 0,
            'next_post_in': None,
            'success_rate': 95.5,
            'active_platforms': [conn['platform'] for conn in connected_platforms],
            'connected_platforms_count': len(connected_platforms),
            'total_posts': 0,
            'last_post_at': None,
            'automation_enabled': user.get('settings', {}).get('auto_posting_enabled', False),
            'plan_limits': {
                'max_posts_per_day': 2 if user.get('plan_type') == 'free' else 20,
                'can_auto_post': user.get('plan_type') != 'free'
            }
        }
        
        return jsonify({
            'success': True,
            'automation_status': status_data
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get automation status: {e}")
        return jsonify({'error': 'Failed to get automation status'}), 500

@auto_posting_bp.route('/start', methods=['POST'])
@jwt_required()
def start_automation():
    """Start auto-posting automation"""
    try:
        current_user_id = get_jwt_identity()
        db = get_db()
        user = User.find_by_id(db, current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check subscription limits
        if user.get('plan_type') == 'free':
            return jsonify({'error': 'Auto-posting requires Pro plan or higher'}), 403
        
        # Check if user has connected platforms
        connected_platforms = PlatformConnection.find_by_user(db, current_user_id)
        if not connected_platforms:
            return jsonify({'error': 'Please connect at least one social media platform first'}), 400
        
        # Update user settings to enable auto-posting
        User.update(db, current_user_id, {
            'settings.auto_posting_enabled': True
        })
        
        # Start automation logic here (would typically involve Celery tasks)
        logger.info(f"Auto-posting started for user {current_user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Auto-posting automation started successfully',
            'status': 'active',
            'platforms_active': [conn['platform'] for conn in connected_platforms]
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to start automation: {e}")
        return jsonify({'error': 'Failed to start automation'}), 500

@auto_posting_bp.route('/stop', methods=['POST'])
@jwt_required()
def stop_automation():
    """Stop auto-posting automation"""
    try:
        current_user_id = get_jwt_identity()
        db = get_db()
        
        # Update user settings to disable auto-posting
        User.update(db, current_user_id, {
            'settings.auto_posting_enabled': False
        })
        
        # Stop automation logic here
        logger.info(f"Auto-posting stopped for user {current_user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Auto-posting automation stopped successfully',
            'status': 'stopped'
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to stop automation: {e}")
        return jsonify({'error': 'Failed to stop automation'}), 500

@auto_posting_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_automation_settings():
    """Get automation configuration settings"""
    try:
        current_user_id = get_jwt_identity()
        db = get_db()
        user = User.find_by_id(db, current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        settings = {
            'auto_posting_enabled': user.get('settings', {}).get('auto_posting_enabled', False),
            'posts_per_day': 2 if user.get('plan_type') == 'free' else 6,
            'posting_hours': {
                'start': '09:00',
                'end': '18:00'
            },
            'active_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
            'content_types': ['ai_generated'],
            'platforms_enabled': {}
        }
        
        return jsonify({
            'success': True,
            'settings': settings
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get automation settings: {e}")
        return jsonify({'error': 'Failed to get automation settings'}), 500

@auto_posting_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_automation_settings():
    """Update automation configuration settings"""
    try:
        current_user_id = get_jwt_identity()
        db = get_db()
        user = User.find_by_id(db, current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate and update settings
        update_data = {}
        
        if 'auto_posting_enabled' in data:
            if user.get('plan_type') == 'free' and data['auto_posting_enabled']:
                return jsonify({'error': 'Auto-posting requires Pro plan or higher'}), 403
            update_data['settings.auto_posting_enabled'] = data['auto_posting_enabled']
        
        if 'posts_per_day' in data:
            max_posts = 2 if user.get('plan_type') == 'free' else 20
            posts_per_day = min(data['posts_per_day'], max_posts)
            update_data['settings.posts_per_day'] = posts_per_day
        
        # Update user settings
        if update_data:
            User.update(db, current_user_id, update_data)
        
        logger.info(f"Automation settings updated for user {current_user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Automation settings updated successfully',
            'settings': data
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to update automation settings: {e}")
        return jsonify({'error': 'Failed to update automation settings'}), 500

@auto_posting_bp.route('/queue', methods=['GET'])
@jwt_required()
def get_posting_queue():
    """Get upcoming scheduled posts"""
    try:
        current_user_id = get_jwt_identity()
        
        # Mock queue data - implement actual database queries
        queue = []
        
        return jsonify({
            'success': True,
            'queue': queue,
            'total': len(queue),
            'next_post_in': '2 hours' if queue else None
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get posting queue: {e}")
        return jsonify({'error': 'Failed to get posting queue'}), 500

@auto_posting_bp.route('/history', methods=['GET'])
@jwt_required()
def get_posting_history():
    """Get recent posting history"""
    try:
        current_user_id = get_jwt_identity()
        
        # Mock history data - implement actual database queries
        history = []
        
        return jsonify({
            'success': True,
            'history': history,
            'total': len(history)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get posting history: {e}")
        return jsonify({'error': 'Failed to get posting history'}), 500