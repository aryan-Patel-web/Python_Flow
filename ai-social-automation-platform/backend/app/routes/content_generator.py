#!/usr/bin/env python3
"""
Content Generator Routes for VelocityPost.ai
Handles AI-powered content generation for social media
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from bson import ObjectId

# Import required modules
try:
    from app.utils.database import get_collection, check_user_limits
    from app.utils.auth_helpers import require_auth, create_response
except ImportError:
    try:
        from config.database import get_collection, check_user_limits
        # Fallback auth decorator
        def require_auth(f):
            from functools import wraps
            @wraps(f)
            def decorated(*args, **kwargs):
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({
                        'success': False,
                        'message': 'Authentication required',
                        'error': 'Missing authorization header'
                    }), 401
                
                import jwt
                try:
                    token = auth_header.split(' ')[1]
                    payload = jwt.decode(token, os.getenv('JWT_SECRET_KEY', 'fallback'), algorithms=['HS256'])
                    request.user_id = payload['user_id']
                    request.user_email = payload['email']
                    return f(*args, **kwargs)
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'message': 'Authentication failed',
                        'error': str(e)
                    }), 401
            return decorated
        
        def create_response(success=True, message="", data=None, error=None, status_code=200):
            response_data = {
                'success': success,
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            }
            if data:
                response_data.update(data)
            if error:
                response_data['error'] = error
            return jsonify(response_data), status_code
    except ImportError:
        raise ImportError("Could not import required database modules")

logger = logging.getLogger(__name__)

# Create blueprint
content_generator_bp = Blueprint('content_generator', __name__)

# Available content domains
CONTENT_DOMAINS = {
    'tech': {
        'name': 'Technology',
        'description': 'Tech news, startup updates, AI developments',
        'hashtags': ['#tech', '#startup', '#AI', '#innovation', '#coding'],
        'tone': 'informative'
    },
    'memes': {
        'name': 'Memes & Humor',
        'description': 'Funny content, memes, entertaining posts',
        'hashtags': ['#meme', '#funny', '#humor', '#lol', '#viral'],
        'tone': 'casual'
    },
    'business': {
        'name': 'Business',
        'description': 'Business tips, entrepreneurship, marketing',
        'hashtags': ['#business', '#entrepreneur', '#marketing', '#success', '#growth'],
        'tone': 'professional'
    },
    'lifestyle': {
        'name': 'Lifestyle',
        'description': 'Life tips, motivation, personal development',
        'hashtags': ['#lifestyle', '#motivation', '#selfcare', '#inspiration', '#wellness'],
        'tone': 'inspirational'
    },
    'fitness': {
        'name': 'Fitness & Health',
        'description': 'Workout tips, health advice, fitness motivation',
        'hashtags': ['#fitness', '#health', '#workout', '#gym', '#motivation'],
        'tone': 'motivational'
    },
    'finance': {
        'name': 'Finance & Investment',
        'description': 'Financial tips, investment advice, money management',
        'hashtags': ['#finance', '#investment', '#money', '#crypto', '#stocks'],
        'tone': 'educational'
    },
    'travel': {
        'name': 'Travel',
        'description': 'Travel tips, destinations, cultural experiences',
        'hashtags': ['#travel', '#wanderlust', '#adventure', '#explore', '#culture'],
        'tone': 'adventurous'
    },
    'food': {
        'name': 'Food & Cooking',
        'description': 'Recipes, food tips, culinary experiences',
        'hashtags': ['#food', '#cooking', '#recipe', '#foodie', '#delicious'],
        'tone': 'enthusiastic'
    }
}

# Supported platforms and their requirements
PLATFORM_REQUIREMENTS = {
    'instagram': {
        'max_length': 2200,
        'optimal_length': 125,
        'supports_hashtags': True,
        'optimal_hashtags': 11,
        'media_required': True
    },
    'twitter': {
        'max_length': 280,
        'optimal_length': 100,
        'supports_hashtags': True,
        'optimal_hashtags': 2,
        'media_required': False
    },
    'facebook': {
        'max_length': 63206,
        'optimal_length': 40,
        'supports_hashtags': True,
        'optimal_hashtags': 3,
        'media_required': False
    },
    'linkedin': {
        'max_length': 3000,
        'optimal_length': 150,
        'supports_hashtags': True,
        'optimal_hashtags': 5,
        'media_required': False
    },
    'youtube': {
        'max_length': 1000,
        'optimal_length': 200,
        'supports_hashtags': True,
        'optimal_hashtags': 15,
        'media_required': True
    }
}

@content_generator_bp.route('/domains', methods=['GET'])
def get_content_domains():
    """Get available content domains"""
    try:
        domains = []
        for domain_id, domain_info in CONTENT_DOMAINS.items():
            domains.append({
                'id': domain_id,
                'name': domain_info['name'],
                'description': domain_info['description'],
                'sample_hashtags': domain_info['hashtags'][:3],
                'tone': domain_info['tone']
            })
        
        return create_response(
            success=True,
            message='Content domains retrieved successfully',
            data={'domains': domains, 'total_count': len(domains)}
        )
        
    except Exception as e:
        logger.error(f"Get content domains error: {str(e)}")
        return create_response(
            success=False,
            message='Failed to retrieve content domains',
            error=str(e)
        ), 500

@content_generator_bp.route('/platforms', methods=['GET'])
def get_supported_platforms():
    """Get supported platforms for content generation"""
    try:
        platforms = []
        for platform_id, platform_info in PLATFORM_REQUIREMENTS.items():
            platforms.append({
                'id': platform_id,
                'name': platform_id.title(),
                'max_length': platform_info['max_length'],
                'optimal_length': platform_info['optimal_length'],
                'supports_hashtags': platform_info['supports_hashtags'],
                'optimal_hashtags': platform_info['optimal_hashtags'],
                'media_required': platform_info['media_required']
            })
        
        return create_response(
            success=True,
            message='Supported platforms retrieved successfully',
            data={'platforms': platforms, 'total_count': len(platforms)}
        )
        
    except Exception as e:
        logger.error(f"Get supported platforms error: {str(e)}")
        return create_response(
            success=False,
            message='Failed to retrieve supported platforms',
            error=str(e)
        ), 500

@content_generator_bp.route('/generate', methods=['POST'])
@require_auth
def generate_content():
    """Generate AI content for specified domain and platform"""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        if not data:
            return create_response(
                success=False,
                message='No data provided',
                error='Request body is required'
            ), 400
        
        # Validate required fields
        domain = data.get('domain')
        platform = data.get('platform', 'instagram')
        count = min(int(data.get('count', 1)), 10)  # Limit to 10 at once
        
        if not domain:
            return create_response(
                success=False,
                message='Domain is required',
                error='Please specify content domain'
            ), 400
        
        if domain not in CONTENT_DOMAINS:
            return create_response(
                success=False,
                message='Invalid domain',
                error=f'Domain must be one of: {", ".join(CONTENT_DOMAINS.keys())}'
            ), 400
        
        if platform not in PLATFORM_REQUIREMENTS:
            return create_response(
                success=False,
                message='Invalid platform',
                error=f'Platform must be one of: {", ".join(PLATFORM_REQUIREMENTS.keys())}'
            ), 400
        
        # Check user limits
        can_generate, limit_message = check_user_limits(user_id, 'generate_content', amount=count)
        if not can_generate:
            return create_response(
                success=False,
                message='Generation limit exceeded',
                error=limit_message
            ), 403
        
        # Generate content
        domain_info = CONTENT_DOMAINS[domain]
        platform_info = PLATFORM_REQUIREMENTS[platform]
        
        generated_content = []
        for i in range(count):
            content = generate_ai_content(
                domain=domain,
                domain_info=domain_info,
                platform=platform,
                platform_info=platform_info,
                custom_prompt=data.get('custom_prompt'),
                tone=data.get('tone', domain_info['tone'])
            )
            
            # Save generated content to database
            content_id = save_generated_content(user_id, domain, platform, content)
            
            content_item = {
                'id': content_id,
                'domain': domain,
                'platform': platform,
                'content': content['text'],
                'hashtags': content['hashtags'],
                'performance_prediction': content['performance_score'],
                'word_count': len(content['text'].split()),
                'character_count': len(content['text']),
                'created_at': datetime.utcnow().isoformat()
            }
            
            generated_content.append(content_item)
        
        return create_response(
            success=True,
            message=f'Generated {count} content item(s) successfully',
            data={
                'generated_content': generated_content,
                'domain': domain,
                'platform': platform,
                'total_generated': count
            }
        )
        
    except Exception as e:
        logger.error(f"Content generation error: {str(e)}")
        return create_response(
            success=False,
            message='Content generation failed',
            error=str(e)
        ), 500

@content_generator_bp.route('/generate-variants', methods=['POST'])
@require_auth
def generate_content_variants():
    """Generate variants of existing content"""
    try:
        user_id = request.user_id
        data = request.get_json()
        
        if not data or not data.get('original_content'):
            return create_response(
                success=False,
                message='Original content required',
                error='Please provide original content to create variants'
            ), 400
        
        original_content = data['original_content']
        platform = data.get('platform', 'instagram')
        variant_count = min(int(data.get('count', 3)), 5)
        
        # Check user limits
        can_generate, limit_message = check_user_limits(user_id, 'generate_content', amount=variant_count)
        if not can_generate:
            return create_response(
                success=False,
                message='Generation limit exceeded',
                error=limit_message
            ), 403
        
        # Generate variants
        variants = []
        for i in range(variant_count):
            variant = generate_content_variant(
                original_content=original_content,
                platform=platform,
                variation_type=data.get('variation_type', 'tone')
            )
            
            variants.append({
                'id': f'variant_{i+1}',
                'content': variant['text'],
                'hashtags': variant['hashtags'],
                'variation_type': variant['type'],
                'performance_prediction': variant['performance_score'],
                'character_count': len(variant['text'])
            })
        
        return create_response(
            success=True,
            message=f'Generated {variant_count} variants successfully',
            data={
                'original_content': original_content,
                'variants': variants,
                'platform': platform
            }
        )
        
    except Exception as e:
        logger.error(f"Content variant generation error: {str(e)}")
        return create_response(
            success=False,
            message='Variant generation failed',
            error=str(e)
        ), 500

@content_generator_bp.route('/templates', methods=['GET'])
@require_auth
def get_content_templates():
    """Get content templates for different domains"""
    try:
        domain = request.args.get('domain')
        
        templates = {
            'tech': [
                "🚀 {topic} is revolutionizing {industry}! Here's what you need to know: {details} #tech #innovation",
                "💡 Breaking: {news_item} - This could change everything in {field}! What do you think? #TechNews #AI",
                "🔥 Hot take: {opinion} about {technology}. Do you agree? Let's discuss! #TechTalk #Future"
            ],
            'memes': [
                "When {situation}: {reaction} 😂 #relatable #meme #mood",
                "Me: *{action}* Also me: {consequence} 🤦‍♂️ #life #funny #true",
                "That awkward moment when {scenario} 😅 #awkward #relatable #lol"
            ],
            'business': [
                "💼 Business tip: {tip}. This simple strategy helped me {result}. Try it! #business #entrepreneur #success",
                "📈 Want to {goal}? Here are 3 proven strategies: {strategy1}, {strategy2}, {strategy3} #marketing #growth",
                "🎯 Successful entrepreneurs know: {insight}. How are you applying this? #entrepreneurship #mindset"
            ],
            'lifestyle': [
                "✨ Daily reminder: {motivation_quote}. You've got this! 💪 #motivation #lifestyle #positivity",
                "🌟 Simple habit that changed my life: {habit}. What's yours? #selfcare #wellness #growth",
                "💫 Gratitude practice: Today I'm grateful for {gratitude_items}. What about you? #gratitude #mindfulness"
            ]
        }
        
        if domain and domain in templates:
            domain_templates = templates[domain]
        else:
            domain_templates = []
            for d, temps in templates.items():
                domain_templates.extend(temps)
        
        return create_response(
            success=True,
            message='Content templates retrieved successfully',
            data={
                'templates': domain_templates,
                'domain': domain,
                'total_count': len(domain_templates)
            }
        )
        
    except Exception as e:
        logger.error(f"Get content templates error: {str(e)}")
        return create_response(
            success=False,
            message='Failed to retrieve content templates',
            error=str(e)
        ), 500

@content_generator_bp.route('/history', methods=['GET'])
@require_auth
def get_generation_history():
    """Get user's content generation history"""
    try:
        user_id = request.user_id
        limit = min(int(request.args.get('limit', 50)), 100)
        domain = request.args.get('domain')
        platform = request.args.get('platform')
        days = int(request.args.get('days', 30))
        
        # Build filter query
        filter_query = {'user_id': ObjectId(user_id)}
        
        if domain:
            filter_query['domain'] = domain
        
        if platform:
            filter_query['platform'] = platform
        
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            filter_query['created_at'] = {'$gte': cutoff_date}
        
        # Get generated content from database
        generated_content_collection = get_collection('generated_content')
        if not generated_content_collection:
            return create_response(
                success=True,
                message='Content history retrieved successfully',
                data={'history': [], 'total_count': 0}
            )
        
        content_history = list(
            generated_content_collection.find(filter_query)
            .sort('created_at', -1)
            .limit(limit)
        )
        
        # Format response
        history_items = []
        for item in content_history:
            history_items.append({
                'id': str(item['_id']),
                'domain': item.get('domain'),
                'platform': item.get('platform'),
                'content': item.get('content'),
                'hashtags': item.get('hashtags', []),
                'performance_prediction': item.get('performance_prediction'),
                'is_used': item.get('is_used', False),
                'created_at': item['created_at'].isoformat() if isinstance(item['created_at'], datetime) else item['created_at']
            })
        
        return create_response(
            success=True,
            message='Content history retrieved successfully',
            data={
                'history': history_items,
                'total_count': len(history_items),
                'filters': {
                    'domain': domain,
                    'platform': platform,
                    'days': days
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Get generation history error: {str(e)}")
        return create_response(
            success=False,
            message='Failed to retrieve generation history',
            error=str(e)
        ), 500

@content_generator_bp.route('/usage-stats', methods=['GET'])
@require_auth
def get_usage_statistics():
    """Get content generation usage statistics"""
    try:
        user_id = request.user_id
        
        # Get usage statistics from database
        generated_content_collection = get_collection('generated_content')
        if not generated_content_collection:
            return create_response(
                success=True,
                message='Usage statistics retrieved successfully',
                data={
                    'total_generated': 0,
                    'generated_today': 0,
                    'generated_this_month': 0,
                    'by_domain': {},
                    'by_platform': {}
                }
            )
        
        # Calculate date ranges
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = today.replace(day=1)
        
        # Get total generated
        total_generated = generated_content_collection.count_documents({
            'user_id': ObjectId(user_id)
        })
        
        # Get generated today
        generated_today = generated_content_collection.count_documents({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': today}
        })
        
        # Get generated this month
        generated_this_month = generated_content_collection.count_documents({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': month_start}
        })
        
        # Get breakdown by domain
        domain_pipeline = [
            {'$match': {'user_id': ObjectId(user_id)}},
            {'$group': {'_id': '$domain', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        
        domain_stats = {}
        for item in generated_content_collection.aggregate(domain_pipeline):
            domain_stats[item['_id']] = item['count']
        
        # Get breakdown by platform
        platform_pipeline = [
            {'$match': {'user_id': ObjectId(user_id)}},
            {'$group': {'_id': '$platform', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        
        platform_stats = {}
        for item in generated_content_collection.aggregate(platform_pipeline):
            platform_stats[item['_id']] = item['count']
        
        return create_response(
            success=True,
            message='Usage statistics retrieved successfully',
            data={
                'total_generated': total_generated,
                'generated_today': generated_today,
                'generated_this_month': generated_this_month,
                'by_domain': domain_stats,
                'by_platform': platform_stats,
                'period': {
                    'today': today.isoformat(),
                    'month_start': month_start.isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Get usage statistics error: {str(e)}")
        return create_response(
            success=False,
            message='Failed to retrieve usage statistics',
            error=str(e)
        ), 500

# Helper functions

def generate_ai_content(domain, domain_info, platform, platform_info, custom_prompt=None, tone=None):
    """Generate AI content based on domain and platform"""
    try:
        # This is a simplified AI content generator
        # In production, you would integrate with OpenAI, Mistral, or other AI services
        
        base_content = {
            'tech': [
                "🚀 The future of AI is here! New breakthroughs in machine learning are transforming industries.",
                "💡 Innovation spotlight: How startups are disrupting traditional markets with cutting-edge technology.",
                "🔥 Tech trend alert: The rise of no-code platforms is democratizing software development.",
            ],
            'memes': [
                "When you finally fix that bug that's been bothering you for hours 😂",
                "Me trying to explain my job to my parents: 'I make computers do things'",
                "That feeling when your code works on the first try... Sus 🤔",
            ],
            'business': [
                "💼 Success tip: Focus on solving real problems, not building solutions looking for problems.",
                "📈 Growth hack: The best marketing is a product so good people can't help but talk about it.",
                "🎯 Mindset shift: Stop selling products, start solving problems.",
            ]
        }
        
        import random
        
        # Get base content for domain

        content_options = base_content.get(domain, base_content['tech'])
        base_text = random.choice(content_options)
        
        # Adjust for platform requirements

        max_length = platform_info['max_length']
        if len(base_text) > max_length:
            base_text = base_text[:max_length-3] + "..."
        
        # Add hashtags if platform supports them

        hashtags = []
        if platform_info['supports_hashtags']:
            hashtags = domain_info['hashtags'][:platform_info['optimal_hashtags']]
            if platform != 'twitter':  # Twitter hashtags are usually in the text
                base_text += " " + " ".join(hashtags)
        
        # Generate performance prediction (simplified)

        performance_score = random.randint(65, 95)  # Mock performance score
        
        return {
            'text': base_text.strip(),
            'hashtags': hashtags,
            'performance_score': performance_score,
            'domain': domain,
            'platform': platform,
            'tone': tone or domain_info['tone']
        }
        
    except Exception as e:
        logger.error(f"AI content generation error: {e}")
        
        # Return fallback content
        return {
            'text': f"Check out the latest in {domain}! 🚀",
            'hashtags': domain_info['hashtags'][:3],
            'performance_score': 70,
            'domain': domain,
            'platform': platform,
            'tone': tone or 'neutral'
        }

def generate_content_variant(original_content, platform, variation_type='tone'):
    """Generate a variant of existing content"""
    try:
        import random
        
        # Simple content variation logic
        # In production, this would use AI to create meaningful variants
        
        variations = {
            'tone': [
                original_content.replace('!', '.'),
                original_content.upper() if len(original_content) < 50 else original_content,
                original_content + " What do you think?",
            ],
            'length': [
                original_content.split('.')[0] + ".",
                original_content + " Let me know your thoughts in the comments!",
                "Quick tip: " + original_content,
            ],
            'style': [
                "🔥 " + original_content,
                "💡 Insight: " + original_content,
                original_content + " 🚀",
            ]
        }
        
        variant_options = variations.get(variation_type, variations['tone'])
        variant_text = random.choice(variant_options)
        
        return {
            'text': variant_text,
            'hashtags': ['#content', '#variation'],
            'performance_score': random.randint(60, 85),
            'type': variation_type
        }
        
    except Exception as e:
        logger.error(f"Content variant generation error: {e}")
        return {
            'text': original_content,
            'hashtags': ['#content'],
            'performance_score': 70,
            'type': 'original'
        }

def save_generated_content(user_id, domain, platform, content):
    """Save generated content to database"""
    try:
        generated_content_collection = get_collection('generated_content')
        if not generated_content_collection:
            return f"mock_id_{datetime.utcnow().timestamp()}"
        
        content_doc = {
            'user_id': ObjectId(user_id),
            'domain': domain,
            'platform': platform,
            'content': content['text'],
            'hashtags': content['hashtags'],
            'performance_prediction': content['performance_score'],
            'tone': content.get('tone', 'neutral'),
            'is_used': False,
            'created_at': datetime.utcnow(),
            'word_count': len(content['text'].split()),
            'character_count': len(content['text'])
        }
        
        result = generated_content_collection.insert_one(content_doc)
        return str(result.inserted_id)
        
    except Exception as e:
        logger.error(f"Save generated content error: {e}")
        return f"error_id_{datetime.utcnow().timestamp()}"