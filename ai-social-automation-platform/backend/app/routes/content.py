# app/routes/content.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
content_bp = Blueprint('content', __name__)

@content_bp.route('/library', methods=['GET'])
@jwt_required()
def get_content_library():
    """Get user's content library"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        limit = int(request.args.get('limit', 20))
        page = int(request.args.get('page', 1))
        domain = request.args.get('domain')
        platform = request.args.get('platform')
        status = request.args.get('status', 'all')  # 'generated', 'posted', 'scheduled', 'all'
        
        # Build query
        query = {'user_id': ObjectId(user_id)}
        
        if domain:
            query['domain'] = domain
        if platform:
            query['platform'] = platform
        if status != 'all':
            query['status'] = status
        
        # Get content with pagination
        skip = (page - 1) * limit
        content_items = list(current_app.db.generated_content.find(query)
                           .sort('created_at', -1)
                           .skip(skip)
                           .limit(limit))
        
        # Convert ObjectId to string and format dates
        for item in content_items:
            item['_id'] = str(item['_id'])
            item['user_id'] = str(item['user_id'])
            if 'created_at' in item:
                item['created_at'] = item['created_at'].isoformat()
        
        # Get total count
        total_count = current_app.db.generated_content.count_documents(query)
        
        return jsonify({
            'success': True,
            'content_items': content_items,
            'pagination': {
                'current_page': page,
                'total_pages': (total_count + limit - 1) // limit,
                'total_count': total_count,
                'limit': limit
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get content library error: {str(e)}")
        return jsonify({'error': 'Failed to fetch content library'}), 500

@content_bp.route('/<content_id>', methods=['GET'])
@jwt_required()
def get_content_item(content_id):
    """Get specific content item"""
    try:
        user_id = get_jwt_identity()
        
        content_item = current_app.db.generated_content.find_one({
            '_id': ObjectId(content_id),
            'user_id': ObjectId(user_id)
        })
        
        if not content_item:
            return jsonify({'error': 'Content not found'}), 404
        
        # Convert ObjectId to string
        content_item['_id'] = str(content_item['_id'])
        content_item['user_id'] = str(content_item['user_id'])
        if 'created_at' in content_item:
            content_item['created_at'] = content_item['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'content_item': content_item
        }), 200
        
    except Exception as e:
        logger.error(f"Get content item error: {str(e)}")
        return jsonify({'error': 'Failed to fetch content item'}), 500

@content_bp.route('/<content_id>', methods=['PUT'])
@jwt_required()
def update_content_item(content_id):
    """Update content item"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Check if content belongs to user
        content_item = current_app.db.generated_content.find_one({
            '_id': ObjectId(content_id),
            'user_id': ObjectId(user_id)
        })
        
        if not content_item:
            return jsonify({'error': 'Content not found'}), 404
        
        # Update allowed fields
        update_fields = {}
        
        if 'content' in data:
            update_fields['content'] = data['content']
        if 'status' in data:
            update_fields['status'] = data['status']
        if 'tags' in data:
            update_fields['tags'] = data['tags']
        
        if update_fields:
            update_fields['updated_at'] = datetime.utcnow()
            
            current_app.db.generated_content.update_one(
                {'_id': ObjectId(content_id)},
                {'$set': update_fields}
            )
        
        return jsonify({
            'success': True,
            'message': 'Content updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Update content item error: {str(e)}")
        return jsonify({'error': 'Failed to update content item'}), 500

@content_bp.route('/<content_id>', methods=['DELETE'])
@jwt_required()
def delete_content_item(content_id):
    """Delete content item"""
    try:
        user_id = get_jwt_identity()
        
        # Check if content belongs to user
        result = current_app.db.generated_content.delete_one({
            '_id': ObjectId(content_id),
            'user_id': ObjectId(user_id)
        })
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Content not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Content deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Delete content item error: {str(e)}")
        return jsonify({'error': 'Failed to delete content item'}), 500

@content_bp.route('/bulk-generate', methods=['POST'])
@jwt_required()
def bulk_generate_content():
    """Generate multiple content pieces"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        domains = data.get('domains', [])
        platforms = data.get('platforms', [])
        count_per_combination = data.get('count_per_combination', 1)
        
        if not domains or not platforms:
            return jsonify({'error': 'Domains and platforms are required'}), 400
        
        if count_per_combination > 3:
            return jsonify({'error': 'Maximum 3 content pieces per domain-platform combination'}), 400
        
        # Import here to avoid circular imports
        from app.ai.content_generators.base_generator import ContentGenerator
        
        content_generator = ContentGenerator(
            current_app.config['MISTRAL_API_KEY'],
            current_app.config['GROQ_API_KEY']
        )
        
        generated_content = []
        total_generated = 0
        
        for domain in domains:
            for platform in platforms:
                for i in range(count_per_combination):
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
                        
                        total_generated += 1
        
        return jsonify({
            'success': True,
            'message': f'Generated {total_generated} content pieces',
            'generated_content': generated_content
        }), 200
        
    except Exception as e:
        logger.error(f"Bulk generate content error: {str(e)}")
        return jsonify({'error': 'Failed to bulk generate content'}), 500

@content_bp.route('/templates', methods=['GET'])
def get_content_templates():
    """Get content templates for different domains"""
    try:
        templates = {
            'memes': [
                "When {situation} happens: {reaction}",
                "Me: {action}\nAlso me: {contradiction}",
                "POV: {scenario}\n{outcome}"
            ],
            'tech_news': [
                "🚀 Breaking: {headline}\n\n{summary}\n\n#TechNews #Innovation",
                "💡 Did you know? {fact}\n\n{explanation}\n\n#TechTips #Learning",
                "🔥 Hot take: {opinion}\n\n{reasoning}\n\n#TechTalk #Discussion"
            ],
            'coding_tips': [
                "💻 Pro tip: {tip}\n\n```{code_example}```\n\n#CodingTips #Programming",
                "🐛 Common mistake: {mistake}\n\n✅ Better approach: {solution}\n\n#CodingBestPractices",
                "🔧 Tool spotlight: {tool_name}\n\n{description}\n\n#DevTools #Productivity"
            ],
            'business': [
                "💼 Business insight: {insight}\n\n{explanation}\n\n#BusinessTips #Entrepreneurship",
                "📈 Growth hack: {strategy}\n\n{implementation}\n\n#GrowthHacking #Business",
                "🎯 Success principle: {principle}\n\n{application}\n\n#Success #Leadership"
            ],
            'motivational': [
                "✨ {quote}\n\n{inspiration}\n\n#Motivation #Success",
                "🌟 Remember: {reminder}\n\n{encouragement}\n\n#Mindset #Growth",
                "💪 Challenge yourself: {challenge}\n\n{benefit}\n\n#SelfImprovement #Goals"
            ]
        }
        
        return jsonify({
            'success': True,
            'templates': templates
        }), 200
        
    except Exception as e:
        logger.error(f"Get content templates error: {str(e)}")
        return jsonify({'error': 'Failed to fetch content templates'}), 500

@content_bp.route('/trending', methods=['GET'])
@jwt_required()
def get_trending_topics():
    """Get trending topics for content generation"""
    try:
        domain = request.args.get('domain', 'tech_news')
        
        # Mock trending topics (in production, fetch from APIs)
        trending_topics = {
            'tech_news': [
                'AI and Machine Learning',
                'Blockchain Technology',
                'Cybersecurity',
                'Cloud Computing',
                'Mobile App Development'
            ],
            'memes': [
                'Work from home life',
                'Social media trends',
                'Gaming culture',
                'Pop culture references',
                'Everyday struggles'
            ],
            'business': [
                'Remote work strategies',
                'Digital transformation',
                'Startup funding',
                'Customer retention',
                'Market analysis'
            ],
            'lifestyle': [
                'Wellness routines',
                'Productivity hacks',
                'Sustainable living',
                'Travel tips',
                'Health and fitness'
            ]
        }
        
        topics = trending_topics.get(domain, [])
        
        return jsonify({
            'success': True,
            'domain': domain,
            'trending_topics': topics
        }), 200
        
    except Exception as e:
        logger.error(f"Get trending topics error: {str(e)}")
        return jsonify({'error': 'Failed to fetch trending topics'}), 500