#!/usr/bin/env python3
"""
VelocityPost.ai - AI Social Media Automation Platform
Main Flask Application with complete auto-posting functionality
"""

import os
import logging
import sys
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

# Import database initialization
try:
    from app.utils.database import init_db, test_database_connection
    print("Database utilities imported successfully")
except ImportError as e:
    try:
        from config.database import init_db, test_database_connection
        print("Database utilities imported from config")
    except ImportError as e2:
        print(f"Database import failed: {e}")
        print(f"Config database import failed: {e2}")
        # Create fallback functions
        def init_db(app=None):
            print("Database initialization not available")
            return None
        
        def test_database_connection():
            print("Database connection test not available")
            return False

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def safe_import_blueprint(module_path, blueprint_name, url_prefix, description):
    """Safely import and register a blueprint"""
    try:
        logger.debug(f"Trying import: {module_path}")
        module = __import__(module_path, fromlist=[blueprint_name])
        blueprint = getattr(module, blueprint_name)
        return blueprint, True
    except ImportError as e:
        logger.warning(f"Import failed for {module_path}: {e}")
        return None, False
    except AttributeError as e:
        logger.warning(f"Blueprint not found in {module_path}: {e}")
        return None, False
    except Exception as e:
        logger.error(f"Unexpected error importing {module_path}: {e}")
        return None, False

def create_app():
    """Create and configure Flask application"""
    
    logger.info("Starting app creation...")
    
    # Create Flask app
    app = Flask(__name__)
    
    # App configuration
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production'),
        JWT_ACCESS_TOKEN_EXPIRES=3600,  # 1 hour
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
        UPLOAD_FOLDER=os.path.join(os.getcwd(), 'uploads', 'temp')
    )
    
    # CORS configuration
    CORS(app, 
         origins=["http://localhost:3000", "http://localhost:5173", "https://velocitypost.ai"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    
    # Initialize database
    try:
        init_db(app)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Register blueprints
    registered_blueprints = []
    
    # Define blueprint configurations
    blueprint_configs = [
        {
            'module_path': 'app.routes.auth',
            'blueprint_name': 'auth_bp',
            'url_prefix': '/api/auth',
            'description': 'Authentication'
        },
        {
            'module_path': 'app.routes.oauth',
            'blueprint_name': 'oauth_bp',
            'url_prefix': '/api/oauth',
            'description': 'OAuth Platform Management'
        },
        {
            'module_path': 'app.routes.automation',
            'blueprint_name': 'automation_bp',
            'url_prefix': '/api/automation',
            'description': 'Auto-Posting Automation'
        },
        {
            'module_path': 'app.routes.content_generator',
            'blueprint_name': 'content_generator_bp',
            'url_prefix': '/api/content-generator',
            'description': 'AI Content Generation'
        }
    ]
    
    # Track successful registrations
    auth_registered = False
    oauth_registered = False
    automation_registered = False
    content_registered = False
    
    # Register each blueprint
    for config in blueprint_configs:
        logger.info(f"Attempting to register {config['description']} blueprint...")
        
        blueprint, success = safe_import_blueprint(
            config['module_path'],
            config['blueprint_name'],
            config['url_prefix'],
            config['description']
        )
        
        if success and blueprint:
            try:
                app.register_blueprint(blueprint, url_prefix=config['url_prefix'])
                registered_blueprints.append(config['blueprint_name'])
                logger.info(f"{config['description']} blueprint registered successfully")
                
                # Track specific blueprints
                if config['blueprint_name'] == 'auth_bp':
                    auth_registered = True
                elif config['blueprint_name'] == 'oauth_bp':
                    oauth_registered = True
                elif config['blueprint_name'] == 'automation_bp':
                    automation_registered = True
                elif config['blueprint_name'] == 'content_generator_bp':
                    content_registered = True
                
            except Exception as e:
                logger.error(f"Failed to register {config['description']} blueprint: {e}")
        else:
            logger.info(f"{config['description']} blueprint not available")
    
    logger.info(f"Blueprint registration complete. Total registered: {len(registered_blueprints)}")
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Endpoint not found',
            'error': 'The requested resource was not found',
            'available_endpoints': [
                '/api/health',
                '/api/docs',
                '/api/auth/*' if auth_registered else None,
                '/api/oauth/*' if oauth_registered else None,
                '/api/automation/*' if automation_registered else None,
                '/api/content-generator/*' if content_registered else None,
            ]
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'message': 'Method not allowed',
            'error': f'The method is not allowed for the requested URL'
        }), 405
    
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        return jsonify({
            'success': False,
            'message': e.name,
            'error': e.description
        }), e.code
    
    # Create upload directories
    upload_dir = app.config.get('UPLOAD_FOLDER')
    if upload_dir:
        os.makedirs(upload_dir, exist_ok=True)
        logger.info(f"Upload directory created: {upload_dir}")
    
    # Root route
    @app.route('/')
    def index():
        available_endpoints = {
            'health': '/api/health',
            'docs': '/api/docs'
        }
        
        if auth_registered:
            available_endpoints['auth'] = '/api/auth'
        if oauth_registered:
            available_endpoints['oauth'] = '/api/oauth'
        if automation_registered:
            available_endpoints['automation'] = '/api/automation'
        if content_registered:
            available_endpoints['content_generator'] = '/api/content-generator'
        
        return jsonify({
            'message': 'Welcome to VelocityPost.ai API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': available_endpoints,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        # Test database connection
        db_status = "error"
        try:
            db_status = "connected" if test_database_connection() else "disconnected"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            db_status = "error"
        
        # Test Redis connection
        redis_status = "not-configured"
        try:
            import redis
            redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'), 
                port=int(os.getenv('REDIS_PORT', 6379)), 
                db=int(os.getenv('REDIS_DB', 0)),
                socket_timeout=2
            )
            redis_client.ping()
            redis_status = "connected"
        except Exception:
            redis_status = "disconnected"
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'database': db_status,
            'redis': redis_status,
            'registered_blueprints': registered_blueprints,
            'config_loaded': app.config.get('ENV', 'development'),
            'features_available': {
                'authentication': auth_registered,
                'oauth_platforms': oauth_registered,
                'automation': automation_registered,
                'content_generation': content_registered
            }
        })
    
    # API Documentation
    @app.route('/api/docs')
    def api_docs():
        endpoints = {}
        
        if auth_registered:
            endpoints['authentication'] = {
                'base_url': '/api/auth',
                'description': 'User authentication and profile management',
                'endpoints': [
                    'POST /register - Register new user',
                    'POST /login - User login',
                    'GET /profile - Get user profile',
                    'PUT /profile - Update user profile',
                    'POST /change-password - Change password',
                    'POST /forgot-password - Request password reset',
                    'POST /reset-password - Reset password with token',
                    'POST /verify-token - Verify JWT token',
                    'POST /logout - User logout',
                    'DELETE /delete-account - Delete user account'
                ]
            }
        
        if oauth_registered:
            endpoints['oauth'] = {
                'base_url': '/api/oauth',
                'description': 'Social media platform OAuth management',
                'endpoints': [
                    'GET /platforms - Get supported platforms',
                    'POST /auth-url/<platform> - Generate OAuth URL',
                    'GET /callback/<platform> - OAuth callback (redirect)',
                    'POST /callback/<platform> - OAuth callback (API)',
                    'GET /connected-accounts - Get connected accounts',
                    'DELETE /disconnect/<platform> - Disconnect platform'
                ]
            }
        
        if automation_registered:
            endpoints['automation'] = {
                'base_url': '/api/automation',
                'description': 'AI-powered auto-posting automation',
                'endpoints': [
                    'GET /status - Get automation status',
                    'POST /start - Start automation',
                    'POST /pause - Pause automation',
                    'POST /stop - Stop automation',
                    'GET /settings - Get automation settings',
                    'PUT /settings - Update automation settings',
                    'POST /generate-optimal-times - Generate optimal posting times',
                    'GET /recent-posts - Get recent automated posts',
                    'GET /queue - Get posting queue',
                    'GET /analytics - Get automation analytics'
                ]
            }
        
        if content_registered:
            endpoints['content_generator'] = {
                'base_url': '/api/content-generator',
                'description': 'AI content generation and management',
                'endpoints': [
                    'GET /domains - Get content domains',
                    'GET /platforms - Get supported platforms',
                    'POST /generate - Generate AI content',
                    'POST /generate-variants - Generate content variants',
                    'GET /templates - Get content templates',
                    'GET /history - Get generation history',
                    'GET /usage-stats - Get usage statistics'
                ]
            }
        
        return jsonify({
            'title': 'VelocityPost.ai API Documentation',
            'version': '1.0.0',
            'description': 'AI-powered social media automation platform',
            'base_url': 'http://localhost:5000',
            'authentication': 'Bearer token required for protected endpoints',
            'endpoints': endpoints,
            'registered_blueprints': registered_blueprints
        })
    
    logger.info(f"App creation complete. Registered blueprints: {registered_blueprints}")
    
    return app

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    logger.info("Starting VelocityPost.ai server...")
    logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    logger.info("Server: http://localhost:5000")
    logger.info("Health check: http://localhost:5000/api/health")
    logger.info("API docs: http://localhost:5000/api/docs")
    
    try:
        app.run(
            host='0.0.0.0',
            port=int(os.getenv('PORT', 5000)),
            debug=os.getenv('FLASK_ENV') == 'development'
        )
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)