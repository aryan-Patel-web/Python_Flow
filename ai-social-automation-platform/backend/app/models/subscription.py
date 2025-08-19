from datetime import datetime, timedelta
from bson import ObjectId

class Subscription:
    def __init__(self, db):
        self.collection = db.subscriptions
    
    def create_subscription(self, user_id, plan_name, billing_cycle='monthly'):
        """Create a new subscription"""
        subscription_data = {
            'user_id': ObjectId(user_id),
            'plan_name': plan_name,
            'billing_cycle': billing_cycle,
            'status': 'active',
            'created_at': datetime.utcnow(),
            'next_billing_date': datetime.utcnow() + timedelta(days=30 if billing_cycle == 'monthly' else 365)
        }
        
        result = self.collection.insert_one(subscription_data)
        return str(result.inserted_id)
    
    def get_active_subscription(self, user_id):
        """Get user's active subscription"""
        return self.collection.find_one({
            'user_id': ObjectId(user_id),
            'status': 'active'
        })
