"""
Content Scheduler Routes for VelocityPost.ai
Manages post scheduling, timing optimization, and automation settings
"""










from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)
scheduler_bp = Blueprint('scheduler', __name__)

@scheduler_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_schedule_settings():
    """Get user's posting schedule settings"""
    try:
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Default schedule settings - in production, store in database
        default_settings = {
            'auto_posting_enabled': False,
            'posting_frequency': {
                'posts_per_day': 3 if user.subscription_plan != 'free' else 2,
                'interval_hours': 8 if user.subscription_plan != 'free' else 12
            },
            'active_hours': {
                'start_time': '09:00',
                'end_time': '18:00',
                'timezone': 'UTC'
            },
            'active_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
            'platform_settings': {
                'instagram': {
                    'enabled': True,
                    'posts_per_day': 2,
                    'optimal_times': ['10:00', '15:00', '19:00'],
                    'hashtag_strategy': 'trending'
                },
                'facebook': {
                    'enabled': False,
                    'posts_per_day': 1,
                    'optimal_times': ['12:00', '18:00'],
                    'hashtag_strategy': 'minimal'
                },
                'twitter': {
                    'enabled': False,
                    'posts_per_day': 4,
                    'optimal_times': ['09:00', '13:00', '17:00', '20:00'],
                    'hashtag_strategy': 'focused'
                },
                'linkedin': {
                    'enabled': False,
                    'posts_per_day': 1,
                    'optimal_times': ['08:00', '12:00', '17:00'],
                    'hashtag_strategy': 'professional'
                }
            },
            'content_distribution': {
                'tech': 40,
                'business': 30,
                'lifestyle': 20,
                'memes': 10
            },
            'smart_scheduling': {
                'enabled': user.subscription_plan != 'free',
                'optimize_for_engagement': True,
                'avoid_holidays': True,
                'analyze_best_times': user.subscription_plan == 'agency'
            },
            'backup_content': {
                'enabled': True,
                'fallback_domains': ['tech', 'business'],
                'minimum_queue_size': 5
            }
        }
        
        # In production, merge with user's saved settings
        # user_settings = user.scheduler_settings or {}
        # settings = {**default_settings, **user_settings}
        
        return jsonify({
            'success': True,
            'settings': default_settings,
            'subscription_plan': user.subscription_plan,
            'features_available': {
                'smart_scheduling': user.subscription_plan != 'free',
                'unlimited_platforms': user.subscription_plan == 'agency',
                'advanced_analytics': user.subscription_plan == 'agency',
                'custom_posting_windows': user.subscription_plan != 'free'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get schedule settings: {e}")
        return jsonify({'error': 'Failed to get schedule settings'}), 500

@scheduler_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_schedule_settings():
    """Update user's posting schedule settings"""
    try:
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate settings based on subscription plan
        if user.subscription_plan == 'free':
            # Limit features for free users
            if data.get('posting_frequency', {}).get('posts_per_day', 0) > 2:
                return jsonify({'error': 'Free plan limited to 2 posts per day'}), 403
            
            if data.get('smart_scheduling', {}).get('enabled', False):
                return jsonify({'error': 'Smart scheduling requires Pro plan'}), 403
        
        # Validate posting frequency
        frequency = data.get('posting_frequency', {})
        if frequency.get('posts_per_day', 0) > 20:
            return jsonify({'error': 'Maximum 20 posts per day allowed'}), 400
        
        # Validate time format
        active_hours = data.get('active_hours', {})
        if active_hours.get('start_time') and active_hours.get('end_time'):
            try:
                start = datetime.strptime(active_hours['start_time'], '%H:%M')
                end = datetime.strptime(active_hours['end_time'], '%H:%M')
                if start >= end:
                    return jsonify({'error': 'End time must be after start time'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid time format. Use HH:MM'}), 400
        
        # In production, save settings to database
        # user.scheduler_settings = data
        # user.updated_at = datetime.utcnow()
        # user.save()
        
        logger.info(f"Schedule settings updated for user {current_user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Schedule settings updated successfully',
            'settings': data
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to update schedule settings: {e}")
        return jsonify({'error': 'Failed to update schedule settings'}), 500

@scheduler_bp.route('/queue', methods=['GET'])
@jwt_required()
def get_posting_queue():
    """Get upcoming scheduled posts"""
    try:
        current_user_id = get_jwt_identity()
        
        # Mock scheduled posts - implement with actual database
        now = datetime.utcnow()
        
        queue = []
        for i in range(10):
            queue.append({
                'id': f'post_{i+1}',
                'scheduled_time': (now + timedelta(hours=2*i)).isoformat(),
                'platform': ['instagram', 'facebook', 'twitter'][i % 3],
                'domain': ['tech', 'business', 'lifestyle'][i % 3],
                'content_preview': f'Scheduled post {i+1} preview...',
                'status': 'pending',
                'estimated_engagement': 85 + (i % 15),
                'content_generated': i < 5,
                'retry_count': 0
            })
        
        return jsonify({
            'success': True,
            'queue': queue,
            'total': len(queue),
            'next_post_in': '2 hours 15 minutes',
            'queue_health': 'good'
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get posting queue: {e}")
        return jsonify({'error': 'Failed to get posting queue'}), 500

@scheduler_bp.route('/queue/<post_id>', methods=['DELETE'])
@jwt_required()
def remove_from_queue(post_id):
    """Remove a post from the scheduled queue"""
    try:
        current_user_id = get_jwt_identity()
        
        # In production, remove from database
        logger.info(f"Removed post {post_id} from queue for user {current_user_id}")
        
        return jsonify({
            'success': True,
            'message': f'Post {post_id} removed from queue'
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to remove post from queue: {e}")
        return jsonify({'error': 'Failed to remove post from queue'}), 500

@scheduler_bp.route('/optimal-times', methods=['GET'])
@jwt_required()
def get_optimal_posting_times():
    """Get AI-recommended optimal posting times"""
    try:
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.subscription_plan == 'free':
            return jsonify({'error': 'Optimal timing analysis requires Pro plan'}), 403
        
        # Mock optimal times - implement with actual analytics
        optimal_times = {
            'instagram': {
                'weekdays': ['10:00', '15:00', '19:00'],
                'weekends': ['11:00', '14:00', '20:00'],
                'best_day': 'wednesday',
                'engagement_peak': '15:00'
            },
            'facebook': {
                'weekdays': ['09:00', '13:00', '18:00'],
                'weekends': ['10:00', '15:00', '19:00'],
                'best_day': 'thursday',
                'engagement_peak': '13:00'
            },
            'twitter': {
                'weekdays': ['08:00', '12:00', '17:00', '20:00'],
                'weekends': ['10:00', '14:00', '18:00'],
                'best_day': 'tuesday',
                'engagement_peak': '12:00'
            },
            'linkedin': {
                'weekdays': ['08:00', '12:00', '17:00'],
                'weekends': ['10:00', '15:00'],
                'best_day': 'wednesday',
                'engagement_peak': '12:00'
            }
        }
        
        return jsonify({
            'success': True,
            'optimal_times': optimal_times,
            'timezone': 'UTC',
            'last_updated': datetime.utcnow().isoformat(),
            'confidence_score': 87
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get optimal times: {e}")
        return jsonify({'error': 'Failed to get optimal times'}), 500

@scheduler_bp.route('/automation/start', methods=['POST'])
@jwt_required()
def start_automation():
    """Start automated posting"""
    try:
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.subscription_plan == 'free':
            return jsonify({'error': 'Automation requires Pro plan'}), 403
        
        # Check if user has connected platforms
        if len(user.connected_platforms) == 0:
            return jsonify({'error': 'Please connect at least one social media platform'}), 400
        
        # In production, start background automation tasks
        logger.info(f"Automation started for user {current_user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Automated posting started successfully',
            'status': 'active',
            'next_post_scheduled': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            'platforms_active': user.connected_platforms
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to start automation: {e}")
        return jsonify({'error': 'Failed to start automation'}), 500

@scheduler_bp.route('/automation/stop', methods=['POST'])
@jwt_required()
def stop_automation():
    """Stop automated posting"""
    try:
        current_user_id = get_jwt_identity()
        
        # In production, stop background automation tasks
        logger.info(f"Automation stopped for user {current_user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Automated posting stopped successfully',
            'status': 'stopped',
            'posts_in_queue': 5
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to stop automation: {e}")
        return jsonify({'error': 'Failed to stop automation'}), 500

@scheduler_bp.route('/automation/status', methods=['GET'])
@jwt_required()
def get_automation_status():
    """Get current automation status"""
    try:
        current_user_id = get_jwt_identity()
        user = User.objects(id=current_user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Mock automation status - implement with actual tracking
        status = {
            'is_active': False,
            'posts_today': 3,
            'posts_scheduled': 7,
            'next_post_in': '1 hour 45 minutes',
            'success_rate': 94.5,
            'active_platforms': user.connected_platforms,
            'last_error': None,
            'queue_health': 'good',
            'content_generated': True,
            'settings_valid': True
        }
        
        return jsonify({
            'success': True,
            'automation_status': status
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get automation status: {e}")
        return jsonify({'error': 'Failed to get automation status'}), 500

@scheduler_bp.route('/preview-schedule', methods=['POST'])
@jwt_required()
def preview_schedule():
    """Preview posting schedule based on current settings"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        days_ahead = min(data.get('days', 7), 30)  # Max 30 days preview
        
        # Generate preview schedule
        now = datetime.utcnow()
        preview = []
        
        for day in range(days_ahead):
            date = now + timedelta(days=day)
            day_name = date.strftime('%A').lower()
            
            # Skip if not in active days (mock logic)
            if day_name not in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                continue
            
            # Generate posts for this day
            for hour in [10, 15, 19]:  # Mock posting times
                preview.append({
                    'date': date.replace(hour=hour, minute=0).isoformat(),
                    'platform': ['instagram', 'facebook', 'twitter'][hour % 3],
                    'domain': ['tech', 'business', 'lifestyle'][day % 3],
                    'estimated_engagement': 75 + (day % 25),
                    'day_of_week': day_name.title(),
                    'optimal_time': hour in [10, 15]
                })
        
        return jsonify({
            'success': True,
            'preview': preview[:50],  # Limit to 50 posts
            'total_posts': len(preview),
            'date_range': {
                'start': now.isoformat(),
                'end': (now + timedelta(days=days_ahead)).isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to generate schedule preview: {e}")
        return jsonify({'error': 'Failed to generate preview'}), 500