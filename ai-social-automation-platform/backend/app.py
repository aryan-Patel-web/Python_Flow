#!/usr/bin/env python3
"""
VelocityPost.ai - Main Flask Application
AI-Powered Social Media Automation Platform
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads/temp')
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['MONGODB_URI'] = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/velocitypost')
    
    # CORS Configuration
    allowed_origins = [
        'http://localhost:3000',
        'http://127.0.0.1:3000', 
        'http://localhost:5173',  # Vite dev server
        'http://127.0.0.1:5173'
    ]
    
    if os.getenv('FRONTEND_URL'):
        allowed_origins.append(os.getenv('FRONTEND_URL'))
    
    CORS(app, origins=allowed_origins, supports_credentials=True)
    
    # Initialize database
    try:
        from config.database import db_instance
        db_instance.init_app(app)
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization warning: {str(e)}")
        # Continue without database for development
    
    # Register blueprints
    registered_blueprints = register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create upload directories
    upload_dir = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    
    logger.info(f"✅ Registered blueprints: {registered_blueprints}")
    
    return app

def register_blueprints(app):
    """Register all application blueprints"""
    registered_blueprints = []
    
    # Try to register auth blueprint
    try:
        from routes.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        registered_blueprints.append('auth_bp')
        logger.info("✅ Registered auth blueprint")
    except ImportError as e:
        logger.warning(f"Could not import auth blueprint: {e}")
    except Exception as e:
        logger.error(f"Error registering auth blueprint: {e}")
    
    # Try to register content generator blueprint
    try:
        from routes.content_generator import content_generator_bp
        app.register_blueprint(content_generator_bp, url_prefix='/api/content-generator')
        registered_blueprints.append('content_generator_bp')
        logger.info("✅ Registered content generator blueprint")
    except ImportError as e:
        logger.warning(f"Could not import content generator blueprint: {e}")
    except Exception as e:
        logger.error(f"Error registering content generator blueprint: {e}")
    
    # Future blueprints (create these later)
    future_blueprints = [
        ('routes.oauth', 'oauth_bp', '/api/oauth'),
        ('routes.platforms', 'platforms_bp', '/api/platforms'),
        ('routes.posts', 'posts_bp', '/api/posts'),
        ('routes.analytics', 'analytics_bp', '/api/analytics'),
        ('routes.billing', 'billing_bp', '/api/billing'),
        ('routes.automation', 'automation_bp', '/api/automation'),
    ]
    
    for module_path, blueprint_name, url_prefix in future_blueprints:
        try:
            module = __import__(module_path, fromlist=[blueprint_name])
            blueprint = getattr(module, blueprint_name)
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            registered_blueprints.append(blueprint_name)
            logger.info(f"✅ Registered {blueprint_name}")
        except ImportError:
            logger.info(f"{blueprint_name} not available yet (will be created later)")
        except Exception as e:
            logger.warning(f"Error with {blueprint_name}: {e}")
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        try:
            # Test database connection
            db_status = 'unknown'
            try:
                from config.database import db_instance
                db_health = db_instance.health_check()
                db_status = db_health.get('status', 'unknown')
            except Exception as e:
                db_status = 'not-configured'
                logger.debug(f"Database health check failed: {e}")
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'database': db_status,
                'redis': 'not-configured',
                'registered_blueprints': registered_blueprints,
                'config_loaded': os.getenv('FLASK_ENV', 'development'),
                'features': [
                    'AI Content Generation',
                    'File Processing', 
                    'User Authentication',
                    'Multi-Platform Support'
                ]
            })
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'partial',
                'timestamp': datetime.utcnow().isoformat(),
                'error': 'Some services unavailable',
                'registered_blueprints': registered_blueprints
            }), 200
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'message': 'VelocityPost.ai API Server',
            'version': '1.0.0',
            'status': 'operational',
            'environment': os.getenv('FLASK_ENV', 'development'),
            'docs': '/api/docs',
            'health': '/api/health'
        })
    
    # API documentation endpoint
    @app.route('/api/docs')
    def api_docs():
        """API documentation"""
        return jsonify({
            'api_version': '1.0.0',
            'base_url': request.host_url + 'api',
            'authentication': 'Bearer token required for protected endpoints',
            'endpoints': {
                'system': {
                    'GET /': 'API information',
                    'GET /api/health': 'Health check',
                    'GET /api/docs': 'API documentation'
                },
                'authentication': {
                    'POST /api/auth/register': 'Register new user',
                    'POST /api/auth/login': 'User login',
                    'GET /api/auth/profile': 'Get user profile (Protected)',
                    'PUT /api/auth/profile': 'Update user profile (Protected)',
                    'POST /api/auth/change-password': 'Change password (Protected)',
                    'POST /api/auth/forgot-password': 'Request password reset',
                    'POST /api/auth/reset-password': 'Reset password with token',
                    'POST /api/auth/verify-token': 'Verify token validity (Protected)',
                    'POST /api/auth/logout': 'Logout user (Protected)',
                    'DELETE /api/auth/delete-account': 'Delete account (Protected)'
                },
                'content_generation': {
                    'GET /api/content-generator/domains': 'Get content domains',
                    'GET /api/content-generator/platforms': 'Get supported platforms',
                    'POST /api/content-generator/generate': 'Generate AI content (Protected)',
                    'POST /api/content-generator/generate-variants': 'Generate content variants (Pro+)',
                    'POST /api/content-generator/upload-file': 'Upload file for processing (Protected)',
                    'GET /api/content-generator/files': 'Get user files (Protected)',
                    'DELETE /api/content-generator/files/<id>': 'Delete file (Protected)',
                    'GET /api/content-generator/generations': 'Get generation history (Protected)',
                    'GET /api/content-generator/usage-stats': 'Get usage statistics (Protected)',
                    'GET /api/content-generator/templates': 'Get content templates'
                }
            },
            'request_format': {
                'authentication_header': 'Authorization: Bearer <token>',
                'content_type': 'application/json'
            },
            'response_format': {
                'success': 'true/false',
                'message': 'Human readable message',
                'data': 'Response data (optional)',
                'timestamp': 'ISO timestamp',
                'status_code': 'HTTP status code'
            },
            'error_codes': {
                '400': 'Bad Request - Invalid input',
                '401': 'Unauthorized - Authentication required',
                '403': 'Forbidden - Insufficient permissions',
                '404': 'Not Found - Resource not found',
                '422': 'Validation Error - Input validation failed',
                '429': 'Rate Limited - Too many requests',
                '500': 'Server Error - Internal error'
            }
        })
    
    return registered_blueprints

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': 'Bad request',
            'error': 'The request was invalid or malformed',
            'status_code': 400,
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'message': 'Unauthorized',
            'error': 'Authentication required',
            'status_code': 401,
            'timestamp': datetime.utcnow().isoformat()
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'message': 'Forbidden',
            'error': 'Insufficient permissions',
            'status_code': 403,
            'timestamp': datetime.utcnow().isoformat()
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Not found',
            'error': 'The requested resource was not found',
            'status_code': 404,
            'timestamp': datetime.utcnow().isoformat()
        }), 404
    
    @app.errorhandler(413)
    def payload_too_large(error):
        return jsonify({
            'success': False,
            'message': 'File too large',
            'error': 'Maximum file size exceeded (50MB)',
            'status_code': 413,
            'timestamp': datetime.utcnow().isoformat()
        }), 413
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'message': 'Validation error',
            'error': 'Input validation failed',
            'status_code': 422,
            'timestamp': datetime.utcnow().isoformat()
        }), 422
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'success': False,
            'message': 'Rate limit exceeded',
            'error': 'Too many requests - please try again later',
            'status_code': 429,
            'timestamp': datetime.utcnow().isoformat()
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': 'Something went wrong on our end',
            'status_code': 500,
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled exception: {str(error)}")
        
        # Don't reveal internal errors in production
        error_message = str(error) if app.debug else 'An unexpected error occurred'
        
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred',
            'error': error_message,
            'status_code': 500,
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Create the Flask app
app = create_app()

# Add request/response logging middleware
@app.before_request
def log_request_info():
    """Log request information"""
    if app.debug:
        logger.debug(f"Request: {request.method} {request.url}")

@app.after_request
def log_response_info(response):
    """Log response information and add headers"""
    if app.debug:
        logger.debug(f"Response: {response.status_code}")
    
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response

if __name__ == '__main__':
    # Development server
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print("🚀 Starting VelocityPost.ai server...")
    print(f"📊 Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"🔗 Server: http://localhost:{port}")
    print(f"📝 Debug mode: {debug}")
    print(f"🏥 Health check: http://localhost:{port}/api/health")
    print(f"📚 API docs: http://localhost:{port}/api/docs")
    print("-" * 50)
    
    logger.info(f"Starting VelocityPost.ai API server on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )