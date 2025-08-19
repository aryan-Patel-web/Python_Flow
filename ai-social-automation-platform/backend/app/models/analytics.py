from datetime import datetime, timedelta
from bson import ObjectId

class Analytics:
    def __init__(self, db):
        self.collection = db.analytics
    
    def record_engagement(self, post_id, platform, engagement_data):
        """Record engagement metrics for a post"""
        analytics_data = {
            'post_id': ObjectId(post_id),
            'platform': platform,
            'engagement': engagement_data,
            'recorded_at': datetime.utcnow()
        }
        
        return self.collection.insert_one(analytics_data)
    
    def get_user_analytics(self, user_id, days=30):
        """Get analytics for user's posts"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {'$lookup': {
                'from': 'posts',
                'localField': 'post_id',
                'foreignField': '_id',
                'as': 'post'
            }},
            {'$unwind': '$post'},
            {'$match': {
                'post.user_id': ObjectId(user_id),
                'recorded_at': {'$gte': start_date}
            }},
            {'$group': {
                '_id': '$post.platform',
                'total_likes': {'$sum': '$engagement.likes'},
                'total_comments': {'$sum': '$engagement.comments'},
                'total_shares': {'$sum': '$engagement.shares'}
            }}
        ]
        
        return list(self.collection.aggregate(pipeline))
