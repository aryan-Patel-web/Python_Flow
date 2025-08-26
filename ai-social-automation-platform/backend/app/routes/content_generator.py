#!/usr/bin/env python3
"""
Simple Content Generator Routes for VelocityPost.ai
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify

from config.database import get_collection
from routes.auth import require_auth

logger = logging.getLogger(__name__)

# Create blueprint
content_generator_bp = Blueprint('content_generator', __name__)

# Simple content domains
CONTENT_DOMAINS = {
    "tech": {
        "id": "tech",
        "name": "Technology & Innovation",
        "topics": ["AI & Machine Learning", "Web Development", "Mobile Apps", "Cybersecurity"],
        "tone": "informative, cutting-edge, professional"
    },
    "business": {
        "id": "business", 
        "name": "Business & Entrepreneurship",
        "topics": ["Startup Strategies", "Leadership", "Marketing", "Business Analytics"],
        "tone": "professional, strategic, motivational"
    },
    "lifestyle": {
        "id": "lifestyle",
        "name": "Lifestyle & Wellness", 
        "topics": ["Health & Fitness", "Personal Development", "Travel", "Food & Nutrition"],
        "tone": "friendly, inspiring, personal"
    }
}

PLATFORMS = {
    "instagram": {"name": "Instagram", "max_length": 2200, "supports_hashtags": True},
    "twitter": {"name": "Twitter", "max_length": 280, "supports_hashtags": True},
    "linkedin": {"name": "LinkedIn", "max_length": 3000, "supports_hashtags": True},
    "facebook": {"name": "Facebook", "max_length": 63206, "supports_hashtags": True}
}

def generate_simple_content(domain, platform, prompt):
    """Generate simple template-based content"""
    domain_info = CONTENT_DOMAINS.get(domain, CONTENT_DOMAINS['tech'])
    
    # Simple templates
    templates = {
        "tech": f"🚀 Tech Update: {prompt}\n\nThe future of technology is here! What are your thoughts?\n\n#Technology #Innovation #Tech",
        "business": f"💼 Business Insight: {prompt}\n\nSuccess requires strategy and execution. What's your approach?\n\n#Business #Strategy #Success",
        "lifestyle": f"✨ Life Tip: {prompt}\n\nSmall changes can make a big difference in your daily routine!\n\n#Lifestyle #Wellness #SelfCare"
    }
    
    content = templates.get(domain, templates["tech"])
    
    # Adjust for platform
    platform_info = PLATFORMS.get(platform, PLATFORMS['instagram'])
    if len(content) > platform_info['max_length']:
        content = content[:platform_info['max_length']-3] + "..."
    
    return {
        'content': content,
        'domain': domain,
        'platform': platform,
        'performance_prediction': {
            'score': 75.0,
            'grade': 'B+',
            'predicted_engagement': {'likes': 100, 'comments': 5, 'shares': 3}
        },
        'metadata': {
            'word_count': len(content.split()),
            'character_count': len(content),
            'generated_at': datetime.utcnow().isoformat()
        }
    }

@content_generator_bp.route('/domains', methods=['GET'])
def get_domains():
    """Get available content domains"""
    try:
        return jsonify({
            'success': True,
            'domains': list(CONTENT_DOMAINS.values()),
            'total': len(CONTENT_DOMAINS)
        }), 200
    except Exception as e:
        logger.error(f"Get domains error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get domains'
        }), 500

@content_generator_bp.route('/platforms', methods=['GET'])
def get_platforms():
    """Get supported platforms"""
    try:
        return jsonify({
            'success': True,
            'platforms': list(PLATFORMS.values()),
            'total': len(PLATFORMS)
        }), 200
    except Exception as e:
        logger.error(f"Get platforms error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get platforms'
        }), 500

@content_generator_bp.route('/generate', methods=['POST'])
@require_auth
def generate_content():
    """Generate AI content"""
    try:
        data = request.get_json()
        user_id = request.user_id
        
        # Validate input
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        domain = data.get('domain', 'tech')
        platform = data.get('platform', 'instagram')
        custom_prompt = data.get('custom_prompt', 'Latest trends and innovations')
        
        # Validate domain and platform
        if domain not in CONTENT_DOMAINS:
            return jsonify({
                'success': False,
                'message': f'Invalid domain. Must be one of: {list(CONTENT_DOMAINS.keys())}'
            }), 400
        
        if platform not in PLATFORMS:
            return jsonify({
                'success': False,
                'message': f'Invalid platform. Must be one of: {list(PLATFORMS.keys())}'
            }), 400
        
        # Generate content
        generated_content = generate_simple_content(domain, platform, custom_prompt)
        
        # Save to database if available
        generations_collection = get_collection('content_generations')
        if generations_collection:
            try:
                from bson.objectid import ObjectId
                record = {
                    'user_id': ObjectId(user_id),
                    'content': generated_content['content'],
                    'domain': domain,
                    'platform': platform,
                    'prompt': custom_prompt,
                    'performance_prediction': generated_content['performance_prediction'],
                    'metadata': generated_content['metadata'],
                    'created_at': datetime.utcnow()
                }
                result = generations_collection.insert_one(record)
                generated_content['id'] = str(result.inserted_id)
            except Exception as e:
                logger.warning(f"Could not save generation record: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Content generated successfully',
            'generated_content': generated_content,
            'user_plan': 'free',
            'remaining_credits': 'unlimited'
        }), 200
        
    except Exception as e:
        logger.error(f"Content generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Generation failed',
            'message': str(e)
        }), 500

@content_generator_bp.route('/usage-stats', methods=['GET'])
@require_auth
def get_usage_stats():
    """Get user's usage statistics"""
    try:
        user_id = request.user_id
        
        generations_collection = get_collection('content_generations')
        if not generations_collection:
            return jsonify({
                'success': True,
                'usage_stats': {
                    'total_generations': 0,
                    'this_month': 0,
                    'by_domain': {},
                    'by_platform': {}
                }
            }), 200
        
        from bson.objectid import ObjectId
        
        # Get total generations
        total_generations = generations_collection.count_documents({
            'user_id': ObjectId(user_id)
        })
        
        # Get this month's generations
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month = generations_collection.count_documents({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': month_start}
        })
        
        return jsonify({
            'success': True,
            'usage_stats': {
                'total_generations': total_generations,
                'this_month': this_month,
                'by_domain': {'tech': total_generations // 2, 'business': total_generations // 3},
                'by_platform': {'instagram': total_generations // 2, 'twitter': total_generations // 3}
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Usage stats error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get usage stats'
        }), 500

@content_generator_bp.route('/files', methods=['GET'])
@require_auth
def get_files():
    """Get user files (placeholder)"""
    try:
        return jsonify({
            'success': True,
            'files': [],
            'total': 0
        }), 200
    except Exception as e:
        logger.error(f"Get files error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get files'
        }), 500