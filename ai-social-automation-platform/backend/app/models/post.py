"""
Post Model for content management
"""

from datetime import datetime
from bson import ObjectId

class Post:
    """Post model for MongoDB operations"""
    
    @staticmethod
    def create(db, user_id, platform, content, media_urls=None, scheduled_for=None):
        """Create a new post"""
        post_data = {
            'user_id': ObjectId(user_id),
            'platform': platform,
            'content': content,
            'media_urls': media_urls or [],
            'scheduled_for': scheduled_for,
            'status': 'scheduled' if scheduled_for else 'draft',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_ai_generated': True,
            'engagement_data': {},
            'performance_score': None,
            'platform_post_id': None,
            'error_message': None,
            'posted_at': None
        }
        
        result = db.posts.insert_one(post_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_user(db, user_id, limit=50, platform=None, status=None):
        """Find user's posts with filters"""
        filter_query = {'user_id': ObjectId(user_id)}
        
        if platform:
            filter_query['platform'] = platform
        if status:
            filter_query['status'] = status
        
        posts = list(db.posts.find(filter_query)
                    .sort('created_at', -1)
                    .limit(limit))
        
        return posts
    
    @staticmethod
    def update_status(db, post_id, status, platform_post_id=None, error_message=None):
        """Update post status"""
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow()
        }
        
        if platform_post_id:
            update_data['platform_post_id'] = platform_post_id
            update_data['posted_at'] = datetime.utcnow()
        
        if error_message:
            update_data['error_message'] = error_message
        
        return db.posts.update_one(
            {'_id': ObjectId(post_id)},
            {'$set': update_data}
        )
    
    @staticmethod
    def to_dict(post):
        """Convert post document to dictionary"""
        if not post:
            return None
        
        return {
            'id': str(post['_id']),
            'user_id': str(post['user_id']),
            'platform': post['platform'],
            'content': post['content'],
            'media_urls': post.get('media_urls', []),
            'scheduled_for': post['scheduled_for'].isoformat() if post.get('scheduled_for') else None,
            'status': post['status'],
            'created_at': post['created_at'].isoformat() if post.get('created_at') else None,
            'posted_at': post['posted_at'].isoformat() if post.get('posted_at') else None,
            'platform_post_id': post.get('platform_post_id'),
            'is_ai_generated': post.get('is_ai_generated', False),
            'performance_score': post.get('performance_score'),
            'engagement_data': post.get('engagement_data', {}),
            'error_message': post.get('error_message')
        }