"""
Main application runner for development and production
"""
import os
import sys
from datetime import datetime
from app import create_app
from app.utils.database import init_db, get_db, UserModel
from dotenv import load_dotenv

load_dotenv()

def create_application():
    """Create and configure the Flask application"""
    config_name = os.getenv('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    with app.app_context():
        try:
            # Initialize database
            db = init_db(app)
            print("✅ Database connection established")
            
            # Create default admin user if it doesn't exist
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@velocitypost.ai')
            existing_admin = UserModel.get_user_by_email(admin_email)
            
            if not existing_admin:
                from werkzeug.security import generate_password_hash
                admin_password = os.getenv('ADMIN_PASSWORD', 'VelocityAdmin123!')
                
                user_id = UserModel.create_user(
                    email=admin_email,
                    password_hash=generate_password_hash(admin_password),
                    name='Admin User',
                    plan_type='agency'
                )
                print(f"✅ Admin user created: {admin_email}")
            else:
                print(f"✅ Admin user already exists: {admin_email}")
                
        except Exception as e:
            print(f"⚠️ Database setup warning: {str(e)}")
    
    return app

def run_development():
    """Run the application in development mode"""
    app = create_application()
    
    port = int(os.getenv('PORT', 5000))
    
    print("🚀 Starting VelocityPost.ai Development Server...")
    print(f"📊 Environment: Development")
    print(f"🔗 Access at: http://localhost:{port}")
    print(f"🏥 Health check: http://localhost:{port}/api/health")
    print("📝 Debug mode: ON")
    print("💡 Auto-reload: ON")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        use_reloader=True
    )

def run_production():
    """Run the application in production mode with Gunicorn"""
    app = create_application()
    
    print("🚀 Starting VelocityPost.ai Production Server...")
    print("📊 Environment: Production")
    print("📝 Debug mode: OFF")
    
    # Import Gunicorn
    try:
        import gunicorn.app.base
    except ImportError:
        print("❌ Gunicorn not installed. Install with: pip install gunicorn")
        sys.exit(1)
    
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
        'bind': f"0.0.0.0:{os.getenv('PORT', 5000)}",
        'workers': int(os.getenv('WORKERS', 4)),
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
        
        # Reset database if requested
        if '--reset' in sys.argv:
            print("⚠️ Resetting database...")
            try:
                from app.utils.database import get_db
                db = get_db()
                
                # Drop collections
                collections = ['users', 'social_accounts', 'posts', 'generated_content', 'automation_settings']
                for collection_name in collections:
                    db[collection_name].drop()
                    print(f"✅ Dropped collection: {collection_name}")
                
            except Exception as e:
                print(f"⚠️ Database reset warning: {e}")
        
        # Initialize database
        init_db(app)
        print("✅ Database setup complete!")

def run_tests():
    """Run the test suite"""
    try:
        import unittest
        
        # Discover and run tests
        loader = unittest.TestLoader()
        start_dir = 'tests'
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    except ImportError:
        print("❌ unittest not available")
        return False
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return
    
    if os.path.exists('.env.example'):
        import shutil
        shutil.copy('.env.example', '.env')
        print("✅ .env file created from template")
        print("⚠️ Please edit .env file with your API keys")
    else:
        print("❌ .env.example not found")

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask', 'flask-cors', 'flask-jwt-extended', 
        'pymongo', 'redis', 'celery', 'python-dotenv',
        'werkzeug', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n🚨 Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies satisfied")
    return True

def show_help():
    """Show help information"""
    help_text = """
🚀 VelocityPost.ai - Application Runner

USAGE:
    python run.py [COMMAND]

COMMANDS:
    dev                 Start development server (default)
    prod                Start production server with Gunicorn
    setup-db            Setup database with initial data
    test                Run test suite
    check-deps          Check if dependencies are installed
    create-env          Create .env file from template
    help                Show this help message

EXAMPLES:
    python run.py                    # Start development server
    python run.py dev                # Start development server
    python run.py prod               # Start production server
    python run.py setup-db           # Setup database
    python run.py setup-db --reset   # Reset and setup database
    python run.py test               # Run tests
    python run.py check-deps         # Check dependencies
    python run.py create-env         # Create .env file

QUICK SETUP:
    1. python run.py create-env      # Create environment file
    2. python run.py check-deps      # Check dependencies
    3. python run.py setup-db        # Setup database
    4. python run.py dev             # Start server

For more information, visit: https://docs.velocitypost.ai
"""
    print(help_text)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'dev':
            run_development()
        elif command == 'prod':
            run_production()
        elif command == 'setup-db':
            setup_database()
        elif command == 'test':
            success = run_tests()
            sys.exit(0 if success else 1)
        elif command == 'check-deps':
            check_dependencies()
        elif command == 'create-env':
            create_env_file()
        elif command == 'help':
            show_help()
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python run.py help' for available commands")
            sys.exit(1)
    else:
        # Default to development mode
        print("Starting in development mode...")
        print("Use 'python run.py help' for more options")
        run_development()