#!/usr/bin/env python3
"""
Main application runner for development and production
"""
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting run.py...")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Script location: {os.path.abspath(__file__)}")

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
logger.info(f"Added to Python path: {current_dir}")

# Load environment variables
try:
    load_dotenv()
    logger.info("Environment variables loaded")
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")

# Try to import app
logger.info("Attempting to import app...")
try:
    from app import create_app
    logger.info("Successfully imported create_app from app.py")
except ImportError as e:
    logger.warning(f"Failed to import create_app: {e}")
    # Try alternative import
    try:
        import app as app_module
        create_app = app_module.create_app
        logger.info("Successfully imported app module")
    except ImportError as e2:
        logger.error(f"Failed to import app module: {e2}")
        sys.exit(1)

def create_application():
    """Create and configure the Flask application"""
    logger.info("Creating Flask application...")
    
    config_name = os.getenv('FLASK_ENV', 'development')
    logger.info(f"Config name: {config_name}")
    
    try:
        app = create_app()
        logger.info("Flask app created successfully")
        
        with app.app_context():
            logger.info("Inside app context...")
            try:
                # Try to initialize database if available
                logger.info("Attempting database initialization...")
                
                # Check if we can import database utilities
                try:
                    from config.database import get_collection
                    logger.info("Database config available")
                    
                    # Test database connection
                    users_collection = get_collection('users')
                    if users_collection:
                        user_count = users_collection.count_documents({})
                        logger.info(f"Database connected. User count: {user_count}")
                    else:
                        logger.warning("Database collection unavailable")
                        
                except ImportError as e:
                    logger.warning(f"Database config not available: {e}")
                except Exception as e:
                    logger.warning(f"Database connection issue: {e}")
                
                # Try to create default admin user
                try:
                    admin_email = os.getenv('ADMIN_EMAIL', 'admin@velocitypost.ai')
                    logger.info(f"Checking for admin user: {admin_email}")
                    
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
                            logger.info(f"Admin user created: {admin_email} (ID: {result.inserted_id})")
                        else:
                            logger.info(f"Admin user already exists: {admin_email}")
                    else:
                        logger.warning("Cannot create admin user - database unavailable")
                        
                except Exception as e:
                    logger.warning(f"Admin user setup failed: {str(e)}")
                    
            except Exception as e:
                logger.warning(f"App context setup warning: {str(e)}")
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to create Flask app: {e}")
        raise

def run_development():
    """Run the application in development mode"""
    logger.info("Starting development server...")
    
    try:
        app = create_application()
        logger.info("Application created for development")
        
        port = int(os.getenv('PORT', 5000))
        
        print("\n" + "="*50)
        print("VelocityPost.ai Development Server Starting...")
        print(f"Environment: Development")
        print(f"Access at: http://localhost:{port}")
        print(f"Health check: http://localhost:{port}/api/health")
        print(f"API docs: http://localhost:{port}/api/docs")
        print(f"Debug mode: ON")
        print(f"Auto-reload: ON")
        print("="*50 + "\n")
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True,
            use_reloader=True
        )
        
    except Exception as e:
        logger.error(f"Development server failed to start: {e}")
        sys.exit(1)

def run_production():
    """Run the application in production mode with Gunicorn"""
    logger.info("Starting production server...")
    
    try:
        app = create_application()
        logger.info("Application created for production")
        
        print("\n" + "="*50)
        print("VelocityPost.ai Production Server Starting...")
        print("Environment: Production")
        print("Debug mode: OFF")
        print("="*50 + "\n")
        
        # Import Gunicorn
        try:
            import gunicorn.app.base
            logger.info("Gunicorn available")
        except ImportError:
            logger.error("Gunicorn not installed. Install with: pip install gunicorn")
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
        
        logger.info(f"Gunicorn options: {options}")
        StandaloneApplication(app, options).run()
        
    except Exception as e:
        logger.error(f"Production server failed to start: {e}")
        sys.exit(1)

def setup_database():
    """Setup database with initial data"""
    logger.info("Starting database setup...")
    
    try:
        app = create_application()
        logger.info("Application created for database setup")
        
        with app.app_context():
            logger.info("Setting up database...")
            
            # Reset database if requested
            if '--reset' in sys.argv:
                logger.warning("Resetting database...")
                try:
                    from config.database import get_collection
                    
                    # Drop collections
                    collections = ['users', 'social_accounts', 'posts', 'content_generations', 'automation_settings']
                    for collection_name in collections:
                        collection = get_collection(collection_name)
                        if collection:
                            collection.drop()
                            logger.info(f"Dropped collection: {collection_name}")
                        else:
                            logger.warning(f"Collection not available: {collection_name}")
                    
                except Exception as e:
                    logger.warning(f"Database reset warning: {e}")
            
            logger.info("Database setup complete!")
            
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)

def run_tests():
    """Run the test suite"""
    logger.info("Starting test suite...")
    
    try:
        import unittest
        logger.info("unittest module available")
        
        # Check if tests directory exists
        test_dir = os.path.join(os.path.dirname(__file__), 'tests')
        logger.info(f"Looking for tests in: {test_dir}")
        
        if not os.path.exists(test_dir):
            logger.warning(f"Tests directory not found: {test_dir}")
            logger.info("Creating basic test structure...")
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
            print("App import test passed")
        except Exception as e:
            self.fail(f"App import failed: {e}")

if __name__ == '__main__':
    unittest.main()
'''
            with open(os.path.join(test_dir, 'test_basic.py'), 'w') as f:
                f.write(basic_test)
            logger.info("Created basic test file")
        
        # Discover and run tests
        loader = unittest.TestLoader()
        suite = loader.discover(test_dir, pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            logger.info("All tests passed!")
            return True
        else:
            logger.error(f"{len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
            return False
            
    except ImportError:
        logger.error("unittest not available")
        return False
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    logger.info("Creating .env file...")
    
    if os.path.exists('.env'):
        logger.info(".env file already exists")
        return
    
    if os.path.exists('.env.example'):
        import shutil
        shutil.copy('.env.example', '.env')
        logger.info(".env file created from template")
        print("Please edit .env file with your API keys")
    else:
        logger.warning(".env.example not found, creating basic .env file...")
        
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
        logger.info("Basic .env file created")
        print("Please edit .env file with your actual API keys and configuration")

def check_dependencies():
    """Check if all required dependencies are installed"""
    logger.info("Checking dependencies...")
    
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
            logger.info(f"{package_name} - available")
        except ImportError:
            missing_packages.append(package_name)
            logger.warning(f"{package_name} - missing")
    
    # Check optional packages
    optional_packages = [
        ('redis', 'Redis'),
        ('celery', 'Celery'),
        ('gunicorn', 'Gunicorn')
    ]
    
    logger.info("Checking optional dependencies...")
    for package_import, package_name in optional_packages:
        try:
            __import__(package_import.replace('-', '_'))
            logger.info(f"{package_name} (optional) - available")
        except ImportError:
            logger.info(f"{package_name} (optional) - not installed")
    
    logger.info(f"Summary:")
    logger.info(f"Available: {len(available_packages)}/{len(required_packages)} required packages")
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        print("Or install individually:")
        for package in missing_packages:
            print(f"  pip install {package}")
        return False
    
    logger.info("All required dependencies satisfied")
    return True

def show_help():
    """Show help information"""
    help_text = """
VelocityPost.ai - Application Runner

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
    - Check that all files are in place: app.py, app/routes/auth.py, etc.
    - Run 'python run.py check-deps' to verify dependencies
    - Check the console output for detailed error messages

For more information, visit: https://docs.velocitypost.ai
"""
    print(help_text)

def check_file_structure():
    """Check if required files exist"""
    logger.info("Checking file structure...")
    
    required_files = [
        'app.py',
        'app/routes/auth.py',
        'app/utils/database.py',
        'app/utils/auth_helpers.py'
    ]
    
    optional_files = [
        '.env',
        'requirements.txt',
        'app/__init__.py',
        'app/routes/__init__.py',
        'app/utils/__init__.py',
        'config/database.py'
    ]
    
    current_dir = os.path.dirname(__file__)
    
    logger.info("Required files:")
    all_required_exist = True
    for file_path in required_files:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            logger.info(f"{file_path} - exists")
        else:
            logger.error(f"{file_path} - MISSING")
            all_required_exist = False
    
    logger.info("Optional files:")
    for file_path in optional_files:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            logger.info(f"{file_path} - exists")
        else:
            logger.info(f"{file_path} - not found")
    
    if not all_required_exist:
        logger.error("Some required files are missing!")
        print("Make sure all files are in the correct locations.")
        return False
    
    logger.info("All required files found")
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        logger.info(f"Running command: {command}")
        
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
            logger.error(f"Unknown command: {command}")
            print("Use 'python run.py help' for available commands")
            sys.exit(1)
    else:
        # Default to development mode
        print("Starting in development mode...")
        print("Use 'python run.py help' for more options")
        
        if check_file_structure():
            run_development()
        else:
            logger.error("Cannot start - missing required files")
            print("Run 'python run.py check-files' to see what's missing")
            sys.exit(1)