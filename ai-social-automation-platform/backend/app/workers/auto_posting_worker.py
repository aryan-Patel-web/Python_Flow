from datetime import datetime, timedelta
import logging
from app.celery_app import celery

logger = logging.getLogger(__name__)

@celery.task
def collect_analytics():
    """Collect analytics for all posted content"""
    try:
        from app import create_app
        from app.services.analytics.analytics_collector import AnalyticsCollector
        
        app = create_app()
        with app.app_context():
            analytics_collector = AnalyticsCollector(app.config)
            week_ago = datetime.utcnow() - timedelta(days=7)
            posts_to_update = app.db.posts.find({
                'status': 'posted',
                'posted_at': {'$gte': week_ago},
                'platform_post_id': {'$exists': True}
            })
            updated_count = 0
            for post in posts_to_update:
                try:
                    engagement_data = analytics_collector.collect_engagement_data(
                        str(post['user_id']), post['platform'], post['platform_post_id']
                    )
                    app.db.posts.update_one(
                        {'_id': post['_id']},
                        {'$set': {'engagement': engagement_data, 'last_analytics_update': datetime.utcnow()}}
                    )
                    updated_count += 1
                except Exception as e:
                    logger.error(f"Failed to collect analytics for post {post['_id']}: {str(e)}")
                    continue
        return f"Analytics collected for {updated_count} posts"
    except Exception as e:
        logger.error(f"Analytics collection worker error: {str(e)}")
        return f"Analytics collection failed: {str(e)}"

@celery.task
def verify_all_credentials():
    """Verify all stored credentials periodically"""
    try:
        from app import create_app
        from app.services.credentials.credential_manager import CredentialManager
        
        app = create_app()
        with app.app_context():
            credential_manager = CredentialManager(app.db, app.config['ENCRYPTION_KEY'])
            credentials = app.db.credentials.find({'status': 'active'})
            verified_count = 0
            failed_count = 0
            for cred in credentials:
                try:
                    user_id = str(cred['user_id'])
                    platform = cred['platform']
                    creds_result = credential_manager.get_credentials(user_id, platform)
                    if creds_result['success']:
                        credential_manager.verify_credentials(user_id, platform, True)
                        verified_count += 1
                    else:
                        credential_manager.verify_credentials(user_id, platform, False)
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Credential verification failed: {str(e)}")
                    failed_count += 1
                    continue
        return f"Verified {verified_count} credentials, {failed_count} failed"
    except Exception as e:
        logger.error(f"Credential verification worker error: {str(e)}")
        return f"Credential verification failed: {str(e)}"
