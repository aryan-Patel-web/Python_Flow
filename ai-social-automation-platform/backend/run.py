"""
Main application runner for development and production
"""
import os
import sys
from app import create_app
from app.models import db, User, Post, Analytics, Subscription
from flask_migrate import upgrade

def create_application():
    """Create and configure the Flask application"""
    app = create_app()
    
    with app.app_context():
        # Create database tables
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Error creating database tables: {str(e)}")
        
        # Create default admin user if it doesn't exist
        try:
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@aisocial.com')
            admin_user = User.query.filter_by(email=admin_email).first()
            
            if not admin_user:
                admin_user = User(
                    email=admin_email,
                    password='admin123',  # This will be hashed by the model
                    name='Admin User',
                    is_active=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print(f"✅ Admin user created: {admin_email}")
            else:
                print(f"✅ Admin user already exists: {admin_email}")
                
        except Exception as e:
            print(f"❌ Error creating admin user: {str(e)}")
    
    return app

def run_development():
    """Run the application in development mode"""
    app = create_application()
    
    print("🚀 Starting AI Social Media Automation Platform...")
    print("📊 Environment: Development")
    print(f"🔗 Access at: http://localhost:{app.config['PORT']}")
    print("📝 Debug mode: ON")
    
    app.run(
        host='0.0.0.0',
        port=app.config['PORT'],
        debug=True,
        use_reloader=True
    )

def run_production():
    """Run the application in production mode with Gunicorn"""
    app = create_application()
    
    print("🚀 Starting AI Social Media Automation Platform (Production)...")
    print("📊 Environment: Production")
    print("📝 Debug mode: OFF")
    
    # Production settings
    import gunicorn.app.base
    
    class StandaloneApplication(gunicorn.app.base.BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()
        
        def load_config(self):
            config = {key: value for key, value in self.options.items()
                     if key in self.cfg.settings and value is not None}
            for key, value in config.items():
                self.cfg.set(key.lower(), value)
        
        def load(self):
            return self.application
    
    options = {
        'bind': f"0.0.0.0:{app.config['PORT']}",
        'workers': 4,
        'worker_class': 'sync',
        'worker_connections': 1000,
        'timeout': 30,
        'keepalive': 2,
        'preload_app': True,
        'max_requests': 1000,
        'max_requests_jitter': 100,
    }
    
    StandaloneApplication(app, options).run()

def setup_database():
    """Setup database with initial data"""
    app = create_application()
    
    with app.app_context():
        print("🗄️ Setting up database...")
        
        # Drop and recreate all tables (use with caution!)
        if '--reset' in sys.argv:
            print("⚠️ Resetting database...")
            db.drop_all()
        
        db.create_all()
        
        # Add sample data for development
        if app.config['ENV'] == 'development':
            print("📊 Adding sample data...")
            # Add sample content domains, subscription plans, etc.
        
        print("✅ Database setup complete!")

def run_tests():
    """Run the test suite"""
    import unittest
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'dev':
            run_development()
        elif command == 'prod':
            run_production()
        elif command == 'setup-db':
            setup_database()
        elif command == 'test':
            success = run_tests()
            sys.exit(0 if success else 1)
        else:
            print("❌ Unknown command. Use: dev, prod, setup-db, or test")
            sys.exit(1)
    else:
        # Default to development mode
        run_development()