#!/usr/bin/env python3
"""
VelocityPost.ai - Main Flask Application
AI-Powered Social Media Automation Platform
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import application modules
from app.utils.database import init_db
from app.utils.logger import setup_logger
from app.utils.error_handlers import register_error_handlers

# Import route blueprints
from app.routes.auth import auth_bp
from app.routes.oauth import oauth_bp
from app.routes.platforms import platforms_bp
from app.routes.content import content_bp
from app.routes.automation import automation_bp
from app.routes.analytics import analytics_bp
from app.routes.billing import billing_bp
from app.routes.admin import admin_bp

# 🔥 NEW: Auto-Posting Route Blueprints
from app.routes.auto_posting import auto_posting_bp
from app.routes.content_generator import content_generator_bp
from app.routes.scheduler import scheduler_bp

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # MongoDB Configuration
    app.config['MONGODB_URI'] = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/velocitypost')
    app.config['MONGODB_ATLAS_URI'] = os.getenv('MONGODB_ATLAS_URI')
    
    # Redis Configuration for Celery
    app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # AI Service Configuration
    app.config['MISTRAL_API_KEY'] = os.getenv('MISTRAL_API_KEY')
    app.config['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    
    # Payment Configuration
    app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY')
    app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv('STRIPE_PUBLISHABLE_KEY')
    app.config['RAZORPAY_KEY_ID'] = os.getenv('RAZORPAY_KEY_ID')
    app.config['RAZORPAY_KEY_SECRET'] = os.getenv('RAZORPAY_KEY_SECRET')
    
    # 🔥 NEW: Social Media Platform API Keys
    app.config['FACEBOOK_APP_ID'] = os.getenv('FACEBOOK_APP_ID')
    app.config['FACEBOOK_APP_SECRET'] = os.getenv('FACEBOOK_APP_SECRET')
    app.config['INSTAGRAM_APP_ID'] = os.getenv('INSTAGRAM_APP_ID')
    app.config['INSTAGRAM_APP_SECRET'] = os.getenv('INSTAGRAM_APP_SECRET')
    app.config['TWITTER_API_KEY'] = os.getenv('TWITTER_API_KEY')
    app.config['TWITTER_API_SECRET'] = os.getenv('TWITTER_API_SECRET')
    app.config['LINKEDIN_CLIENT_ID'] = os.getenv('LINKEDIN_CLIENT_ID')
    app.config['LINKEDIN_CLIENT_SECRET'] = os.getenv('LINKEDIN_CLIENT_SECRET')
    app.config['YOUTUBE_CLIENT_ID'] = os.getenv('YOUTUBE_CLIENT_ID')
    app.config['YOUTUBE_CLIENT_SECRET'] = os.getenv('YOUTUBE_CLIENT_SECRET')
    app.config['TIKTOK_CLIENT_KEY'] = os.getenv('TIKTOK_CLIENT_KEY')
    app.config['TIKTOK_CLIENT_SECRET'] = os.getenv('TIKTOK_CLIENT_SECRET')
    app.config['PINTEREST_APP_ID'] = os.getenv('PINTEREST_APP_ID')
    app.config['PINTEREST_APP_SECRET'] = os.getenv('PINTEREST_APP_SECRET')
    
    # Extensions initialization
    CORS(app, origins=['http://localhost:3000', 'http://localhost:5173'])
    jwt = JWTManager(app)
    
    # Rate limiter setup
    redis_client = redis.Redis.from_url(app.config['REDIS_URL'])
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        storage_uri=app.config['REDIS_URL'],
        default_limits=["1000 per day", "100 per hour"]
    )
    
    # Database initialization
    init_db(app)
    
    # Setup logging
    setup_logger(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(oauth_bp, url_prefix='/api/oauth')
    app.register_blueprint(platforms_bp, url_prefix='/api/platforms')
    app.register_blueprint(content_bp, url_prefix='/api/content')
    app.register_blueprint(automation_bp, url_prefix='/api/automation')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(billing_bp, url_prefix='/api/billing')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # 🔥 NEW: Auto-Posting Blueprints
    app.register_blueprint(auto_posting_bp, url_prefix='/api/auto-posting')
    app.register_blueprint(content_generator_bp, url_prefix='/api/content-generator')
    app.register_blueprint(scheduler_bp, url_prefix='/api/scheduler')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'services': {
                'database': 'connected',
                'redis': 'connected',
                'ai_services': 'operational'
            }
        })
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'message': 'VelocityPost.ai API Server',
            'version': '1.0.0',
            'status': 'operational',
            'documentation': '/api/docs'
        })
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token has expired',
            'message': 'Please refresh your token'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid token',
            'message': 'Please provide a valid token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Token required',
            'message': 'Please provide an authorization token'
        }), 401
    
    return app

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    # Development server
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    app.logger.info(f'Starting VelocityPost.ai server on port {port}')
    app.run(host='0.0.0.0', port=port, debug=debug)