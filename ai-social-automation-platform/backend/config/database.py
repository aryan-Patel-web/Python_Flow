#!/usr/bin/env python3
"""
Configuration file for database imports
Provides compatibility layer for different import paths
"""

# Import the main database functions from the utils directory
try:
    from app.utils.database import (
        init_db,
        get_db,
        get_database,
        get_collection,
        test_database_connection,
        UserModel,
        SocialAccountModel,
        PostModel,
        check_user_limits,
        get_user_stats,
        cleanup_expired_data,
        get_database_health,
        PLAN_LIMITS
    )
    
    # Re-export all functions for compatibility
    __all__ = [
        'init_db',
        'get_db',
        'get_database', 
        'get_collection',
        'test_database_connection',
        'UserModel',
        'SocialAccountModel',
        'PostModel',
        'check_user_limits',
        'get_user_stats',
        'cleanup_expired_data',
        'get_database_health',
        'PLAN_LIMITS'
    ]
    
except ImportError as e:
    print(f"Failed to import database functions: {e}")
    
    # Provide fallback implementations
    def init_db(app=None):
        raise ImportError("Database module not available")
    
    def get_db():
        raise ImportError("Database module not available")
    
    def get_database():
        raise ImportError("Database module not available")
    
    def get_collection(name):
        raise ImportError("Database module not available")
    
    def test_database_connection():
        return False
    
    class UserModel:
        @staticmethod
        def create_user(*args, **kwargs):
            raise ImportError("Database module not available")
        
        @staticmethod
        def get_user_by_email(*args, **kwargs):
            raise ImportError("Database module not available")
        
        @staticmethod
        def get_user_by_id(*args, **kwargs):
            raise ImportError("Database module not available")
    
    class SocialAccountModel:
        @staticmethod
        def save_account(*args, **kwargs):
            raise ImportError("Database module not available")
    
    class PostModel:
        @staticmethod
        def create_post(*args, **kwargs):
            raise ImportError("Database module not available")
    
    def check_user_limits(*args, **kwargs):
        return False, "Database unavailable"
    
    def get_user_stats(*args, **kwargs):
        return {}
    
    from typing import Literal

    def cleanup_expired_data() -> Literal[False]:
        return False
    
    def get_database_health():
        return {'status': 'unavailable'}
    
    PLAN_LIMITS = {
        'free': {'max_platforms': 2, 'max_posts_per_day': 2},
        'pro': {'max_platforms': 5, 'max_posts_per_day': 20},
        'agency': {'max_platforms': -1, 'max_posts_per_day': -1}
    }