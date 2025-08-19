import logging
from celery import shared_task
from datetime import datetime, timedelta
from app.core.celery_app import celery_app
from app.services.analytics_service import AnalyticsService
from app import create_app

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="analyze_post_performance")
def analyze_post_performance(self, user_id, platform, post_id):
    """
    Task to analyze performance of a single post
    """
    try:
        app = create_app()
        with app.app_context():
            analytics = AnalyticsService()

            performance = analytics.fetch_post_metrics(
                user_id=user_id,
                platform=platform,
                post_id=post_id
            )

            if not performance:
                logger.warning(
                    f"No performance data returned for post {post_id} ({platform})"
                )
                return False

            app.db.analytics.insert_one({
                'user_id': user_id,
                'platform': platform,
                'post_id': post_id,
                'metrics': performance,
                'analyzed_at': datetime.utcnow()
            })

            logger.info(
                f"Analytics stored for post {post_id} on {platform}"
            )
            return True

    except Exception as e:
        logger.error(
            f"Error analyzing performance for post {post_id} ({platform}): {str(e)}",
            exc_info=True
        )
        return False


@shared_task(bind=True, name="generate_weekly_report")
def generate_weekly_report(self, user_id):
    """
    Task to generate a weekly analytics report for a user
    """
    try:
        app = create_app()
        with app.app_context():
            analytics = AnalyticsService()

            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)

            report = analytics.generate_summary_report(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )

            if not report:
                logger.warning(f"No analytics report generated for user {user_id}")
                return False

            app.db.reports.insert_one({
                'user_id': user_id,
                'report_type': 'weekly',
                'report': report,
                'generated_at': datetime.utcnow()
            })

            logger.info(f"Weekly report generated for user {user_id}")
            return True

    except Exception as e:
        logger.error(f"Error generating weekly report for user {user_id}: {str(e)}",
                     exc_info=True)
        return False
