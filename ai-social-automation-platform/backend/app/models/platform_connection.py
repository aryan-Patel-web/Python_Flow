"""
Platform Connection Model for OAuth tokens
"""

from datetime import datetime, timedelta
from bson import ObjectId

class PlatformConnection:
    """Platform connection model for MongoDB operations"""
    
    @staticmethod
    def create(db, user_id, platform, token_data, profile_data):
        """Create or update platform connection"""
        
        # Calculate token expiry
        expires_at = None
        if token_data.get('expires_in'):
            expires_at = datetime.utcnow() + timedelta(seconds=int(token_data['expires_in']))
        
        connection_data = {
            'user_id': ObjectId(user_id),
            'platform': platform,
            'platform_user_id': profile_data.get('id', ''),
            'username': profile_data.get('username', ''),
            'display_name': profile_data.get('name', ''),
            'profile_picture': profile_data.get('picture', ''),
            'access_token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token'),
            'token_expires_at': expires_at,
            'profile_data': profile_data,
            'permissions': token_data.get('scope', '').split() if token_data.get('scope') else [],
            'is_active': True,
            'connected_at': datetime.utcnow(),
            'last_used_at': datetime.utcnow(),
            'posts_count': 0,
            'last_post_at': None
        }
        
        # Update existing or insert new
        result = db.platform_connections.update_one(
            {'user_id': ObjectId(user_id), 'platform': platform},
            {'$set': connection_data},
            upsert=True
        )
        
        return result.upserted_id or result.matched_count > 0
    
    @staticmethod
    def find_by_user_and_platform(db, user_id, platform):
        """Find connection by user and platform"""
        return db.platform_connections.find_one({
            'user_id': ObjectId(user_id),
            'platform': platform,
            'is_active': True
        })
    
    @staticmethod
    def find_by_user(db, user_id):
        """Find all active connections for user"""
        return list(db.platform_connections.find({
            'user_id': ObjectId(user_id),
            'is_active': True
        }))
    
    @staticmethod
    def deactivate(db, user_id, platform):
        """Deactivate platform connection"""
        return db.platform_connections.update_one(
            {'user_id': ObjectId(user_id), 'platform': platform},
            {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
        )
    
    @staticmethod
    def to_dict(connection):
        """Convert connection document to dictionary"""
        if not connection:
            return None
        
        return {
            'id': str(connection['_id']),
            'platform': connection['platform'],
            'username': connection.get('username', ''),
            'display_name': connection.get('display_name', ''),
            'profile_picture': connection.get('profile_picture', ''),
            'is_active': connection['is_active'],
            'connected_at': connection['connected_at'].isoformat() if connection.get('connected_at') else None,
            'last_used_at': connection.get('last_used_at').isoformat() if connection.get('last_used_at') else None,
            'posts_count': connection.get('posts_count', 0),
            'permissions': connection.get('permissions', [])
        }