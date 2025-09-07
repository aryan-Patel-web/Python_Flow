"""
Content Generation Routes for VelocityPost.ai
Handles AI content generation and management
"""






from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId

from app.utils.database import get_database
from app.utils.helpers import generate_response
from app.services.ai_content_generator import content_generator

content_bp = Blueprint('content', __name__)

@content_bp.route('/domains', methods=['GET'])
def get_available_domains():
    """Get available content domains"""
    try:
        domains = content_generator.content_domains
        
        domains_list = []
        for domain_key, domain_config in domains.items():
            domains_list.append({
                'id': domain_key,
                'name': domain_config['name'],
                'description': f"Generate {domain_config['name'].lower()} content",
                'keywords': domain_config['keywords'][:5],  # First 5 keywords
                'sample_hashtags': domain_config['hashtags'][:3],  # First 3 hashtags
                'tone': domain_config['tone']
            })
        
        return generate_response(
            True,
            'Content domains retrieved successfully',
            data={'domains': domains_list}
        )
        
    except Exception as e:
        current_app.logger.error(f'Get domains error: {str(e)}')
        return generate_response(False, 'Failed to get content domains', status_code=500)

@content_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_content():
    """Generate AI content for specific domain and platform"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        domain = data.get('domain')
        platform = data.get('platform')
        
        if not domain or not platform:
            return generate_response(False, 'Domain and platform are required', status_code=400)
        
        # Check user's plan limits
        db = get_database()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return generate_response(False, 'User not found', status_code=404)
        
        # Check if user has reached daily content generation limit
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_content_count = db.generated_content.find({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': today}
        }).count()
        
        plan_limits = user.get('plan_limits', {})
        max_content_per_day = plan_limits.get('max_posts_per_day', 2) * 5  # 5x posts for generation
        
        if today_content_count >= max_content_per_day:
            return generate_response(
                False,
                f'Daily content generation limit reached ({max_content_per_day}). Upgrade your plan for more content.',
                status_code=403
            )
        
        # Check if platform is connected
        platform_connection = db.platform_connections.find_one({
            'user_id': ObjectId(user_id),
            'platform': platform.lower(),
            'is_active': True
        })
        
        if not platform_connection:
            return generate_response(False, f'{platform.title()} is not connected. Please connect it first.', status_code=400)
        
        # Generate content using AI
        custom_prompt = data.get('custom_prompt')
        tone = data.get('tone')
        target_audience = data.get('target_audience')
        
        generated_content = content_generator.generate_content(
            domain=domain,
            platform=platform,
            custom_prompt=custom_prompt,
            tone=tone,
            target_audience=target_audience
        )
        
        # Save generated content to database
        content_doc = {
            'user_id': ObjectId(user_id),
            'domain': domain,
            'platform': platform,
            'content': generated_content['content'],
            'hashtags': generated_content['hashtags'],
            'character_count': generated_content['character_count'],
            'performance_prediction': generated_content['performance_prediction'],
            'ai_provider': generated_content['ai_provider'],
            'custom_prompt': custom_prompt,
            'tone': tone,
            'target_audience': target_audience,
            'status': 'generated',  # generated, scheduled, posted
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = db.generated_content.insert_one(content_doc)
        content_id = str(result.inserted_id)
        
        # Add ID to response
        generated_content['id'] = content_id
        
        return generate_response(
            True,
            'Content generated successfully',
            data={'content': generated_content}
        )
        
    except ValueError as e:
        return generate_response(False, str(e), status_code=400)
    except Exception as e:
        current_app.logger.error(f'Content generation error: {str(e)}')
        return generate_response(False, 'Failed to generate content', status_code=500)

@content_bp.route('/generate-bulk', methods=['POST'])
@jwt_required()
def generate_bulk_content():
    """Generate multiple content pieces"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        domain = data.get('domain')
        platforms = data.get('platforms', [])
        count = min(data.get('count', 3), 10)  # Max 10 pieces at once
        
        if not domain or not platforms:
            return generate_response(False, 'Domain and platforms are required', status_code=400)
        
        # Check user's plan limits
        db = get_database()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return generate_response(False, 'User not found', status_code=404)
        
        # Check daily limits
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_content_count = db.generated_content.find({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': today}
        }).count()
        
        total_to_generate = len(platforms) * count
        plan_limits = user.get('plan_limits', {})
        max_content_per_day = plan_limits.get('max_posts_per_day', 2) * 5
        
        if today_content_count + total_to_generate > max_content_per_day:
            return generate_response(
                False,
                f'Not enough daily quota. You can generate {max_content_per_day - today_content_count} more pieces today.',
                status_code=403
            )
        
        # Generate content for each platform
        generated_contents = []
        
        for platform in platforms:
            # Check if platform is connected
            platform_connection = db.platform_connections.find_one({
                'user_id': ObjectId(user_id),
                'platform': platform.lower(),
                'is_active': True
            })
            
            if not platform_connection:
                continue  # Skip disconnected platforms
            
            for i in range(count):
                try:
                    generated_content = content_generator.generate_content(
                        domain=domain,
                        platform=platform
                    )
                    
                    # Save to database
                    content_doc = {
                        'user_id': ObjectId(user_id),
                        'domain': domain,
                        'platform': platform,
                        'content': generated_content['content'],
                        'hashtags': generated_content['hashtags'],
                        'character_count': generated_content['character_count'],
                        'performance_prediction': generated_content['performance_prediction'],
                        'ai_provider': generated_content['ai_provider'],
                        'status': 'generated',
                        'created_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                    
                    result = db.generated_content.insert_one(content_doc)
                    generated_content['id'] = str(result.inserted_id)
                    
                    generated_contents.append(generated_content)
                    
                except Exception as e:
                    current_app.logger.error(f'Bulk generation error for {platform}: {str(e)}')
                    continue
        
        return generate_response(
            True,
            f'Generated {len(generated_contents)} content pieces',
            data={'contents': generated_contents}
        )
        
    except Exception as e:
        current_app.logger.error(f'Bulk content generation error: {str(e)}')
        return generate_response(False, 'Failed to generate bulk content', status_code=500)

@content_bp.route('/library', methods=['GET'])
@jwt_required()
def get_content_library():
    """Get user's generated content library"""
    try:
        user_id = get_jwt_identity()
        
        # Query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)
        domain = request.args.get('domain')
        platform = request.args.get('platform')
        status = request.args.get('status')
        
        # Build query
        query = {'user_id': ObjectId(user_id)}
        
        if domain:
            query['domain'] = domain
        if platform:
            query['platform'] = platform
        if status:
            query['status'] = status
        
        db = get_database()
        
        # Get total count
        total_count = db.generated_content.find(query).count()
        
        # Get paginated content
        skip = (page - 1) * limit
        contents = list(db.generated_content.find(query)
                       .sort('created_at', -1)
                       .skip(skip)
                       .limit(limit))
        
        # Format response
        content_list = []
        for content in contents:
            content_list.append({
                'id': str(content['_id']),
                'domain': content['domain'],
                'platform': content['platform'],
                'content': content['content'],
                'hashtags': content['hashtags'],
                'character_count': content['character_count'],
                'performance_prediction': content['performance_prediction'],
                'status': content['status'],
                'created_at': content['created_at'].isoformat(),
                'ai_provider': content.get('ai_provider', 'mistral')
            })
        
        return generate_response(
            True,
            'Content library retrieved',
            data={
                'contents': content_list,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total_count,
                    'pages': (total_count + limit - 1) // limit
                }
            }
        )
        
    except Exception as e:
        current_app.logger.error(f'Get content library error: {str(e)}')
        return generate_response(False, 'Failed to get content library', status_code=500)

@content_bp.route('/<content_id>', methods=['GET'])
@jwt_required()
def get_content_by_id(content_id):
    """Get specific content by ID"""
    try:
        user_id = get_jwt_identity()
        
        if not ObjectId.is_valid(content_id):
            return generate_response(False, 'Invalid content ID', status_code=400)
        
        db = get_database()
        content = db.generated_content.find_one({
            '_id': ObjectId(content_id),
            'user_id': ObjectId(user_id)
        })
        
        if not content:
            return generate_response(False, 'Content not found', status_code=404)
        
        content_response = {
            'id': str(content['_id']),
            'domain': content['domain'],
            'platform': content['platform'],
            'content': content['content'],
            'hashtags': content['hashtags'],
            'character_count': content['character_count'],
            'performance_prediction': content['performance_prediction'],
            'status': content['status'],
            'custom_prompt': content.get('custom_prompt'),
            'tone': content.get('tone'),
            'target_audience': content.get('target_audience'),
            'created_at': content['created_at'].isoformat(),
            'updated_at': content['updated_at'].isoformat(),
            'ai_provider': content.get('ai_provider', 'mistral')
        }
        
        return generate_response(True, 'Content retrieved', data={'content': content_response})
        
    except Exception as e:
        current_app.logger.error(f'Get content by ID error: {str(e)}')
        return generate_response(False, 'Failed to get content', status_code=500)

@content_bp.route('/<content_id>', methods=['PUT'])
@jwt_required()
def update_content(content_id):
    """Update generated content"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not ObjectId.is_valid(content_id):
            return generate_response(False, 'Invalid content ID', status_code=400)
        
        # Fields that can be updated
        allowed_fields = ['content', 'hashtags', 'status']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return generate_response(False, 'No valid fields to update', status_code=400)
        
        # Add update timestamp and recalculate character count
        update_data['updated_at'] = datetime.utcnow()
        if 'content' in update_data:
            update_data['character_count'] = len(update_data['content'])
        
        db = get_database()
        result = db.generated_content.update_one(
            {
                '_id': ObjectId(content_id),
                'user_id': ObjectId(user_id)
            },
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return generate_response(False, 'Content not found', status_code=404)
        
        # Get updated content
        updated_content = db.generated_content.find_one({'_id': ObjectId(content_id)})
        
        content_response = {
            'id': str(updated_content['_id']),
            'content': updated_content['content'],
            'hashtags': updated_content['hashtags'],
            'character_count': updated_content['character_count'],
            'status': updated_content['status'],
            'updated_at': updated_content['updated_at'].isoformat()
        }
        
        return generate_response(True, 'Content updated successfully', data={'content': content_response})
        
    except Exception as e:
        current_app.logger.error(f'Update content error: {str(e)}')
        return generate_response(False, 'Failed to update content', status_code=500)

@content_bp.route('/<content_id>', methods=['DELETE'])
@jwt_required()
def delete_content(content_id):
    """Delete generated content"""
    try:
        user_id = get_jwt_identity()
        
        if not ObjectId.is_valid(content_id):
            return generate_response(False, 'Invalid content ID', status_code=400)
        
        db = get_database()
        result = db.generated_content.delete_one({
            '_id': ObjectId(content_id),
            'user_id': ObjectId(user_id)
        })
        
        if result.deleted_count == 0:
            return generate_response(False, 'Content not found', status_code=404)
        
        return generate_response(True, 'Content deleted successfully')
        
    except Exception as e:
        current_app.logger.error(f'Delete content error: {str(e)}')
        return generate_response(False, 'Failed to delete content', status_code=500)

@content_bp.route('/regenerate/<content_id>', methods=['POST'])
@jwt_required()
def regenerate_content(content_id):
    """Regenerate content with same parameters"""
    try:
        user_id = get_jwt_identity()
        
        if not ObjectId.is_valid(content_id):
            return generate_response(False, 'Invalid content ID', status_code=400)
        
        db = get_database()
        original_content = db.generated_content.find_one({
            '_id': ObjectId(content_id),
            'user_id': ObjectId(user_id)
        })
        
        if not original_content:
            return generate_response(False, 'Content not found', status_code=404)
        
        # Check daily limits
        user = db.users.find_one({'_id': ObjectId(user_id)})
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_content_count = db.generated_content.find({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': today}
        }).count()
        
        plan_limits = user.get('plan_limits', {})
        max_content_per_day = plan_limits.get('max_posts_per_day', 2) * 5
        
        if today_content_count >= max_content_per_day:
            return generate_response(
                False,
                'Daily content generation limit reached. Upgrade your plan for more content.',
                status_code=403
            )
        
        # Regenerate content
        generated_content = content_generator.generate_content(
            domain=original_content['domain'],
            platform=original_content['platform'],
            custom_prompt=original_content.get('custom_prompt'),
            tone=original_content.get('tone'),
            target_audience=original_content.get('target_audience')
        )
        
        # Update existing content
        update_data = {
            'content': generated_content['content'],
            'hashtags': generated_content['hashtags'],
            'character_count': generated_content['character_count'],
            'performance_prediction': generated_content['performance_prediction'],
            'ai_provider': generated_content['ai_provider'],
            'updated_at': datetime.utcnow(),
            'regenerated_at': datetime.utcnow()
        }
        
        db.generated_content.update_one(
            {'_id': ObjectId(content_id)},
            {'$set': update_data}
        )
        
        # Add ID to response
        generated_content['id'] = content_id
        
        return generate_response(
            True,
            'Content regenerated successfully',
            data={'content': generated_content}
        )
        
    except Exception as e:
        current_app.logger.error(f'Regenerate content error: {str(e)}')
        return generate_response(False, 'Failed to regenerate content', status_code=500)

@content_bp.route('/schedule', methods=['POST'])
@jwt_required()
def schedule_content():
    """Schedule content for posting"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        content_id = data.get('content_id')
        scheduled_time = data.get('scheduled_time')  # ISO format
        
        if not content_id or not scheduled_time:
            return generate_response(False, 'Content ID and scheduled time are required', status_code=400)
        
        if not ObjectId.is_valid(content_id):
            return generate_response(False, 'Invalid content ID', status_code=400)
        
        # Parse scheduled time
        try:
            scheduled_datetime = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        except ValueError:
            return generate_response(False, 'Invalid scheduled time format', status_code=400)
        
        # Check if time is in the future
        if scheduled_datetime <= datetime.utcnow():
            return generate_response(False, 'Scheduled time must be in the future', status_code=400)
        
        db = get_database()
        
        # Update content status and schedule
        result = db.generated_content.update_one(
            {
                '_id': ObjectId(content_id),
                'user_id': ObjectId(user_id)
            },
            {
                '$set': {
                    'status': 'scheduled',
                    'scheduled_time': scheduled_datetime,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            return generate_response(False, 'Content not found', status_code=404)
        
        # Create scheduled post entry
        scheduled_post = {
            'user_id': ObjectId(user_id),
            'content_id': ObjectId(content_id),
            'scheduled_time': scheduled_datetime,
            'status': 'pending',  # pending, posted, failed
            'created_at': datetime.utcnow()
        }
        
        db.scheduled_posts.insert_one(scheduled_post)
        
        return generate_response(
            True,
            'Content scheduled successfully',
            data={'scheduled_time': scheduled_datetime.isoformat()}
        )
        
    except Exception as e:
        current_app.logger.error(f'Schedule content error: {str(e)}')
        return generate_response(False, 'Failed to schedule content', status_code=500)

@content_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_content_analytics():
    """Get content generation analytics"""
    try:
        user_id = get_jwt_identity()
        
        db = get_database()
        
        # Get date range (last 30 days by default)
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = start_date.replace(day=start_date.day - days)
        
        # Aggregate content statistics
        pipeline = [
            {
                '$match': {
                    'user_id': ObjectId(user_id),
                    'created_at': {'$gte': start_date}
                }
            },
            {
                '$group': {
                    '_id': {
                        'domain': '$domain',
                        'platform': '$platform'
                    },
                    'count': {'$sum': 1},
                    'avg_performance': {
                        '$avg': '$performance_prediction.overall_score'
                    }
                }
            }
        ]
        
        content_stats = list(db.generated_content.aggregate(pipeline))
        
        # Format statistics
        domain_stats = {}
        platform_stats = {}
        
        for stat in content_stats:
            domain = stat['_id']['domain']
            platform = stat['_id']['platform']
            
            if domain not in domain_stats:
                domain_stats[domain] = {'count': 0, 'avg_performance': 0}
            if platform not in platform_stats:
                platform_stats[platform] = {'count': 0, 'avg_performance': 0}
            
            domain_stats[domain]['count'] += stat['count']
            domain_stats[domain]['avg_performance'] = stat['avg_performance']
            
            platform_stats[platform]['count'] += stat['count']
            platform_stats[platform]['avg_performance'] = stat['avg_performance']
        
        # Get total counts
        total_generated = db.generated_content.find({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': start_date}
        }).count()
        
        total_scheduled = db.generated_content.find({
            'user_id': ObjectId(user_id),
            'status': 'scheduled',
            'created_at': {'$gte': start_date}
        }).count()
        
        total_posted = db.generated_content.find({
            'user_id': ObjectId(user_id),
            'status': 'posted',
            'created_at': {'$gte': start_date}
        }).count()
        
        analytics_data = {
            'total_generated': total_generated,
            'total_scheduled': total_scheduled,
            'total_posted': total_posted,
            'domain_breakdown': domain_stats,
            'platform_breakdown': platform_stats,
            'period_days': days
        }
        
        return generate_response(
            True,
            'Content analytics retrieved',
            data={'analytics': analytics_data}
        )
        
    except Exception as e:
        current_app.logger.error(f'Content analytics error: {str(e)}')
        return generate_response(False, 'Failed to get content analytics', status_code=500)