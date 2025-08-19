from datetime import datetime, timedelta
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class SubscriptionManager:
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.subscription_plans = config['SUBSCRIPTION_PLANS']
    
    def create_subscription(self, user_id, plan_name, billing_cycle='monthly'):
        """Create a new subscription"""
        try:
            if plan_name not in self.subscription_plans:
                return {'success': False, 'error': 'Invalid plan name'}
            
            plan_details = self.subscription_plans[plan_name]
            
            # Calculate next billing date
            if billing_cycle == 'monthly':
                next_billing = datetime.utcnow() + timedelta(days=30)
                price = plan_details['price']
            else:  # yearly
                next_billing = datetime.utcnow() + timedelta(days=365)
                price = plan_details['price'] * 12 * 0.8  # 20% discount
            
            subscription_data = {
                'user_id': ObjectId(user_id),
                'plan_name': plan_name,
                'billing_cycle': billing_cycle,
                'price': price,
                'status': 'active',
                'created_at': datetime.utcnow(),
                'next_billing_date': next_billing
            }
            
            # Cancel existing subscriptions
            self.db.subscriptions.update_many(
                {'user_id': ObjectId(user_id), 'status': 'active'},
                {'$set': {'status': 'cancelled'}}
            )
            
            # Create new subscription
            result = self.db.subscriptions.insert_one(subscription_data)
            
            # Update user's plan
            self.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'subscription_plan': plan_name}}
            )
            
            return {
                'success': True,
                'subscription_id': str(result.inserted_id),
                'message': f'Subscribed to {plan_name} plan successfully'
            }
            
        except Exception as e:
            logger.error(f"Subscription creation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def check_usage_limits(self, user_id):
        """Check if user has exceeded usage limits"""
        try:
            user = self.db.users.find_one({'_id': ObjectId(user_id)})
            if not user:
                return {'valid': False, 'error': 'User not found'}
            
            plan_name = user.get('subscription_plan', 'starter')
            plan_limits = self.subscription_plans.get(plan_name, {})
            
            # Check daily post limit
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_posts = self.db.posts.count_documents({
                'user_id': ObjectId(user_id),
                'created_at': {'$gte': today_start}
            })
            
            max_posts_per_day = plan_limits.get('max_posts_per_day', 3)
            
            if today_posts >= max_posts_per_day:
                return {
                    'valid': False,
                    'error': f'Daily post limit reached ({max_posts_per_day})',
                    'usage': {
                        'posts_today': today_posts,
                        'limit': max_posts_per_day
                    }
                }
            
            return {
                'valid': True,
                'usage': {
                    'posts_today': today_posts,
                    'limit': max_posts_per_day,
                    'remaining': max_posts_per_day - today_posts
                }
            }
            
        except Exception as e:
            logger.error(f"Usage limit check error: {str(e)}")
            return {'valid': False, 'error': str(e)}
