from datetime import datetime
from bson import ObjectId

class AutomationLog:
    def __init__(self, db):
        self.collection = db.automation_logs
    
    def log_action(self, user_id, action_type, platform=None, success=True, message='', error=None):
        """Log automation action"""
        log_data = {
            'user_id': ObjectId(user_id),
            'action_type': action_type,
            'platform': platform,
            'success': success,
            'message': message,
            'error': error,
            'timestamp': datetime.utcnow()
        }
        
        return self.collection.insert_one(log_data)
    
    def get_user_logs(self, user_id, limit=50):
        """Get user's automation logs"""
        return list(self.collection.find({
            'user_id': ObjectId(user_id)
        }).sort('timestamp', -1).limit(limit))
