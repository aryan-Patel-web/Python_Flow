"""
Generated Content Model
"""

from datetime import datetime
from bson import ObjectId
import re

class GeneratedContent:
    """Generated content model for MongoDB operations"""
    
    @staticmethod
    def create(db, user_id, domain, platform, content, performance_prediction=None):
        """Save AI-generated content"""
        content_data = {
            'user_id': ObjectId(user_id),
            'domain': domain,
            'platform': platform,
            'content': content,
            'performance_prediction': performance_prediction,
            'is_used': False,
            'created_at': datetime.utcnow(),
            'hashtags': GeneratedContent._extract_hashtags(content),
            'word_count': len(content.split()),
            'character_count': len(content),
            'ai_service': performance_prediction.get('ai_model_used') if performance_prediction else None
        }
        
        result = db.generated_content.insert_one(content_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_user(db, user_id, domain=None, platform=None, limit=20):
        """Get generated content with filters"""
        filter_query = {'user_id': ObjectId(user_id)}
        
        if domain:
            filter_query['domain'] = domain
        if platform:
            filter_query['platform'] = platform
        
        content = list(db.generated_content.find(filter_query)
                      .sort('created_at', -1)
                      .limit(limit))
        
        return content
    
    @staticmethod
    def mark_as_used(db, content_id):
        """Mark content as used"""
        return db.generated_content.update_one(
            {'_id': ObjectId(content_id)},
            {'$set': {'is_used': True, 'used_at': datetime.utcnow()}}
        )
    
    @staticmethod
    def _extract_hashtags(content):
        """Extract hashtags from content"""
        return re.findall(r'#\w+', content)
    
    @staticmethod
    def to_dict(content):
        """Convert content document to dictionary"""
        if not content:
            return None
        
        return {
            'id': str(content['_id']),
            'user_id': str(content['user_id']),
            'domain': content['domain'],
            'platform': content['platform'],
            'content': content['content'],
            'performance_prediction': content.get('performance_prediction', {}),
            'is_used': content.get('is_used', False),
            'created_at': content['created_at'].isoformat() if content.get('created_at') else None,
            'hashtags': content.get('hashtags', []),
            'word_count': content.get('word_count', 0),
            'character_count': content.get('character_count', 0),
            'ai_service': content.get('ai_service')
        }