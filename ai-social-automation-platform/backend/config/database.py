#!/usr/bin/env python3
"""
Database configuration and connection management
"""

import os
import logging
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Singleton database connection class"""
    _instance = None
    _client = None
    _database = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def init_app(self, app=None):
        """Initialize database connection with Flask app"""
        try:
            mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/velocitypost')
            print(f"Connecting to MongoDB: {mongodb_uri.replace('mongodb://', 'mongodb://***@')}")
            
            # Create MongoDB client
            self._client = MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Test connection
            self._client.admin.command('ping')
            
            # Get database name from URI or use default
            if mongodb_uri.count('/') > 2:
                db_name = mongodb_uri.split('/')[-1]
            else:
                db_name = 'velocitypost'
            
            self._database = self._client[db_name]
            print(f"Connected to database: {db_name}")
            
            if app:
                app.config['DATABASE'] = self._database
            
            return self._database
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"Database connection failed: {str(e)}")
            print("Continuing without database connection...")
            self._client = None
            self._database = None
            return None
        except Exception as e:
            print(f"Database initialization error: {str(e)}")
            self._client = None
            self._database = None
            return None
    
    def get_database(self):
        """Get database instance"""
        return self._database
    
    def get_client(self):
        """Get MongoDB client"""
        return self._client
    
    def health_check(self):
        """Check database health"""
        try:
            if self._client and self._database:
                # Ping database
                self._client.admin.command('ping')
                
                # Get some basic stats
                stats = self._database.command('dbstats')
                
                return {
                    'status': 'healthy',
                    'connected': True,
                    'database': self._database.name,
                    'collections': len(self._database.list_collection_names()),
                    'data_size': stats.get('dataSize', 0),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'status': 'disconnected',
                    'connected': False,
                    'error': 'No database connection',
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {
                'status': 'error',
                'connected': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

# Create singleton instance
db_instance = DatabaseConnection()

def get_collection(collection_name):
    """Get a collection from the database"""
    try:
        database = db_instance.get_database()
        if database:
            return database[collection_name]
        else:
            print(f"Database not available for collection: {collection_name}")
            return None
    except Exception as e:
        print(f"Error getting collection {collection_name}: {str(e)}")
        return None

def get_database():
    """Get the database instance"""
    return db_instance.get_database()

def init_collections():
    """Initialize collections with indexes"""
    try:
        database = db_instance.get_database()
        if not database:
            print("Database not available - skipping index creation")
            return False
        
        print("Creating database indexes...")
        
        # Users collection indexes
        users_collection = database['users']
        users_collection.create_index('email', unique=True)
        users_collection.create_index('created_at')
        users_collection.create_index([('email', 1), ('is_active', 1)])
        
        # Content generations collection indexes
        generations_collection = database['content_generations']
        generations_collection.create_index('user_id')
        generations_collection.create_index('created_at')
        generations_collection.create_index([('user_id', 1), ('created_at', -1)])
        
        # Social accounts collection indexes
        social_accounts_collection = database['social_accounts']
        social_accounts_collection.create_index('user_id')
        social_accounts_collection.create_index([('user_id', 1), ('platform', 1)], unique=True)
        
        # Posts collection indexes
        posts_collection = database['posts']
        posts_collection.create_index('user_id')
        posts_collection.create_index('scheduled_for')
        posts_collection.create_index([('user_id', 1), ('created_at', -1)])
        
        print("Database indexes created successfully")
        return True
        
    except Exception as e:
        print(f"Failed to create indexes: {str(e)}")
        return False

# Initialize collections when module is imported
try:
    if db_instance.get_database():
        init_collections()
except Exception as e:
    print(f"Collection initialization failed: {str(e)}")