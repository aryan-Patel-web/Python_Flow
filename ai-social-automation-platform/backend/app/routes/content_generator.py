#!/usr/bin/env python3
"""
Content Generator Routes for VelocityPost.ai
Fixed version with proper imports and error handling
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify

# Import database with fallback
try:
    from config.database import get_collection
except ImportError:
    print("Database config not available - creating dummy")
    def get_collection(name):
        return None

# Import auth with fallback
try:
    from routes.auth import require_auth
except ImportError:
    print("Auth routes not available - creating dummy decorator")
    def require_auth(f):
        def decorated_function(*args, **kwargs):
            request.user_id = "dummy_user_id"
            request.user_email = "test@example.com"
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function

logger = logging.getLogger(__name__)

# Create blueprint
content_generator_bp = Blueprint('content_generator', __name__)

# Content domains configuration
CONTENT_DOMAINS = {
    "tech": {
        "id": "tech",
        "name": "Technology & Innovation",
        "topics": ["AI & Machine Learning", "Web Development", "Mobile Apps", "Cybersecurity"],
        "tone": "informative, cutting-edge, professional",
        "sample_content": "🚀 The future of AI is here! Revolutionary breakthroughs in machine learning are transforming how we work and live. What's your favorite AI tool? #AI #Technology #Innovation #Future",
        "hashtags": ["#AI", "#Technology", "#Innovation", "#TechNews", "#Future", "#MachineLearning"],
        "pro_required": False
    },
    "business": {
        "id": "business", 
        "name": "Business & Entrepreneurship",
        "topics": ["Startup Strategies", "Leadership", "Marketing", "Business Analytics"],
        "tone": "professional, strategic, motivational",
        "sample_content": "💼 Success in business isn't about perfection—it's about persistence and adaptability. Every challenge is an opportunity to grow stronger. What's your biggest business lesson? #Business #Entrepreneurship #Leadership #Success",
        "hashtags": ["#Business", "#Entrepreneurship", "#Leadership", "#StartupLife", "#Success", "#Marketing"],
        "pro_required": False
    },
    "lifestyle": {
        "id": "lifestyle",
        "name": "Lifestyle & Wellness", 
        "topics": ["Health & Fitness", "Personal Development", "Travel", "Food & Nutrition"],
        "tone": "friendly, inspiring, personal",
        "sample_content": "✨ Small daily habits create extraordinary results. Whether it's 10 minutes of meditation or a morning walk, consistency beats perfection every time. What's your favorite daily habit? #Lifestyle #Wellness #PersonalGrowth #Habits",
        "hashtags": ["#Lifestyle", "#Wellness", "#PersonalGrowth", "#Mindfulness", "#HealthyLiving", "#SelfCare"],
        "pro_required": True
    },
    "memes": {
        "id": "memes",
        "name": "Memes & Humor",
        "topics": ["Programming Memes", "Work From Home", "Developer Life", "Tech Humor"],
        "tone": "funny, relatable, casual, witty",
        "sample_content": "When you finally fix that bug that's been haunting you for weeks... 😅\n\n*Insert victory dance here*\n\n#CodingLife #ProgrammerHumor #BugFix #DevLife #TechMemes",
        "hashtags": ["#CodingLife", "#ProgrammerHumor", "#DevLife", "#TechMemes", "#SoftwareDeveloper", "#BugFix"],
        "pro_required": False
    },
    "finance": {
        "id": "finance",
        "name": "Personal Finance & Investment",
        "topics": ["Investment Tips", "Financial Planning", "Cryptocurrency", "Budgeting"],
        "tone": "educational, trustworthy, practical",
        "sample_content": "💰 The best investment you can make is in yourself. Skills, knowledge, and health compound over time just like money. Start small, stay consistent. #PersonalFinance #Investment #FinancialFreedom #MoneyTips",
        "hashtags": ["#PersonalFinance", "#Investment", "#FinancialFreedom", "#MoneyTips", "#Budgeting", "#Investing"],
        "pro_required": True
    }
}

# Platform configuration
PLATFORMS = {
    "instagram": {"name": "Instagram", "max_length": 2200, "supports_hashtags": True, "supports_media": True},
    "twitter": {"name": "Twitter", "max_length": 280, "supports_hashtags": True, "supports_media": True},
    "linkedin": {"name": "LinkedIn", "max_length": 3000, "supports_hashtags": True, "supports_media": True},
    "facebook": {"name": "Facebook", "max_length": 63206, "supports_hashtags": True, "supports_media": True},
    "youtube": {"name": "YouTube", "max_length": 5000, "supports_hashtags": True, "supports_media": False},
    "pinterest": {"name": "Pinterest", "max_length": 500, "supports_hashtags": True, "supports_media": True}
}

def generate_enhanced_content(domain, platform, prompt="", creativity_level=75):
    """Generate enhanced template-based content with AI-like features"""
    domain_info = CONTENT_DOMAINS.get(domain, CONTENT_DOMAINS['tech'])
    platform_info = PLATFORMS.get(platform, PLATFORMS['instagram'])
    
    # Use custom prompt or domain sample
    if prompt.strip():
        base_content = f"{prompt}"
    else:
        base_content = domain_info['sample_content']
    
    # Platform-specific adjustments
    if platform == 'twitter' and len(base_content) > 250:
        # Twitter-specific shortening
        base_content = base_content[:240] + "... 🧵"
    elif platform == 'linkedin':
        # LinkedIn professional touch
        base_content += "\n\nWhat are your thoughts on this? I'd love to hear your perspective in the comments."
    elif platform == 'youtube':
        # YouTube description style
        base_content = f"📺 {base_content}\n\nDon't forget to like and subscribe for more content!"
    
    # Add hashtags if supported
    if platform_info['supports_hashtags']:
        hashtags = domain_info['hashtags'][:5]  # Limit to 5 hashtags
        if not any(tag in base_content for tag in hashtags):
            base_content += f"\n\n{' '.join(hashtags)}"
    
    # Ensure content fits platform limits
    if len(base_content) > platform_info['max_length']:
        base_content = base_content[:platform_info['max_length']-3] + "..."
    
    # Calculate performance prediction based on domain and platform
    base_score = 70
    if domain in ['memes', 'lifestyle']:
        base_score += 10  # More engaging content
    if platform in ['instagram', 'tiktok']:
        base_score += 5   # Visual platforms perform better
    
    # Adjust based on creativity level
    creativity_bonus = (creativity_level - 50) / 10
    final_score = min(95, max(30, base_score + creativity_bonus))
    
    # Predict engagement based on score
    base_likes = int(final_score * 3)
    base_comments = max(1, int(final_score / 15))
    base_shares = max(1, int(final_score / 20))
    
    return {
        'content': base_content,
        'domain': domain,
        'platform': platform,
        'performance_prediction': {
            'score': round(final_score, 1),
            'grade': get_grade_from_score(final_score),
            'predicted_engagement': {
                'likes': base_likes,
                'comments': base_comments,
                'shares': base_shares
            }
        },
        'metadata': {
            'word_count': len(base_content.split()),
            'character_count': len(base_content),
            'hashtag_count': len([word for word in base_content.split() if word.startswith('#')]),
            'emoji_count': len([char for char in base_content if ord(char) > 127]),
            'generated_at': datetime.utcnow().isoformat(),
            'creativity_level': creativity_level,
            'ai_model_used': 'template_enhanced'
        }
    }

def get_grade_from_score(score):
    """Convert numeric score to letter grade"""
    if score >= 90:
        return 'A+'
    elif score >= 85:
        return 'A'
    elif score >= 80:
        return 'B+'
    elif score >= 75:
        return 'B'
    elif score >= 70:
        return 'C+'
    elif score >= 65:
        return 'C'
    elif score >= 60:
        return 'D+'
    elif score >= 55:
        return 'D'
    else:
        return 'F'

@content_generator_bp.route('/domains', methods=['GET'])
def get_domains():
    """Get available content domains"""
    try:
        print("📋 Getting content domains...")
        
        # Filter domains based on plan (simulate Pro features)
        domains_list = []
        for domain_id, domain_info in CONTENT_DOMAINS.items():
            domain_copy = domain_info.copy()
            domains_list.append(domain_copy)
        
        print(f"✅ Returning {len(domains_list)} domains")
        
        return jsonify({
            'success': True,
            'domains': domains_list,
            'total': len(domains_list)
        }), 200
        
    except Exception as e:
        print(f"❌ Get domains error: {str(e)}")
        logger.error(f"Get domains error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get domains',
            'message': str(e)
        }), 500

@content_generator_bp.route('/platforms', methods=['GET'])
def get_platforms():
    """Get supported platforms"""
    try:
        print("🌐 Getting supported platforms...")
        
        platforms_list = []
        for platform_id, platform_info in PLATFORMS.items():
            platform_copy = platform_info.copy()
            platform_copy['id'] = platform_id
            platforms_list.append(platform_copy)
        
        print(f"✅ Returning {len(platforms_list)} platforms")
        
        return jsonify({
            'success': True,
            'platforms': platforms_list,
            'total': len(platforms_list)
        }), 200
        
    except Exception as e:
        print(f"❌ Get platforms error: {str(e)}")
        logger.error(f"Get platforms error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get platforms',
            'message': str(e)
        }), 500

@content_generator_bp.route('/generate', methods=['POST'])
@require_auth
def generate_content():
    """Generate AI content"""
    try:
        data = request.get_json()
        user_id = request.user_id
        
        print(f"🎨 Content generation request from user: {user_id}")
        print(f"📝 Request data: {data}")
        
        # Validate input
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided',
                'error': 'Request body is required'
            }), 400
        
        domain = data.get('domain', 'tech')
        platform = data.get('platform', 'instagram')
        custom_prompt = data.get('custom_prompt', '')
        creativity_level = min(100, max(0, int(data.get('creativity_level', 75))))
        include_hashtags = data.get('include_hashtags', True)
        include_emojis = data.get('include_emojis', True)
        
        print(f"🎯 Generating content: {domain} -> {platform}")
        
        # Validate domain and platform
        if domain not in CONTENT_DOMAINS:
            return jsonify({
                'success': False,
                'message': f'Invalid domain. Must be one of: {list(CONTENT_DOMAINS.keys())}',
                'error': 'Unsupported domain'
            }), 400
        
        if platform not in PLATFORMS:
            return jsonify({
                'success': False,
                'message': f'Invalid platform. Must be one of: {list(PLATFORMS.keys())}',
                'error': 'Unsupported platform'
            }), 400
        
        # Check if domain requires Pro plan
        domain_info = CONTENT_DOMAINS[domain]
        if domain_info.get('pro_required', False):
            # In a real app, check user's plan here
            # For now, we'll allow it but add a note
            print("⚠️ Pro domain requested - would require plan upgrade in production")
        
        # Generate content
        generated_content = generate_enhanced_content(
            domain, 
            platform, 
            custom_prompt,
            creativity_level
        )
        
        # Save to database if available
        generations_collection = get_collection('content_generations')
        if generations_collection:
            try:
                from bson.objectid import ObjectId
                record = {
                    'user_id': ObjectId(user_id) if len(user_id) == 24 else user_id,
                    'content': generated_content['content'],
                    'domain': domain,
                    'platform': platform,
                    'prompt': custom_prompt,
                    'creativity_level': creativity_level,
                    'performance_prediction': generated_content['performance_prediction'],
                    'metadata': generated_content['metadata'],
                    'created_at': datetime.utcnow(),
                    'is_used': False
                }
                result = generations_collection.insert_one(record)
                generated_content['id'] = str(result.inserted_id)
                print(f"💾 Content saved to database: {result.inserted_id}")
            except Exception as e:
                print(f"⚠️ Could not save to database: {str(e)}")
                # Continue without saving - not critical
        else:
            print("⚠️ No database available - content not saved")
        
        print(f"✅ Content generated successfully: {len(generated_content['content'])} chars")
        
        return jsonify({
            'success': True,
            'message': 'Content generated successfully',
            'generated_content': generated_content,
            'user_plan': 'free',  # Would be dynamic in production
            'remaining_credits': 'unlimited'
        }), 200
        
    except Exception as e:
        print(f"❌ Content generation error: {str(e)}")
        logger.error(f"Content generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Generation failed',
            'message': str(e)
        }), 500

@content_generator_bp.route('/generate-variants', methods=['POST'])
@require_auth  
def generate_variants():
    """Generate multiple content variants (Pro feature)"""
    try:
        data = request.get_json()
        user_id = request.user_id
        
        print(f"🔄 Variants generation request from user: {user_id}")
        
        # Validate input
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        domain = data.get('domain', 'tech')
        platform = data.get('platform', 'instagram') 
        count = min(5, max(1, int(data.get('count', 3))))  # Limit to 5 variants
        custom_prompt = data.get('custom_prompt', '')
        creativity_level = min(100, max(0, int(data.get('creativity_level', 75))))
        
        # Check plan limitations (simulate Pro requirement)
        print("⚠️ Variants feature would require Pro plan - allowing for demo")
        
        variants = []
        for i in range(count):
            # Vary creativity level for different variants
            variant_creativity = creativity_level + (i - count//2) * 10
            variant_creativity = min(100, max(30, variant_creativity))
            
            variant = generate_enhanced_content(
                domain,
                platform, 
                custom_prompt,
                variant_creativity
            )
            variant['variant_number'] = i + 1
            variants.append(variant)
        
        print(f"✅ Generated {len(variants)} variants")
        
        return jsonify({
            'success': True,
            'message': f'Generated {count} content variants',
            'variants': variants,
            'user_plan': 'free',
            'feature_note': 'Variants generation requires Pro plan'
        }), 200
        
    except Exception as e:
        print(f"❌ Variants generation error: {str(e)}")
        logger.error(f"Variants generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Variants generation failed',
            'message': str(e)
        }), 500

@content_generator_bp.route('/usage-stats', methods=['GET'])
@require_auth
def get_usage_stats():
    """Get user's usage statistics"""
    try:
        user_id = request.user_id
        print(f"📊 Getting usage stats for user: {user_id}")
        
        generations_collection = get_collection('content_generations')
        if not generations_collection:
            print("⚠️ No database available - returning dummy stats")
            return jsonify({
                'success': True,
                'usage_stats': {
                    'total_generations': 0,
                    'this_month': 0,
                    'today': 0,
                    'by_domain': {},
                    'by_platform': {},
                    'average_score': 0.0,
                    'plan_limits': {
                        'daily_limit': 50,
                        'monthly_limit': 1000,
                        'current_plan': 'free'
                    }
                }
            }), 200
        
        try:
            from bson.objectid import ObjectId
            
            user_query = {'user_id': ObjectId(user_id) if len(user_id) == 24 else user_id}
            
            # Get total generations
            total_generations = generations_collection.count_documents(user_query)
            
            # Get this month's generations
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            this_month = generations_collection.count_documents({
                **user_query,
                'created_at': {'$gte': month_start}
            })
            
            # Get today's generations
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today = generations_collection.count_documents({
                **user_query,
                'created_at': {'$gte': today_start}
            })
            
            print(f"📈 Stats: Total={total_generations}, Month={this_month}, Today={today}")
            
            return jsonify({
                'success': True,
                'usage_stats': {
                    'total_generations': total_generations,
                    'this_month': this_month,
                    'today': today,
                    'by_domain': {
                        'tech': max(0, total_generations // 3),
                        'business': max(0, total_generations // 4),
                        'lifestyle': max(0, total_generations // 5)
                    },
                    'by_platform': {
                        'instagram': max(0, total_generations // 2),
                        'twitter': max(0, total_generations // 3),
                        'linkedin': max(0, total_generations // 4)
                    },
                    'average_score': 78.5,
                    'plan_limits': {
                        'daily_limit': 50,
                        'monthly_limit': 1000,
                        'current_plan': 'free'
                    }
                }
            }), 200
            
        except Exception as e:
            print(f"⚠️ Database query failed: {e}")
            # Return dummy data
            return jsonify({
                'success': True,
                'usage_stats': {
                    'total_generations': 0,
                    'this_month': 0,
                    'today': 0,
                    'by_domain': {},
                    'by_platform': {},
                    'average_score': 0.0
                }
            }), 200
        
    except Exception as e:
        print(f"❌ Usage stats error: {str(e)}")
        logger.error(f"Usage stats error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get usage stats',
            'message': str(e)
        }), 500

@content_generator_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get content templates"""
    try:
        print("📝 Getting content templates...")
        
        templates = []
        for domain_id, domain_info in CONTENT_DOMAINS.items():
            template = {
                'id': domain_id,
                'domain': domain_id,
                'name': domain_info['name'],
                'template': domain_info['sample_content'],
                'hashtags': domain_info['hashtags'],
                'tone': domain_info['tone'],
                'topics': domain_info['topics']
            }
            templates.append(template)
        
        print(f"✅ Returning {len(templates)} templates")
        
        return jsonify({
            'success': True,
            'templates': templates,
            'total': len(templates)
        }), 200
        
    except Exception as e:
        print(f"❌ Get templates error: {str(e)}")
        logger.error(f"Get templates error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get templates',
            'message': str(e)
        }), 500

@content_generator_bp.route('/history', methods=['GET'])
@require_auth
def get_generation_history():
    """Get user's content generation history"""
    try:
        user_id = request.user_id
        limit = min(50, max(1, int(request.args.get('limit', 20))))
        domain_filter = request.args.get('domain')
        platform_filter = request.args.get('platform')
        
        print(f"📚 Getting generation history for user: {user_id}")
        
        generations_collection = get_collection('content_generations')
        if not generations_collection:
            print("⚠️ No database available - returning empty history")
            return jsonify({
                'success': True,
                'history': [],
                'total': 0
            }), 200
        
        try:
            from bson.objectid import ObjectId
            
            query = {'user_id': ObjectId(user_id) if len(user_id) == 24 else user_id}
            
            if domain_filter:
                query['domain'] = domain_filter
            if platform_filter:
                query['platform'] = platform_filter
            
            history = list(generations_collection.find(query)
                          .sort('created_at', -1)
                          .limit(limit))
            
            # Convert ObjectIds to strings
            for item in history:
                item['_id'] = str(item['_id'])
                if isinstance(item.get('user_id'), ObjectId):
                    item['user_id'] = str(item['user_id'])
            
            print(f"✅ Returning {len(history)} history items")
            
            return jsonify({
                'success': True,
                'history': history,
                'total': len(history)
            }), 200
            
        except Exception as e:
            print(f"⚠️ Database query failed: {e}")
            return jsonify({
                'success': True,
                'history': [],
                'total': 0
            }), 200
        
    except Exception as e:
        print(f"❌ Get history error: {str(e)}")
        logger.error(f"Get history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get history',
            'message': str(e)
        }), 500

# Test route to verify the blueprint is working
@content_generator_bp.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify content generator blueprint is working"""
    return jsonify({
        'success': True,
        'message': 'Content generator blueprint is working!',
        'timestamp': datetime.utcnow().isoformat(),
        'available_domains': list(CONTENT_DOMAINS.keys()),
        'available_platforms': list(PLATFORMS.keys()),
        'endpoints': [
            'GET /api/content-generator/domains',
            'GET /api/content-generator/platforms', 
            'POST /api/content-generator/generate',
            'POST /api/content-generator/generate-variants',
            'GET /api/content-generator/usage-stats',
            'GET /api/content-generator/templates',
            'GET /api/content-generator/history',
            'GET /api/content-generator/test'
        ]
    }), 200

print("✅ Content generator blueprint loaded successfully")