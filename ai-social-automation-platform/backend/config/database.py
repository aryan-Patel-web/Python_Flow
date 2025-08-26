#!/usr/bin/env python3
"""
Database Configuration for VelocityPost.ai
Simple MongoDB setup with graceful fallback
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Simple Database Manager - works with or without MongoDB"""
    
    def __init__(self):
        self.client = None
        self.db = None
        
    def init_app(self, app):
        """Initialize database connection"""
        print("🔄 Attempting database connection...")
        try:
            print("📦 Importing pymongo...")
            import pymongo
            from pymongo import MongoClient
            print("✅ pymongo imported successfully")
            
            connection_string = app.config.get('MONGODB_URI', 'mongodb://localhost:27017/velocitypost')
            print(f"🌐 Connecting to: {connection_string}")
            
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=3000)
            
            # Test connection
            print("🏓 Testing database connection...")
            self.client.admin.command('ping')
            print("✅ Database ping successful")
            
            # Get database name from URI
            db_name = connection_string.split('/')[-1] if '/' in connection_string else 'velocitypost'
            self.db = self.client[db_name]
            
            print(f"✅ Connected to MongoDB: {db_name}")
            logger.info(f"Connected to MongoDB: {db_name}")
            
        except ImportError as e:
            print(f"❌ pymongo not installed: {e}")
            logger.warning("pymongo not installed - running without database")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
            logger.warning(f"MongoDB connection failed: {str(e)} - running without database")
    
    def health_check(self):
        """Check database health"""
        print("🏥 Checking database health...")
        try:
            if not self.client:
                print("❌ No database client available")
                return {
                    'status': 'not-configured',
                    'message': 'No database connection'
                }
            
            self.client.admin.command('ping')
            print("✅ Database health check passed")
            return {
                'status': 'connected',
                'message': 'Database connection healthy'
            }
        except Exception as e:
            print(f"❌ Database health check failed: {str(e)}")
            return {
                'status': 'error',
                'message': f'Database error: {str(e)}'
            }
    
    def get_collection(self, collection_name):
        """Get a collection"""
        if self.db:
            print(f"📚 Getting collection: {collection_name}")
            return self.db[collection_name]
        print(f"❌ No database available for collection: {collection_name}")
        return None

# Global instance
db_instance = DatabaseManager()

def get_collection(collection_name):
    """Helper function to get collections"""
    return db_instance.get_collection(collection_name)