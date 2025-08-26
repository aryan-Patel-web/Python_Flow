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
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
print(f"🔍 Current directory: {current_dir}")
print(f"🔍 Python path: {sys.path[:3]}...")  # Show first 3 paths

# Load environment variables
load_dotenv()
print("🔍 Environment variables loaded")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern"""
    print("🔍 Creating Flask app...")
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads/temp')
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['MONGODB_URI'] = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/velocitypost')
    print("🔍 Flask app configuration set")
    
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
    print("🔍 CORS configured")
    
    # Initialize database
    print("🔍 Attempting to initialize database...")
    try:
        from config.database import db_instance
        db_instance.init_app(app)
        print("✅ Database initialized successfully")
    except ImportError as e:
        print(f"⚠️ Database import failed: {str(e)}")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {str(e)}")
        # Continue without database for development
    
    # Register blueprints
    print("🔍 Starting blueprint registration...")
    registered_blueprints = register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create upload directories
    upload_dir = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    print(f"🔍 Upload directory created: {upload_dir}")
    
    print(f"✅ App creation complete. Registered blueprints: {registered_blueprints}")
    
    return app

def register_blueprints(app):
    """Register all application blueprints"""
    registered_blueprints = []
    
    # Check if routes directory exists
    routes_dir = os.path.join(os.path.dirname(__file__), 'routes')
    print(f"🔍 Checking routes directory: {routes_dir}")
    print(f"🔍 Routes directory exists: {os.path.exists(routes_dir)}")
    
    if os.path.exists(routes_dir):
        files_in_routes = os.listdir(routes_dir)
        print(f"🔍 Files in routes directory: {files_in_routes}")
    
    # Try to register auth blueprint
    print("🔍 Attempting to register auth blueprint...")
    try:
        # Try different import patterns
        import_attempts = [
            'app.routes.auth',
            'routes.auth', 
            '.routes.auth'
        ]
        
        auth_bp = None
        for import_path in import_attempts:
            try:
                print(f"🔍 Trying import: {import_path}")
                if import_path.startswith('.'):
                    from .routes.auth import auth_bp
                else:
                    module = __import__(import_path, fromlist=['auth_bp'])
                    auth_bp = getattr(module, 'auth_bp')
                print(f"✅ Successfully imported from: {import_path}")
                break
            except ImportError as e:
                print(f"❌ Import failed for {import_path}: {e}")
                continue
            except AttributeError as e:
                print(f"❌ Blueprint not found in {import_path}: {e}")
                continue
        
        if auth_bp:
            app.register_blueprint(auth_bp, url_prefix='/api/auth')
            registered_blueprints.append('auth_bp')
            print("✅ Auth blueprint registered successfully")
        else:
            print("❌ Could not import auth blueprint from any path")
            
    except Exception as e:
        print(f"❌ Unexpected error with auth blueprint: {e}")
    
    # Try to register content generator blueprint
    print("🔍 Attempting to register content generator blueprint...")
    try:
        import_attempts = [
            'app.routes.content_generator',
            'routes.content_generator', 
            '.routes.content_generator'
        ]
        
        content_generator_bp = None
        for import_path in import_attempts:
            try:
                print(f"🔍 Trying import: {import_path}")
                if import_path.startswith('.'):
                    from .routes.content_generator import content_generator_bp
                else:
                    module = __import__(import_path, fromlist=['content_generator_bp'])
                    content_generator_bp = getattr(module, 'content_generator_bp')
                print(f"✅ Successfully imported from: {import_path}")
                break
            except ImportError as e:
                print(f"❌ Import failed for {import_path}: {e}")
                continue
            except AttributeError as e:
                print(f"❌ Blueprint not found in {import_path}: {e}")
                continue
        
        if content_generator_bp:
            app.register_blueprint(content_generator_bp, url_prefix='/api/content-generator')
            registered_blueprints.append('content_generator_bp')
            print("✅ Content generator blueprint registered successfully")
        else:
            print("❌ Could not import content generator blueprint from any path")
            
    except Exception as e:
        print(f"❌ Unexpected error with content generator blueprint: {e}")
    
    # Future blueprints (create these later)
    future_blueprints = [
        ('app.routes.oauth', 'oauth_bp', '/api/oauth'),
        ('app.routes.platforms', 'platforms_bp', '/api/platforms'),
        ('app.routes.posts', 'posts_bp', '/api/posts'),
        ('app.routes.analytics', 'analytics_bp', '/api/analytics'),
        ('app.routes.billing', 'billing_bp', '/api/billing'),
        ('app.routes.automation', 'automation_bp', '/api/automation'),
    ]
    
    print("🔍 Checking for future blueprints...")
    for module_path, blueprint_name, url_prefix in future_blueprints:
        try:
            module = __import__(module_path, fromlist=[blueprint_name])
            blueprint = getattr(module, blueprint_name)
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            registered_blueprints.append(blueprint_name)
            print(f"✅ Registered {blueprint_name}")
        except ImportError:
            print(f"ℹ️ {blueprint_name} not available yet (will be created later)")
        except Exception as e:
            print(f"⚠️ Error with {blueprint_name}: {e}")
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        print("🔍 Health check endpoint called")
        try:
            # Test database connection
            db_status = 'unknown'
            try:
                from config.database import db_instance
                db_health = db_instance.health_check()
                db_status = db_health.get('status', 'unknown')
                print(f"🔍 Database status: {db_status}")
            except Exception as e:
                db_status = 'not-configured'
                print(f"🔍 Database health check failed: {e}")
            
            health_data = {
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
            }
            print(f"🔍 Health check response: {health_data}")
            return jsonify(health_data)
        except Exception as e:
            print(f"❌ Health check failed: {str(e)}")
            return jsonify({
                'status': 'partial',
                'timestamp': datetime.utcnow().isoformat(),
                'error': 'Some services unavailable',
                'registered_blueprints': registered_blueprints
            }), 200
    
    # Root endpoint
    @app.route('/')
    def root():
        print("🔍 Root endpoint called")
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
        print("🔍 API docs endpoint called")
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
                    'GET /api/content-generator/usage-stats': 'Get usage statistics (Protected)',
                    'GET /api/content-generator/templates': 'Get content templates',
                    'GET /api/content-generator/history': 'Get generation history (Protected)'
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
    
    print(f"🔍 Blueprint registration complete. Total registered: {len(registered_blueprints)}")
    return registered_blueprints

def register_error_handlers(app):
    """Register error handlers"""
    print("🔍 Registering error handlers...")
    
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
    
    print("✅ Error handlers registered")

# Create the Flask app
print("🔍 Starting app creation...")
app = create_app()
print("✅ App created successfully")

# Add request/response logging middleware
@app.before_request
def log_request_info():
    """Log request information"""
    if app.debug:
        print(f"🔍 Request: {request.method} {request.url}")

@app.after_request
def log_response_info(response):
    """Log response information and add headers"""
    if app.debug:
        print(f"🔍 Response: {response.status_code}")
    
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