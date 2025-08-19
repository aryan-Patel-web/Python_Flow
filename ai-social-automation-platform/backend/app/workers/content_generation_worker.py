from datetime import datetime
from bson import ObjectId
import logging
from app.celery_app import celery

logger = logging.getLogger(__name__)

@celery.task
def generate_user_content(user_id):
    """Generate content for a specific user"""
    try:
        from app import create_app
        from app.ai.content_generators.base_generator import ContentGenerator
        from app.services.credentials.credential_manager import CredentialManager
        
        app = create_app()
        
        with app.app_context():
            user_domains = app.db.user_domains.find_one({
                'user_id': ObjectId(user_id),
                'active': True
            })
            if not user_domains:
                logger.warning(f"No domains selected for user {user_id}")
                return
            
            connected_platforms = list(app.db.credentials.find({
                'user_id': ObjectId(user_id),
                'status': 'active'
            }))
            if not connected_platforms:
                logger.warning(f"No platforms connected for user {user_id}")
                return
            
            content_generator = ContentGenerator(
                app.config['MISTRAL_API_KEY'],
                app.config['GROQ_API_KEY']
            )
            
            selected_domains = user_domains.get('selected_domains', [])
            daily_limits = user_domains.get('daily_limits', {})
            
            for domain in selected_domains:
                for platform_cred in connected_platforms:
                    platform = platform_cred['platform']
                    platform_limit = daily_limits.get(platform, 2)
                    
                    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                    today_generated = app.db.generated_content.count_documents({
                        'user_id': ObjectId(user_id),
                        'platform': platform,
                        'domain': domain,
                        'created_at': {'$gte': today_start}
                    })
                    
                    if today_generated >= platform_limit:
                        continue
                    
                    result = content_generator.generate_content(domain, platform)
                    
                    if result.get('success'):
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
                        app.db.generated_content.insert_one(content_doc)
                        app.db.automation_logs.insert_one({
                            'user_id': ObjectId(user_id),
                            'log_type': 'content_generation',
                            'platform': platform,
                            'domain': domain,
                            'success': True,
                            'message': f'Generated {domain} content for {platform}',
                            'created_at': datetime.utcnow()
                        })
                        logger.info(f"Generated {domain} content for {platform} - user {user_id}")
            
        return f"Content generation completed for user {user_id}"
    except Exception as e:
        logger.error(f"Content generation worker error: {str(e)}")
        return f"Content generation failed for user {user_id}: {str(e)}"

@celery.task
def generate_scheduled_content():
    """Generate content for all active users"""
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            active_users = app.db.users.find({
                'automation_active': True,
                'is_active': True
            })
            for user in active_users:
                generate_user_content.delay(str(user['_id']))
                
        return "Scheduled content generation triggered for all active users"
    except Exception as e:
        logger.error(f"Scheduled content generation error: {str(e)}")
        return f"Scheduled content generation failed: {str(e)}"
    