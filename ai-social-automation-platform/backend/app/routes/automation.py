# app/routes/automation.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
automation_bp = Blueprint('automation', __name__)

@automation_bp.route('/start', methods=['POST'])
@jwt_required()
def start_automation():
    """Start automation for user"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user has credentials and domains set up
        credentials_count = current_app.db.credentials.count_documents({
            'user_id': ObjectId(user_id),
            'status': 'active'
        })
        
        domains_config = current_app.db.user_domains.find_one({
            'user_id': ObjectId(user_id),
            'active': True
        })
        
        if credentials_count == 0:
            return jsonify({'error': 'No social media credentials found. Please add credentials first.'}), 400
        
        if not domains_config or not domains_config.get('selected_domains'):
            return jsonify({'error': 'No content domains selected. Please select domains first.'}), 400
        
        # Update user automation status
        current_app.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'automation_active': True,
                    'automation_started_at': datetime.utcnow()
                }
            }
        )
        
        # Trigger content generation and posting (if celery is available)
        try:
            from app.workers.content_generation_worker import generate_user_content
            from app.workers.auto_posting_worker import schedule_user_posts
            
            # Schedule background tasks
            generate_user_content.delay(user_id)
            schedule_user_posts.delay(user_id)
        except ImportError:
            logger.warning("Celery workers not available, automation will run on schedule")
        
        logger.info(f"Automation started for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Automation started successfully',
            'automation_active': True
        }), 200
        
    except Exception as e:
        logger.error(f"Schedule posts error: {str(e)}")
        return jsonify({'error': 'Failed to schedule posts'}), 500

@automation_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_automation_logs():
    """Get automation logs for user"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        page = int(request.args.get('page', 1))
        log_type = request.args.get('type', 'all')  # 'content_generation', 'posting', 'error', 'all'
        
        # Build query
        query = {'user_id': ObjectId(user_id)}
        if log_type != 'all':
            query['log_type'] = log_type
        
        # Get logs with pagination
        skip = (page - 1) * limit
        logs = list(current_app.db.automation_logs.find(query)
                   .sort('created_at', -1)
                   .skip(skip)
                   .limit(limit))
        
        # Convert ObjectId to string
        for log in logs:
            log['_id'] = str(log['_id'])
            log['user_id'] = str(log['user_id'])
            if 'created_at' in log:
                log['created_at'] = log['created_at'].isoformat()
        
        # Get total count
        total_count = current_app.db.automation_logs.count_documents(query)
        
        return jsonify({
            'success': True,
            'logs': logs,
            'pagination': {
                'current_page': page,
                'total_pages': (total_count + limit - 1) // limit,
                'total_count': total_count,
                'limit': limit
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get automation logs error: {str(e)}")
        return jsonify({'error': 'Failed to fetch automation logs'}), 500

@automation_bp.route('/post-now', methods=['POST'])
@jwt_required()
def post_now():
    """Post content immediately to platform"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        platform = data.get('platform')
        content = data.get('content')
        content_type = data.get('content_type', 'text')
        media_url = data.get('media_url')
        
        if not platform or not content:
            return jsonify({'error': 'Platform and content are required'}), 400
        
        # Get user credentials for the platform
        from app.services.credentials.credential_manager import CredentialManager
        
        credential_manager = CredentialManager(
            current_app.db, 
            current_app.config['ENCRYPTION_KEY']
        )
        
        creds_result = credential_manager.get_credentials(user_id, platform)
        
        if not creds_result['success']:
            return jsonify({'error': f'No {platform} credentials found'}), 400
        
        # Post to platform
        from app.services.posting.auto_poster import AutoPoster
        
        auto_poster = AutoPoster(current_app.config)
        result = auto_poster.post_to_platform(
            platform=platform,
            username=creds_result['username'],
            password=creds_result['password'],
            content=content,
            content_type=content_type,
            media_url=media_url
        )
        
        # Log the posting attempt
        log_entry = {
            'user_id': ObjectId(user_id),
            'log_type': 'posting',
            'platform': platform,
            'content_type': content_type,
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'error': result.get('error'),
            'created_at': datetime.utcnow()
        }
        current_app.db.automation_logs.insert_one(log_entry)
        
        if result.get('success'):
            # Save successful post
            post_doc = {
                'user_id': ObjectId(user_id),
                'platform': platform,
                'content': content,
                'content_type': content_type,
                'status': 'posted',
                'platform_post_id': result.get('post_id'),
                'platform_url': result.get('post_url'),
                'posted_at': datetime.utcnow(),
                'created_at': datetime.utcnow()
            }
            current_app.db.posts.insert_one(post_doc)
        
        return jsonify(result), 200 if result.get('success') else 500
        
    except Exception as e:
        logger.error(f"Post now error: {str(e)}")
        return jsonify({'error': 'Failed to post content'}), 500Start automation error: {str(e)}")
        return jsonify({'error': 'Failed to start automation'}), 500

@automation_bp.route('/stop', methods=['POST'])
@jwt_required()
def stop_automation():
    """Stop automation for user"""
    try:
        user_id = get_jwt_identity()
        
        # Update user automation status
        current_app.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'automation_active': False,
                    'automation_stopped_at': datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Automation stopped for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Automation stopped successfully',
            'automation_active': False
        }), 200
        
    except Exception as e:
        logger.error(f"Stop automation error: {str(e)}")
        return jsonify({'error': 'Failed to stop automation'}), 500

@automation_bp.route('/status', methods=['GET'])
@jwt_required()
def get_automation_status():
    """Get automation status for user"""
    try:
        user_id = get_jwt_identity()
        
        user = current_app.db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get recent posts count
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_posts = current_app.db.posts.count_documents({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': today_start}
        })
        
        # Get pending posts count
        pending_posts = current_app.db.scheduled_posts.count_documents({
            'user_id': ObjectId(user_id),
            'status': 'pending'
        })
        
        # Get user's subscription limits
        subscription_plan = user.get('subscription_plan', 'starter')
        plan_limits = current_app.config['SUBSCRIPTION_PLANS'].get(subscription_plan, {})
        
        return jsonify({
            'success': True,
            'automation_active': user.get('automation_active', False),
            'automation_started_at': user.get('automation_started_at'),
            'automation_stopped_at': user.get('automation_stopped_at'),
            'today_posts_count': today_posts,
            'pending_posts_count': pending_posts,
            'daily_post_count': user.get('daily_post_count', 0),
            'subscription_plan': subscription_plan,
            'plan_limits': plan_limits
        }), 200
        
    except Exception as e:
        logger.error(f"Get automation status error: {str(e)}")
        return jsonify({'error': 'Failed to fetch automation status'}), 500

@automation_bp.route('/generate-content', methods=['POST'])
@jwt_required()
def generate_content_now():
    """Generate content immediately for user"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        domain = data.get('domain')
        platform = data.get('platform')
        count = data.get('count', 1)
        
        if not domain or not platform:
            return jsonify({'error': 'Domain and platform are required'}), 400
        
        if count > 5:
            return jsonify({'error': 'Maximum 5 content pieces can be generated at once'}), 400
        
        # Import here to avoid circular imports
        from app.ai.content_generators.base_generator import ContentGenerator
        
        # Initialize content generator
        content_generator = ContentGenerator(
            current_app.config['MISTRAL_API_KEY'],
            current_app.config['GROQ_API_KEY']
        )
        
        generated_content = []
        
        for i in range(count):
            result = content_generator.generate_content(domain, platform)
            
            if result.get('success'):
                # Save generated content
                content_doc = {
                    'user_id': ObjectId(user_id),
                    'domain': domain,
                    'platform': platform,
                    'content': result['content'],
                    'content_type': result.get('content_type', 'post'),
                    'provider': result.get('provider'),
                    'tokens_used': result.get('tokens_used', 0),
                    'status': 'generated',
                    'created_at': datetime.utcnow()
                }
                
                content_id = current_app.db.generated_content.insert_one(content_doc).inserted_id
                
                generated_content.append({
                    'id': str(content_id),
                    'content': result['content'],
                    'domain': domain,
                    'platform': platform,
                    'provider': result.get('provider')
                })
        
        return jsonify({
            'success': True,
            'message': f'Generated {len(generated_content)} content pieces',
            'generated_content': generated_content
        }), 200
        
    except Exception as e:
        logger.error(f"Generate content error: {str(e)}")
        return jsonify({'error': 'Failed to generate content'}), 500

@automation_bp.route('/schedule', methods=['POST'])
@jwt_required()
def schedule_posts():
    """Schedule posts for user"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        posts = data.get('posts', [])
        schedule_times = data.get('schedule_times', [])
        
        if not posts:
            return jsonify({'error': 'No posts provided for scheduling'}), 400
        
        scheduled_posts = []
        
        for i, post in enumerate(posts):
            # Default to next available time if not specified
            if i < len(schedule_times):
                scheduled_time = datetime.fromisoformat(schedule_times[i])
            else:
                # Schedule for next hour
                scheduled_time = datetime.utcnow() + timedelta(hours=i+1)
            
            scheduled_post = {
                'user_id': ObjectId(user_id),
                'content_id': ObjectId(post.get('content_id')) if post.get('content_id') else None,
                'platform': post.get('platform'),
                'content': post.get('content'),
                'content_type': post.get('content_type', 'post'),
                'scheduled_time': scheduled_time,
                'status': 'pending',
                'created_at': datetime.utcnow()
            }
            
            result = current_app.db.scheduled_posts.insert_one(scheduled_post)
            scheduled_posts.append({
                'id': str(result.inserted_id),
                'scheduled_time': scheduled_time.isoformat(),
                'platform': post.get('platform'),
                'status': 'pending'
            })
        
        return jsonify({
            'success': True,
            'message': f'Scheduled {len(scheduled_posts)} posts',
            'scheduled_posts': scheduled_posts
        }), 201
        
    except Exception as e:
        logger.error(f" Schedule posts error: {str(e)}")
        return jsonify({'error': 'Failed to schedule posts'}), 500
    