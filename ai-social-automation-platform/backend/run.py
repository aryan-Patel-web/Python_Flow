"""
Main application runner for development and production
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Print initial debug info
print("🔍 Starting run.py...")
print(f"🔍 Current working directory: {os.getcwd()}")
print(f"🔍 Script location: {os.path.abspath(__file__)}")

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
print(f"🔍 Added to Python path: {current_dir}")

# Load environment variables
load_dotenv()
print("🔍 Environment variables loaded")

# Try to import app
print("🔍 Attempting to import app...")
try:
    from app import create_app
    print("✅ Successfully imported create_app from app.py")
except ImportError as e:
    print(f"❌ Failed to import create_app: {e}")
    # Try alternative import
    try:
        import app as app_module
        create_app = app_module.create_app
        print("✅ Successfully imported app module")
    except ImportError as e2:
        print(f"❌ Failed to import app module: {e2}")
        sys.exit(1)

def create_application():
    """Create and configure the Flask application"""
    print("🔍 Creating Flask application...")
    
    config_name = os.getenv('FLASK_ENV', 'development')
    print(f"🔍 Config name: {config_name}")
    
    try:
        app = create_app()
        print("✅ Flask app created successfully")
        
        with app.app_context():
            print("🔍 Inside app context...")
            try:
                # Try to initialize database if available
                print("🔍 Attempting database initialization...")
                
                # Check if we can import database utilities
                try:
                    from config.database import get_collection
                    print("✅ Database config available")
                    
                    # Test database connection
                    users_collection = get_collection('users')
                    if users_collection:
                        user_count = users_collection.count_documents({})
                        print(f"✅ Database connected. User count: {user_count}")
                    else:
                        print("⚠️ Database collection unavailable")
                        
                except ImportError as e:
                    print(f"⚠️ Database config not available: {e}")
                except Exception as e:
                    print(f"⚠️ Database connection issue: {e}")
                
                # Try to create default admin user
                try:
                    admin_email = os.getenv('ADMIN_EMAIL', 'admin@velocitypost.ai')
                    print(f"🔍 Checking for admin user: {admin_email}")
                    
                    # This is optional - only if database is available
                    from config.database import get_collection
                    users_collection = get_collection('users')
                    
                    if users_collection:
                        existing_admin = users_collection.find_one({'email': admin_email})
                        
                        if not existing_admin:
                            from werkzeug.security import generate_password_hash
                            admin_password = os.getenv('ADMIN_PASSWORD', 'VelocityAdmin123!')
                            
                            admin_doc = {
                                'email': admin_email,
                                'password': generate_password_hash(admin_password),
                                'name': 'Admin User',
                                'plan_type': 'agency',
                                'is_active': True,
                                'created_at': datetime.utcnow(),
                                'updated_at': datetime.utcnow()
                            }
                            
                            result = users_collection.insert_one(admin_doc)
                            print(f"✅ Admin user created: {admin_email} (ID: {result.inserted_id})")
                        else:
                            print(f"✅ Admin user already exists: {admin_email}")
                    else:
                        print("⚠️ Cannot create admin user - database unavailable")
                        
                except Exception as e:
                    print(f"⚠️ Admin user setup failed: {str(e)}")
                    
            except Exception as e:
                print(f"⚠️ App context setup warning: {str(e)}")
        
        return app
        
    except Exception as e:
        print(f"❌ Failed to create Flask app: {e}")
        raise

def run_development():
    """Run the application in development mode"""
    print("🔍 Starting development server...")
    
    try:
        app = create_application()
        print("✅ Application created for development")
        
        port = int(os.getenv('PORT', 5000))
        
        print("\n" + "="*50)
        print("🚀 VelocityPost.ai Development Server Starting...")
        print(f"📊 Environment: Development")
        print(f"🔗 Access at: http://localhost:{port}")
        print(f"🏥 Health check: http://localhost:{port}/api/health")
        print(f"📚 API docs: http://localhost:{port}/api/docs")
        print(f"📝 Debug mode: ON")
        print(f"💡 Auto-reload: ON")
        print("="*50 + "\n")
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True,
            use_reloader=True
        )
        
    except Exception as e:
        print(f"❌ Development server failed to start: {e}")
        sys.exit(1)

def run_production():
    """Run the application in production mode with Gunicorn"""
    print("🔍 Starting production server...")
    
    try:
        app = create_application()
        print("✅ Application created for production")
        
        print("\n" + "="*50)
        print("🚀 VelocityPost.ai Production Server Starting...")
        print("📊 Environment: Production")
        print("📝 Debug mode: OFF")
        print("="*50 + "\n")
        
        # Import Gunicorn
        try:
            import gunicorn.app.base
            print("✅ Gunicorn available")
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
        
        print(f"🔍 Gunicorn options: {options}")
        StandaloneApplication(app, options).run()
        
    except Exception as e:
        print(f"❌ Production server failed to start: {e}")
        sys.exit(1)

def setup_database():
    """Setup database with initial data"""
    print("🔍 Starting database setup...")
    
    try:
        app = create_application()
        print("✅ Application created for database setup")
        
        with app.app_context():
            print("🗄️ Setting up database...")
            
            # Reset database if requested
            if '--reset' in sys.argv:
                print("⚠️ Resetting database...")
                try:
                    from config.database import get_collection
                    
                    # Drop collections
                    collections = ['users', 'social_accounts', 'posts', 'content_generations', 'automation_settings']
                    for collection_name in collections:
                        collection = get_collection(collection_name)
                        if collection:
                            collection.drop()
                            print(f"✅ Dropped collection: {collection_name}")
                        else:
                            print(f"⚠️ Collection not available: {collection_name}")
                    
                except Exception as e:
                    print(f"⚠️ Database reset warning: {e}")
            
            print("✅ Database setup complete!")
            
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)

def run_tests():
    """Run the test suite"""
    print("🔍 Starting test suite...")
    
    try:
        import unittest
        print("✅ unittest module available")
        
        # Check if tests directory exists
        test_dir = os.path.join(os.path.dirname(__file__), 'tests')
        print(f"🔍 Looking for tests in: {test_dir}")
        
        if not os.path.exists(test_dir):
            print(f"⚠️ Tests directory not found: {test_dir}")
            print("Creating basic test structure...")
            os.makedirs(test_dir, exist_ok=True)
            
            # Create a basic test file
            basic_test = '''
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class BasicTest(unittest.TestCase):
    def test_imports(self):
        """Test that we can import the main app"""
        try:
            from app import create_app
            app = create_app()
            self.assertTrue(app is not None)
            print("✅ App import test passed")
        except Exception as e:
            self.fail(f"App import failed: {e}")

if __name__ == '__main__':
    unittest.main()
'''
            with open(os.path.join(test_dir, 'test_basic.py'), 'w') as f:
                f.write(basic_test)
            print("✅ Created basic test file")
        
        # Discover and run tests
        loader = unittest.TestLoader()
        suite = loader.discover(test_dir, pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print("✅ All tests passed!")
            return True
        else:
            print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
            return False
            
    except ImportError:
        print("❌ unittest not available")
        return False
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    print("🔍 Creating .env file...")
    
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return
    
    if os.path.exists('.env.example'):
        import shutil
        shutil.copy('.env.example', '.env')
        print("✅ .env file created from template")
        print("⚠️ Please edit .env file with your API keys")
    else:
        print("⚠️ .env.example not found, creating basic .env file...")
        
        # Create a basic .env file
        basic_env_content = """# VelocityPost.ai Environment Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-key-change-in-production
PORT=5000

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/velocitypost

# Admin User (Optional)
ADMIN_EMAIL=admin@velocitypost.ai
ADMIN_PASSWORD=VelocityAdmin123!

# File Upload
UPLOAD_FOLDER=uploads/temp

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# Redis (Optional - for caching and queues)
REDIS_URL=redis://localhost:6379/0

# API Keys (Add your API keys here)
# OPENAI_API_KEY=your_openai_key_here
# GOOGLE_API_KEY=your_google_key_here
"""
        
        with open('.env', 'w') as f:
            f.write(basic_env_content)
        print("✅ Basic .env file created")
        print("⚠️ Please edit .env file with your actual API keys and configuration")

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('pymongo', 'PyMongo'),
        ('python-dotenv', 'python-dotenv'),
        ('werkzeug', 'Werkzeug'),
        ('requests', 'requests'),
        ('jwt', 'PyJWT')
    ]
    
    missing_packages = []
    available_packages = []
    
    for package_import, package_name in required_packages:
        try:
            __import__(package_import.replace('-', '_'))
            available_packages.append(package_name)
            print(f"✅ {package_name}")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name}")
    
    # Check optional packages
    optional_packages = [
        ('redis', 'Redis'),
        ('celery', 'Celery'),
        ('gunicorn', 'Gunicorn')
    ]
    
    print("\n🔍 Checking optional dependencies...")
    for package_import, package_name in optional_packages:
        try:
            __import__(package_import.replace('-', '_'))
            print(f"✅ {package_name} (optional)")
        except ImportError:
            print(f"⚠️ {package_name} (optional - not installed)")
    
    print(f"\n📊 Summary:")
    print(f"✅ Available: {len(available_packages)}/{len(required_packages)} required packages")
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        print("Or install individually:")
        for package in missing_packages:
            print(f"  pip install {package}")
        return False
    
    print("✅ All required dependencies satisfied")
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

TROUBLESHOOTING:
    - If imports fail, make sure you're in the correct directory
    - Check that all files are in place: app.py, routes/auth.py, routes/content_generator.py
    - Run 'python run.py check-deps' to verify dependencies
    - Check the console output for detailed error messages

For more information, visit: https://docs.velocitypost.ai
"""
    print(help_text)

def check_file_structure():
    """Check if required files exist"""
    print("🔍 Checking file structure...")
    
    required_files = [
        'app.py',
        'routes/auth.py',
        'routes/content_generator.py',
        'config/database.py'
    ]
    
    optional_files = [
        '.env',
        'requirements.txt',
        'config/__init__.py',
        'routes/__init__.py'
    ]
    
    current_dir = os.path.dirname(__file__)
    
    print("Required files:")
    all_required_exist = True
    for file_path in required_files:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (MISSING)")
            all_required_exist = False
    
    print("\nOptional files:")
    for file_path in optional_files:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"⚠️ {file_path} (not found)")
    
    if not all_required_exist:
        print("\n❌ Some required files are missing!")
        print("Make sure all files are in the correct locations.")
        return False
    
    print("\n✅ All required files found")
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        print(f"🔍 Running command: {command}")
        
        if command == 'dev':
            if check_file_structure():
                run_development()
            else:
                sys.exit(1)
                
        elif command == 'prod':
            if check_file_structure():
                run_production()
            else:
                sys.exit(1)
                
        elif command == 'setup-db':
            if check_file_structure():
                setup_database()
            else:
                sys.exit(1)
                
        elif command == 'test':
            success = run_tests()
            sys.exit(0 if success else 1)
            
        elif command == 'check-deps':
            success = check_dependencies()
            sys.exit(0 if success else 1)
            
        elif command == 'create-env':
            create_env_file()
            
        elif command == 'check-files':
            success = check_file_structure()
            sys.exit(0 if success else 1)
            
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
        
        if check_file_structure():
            run_development()
        else:
            print("\n❌ Cannot start - missing required files")
            print("Run 'python run.py check-files' to see what's missing")
            sys.exit(1)