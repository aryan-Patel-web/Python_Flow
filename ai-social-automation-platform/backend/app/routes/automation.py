#!/usr/bin/env python3
"""
Automation Routes for VelocityPost.ai
Handles auto-posting automation controls and settings
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

# Import database functions
from app.utils.database import get_collection

# Create blueprint
automation_bp = Blueprint('automation', __name__)

logger = logging.getLogger(__name__)

@automation_bp.route('/status', methods=['GET'])
@jwt_required()
def get_automation_status():
    """Get current automation status for user"""
    try:
        user_id = get_jwt_identity()
        
        # Get automation settings
        automation_settings = get_collection('automation_settings')
        settings = None
        if automation_settings:
            settings = automation_settings.find_one({'user_id': user_id})
        
        # Get connected platforms count
        social_accounts = get_collection('social_accounts')
        connected_count = 0
        if social_accounts:
            connected_count = social_accounts.count_documents({
                'user_id': user_id,
                'is_active': True
            })
        
        # Get recent posts count
        posts = get_collection('posts')
        today_posts = 0
        total_automated_posts = 0
        
        if posts:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            today_posts = posts.count_documents({
                'user_id': user_id,
                'created_at': {'$gte': today, '$lt': tomorrow}
            })
            
            total_automated_posts = posts.count_documents({
                'user_id': user_id,
                'is_automated': True
            })
        
        # Default settings if not found
        if not settings:
            settings = {
                'is_active': False,
                'selected_domains': [],
                'posting_frequency': {
                    'posts_per_day': 2,
                    'interval_hours': 12
                },
                'posting_schedule': {
                    'times': ['09:00', '13:00', '17:00'],
                    'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
                    'timezone': 'UTC'
                },
                'content_settings': {
                    'tone': 'professional',
                    'target_audience': 'general',
                    'include_hashtags': True,
                    'auto_optimize': True
                },
                'active_hours': {
                    'start_time': '09:00',
                    'end_time': '18:00',
                    'timezone': 'UTC'
                }
            }
        
        # Calculate next post time
        next_post_time = None
        if settings.get('is_active') and settings.get('posting_frequency'):
            next_post_time = datetime.utcnow() + timedelta(hours=settings['posting_frequency']['interval_hours'])
        
        automation_status = {
            'is_active': settings.get('is_active', False),
            'selected_domains': settings.get('selected_domains', []),
            'connected_platforms_count': connected_count,
            'posting_frequency': settings.get('posting_frequency', {}),
            'posting_schedule': settings.get('posting_schedule', {}),
            'content_settings': settings.get('content_settings', {}),
            'active_hours': settings.get('active_hours', {}),
            'statistics': {
                'posts_today': today_posts,
                'total_automated_posts': total_automated_posts,
                'next_post_time': next_post_time.isoformat() if next_post_time else None,
                'max_posts_per_day': settings.get('posting_frequency', {}).get('posts_per_day', 2)
            },
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'automation_status': automation_status
        })
        
    except Exception as e:
        logger.error(f"Error getting automation status: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get automation status',
            'error': str(e)
        }), 500

@automation_bp.route('/start', methods=['POST'])
@jwt_required()
def start_automation():
    """Start automation for user"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # Check if user has connected platforms
        social_accounts = get_collection('social_accounts')
        connected_count = 0
        if social_accounts:
            connected_count = social_accounts.count_documents({
                'user_id': user_id,
                'is_active': True
            })
        
        if connected_count == 0:
            return jsonify({
                'success': False,
                'message': 'No connected platforms found',
                'error': 'Please connect at least one social media platform'
            }), 400
        
        # Get user plan limits
        users = get_collection('users')
        user = None
        if users:
            user = users.find_one({'_id': ObjectId(user_id)})
        
        plan_type = user.get('plan_type', 'free') if user else 'free'
        
        # Plan limits
        plan_limits = {
            'free': {'max_platforms': 2, 'max_posts_per_day': 2},
            'pro': {'max_platforms': 5, 'max_posts_per_day': 6},
            'agency': {'max_platforms': 999, 'max_posts_per_day': 20}
        }
        
        limits = plan_limits.get(plan_type, plan_limits['free'])
        
        if connected_count > limits['max_platforms']:
            return jsonify({
                'success': False,
                'message': f'Plan limit exceeded. {plan_type.title()} plan allows {limits["max_platforms"]} platforms',
                'error': 'Upgrade your plan to connect more platforms'
            }), 400
        
        # Save automation settings
        automation_settings = get_collection('automation_settings')
        if not automation_settings:
            return jsonify({
                'success': False,
                'message': 'Database unavailable'
            }), 503
        
        settings_data = {
            'user_id': user_id,
            'is_active': True,
            'platforms': data.get('platforms', []),
            'content_domains': data.get('content_domains', []),
            'selected_domains': data.get('content_domains', []),
            'posting_frequency': data.get('posting_frequency', {
                'posts_per_day': min(data.get('posting_frequency', {}).get('posts_per_day', 2), limits['max_posts_per_day']),
                'interval_hours': 12
            }),
            'posting_schedule': data.get('posting_schedule', {
                'times': ['09:00', '15:00'],
                'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
                'timezone': 'UTC'
            }),
            'content_settings': data.get('content_settings', {
                'tone': 'professional',
                'target_audience': 'business',
                'include_hashtags': True,
                'auto_optimize': True
            }),
            'active_hours': data.get('active_hours', {
                'start_time': '09:00',
                'end_time': '18:00',
                'timezone': 'UTC'
            }),
            'started_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Update or insert automation settings
        automation_settings.update_one(
            {'user_id': user_id},
            {'$set': settings_data},
            upsert=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Auto-posting automation started successfully',
            'automation_settings': {
                'platforms': data.get('platforms', []),
                'content_domains': data.get('content_domains', []),
                'posting_frequency': settings_data['posting_frequency'],
                'is_active': True
            }
        })
        
    except Exception as e:
        logger.error(f"Start automation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to start automation',
            'error': str(e)
        }), 500

@automation_bp.route('/pause', methods=['POST'])
@jwt_required()
def pause_automation():
    """Pause automation"""
    try:
        user_id = get_jwt_identity()
        
        automation_settings = get_collection('automation_settings')
        if not automation_settings:
            return jsonify({
                'success': False,
                'message': 'Database unavailable'
            }), 503
        
        result = automation_settings.update_one(
            {'user_id': user_id},
            {'$set': {
                'is_active': False,
                'paused_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }}
        )
        
        if result.matched_count == 0:
            return jsonify({
                'success': False,
                'message': 'Automation not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Automation paused successfully'
        })
        
    except Exception as e:
        logger.error(f"Pause automation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to pause automation',
            'error': str(e)
        }), 500

@automation_bp.route('/stop', methods=['POST'])
@jwt_required()
def stop_automation():
    """Stop automation"""
    try:
        user_id = get_jwt_identity()
        
        automation_settings = get_collection('automation_settings')
        if not automation_settings:
            return jsonify({
                'success': False,
                'message': 'Database unavailable'
            }), 503
        
        result = automation_settings.update_one(
            {'user_id': user_id},
            {'$set': {
                'is_active': False,
                'stopped_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }}
        )
        
        if result.matched_count == 0:
            return jsonify({
                'success': False,
                'message': 'Automation not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Automation stopped successfully'
        })
        
    except Exception as e:
        logger.error(f"Stop automation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to stop automation',
            'error': str(e)
        }), 500

@automation_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_automation_settings():
    """Get automation settings"""
    try:
        user_id = get_jwt_identity()
        
        automation_settings = get_collection('automation_settings')
        if not automation_settings:
            return jsonify({
                'success': False,
                'message': 'Database unavailable'
            }), 503
        
        settings = automation_settings.find_one({'user_id': user_id})
        
        if not settings:
            return jsonify({
                'success': False,
                'message': 'Automation settings not found'
            }), 404
        
        settings_response = {
            'selected_domains': settings.get('selected_domains', []),
            'content_domains': settings.get('content_domains', []),
            'posting_frequency': settings.get('posting_frequency', {}),
            'posting_schedule': settings.get('posting_schedule', {}),
            'content_settings': settings.get('content_settings', {}),
            'active_hours': settings.get('active_hours', {}),
            'platform_settings': settings.get('platform_settings', {}),
            'is_active': settings.get('is_active', False),
            'created_at': settings.get('created_at', datetime.utcnow()).isoformat(),
            'updated_at': settings.get('updated_at', datetime.utcnow()).isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': 'Automation settings retrieved',
            'settings': settings_response
        })
        
    except Exception as e:
        logger.error(f"Get automation settings error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get automation settings',
            'error': str(e)
        }), 500

@automation_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_automation_settings():
    """Update automation settings"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        automation_settings = get_collection('automation_settings')
        if not automation_settings:
            return jsonify({
                'success': False,
                'message': 'Database unavailable'
            }), 503
        
        # Fields that can be updated
        allowed_fields = [
            'selected_domains', 'content_domains', 'posting_frequency', 
            'posting_schedule', 'content_settings', 'active_hours', 'platform_settings'
        ]
        
        update_data = {}
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({
                'success': False,
                'message': 'No valid fields to update'
            }), 400
        
        # Add update timestamp
        update_data['updated_at'] = datetime.utcnow()
        
        # Update settings
        result = automation_settings.update_one(
            {'user_id': user_id},
            {'$set': update_data},
            upsert=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Automation settings updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Update automation settings error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update automation settings',
            'error': str(e)
        }), 500

@automation_bp.route('/generate-optimal-times', methods=['POST'])
@jwt_required()
def generate_optimal_posting_times():
    """Generate optimal posting times"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        platforms = data.get('platforms', [])
        timezone = data.get('timezone', 'UTC')
        posts_per_day = data.get('posts_per_day', 3)
        
        # Default optimal times
        optimal_times = ['11:00', '13:00', '15:00']
        
        schedule = {
            'weekdays': {
                'times': optimal_times[:posts_per_day],
                'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
                'timezone': timezone
            },
            'weekends': {
                'times': optimal_times[:2],
                'days': ['saturday', 'sunday'],
                'timezone': timezone
            },
            'recommended_times': optimal_times,
            'platform_analysis': {},
            'generated_at': datetime.utcnow().isoformat(),
            'timezone': timezone
        }
        
        return jsonify({
            'success': True,
            'message': 'Optimal posting times generated',
            'schedule': schedule
        })
        
    except Exception as e:
        logger.error(f"Generate optimal times error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to generate optimal times',
            'error': str(e)
        }), 500

@automation_bp.route('/recent-posts', methods=['GET'])
@jwt_required()
def get_recent_automated_posts():
    """Get recent automated posts"""
    try:
        user_id = get_jwt_identity()
        limit = min(int(request.args.get('limit', 20)), 100)
        
        posts = get_collection('posts')
        posts_list = []
        
        if posts:
            recent_posts = list(posts.find({
                'user_id': user_id,
                'is_automated': True
            }).sort('created_at', -1).limit(limit))
            
            for post in recent_posts:
                posts_list.append({
                    'id': str(post['_id']),
                    'platform': post.get('platform', ''),
                    'content': post.get('content', ''),
                    'hashtags': post.get('hashtags', []),
                    'domain': post.get('domain', ''),
                    'posted_at': post.get('created_at', datetime.utcnow()).isoformat(),
                    'engagement': post.get('engagement', {}),
                    'status': post.get('status', 'posted'),
                    'performance_score': post.get('performance_score', 0),
                    'ai_generated': post.get('is_ai_generated', True)
                })
        
        return jsonify({
            'success': True,
            'message': 'Recent automated posts retrieved',
            'posts': posts_list,
            'total': len(posts_list)
        })
        
    except Exception as e:
        logger.error(f"Get recent posts error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get recent posts',
            'error': str(e)
        }), 500

@automation_bp.route('/queue', methods=['GET'])
@jwt_required()
def get_posting_queue():
    """Get posting queue"""
    try:
        user_id = get_jwt_identity()
        
        # Simplified queue - in production you'd have actual scheduled posts
        queue = []
        
        return jsonify({
            'success': True,
            'message': 'Posting queue retrieved',
            'queue': queue,
            'total': len(queue)
        })
        
    except Exception as e:
        logger.error(f"Get posting queue error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get posting queue',
            'error': str(e)
        }), 500

@automation_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_automation_analytics():
    """Get automation analytics"""
    try:
        user_id = get_jwt_identity()
        days = int(request.args.get('days', 30))
        
        # Simplified analytics
        analytics_data = {
            'automated_posts': 0,
            'manual_posts': 0,
            'time_saved_hours': 0,
            'platform_breakdown': {},
            'period_days': days,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': 'Automation analytics retrieved',
            'analytics': analytics_data
        })
        
    except Exception as e:
        logger.error(f"Automation analytics error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get automation analytics',
            'error': str(e)
        }), 500