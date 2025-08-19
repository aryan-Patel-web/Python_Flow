from datetime import datetime
from bson import ObjectId

class Post:
    def __init__(self, db):
        self.collection = db.posts
    
    def create_post(self, user_id, platform, content_type, title, description, file_path=None, status='draft'):
        """Create a new post"""
        post_data = {
            'user_id': ObjectId(user_id),
            'platform': platform,
            'content_type': content_type,
            'title': title,
            'description': description,
            'file_path': file_path,
            'status': status,
            'created_at': datetime.utcnow(),
            'scheduled_at': None,
            'posted_at': None,
            'platform_post_id': None,
            'platform_url': None,
            'engagement': {'likes': 0, 'comments': 0, 'shares': 0},
            'metadata': {}
        }
        
        result = self.collection.insert_one(post_data)
        return str(result.inserted_id)
    
    def update_post_status(self, post_id, status, platform_post_id=None, platform_url=None):
        """Update post status after posting"""
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow()
        }
        
        if status == 'posted':
            update_data['posted_at'] = datetime.utcnow()
            if platform_post_id:
                update_data['platform_post_id'] = platform_post_id
            if platform_url:
                update_data['platform_url'] = platform_url
        
        return self.collection.update_one(
            {'_id': ObjectId(post_id)},
            {'$set': update_data}
        )
