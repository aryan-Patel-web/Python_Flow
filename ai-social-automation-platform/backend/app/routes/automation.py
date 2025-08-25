"""
Automation Routes for VelocityPost.ai
Handles auto-posting automation controls and settings
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from bson import ObjectId
import json

from app.utils.database import get_database
from app.utils.helpers import generate_response
from app.services.ai_content_generator import content_generator

automation_bp = Blueprint('automation', __name__)

@automation_bp.route('/status', methods=['GET'])
@jwt_required()
def get_automation_status():
    """Get user's automation status"""
    try:
        user_id = get_jwt_identity()
        
        db = get_database()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return generate_response(False, 'User not found', status_code=404)
        
        # Get automation settings
        automation_settings = db.automation_settings.find_one({
            'user_id': ObjectId(user_id)
        })
        
        if not automation_settings:
            # Create default automation settings
            default_settings = {
                'user_id': ObjectId(user_id),
                'is_active': False,
                'selected_domains': [],
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
                'platform_settings': {},
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            db.automation_settings.insert_one(default_settings)
            automation_settings = default_settings
        
        # Get connected platforms
        connected_platforms = list(db.platform_connections.find({
            'user_id': ObjectId(user_id),
            'is_active': True
        }))
        
        # Get recent automation activity
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        posts_today = db.posts.find({
            'user_id': ObjectId(user_id),
            'posted_at': {'$gte': today},
            'source': 'automation'
        }).count()
        
        # Calculate next posting time
        next_post_time = None
        if automation_settings['is_active']:
            next_post_time = calculate_next_post_time(automation_settings['posting_schedule'])
        
        # Get plan limits
        plan_limits = user.get('plan_limits', {})
        
        status_data = {
            'is_active': automation_settings['is_active'],
            'selected_domains': automation_settings['selected_domains'],
            'connected_platforms': [{
                'platform': p['platform'],
                'username': p['username'],
                'is_active': p['is_active']
            } for p in connected_platforms],
            'posting_schedule': automation_settings['posting_schedule'],
            'content_settings': automation_settings['content_settings'],
            'posts_today': posts_today,
            'max_posts_per_day': plan_limits.get('max_posts_per_day', 2),
            'next_post_time': next_post_time.isoformat() if next_post_time else None,
            'last_updated': automation_settings['updated_at'].isoformat()
        }
        
        return generate_response(
            True,
            'Automation status retrieved',
            data={'status': status_data}
        )
        
    except Exception as e:
        current_app.logger.error(f'Get automation status error: {str(e)}')
        return generate_response(False, 'Failed to get automation status', status_code=500)

@automation_bp.route('/start', methods=['POST'])
@jwt_required()
def start_automation():
    """Start auto-posting automation"""
    try:
        user_id = get_jwt_identity()
        
        db = get_database()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return generate_response(False, 'User not found', status_code=404)
        
        # Check if user has connected platforms
        connected_platforms_count = db.platform_connections.find({
            'user_id': ObjectId(user_id),
            'is_active': True
        }).count()
        
        if connected_platforms_count == 0:
            return generate_response(False, 'Please connect at least one social media platform first', status_code=400)
        
        # Get or create automation settings
        automation_settings = db.automation_settings.find_one({
            'user_id': ObjectId(user_id)
        })
        
        if not automation_settings:
            return generate_response(False, 'Please configure automation settings first', status_code=400)
        
        # Check if user has selected domains
        if not automation_settings.get('selected_domains'):
            return generate_response(False, 'Please select at least one content domain', status_code=400)
        
        # Start automation
        db.automation_settings.update_one(
            {'user_id': ObjectId(user_id)},
            {
                '$set': {
                    'is_active': True,
                    'started_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        # Update user automation status
        db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'auto_posting_active': True}}
        )
        
        # Schedule first automated posts
        schedule_next_automated_posts(user_id)
        
        return generate_response(True, 'Automation started successfully')
        
    except Exception as e:
        current_app.logger.error(f'Start automation error: {str(e)}')
        return generate_response(False, 'Failed to start automation', status_code=500)

@automation_bp.route('/pause', methods=['POST'])
@jwt_required()
def pause_automation():
    """Pause auto-posting automation"""
    try:
        user_id = get_jwt_identity()
        
        db = get_database()
        
        # Pause automation
        result = db.automation_settings.update_one(
            {'user_id': ObjectId(user_id)},
            {
                '$set': {
                    'is_active': False,
                    'paused_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            return generate_response(False, 'Automation settings not found', status_code=404)
        
        # Update user automation status
        db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'auto_posting_active': False}}
        )
        
        # Cancel pending scheduled posts
        db.scheduled_posts.update_many(
            {
                'user_id': ObjectId(user_id),
                'status': 'pending',
                'source': 'automation'
            },
            {
                '$set': {
                    'status': 'cancelled',
                    'cancelled_at': datetime.utcnow()
                }
            }
        )
        
        return generate_response(True, 'Automation paused successfully')
        
    except Exception as e:
        current_app.logger.error(f'Pause automation error: {str(e)}')
        return generate_response(False, 'Failed to pause automation', status_code=500)

@automation_bp.route('/stop', methods=['POST'])
@jwt_required()
def stop_automation():
    """Stop auto-posting automation completely"""
    try:
        user_id = get_jwt_identity()
        
        db = get_database()
        
        # Stop automation
        result = db.automation_settings.update_one(
            {'user_id': ObjectId(user_id)},
            {
                '$set': {
                    'is_active': False,
                    'stopped_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            return generate_response(False, 'Automation settings not found', status_code=404)
        
        # Update user automation status
        db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'auto_posting_active': False}}
        )
        
        # Cancel all pending scheduled posts
        db.scheduled_posts.update_many(
            {
                'user_id': ObjectId(user_id),
                'status': 'pending'
            },
            {
                '$set': {
                    'status': 'cancelled',
                    'cancelled_at': datetime.utcnow()
                }
            }
        )
        
        return generate_response(True, 'Automation stopped successfully')
        
    except Exception as e:
        current_app.logger.error(f'Stop automation error: {str(e)}')
        return generate_response(False, 'Failed to stop automation', status_code=500)

@automation_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_automation_settings():
    """Get automation settings"""
    try:
        user_id = get_jwt_identity()
        
        db = get_database()
        settings = db.automation_settings.find_one({
            'user_id': ObjectId(user_id)
        })
        
        if not settings:
            return generate_response(False, 'Automation settings not found', status_code=404)
        
        settings_response = {
            'selected_domains': settings['selected_domains'],
            'posting_schedule': settings['posting_schedule'],
            'content_settings': settings['content_settings'],
            'platform_settings': settings.get('platform_settings', {}),
            'is_active': settings['is_active']
        }
        
        return generate_response(
            True,
            'Automation settings retrieved',
            data={'settings': settings_response}
        )
        
    except Exception as e:
        current_app.logger.error(f'Get automation settings error: {str(e)}')
        return generate_response(False, 'Failed to get automation settings', status_code=500)

@automation_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_automation_settings():
    """Update automation settings"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        db = get_database()
        
        # Fields that can be updated
        allowed_fields = [
            'selected_domains', 'posting_schedule', 'content_settings', 'platform_settings'
        ]
        
        update_data = {}
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return generate_response(False, 'No valid fields to update', status_code=400)
        
        # Add update timestamp
        update_data['updated_at'] = datetime.utcnow()
        
        # Update or create settings
        result = db.automation_settings.update_one(
            {'user_id': ObjectId(user_id)},
            {'$set': update_data},
            upsert=True
        )
        
        # If automation is active, reschedule posts with new settings
        current_settings = db.automation_settings.find_one({
            'user_id': ObjectId(user_id)
        })
        
        if current_settings and current_settings.get('is_active'):
            # Cancel existing pending posts
            db.scheduled_posts.update_many(
                {
                    'user_id': ObjectId(user_id),
                    'status': 'pending',
                    'source': 'automation'
                },
                {
                    '$set': {
                        'status': 'cancelled',
                        'cancelled_at': datetime.utcnow()
                    }
                }
            )
            
            # Schedule new posts with updated settings
            schedule_next_automated_posts(user_id)
        
        return generate_response(True, 'Automation settings updated successfully')
        
    except Exception as e:
        current_app.logger.error(f'Update automation settings error: {str(e)}')
        return generate_response(False, 'Failed to update automation settings', status_code=500)

@automation_bp.route('/generate-optimal-times', methods=['POST'])
@jwt_required()
def generate_optimal_posting_times():
    """Generate AI-optimized posting times"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        platforms = data.get('platforms', [])
        timezone = data.get('timezone', 'UTC')
        
        if not platforms:
            return generate_response(False, 'Platforms list is required', status_code=400)
        
        # AI-optimized posting times based on platform research
        optimal_times = {
            'facebook': ['13:00', '15:00', '20:00'],
            'instagram': ['11:00', '14:00', '19:00'],
            'twitter': ['09:00', '13:00', '17:00'],
            'linkedin': ['08:00', '12:00', '17:00'],
            'youtube': ['14:00', '20:00', '21:00'],
            'tiktok': ['06:00', '10:00', '19:00'],
            'pinterest': ['08:00', '11:00', '20:00']
        }
        
        # Generate combined optimal schedule
        all_times = set()
        for platform in platforms:
            if platform.lower() in optimal_times:
                all_times.update(optimal_times[platform.lower()])
        
        # Sort and limit to reasonable number of posts per day
        sorted_times = sorted(list(all_times))[:5]  # Max 5 times per day
        
        optimal_schedule = {
            'times': sorted_times,
            'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
            'timezone': timezone,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return generate_response(
            True,
            'Optimal posting times generated',
            data={'schedule': optimal_schedule}
        )
        
    except Exception as e:
        current_app.logger.error(f'Generate optimal times error: {str(e)}')
        return generate_response(False, 'Failed to generate optimal times', status_code=500)

@automation_bp.route('/recent-posts', methods=['GET'])
@jwt_required()
def get_recent_automated_posts():
    """Get recent automated posts"""
    try:
        user_id = get_jwt_identity()
        
        limit = min(int(request.args.get('limit', 20)), 100)
        
        db = get_database()
        
        # Get recent automated posts
        posts = list(db.posts.find({
            'user_id': ObjectId(user_id),
            'source': 'automation'
        }).sort('posted_at', -1).limit(limit))
        
        posts_list = []
        for post in posts:
            posts_list.append({
                'id': str(post['_id']),
                'platform': post['platform'],
                'content': post['content'],
                'hashtags': post.get('hashtags', []),
                'domain': post.get('domain'),
                'posted_at': post['posted_at'].isoformat(),
                'engagement': post.get('engagement', {}),
                'status': post['status']
            })
        
        return generate_response(
            True,
            'Recent automated posts retrieved',
            data={'posts': posts_list}
        )
        
    except Exception as e:
        current_app.logger.error(f'Get recent posts error: {str(e)}')
        return generate_response(False, 'Failed to get recent posts', status_code=500)

def calculate_next_post_time(posting_schedule):
    """Calculate next posting time based on schedule"""
    try:
        current_time = datetime.utcnow()
        times = posting_schedule.get('times', [])
        days = posting_schedule.get('days', [])
        
        if not times or not days:
            return None
        
        # Convert day names to numbers
        day_mapping = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        active_days = [day_mapping[day] for day in days if day in day_mapping]
        
        # Find next posting time
        for days_ahead in range(7):  # Check next 7 days
            check_date = current_time + timedelta(days=days_ahead)
            
            if check_date.weekday() in active_days:
                for time_str in sorted(times):
                    hour, minute = map(int, time_str.split(':'))
                    post_time = check_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    if post_time > current_time:
                        return post_time
        
        return None
        
    except Exception:
        return None

def schedule_next_automated_posts(user_id):
    """Schedule next batch of automated posts"""
    try:
        db = get_database()
        
        # Get automation settings
        settings = db.automation_settings.find_one({
            'user_id': ObjectId(user_id)
        })
        
        if not settings or not settings.get('is_active'):
            return
        
        # Get user's plan limits
        user = db.users.find_one({'_id': ObjectId(user_id)})
        plan_limits = user.get('plan_limits', {})
        max_posts_per_day = plan_limits.get('max_posts_per_day', 2)
        
        # Get connected platforms
        platforms = list(db.platform_connections.find({
            'user_id': ObjectId(user_id),
            'is_active': True
        }))
        
        if not platforms:
            return
        
        # Calculate posting times for next 24 hours
        posting_schedule = settings['posting_schedule']
        next_post_times = []
        
        for days_ahead in range(2):  # Next 2 days
            for time_str in posting_schedule.get('times', []):
                try:
                    hour, minute = map(int, time_str.split(':'))
                    post_time = datetime.utcnow().replace(
                        hour=hour, minute=minute, second=0, microsecond=0
                    ) + timedelta(days=days_ahead)
                    
                    if post_time > datetime.utcnow():
                        next_post_times.append(post_time)
                except ValueError:
                    continue
        
        # Limit posts per day
        next_post_times = sorted(next_post_times)[:max_posts_per_day * 2]
        
        # Generate and schedule content
        selected_domains = settings.get('selected_domains', [])
        content_settings = settings.get('content_settings', {})
        
        for post_time in next_post_times:
            # Check if already have post scheduled for this time
            existing = db.scheduled_posts.find_one({
                'user_id': ObjectId(user_id),
                'scheduled_time': post_time,
                'status': 'pending'
            })
            
            if existing:
                continue
            
            # Select random domain and platform
            import random
            if selected_domains and platforms:
                domain = random.choice(selected_domains)
                platform_connection = random.choice(platforms)
                platform = platform_connection['platform']
                
                # Generate content
                try:
                    generated_content = content_generator.generate_content(
                        domain=domain,
                        platform=platform,
                        tone=content_settings.get('tone'),
                        target_audience=content_settings.get('target_audience')
                    )
                    
                    # Save generated content
                    content_doc = {
                        'user_id': ObjectId(user_id),
                        'domain': domain,
                        'platform': platform,
                        'content': generated_content['content'],
                        'hashtags': generated_content['hashtags'],
                        'character_count': generated_content['character_count'],
                        'performance_prediction': generated_content['performance_prediction'],
                        'ai_provider': generated_content['ai_provider'],
                        'status': 'scheduled',
                        'scheduled_time': post_time,
                        'source': 'automation',
                        'created_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                    
                    content_result = db.generated_content.insert_one(content_doc)
                    
                    # Create scheduled post
                    scheduled_post = {
                        'user_id': ObjectId(user_id),
                        'content_id': content_result.inserted_id,
                        'platform': platform,
                        'platform_connection_id': platform_connection['_id'],
                        'scheduled_time': post_time,
                        'status': 'pending',
                        'source': 'automation',
                        'created_at': datetime.utcnow()
                    }
                    
                    db.scheduled_posts.insert_one(scheduled_post)
                    
                except Exception as e:
                    current_app.logger.error(f'Error generating automated content: {str(e)}')
                    continue
        
    except Exception as e:
        current_app.logger.error(f'Schedule automated posts error: {str(e)}')

@automation_bp.route('/test-post', methods=['POST'])
@jwt_required()
def create_test_post():
    """Create a test post to verify automation setup"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        domain = data.get('domain')
        platform = data.get('platform')
        
        if not domain or not platform:
            return generate_response(False, 'Domain and platform are required', status_code=400)
        
        db = get_database()
        
        # Check if platform is connected
        platform_connection = db.platform_connections.find_one({
            'user_id': ObjectId(user_id),
            'platform': platform.lower(),
            'is_active': True
        })
        
        if not platform_connection:
            return generate_response(False, f'{platform.title()} is not connected', status_code=400)
        
        # Generate test content
        generated_content = content_generator.generate_content(
            domain=domain,
            platform=platform
        )
        
        # Save as test content (not scheduled)
        content_doc = {
            'user_id': ObjectId(user_id),
            'domain': domain,
            'platform': platform,
            'content': generated_content['content'],
            'hashtags': generated_content['hashtags'],
            'character_count': generated_content['character_count'],
            'performance_prediction': generated_content['performance_prediction'],
            'ai_provider': generated_content['ai_provider'],
            'status': 'test',
            'source': 'test',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = db.generated_content.insert_one(content_doc)
        generated_content['id'] = str(result.inserted_id)
        
        return generate_response(
            True,
            'Test content generated successfully',
            data={'content': generated_content}
        )
        
    except Exception as e:
        current_app.logger.error(f'Test post error: {str(e)}')
        return generate_response(False, 'Failed to create test post', status_code=500)

@automation_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_automation_analytics():
    """Get automation performance analytics"""
    try:
        user_id = get_jwt_identity()
        
        # Get date range
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = start_date.replace(day=start_date.day - days)
        
        db = get_database()
        
        # Get automation posts vs manual posts
        automated_posts = db.posts.find({
            'user_id': ObjectId(user_id),
            'source': 'automation',
            'posted_at': {'$gte': start_date}
        }).count()
        
        manual_posts = db.posts.find({
            'user_id': ObjectId(user_id),
            'source': {'$ne': 'automation'},
            'posted_at': {'$gte': start_date}
        }).count()
        
        # Get successful vs failed posts
        successful_posts = db.posts.find({
            'user_id': ObjectId(user_id),
            'source': 'automation',
            'status': 'posted',
            'posted_at': {'$gte': start_date}
        }).count()
        
        failed_posts = db.scheduled_posts.find({
            'user_id': ObjectId(user_id),
            'source': 'automation',
            'status': 'failed',
            'scheduled_time': {'$gte': start_date}
        }).count()
        
        # Get platform breakdown
        platform_pipeline = [
            {
                '$match': {
                    'user_id': ObjectId(user_id),
                    'source': 'automation',
                    'posted_at': {'$gte': start_date}
                }
            },
            {
                '$group': {
                    '_id': '$platform',
                    'count': {'$sum': 1},
                    'avg_engagement': {'$avg': '$engagement.total'}
                }
            }
        ]
        
        platform_stats = list(db.posts.aggregate(platform_pipeline))
        
        # Calculate time saved (assuming 10 minutes per manual post)
        time_saved_minutes = automated_posts * 10
        time_saved_hours = time_saved_minutes // 60
        
        analytics_data = {
            'automated_posts': automated_posts,
            'manual_posts': manual_posts,
            'successful_posts': successful_posts,
            'failed_posts': failed_posts,
            'success_rate': (successful_posts / (successful_posts + failed_posts)) * 100 if (successful_posts + failed_posts) > 0 else 0,
            'time_saved_hours': time_saved_hours,
            'platform_breakdown': {stat['_id']: {'count': stat['count'], 'avg_engagement': stat.get('avg_engagement', 0)} for stat in platform_stats},
            'period_days': days
        }
        
        return generate_response(
            True,
            'Automation analytics retrieved',
            data={'analytics': analytics_data}
        )
        
    except Exception as e:
        current_app.logger.error(f'Automation analytics error: {str(e)}')
        return generate_response(False, 'Failed to get automation analytics', status_code=500)