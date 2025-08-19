from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
import os
import logging
from datetime import datetime

# Import configuration
from config import config

# Import routes
from app.routes.auth import auth_bp
from app.routes.credentials import credentials_bp
from app.routes.domains import domains_bp
from app.routes.content import content_bp
from app.routes.automation import automation_bp
from app.routes.analytics import analytics_bp
from app.routes.billing import billing_bp

# Import error handlers
from app.utils.error_handlers import register_error_handlers

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    jwt = JWTManager(app)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO if not app.config['DEBUG'] else logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # MongoDB connection
    try:
        # Try Atlas first, then local
        mongo_uri = app.config.get('MONGO_ATLAS_URI') or app.config['MONGO_URI']
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        
        # Get database name from URI or use default
        db_name = mongo_uri.split('/')[-1].split('?')[0]
        if not db_name or db_name == 'localhost:27017':
            db_name = 'ai_social_automation'
        
        db = client[db_name]
        app.db = db
        
        print(f"✅ Connected to MongoDB: {mongo_uri}")
        print(f"📁 Database: {db_name}")
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("💡 Make sure MongoDB is running or check your Atlas connection string")
        return None
    
    # Create storage directories
    storage_dirs = [
        'storage/generated_content',
        'storage/images',
        'storage/videos',
        'storage/temp'
    ]
    
    for directory in storage_dirs:
        os.makedirs(directory, exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(credentials_bp, url_prefix='/api/credentials')
    app.register_blueprint(domains_bp, url_prefix='/api/domains')
    app.register_blueprint(content_bp, url_prefix='/api/content')
    app.register_blueprint(automation_bp, url_prefix='/api/automation')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(billing_bp, url_prefix='/api/billing')
    
    # Register error handlers
    register_error_handlers(app)
    
    # JWT token handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization token required'}), 401
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'AI Social Media Automation Platform is running',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'features': [
                'AI Content Generation (Mistral + Groq)',
                'Multi-Platform Auto-Posting',
                'Credential Management',
                'Analytics & Engagement Tracking',
                'Subscription Management'
            ]
        })
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'message': 'AI Social Media Automation Platform API',
            'description': 'Users enter social media credentials → AI generates and posts content automatically',
            'version': '1.0.0',
            'documentation': '/api/docs',
            'health_check': '/api/health',
            'endpoints': {
                'authentication': '/api/auth',
                'credentials': '/api/credentials',
                'domains': '/api/domains',
                'content': '/api/content',
                'automation': '/api/automation',
                'analytics': '/api/analytics',
                'billing': '/api/billing'
            },
            'supported_platforms': list(app.config['SUPPORTED_PLATFORMS'].keys()),
            'content_domains': list(app.config['CONTENT_DOMAINS'].keys())
        })
    
    # API documentation endpoint
    @app.route('/api/docs')
    def api_docs():
        return jsonify({
            'title': 'AI Social Media Automation Platform API',
            'version': '1.0.0',
            'description': 'Complete API for automated social media management using AI',
            'base_url': request.host_url + 'api',
            'authentication': 'JWT Bearer Token',
            'endpoints': {
                'auth': {
                    'POST /auth/register': 'Register new user',
                    'POST /auth/login': 'Login user',
                    'GET /auth/profile': 'Get user profile',
                    'PUT /auth/profile': 'Update user profile'
                },
                'credentials': {
                    'POST /credentials': 'Save platform credentials',
                    'GET /credentials': 'Get all user credentials',
                    'GET /credentials/{platform}': 'Get specific platform credentials',
                    'PUT /credentials/{platform}': 'Update platform credentials',
                    'DELETE /credentials/{platform}': 'Delete platform credentials',
                    'POST /credentials/{platform}/test': 'Test platform connection'
                },
                'domains': {
                    'GET /domains': 'Get available content domains',
                    'POST /domains/select': 'Select user domains',
                    'GET /domains/user': 'Get user selected domains',
                    'PUT /domains/settings': 'Update domain settings'
                },
                'content': {
                    'POST /content/generate': 'Generate content for domains',
                    'GET /content/library': 'Get user content library',
                    'GET /content/{id}': 'Get specific content',
                    'PUT /content/{id}': 'Update content',
                    'DELETE /content/{id}': 'Delete content'
                },
                'automation': {
                    'POST /automation/start': 'Start automation for user',
                    'POST /automation/stop': 'Stop automation for user',
                    'GET /automation/status': 'Get automation status',
                    'POST /automation/schedule': 'Schedule posts',
                    'GET /automation/logs': 'Get automation logs'
                },
                'analytics': {
                    'GET /analytics/overview': 'Get analytics overview',
                    'GET /analytics/engagement': 'Get engagement metrics',
                    'GET /analytics/growth': 'Get growth statistics',
                    'GET /analytics/platform/{platform}': 'Get platform-specific analytics'
                },
                'billing': {
                    'GET /billing/plans': 'Get subscription plans',
                    'POST /billing/subscribe': 'Subscribe to plan',
                    'GET /billing/subscription': 'Get current subscription',
                    'GET /billing/usage': 'Get usage statistics'
                }
            }
        })
    
    # Platform status endpoint
    @app.route('/api/platforms')
    def platforms_info():
        return jsonify({
            'supported_platforms': app.config['SUPPORTED_PLATFORMS'],
            'content_domains': app.config['CONTENT_DOMAINS'],
            'subscription_plans': app.config['SUBSCRIPTION_PLANS']
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    if app:
        print("🚀 Starting AI Social Media Automation Platform...")
        print("🤖 Features: AI Content Generation + Auto-Posting + Analytics")
        print("🌐 Frontend: http://localhost:3000")
        print("⚙️ Backend: http://localhost:5000")
        print("📚 API Docs: http://localhost:5000/api/docs")
        print("💊 Health Check: http://localhost:5000/api/health")
        
        # Run the application
        app.run(
            debug=app.config['DEBUG'],
            host='0.0.0.0',
            port=int(os.getenv('PORT', 5000))
        )
    else:
        print("❌ Failed to start application - Check MongoDB connection")