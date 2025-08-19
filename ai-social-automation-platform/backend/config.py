import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Config
    SECRET_KEY = os.getenv('SECRET_KEY', 'ai-social-automation-secret-key-2024')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-for-ai-platform')
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 hours
    
    # MongoDB Config (supports both Atlas and Local)
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ai_social_automation')
    MONGO_ATLAS_URI = os.getenv('MONGO_ATLAS_URI', None)
    
    # Redis Config (for Celery and caching)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # File Storage Config
    UPLOAD_FOLDER = 'storage'
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    
    # AI API Keys (Primary: Mistral, Fallback: Groq)
    MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # For DALL-E image generation
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')  # Additional fallback
    
    # Content Sources & News APIs
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'AI Social Automation Bot 1.0')
    
    # Social Media APIs (for official API access when available)
    YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID')
    YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET')
    FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
    LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
    LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
    
    # Encryption Key for storing user credentials (must be 32 bytes)
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'ai-social-platform-32-char-key!!')
    
    # Subscription Plans & Limits
    SUBSCRIPTION_PLANS = {
        'starter': {
            'price': 29,
            'max_platforms': 2,
            'max_posts_per_day': 3,
            'max_domains': 3,
            'analytics': False,
            'api_access': False
        },
        'pro': {
            'price': 79,
            'max_platforms': 5,
            'max_posts_per_day': 6,
            'max_domains': 10,
            'analytics': True,
            'api_access': False
        },
        'agency': {
            'price': 299,
            'max_platforms': 999,
            'max_posts_per_day': 20,
            'max_domains': 999,
            'analytics': True,
            'api_access': True
        }
    }
    
    # Supported Content Domains
    CONTENT_DOMAINS = {
        'memes': {
            'name': 'Memes & Humor',
            'description': 'Funny memes, jokes, and humor content',
            'platforms': ['instagram', 'facebook', 'twitter', 'reddit']
        },
        'tech_news': {
            'name': 'Tech News',
            'description': 'Latest technology news and updates',
            'platforms': ['linkedin', 'twitter', 'facebook', 'youtube']
        },
        'coding_tips': {
            'name': 'Coding Tips',
            'description': 'Programming tutorials and coding advice',
            'platforms': ['linkedin', 'youtube', 'twitter', 'github']
        },
        'lifestyle': {
            'name': 'Lifestyle',
            'description': 'Health, fitness, and lifestyle content',
            'platforms': ['instagram', 'facebook', 'pinterest', 'youtube']
        },
        'business': {
            'name': 'Business Tips',
            'description': 'Entrepreneurship and business advice',
            'platforms': ['linkedin', 'facebook', 'youtube', 'twitter']
        },
        'motivational': {
            'name': 'Motivational',
            'description': 'Inspirational quotes and motivation',
            'platforms': ['instagram', 'facebook', 'linkedin', 'twitter']
        },
        'finance': {
            'name': 'Finance & Investment',
            'description': 'Financial advice and investment tips',
            'platforms': ['linkedin', 'youtube', 'twitter', 'reddit']
        },
        'gaming': {
            'name': 'Gaming',
            'description': 'Gaming news, reviews, and content',
            'platforms': ['youtube', 'twitch', 'twitter', 'reddit']
        },
        'travel': {
            'name': 'Travel',
            'description': 'Travel tips, destinations, and experiences',
            'platforms': ['instagram', 'facebook', 'pinterest', 'youtube']
        },
        'food': {
            'name': 'Food & Recipes',
            'description': 'Cooking, recipes, and food content',
            'platforms': ['instagram', 'facebook', 'pinterest', 'youtube']
        }
    }
    
    # Supported Social Media Platforms
    SUPPORTED_PLATFORMS = {
        'youtube': {
            'name': 'YouTube',
            'automation_method': 'api',  # or 'browser'
            'post_types': ['video', 'short', 'community_post'],
            'optimal_times': ['14:00', '16:00', '20:00'],
            'max_title_length': 100,
            'max_description_length': 5000
        },
        'instagram': {
            'name': 'Instagram',
            'automation_method': 'browser',
            'post_types': ['image', 'video', 'reel', 'story'],
            'optimal_times': ['09:00', '14:00', '19:00'],
            'max_caption_length': 2200,
            'max_hashtags': 30
        },
        'facebook': {
            'name': 'Facebook',
            'automation_method': 'api',
            'post_types': ['text', 'image', 'video', 'reel'],
            'optimal_times': ['10:00', '15:00', '20:00'],
            'max_text_length': 63206,
            'max_hashtags': 25
        },
        'twitter': {
            'name': 'Twitter/X',
            'automation_method': 'api',
            'post_types': ['text', 'image', 'video'],
            'optimal_times': ['08:00', '12:00', '17:00', '19:00'],
            'max_text_length': 280,
            'max_hashtags': 10
        },
        'linkedin': {
            'name': 'LinkedIn',
            'automation_method': 'browser',
            'post_types': ['text', 'image', 'video', 'article'],
            'optimal_times': ['08:00', '12:00', '17:00'],
            'max_text_length': 3000,
            'max_hashtags': 15
        },
        'pinterest': {
            'name': 'Pinterest',
            'automation_method': 'browser',
            'post_types': ['image', 'video'],
            'optimal_times': ['11:00', '15:00', '20:00'],
            'max_description_length': 500,
            'max_hashtags': 20
        },
        'reddit': {
            'name': 'Reddit',
            'automation_method': 'api',
            'post_types': ['text', 'image', 'video', 'link'],
            'optimal_times': ['10:00', '14:00', '19:00'],
            'max_title_length': 300,
            'max_text_length': 40000
        }
    }
    
    # Browser Automation Settings
    CHROME_OPTIONS = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--window-size=1920,1080',
        '--disable-blink-features=AutomationControlled',
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    ]
    
    # Content Generation Settings
    AI_GENERATION_SETTINGS = {
        'mistral_model': 'mistral-medium',
        'groq_model': 'mixtral-8x7b-32768',
        'max_tokens': 1000,
        'temperature': 0.7,
        'retry_attempts': 3,
        'fallback_chain': ['mistral', 'groq', 'openai']
    }
    
    # Image Generation Settings
    IMAGE_GENERATION = {
        'dalle_model': 'dall-e-3',
        'default_size': '1024x1024',
        'quality': 'standard',
        'style': 'vivid'
    }
    
    # Posting Schedule Settings
    POSTING_SCHEDULE = {
        'timezone': 'UTC',
        'spread_posts': True,  # Spread posts throughout the day
        'avoid_weekends': False,
        'min_interval_minutes': 60,  # Minimum time between posts
        'max_daily_posts': 6
    }
    
    # Rate Limiting
    RATE_LIMITS = {
        'content_generation': '100/hour',
        'social_posting': '50/hour',
        'credential_tests': '10/hour',
        'api_calls': '1000/hour'
    }
    
    # Monitoring & Analytics
    ANALYTICS_SETTINGS = {
        'collect_engagement': True,
        'track_growth': True,
        'generate_reports': True,
        'retention_days': 90
    }
    
    # Security Settings
    SECURITY = {
        'password_min_length': 8,
        'max_login_attempts': 5,
        'account_lockout_duration': 300,  # 5 minutes
        'session_timeout': 3600,  # 1 hour
        'require_2fa': False
    }
    
    # CORS Config
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # Celery Configuration
    CELERY_CONFIG = {
        'broker_url': REDIS_URL,
        'result_backend': REDIS_URL,
        'task_serializer': 'json',
        'accept_content': ['json'],
        'result_serializer': 'json',
        'timezone': 'UTC',
        'enable_utc': True,
        'beat_schedule': {
            'generate-content': {
                'task': 'app.workers.content_generation_worker.generate_scheduled_content',
                'schedule': 3600.0,  # Every hour
            },
            'post-content': {
                'task': 'app.workers.auto_posting_worker.post_scheduled_content',
                'schedule': 1800.0,  # Every 30 minutes
            },
            'collect-analytics': {
                'task': 'app.workers.analytics_collection_worker.collect_analytics',
                'schedule': 7200.0,  # Every 2 hours
            },
            'verify-credentials': {
                'task': 'app.workers.credential_verification_worker.verify_all_credentials',
                'schedule': 86400.0,  # Daily
            }
        }
    }

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    MONGO_URI = 'mongodb://localhost:27017/ai_social_automation_dev'

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    MONGO_URI = os.getenv('MONGO_ATLAS_URI', Config.MONGO_URI)
    
    # Production-specific settings
    CHROME_OPTIONS = Config.CHROME_OPTIONS + [
        '--headless',
        '--disable-logging',
        '--disable-dev-shm-usage'
    ]

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/ai_social_automation_test'
    JWT_ACCESS_TOKEN_EXPIRES = 300  # 5 minutes for testing

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}