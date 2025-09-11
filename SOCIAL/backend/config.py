"""
Configuration module for Multi-Platform Automation System
Handles environment variables, settings validation, and configuration management
"""

import os
from typing import List, Optional
from functools import lru_cache
from pydantic import BaseSettings, validator
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings with validation and type checking
    """
    
    # ==============================================
    # APPLICATION CORE SETTINGS
    # ==============================================
    debug: bool = True
    environment: str = "development"
    api_host: str = "localhost"
    api_port: int = 8000
    workers: int = 4
    log_level: str = "INFO"
    
    # Security
    secret_key: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8501"
    ]
    
    # ==============================================
    # AI SERVICES CONFIGURATION
    # ==============================================
    mistral_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    @validator('mistral_api_key', 'groq_api_key')
    def validate_ai_keys(cls, v):
        """Ensure at least one AI service is configured"""
        return v
    
    # ==============================================
    # REDDIT API CONFIGURATION
    # ==============================================
    reddit_client_id: str
    reddit_client_secret: str
    reddit_user_agent: str = "IndianAutomationPlatform/1.0"
    reddit_username: str
    reddit_password: str
    
    @validator('reddit_client_id', 'reddit_client_secret')
    def validate_reddit_credentials(cls, v):
        if not v:
            raise ValueError("Reddit credentials are required")
        return v
    
    # ==============================================
    # TWITTER API CONFIGURATION
    # ==============================================
    twitter_bearer_token: Optional[str] = None
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    twitter_client_id: Optional[str] = None
    twitter_client_secret: Optional[str] = None
    
    # ==============================================
    # STACK OVERFLOW API CONFIGURATION
    # ==============================================
    stackoverflow_key: Optional[str] = None
    stackoverflow_access_token: Optional[str] = None
    
    # ==============================================
    # DATABASE CONFIGURATION
    # ==============================================
    mongodb_uri: str = "mongodb://localhost:27017/automation_platform"
    mongodb_test_uri: str = "mongodb://localhost:27017/automation_platform_test"
    redis_url: str = "redis://localhost:6379/0"
    
    @validator('mongodb_uri')
    def validate_mongodb_uri(cls, v):
        if not v.startswith(('mongodb://', 'mongodb+srv://')):
            raise ValueError("Invalid MongoDB URI format")
        return v
    
    # ==============================================
    # RATE LIMITING CONFIGURATION
    # ==============================================
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # ==============================================
    # VOICE PROCESSING CONFIGURATION
    # ==============================================
    google_cloud_tts_key: Optional[str] = None
    azure_speech_key: Optional[str] = None
    azure_speech_region: Optional[str] = None
    
    # ==============================================
    # SELENIUM/BROWSER CONFIGURATION
    # ==============================================
    webdriver_path: str = "/usr/local/bin/chromedriver"
    selenium_headless: bool = True
    selenium_timeout: int = 30
    
    # ==============================================
    # MONITORING & LOGGING
    # ==============================================
    sentry_dsn: Optional[str] = None
    
    # ==============================================
    # FEATURE FLAGS
    # ==============================================
    enable_voice_processing: bool = True
    enable_web_scraping: bool = True
    enable_ai_content_generation: bool = True
    enable_multi_language: bool = True
    enable_analytics: bool = True
    
    # ==============================================
    # PLATFORM SPECIFIC SETTINGS
    # ==============================================
    
    # Reddit specific
    reddit_rate_limit_delay: int = 2  # seconds between requests
    reddit_max_retries: int = 3
    
    # Twitter specific
    twitter_rate_limit_delay: int = 1
    twitter_max_retries: int = 3
    
    # WebMD specific
    webmd_request_delay: int = 3
    webmd_max_retries: int = 2
    
    # Stack Overflow specific
    stackoverflow_rate_limit: int = 300  # requests per day
    
    # ==============================================
    # CONTENT GENERATION SETTINGS
    # ==============================================
    max_content_length: int = 2000
    min_content_length: int = 50
    default_tone: str = "professional"
    default_language: str = "en"
    
    # AI model preferences
    primary_ai_model: str = "mistral-large-latest"
    fallback_ai_model: str = "mixtral-8x7b-32768"
    ai_temperature: float = 0.7
    ai_max_tokens: int = 1000
    
    # ==============================================
    # SUPPORTED LANGUAGES
    # ==============================================
    supported_languages: List[str] = [
        "en", "hi", "ta", "te", "bn", "mr", "gu", 
        "kn", "ml", "pa", "or", "as"
    ]
    
    # ==============================================
    # BUSINESS LOGIC SETTINGS
    # ==============================================
    
    # Subscription tiers
    free_tier_platforms: int = 1
    free_tier_monthly_actions: int = 50
    
    pro_tier_platforms: int = 3
    pro_tier_monthly_actions: int = 500
    pro_tier_price: float = 999.0  # INR
    
    gold_tier_platforms: int = 5
    gold_tier_monthly_actions: int = 2000
    gold_tier_price: float = 2499.0  # INR
    
    diamond_tier_platforms: int = -1  # unlimited
    diamond_tier_monthly_actions: int = -1  # unlimited
    diamond_tier_price: float = 4999.0  # INR
    
    # Monetization settings
    qa_commission_rate: float = 0.30  # 30% commission
    min_payout_amount: float = 500.0  # INR
    
    # ==============================================
    # CACHE SETTINGS
    # ==============================================
    cache_ttl_short: int = 300      # 5 minutes
    cache_ttl_medium: int = 1800    # 30 minutes
    cache_ttl_long: int = 3600      # 1 hour
    cache_ttl_daily: int = 86400    # 24 hours
    
    # ==============================================
    # FILE UPLOAD SETTINGS
    # ==============================================
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = [
        "image/jpeg", "image/png", "image/gif", 
        "audio/wav", "audio/mp3", "audio/webm"
    ]
    upload_path: str = "uploads"
    
    # ==============================================
    # NOTIFICATION SETTINGS
    # ==============================================
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    
    # ==============================================
    # ANALYTICS SETTINGS
    # ==============================================
    analytics_retention_days: int = 365
    enable_user_tracking: bool = True
    enable_performance_monitoring: bool = True
    
    # ==============================================
    # SECURITY SETTINGS
    # ==============================================
    enable_rate_limiting: bool = True
    enable_request_logging: bool = True
    enable_input_validation: bool = True
    enable_xss_protection: bool = True
    enable_csrf_protection: bool = True
    
    # Password requirements
    min_password_length: int = 8
    require_password_numbers: bool = True
    require_password_symbols: bool = True
    require_password_uppercase: bool = True
    
    # Session settings
    session_timeout_minutes: int = 120
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    # ==============================================
    # DEVELOPMENT SETTINGS
    # ==============================================
    enable_debug_toolbar: bool = False
    enable_api_docs: bool = True
    enable_cors: bool = True
    reload_on_change: bool = True
    
    # Testing
    test_mode: bool = False
    mock_ai_responses: bool = False
    mock_platform_apis: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_configuration()
    
    def _validate_configuration(self):
        """Validate configuration after initialization"""
        
        # Ensure at least one AI service is configured
        if not any([self.mistral_api_key, self.groq_api_key, self.openai_api_key]):
            logger.warning("No AI service API keys configured. AI features will be limited.")
        
        # Validate database connections in production
        if self.environment == "production":
            if "localhost" in self.mongodb_uri:
                logger.warning("Using localhost MongoDB in production environment")
            
            if "localhost" in self.redis_url:
                logger.warning("Using localhost Redis in production environment")
        
        # Validate security settings
        if self.environment == "production" and self.debug:
            logger.warning("Debug mode enabled in production environment")
        
        if len(self.secret_key) < 32:
            logger.warning("Secret key should be at least 32 characters long")
        
        # Log configuration status
        logger.info(f"Configuration loaded for {self.environment} environment")
        logger.info(f"AI Services: Mistral={'✓' if self.mistral_api_key else '✗'}, "
                   f"Groq={'✓' if self.groq_api_key else '✗'}, "
                   f"OpenAI={'✓' if self.openai_api_key else '✗'}")
        logger.info(f"Platforms: Reddit={'✓'}, Twitter={'✓' if self.twitter_bearer_token else '✗'}, "
                   f"StackOverflow={'✓' if self.stackoverflow_key else '✗'}")
    
    @property
    def database_url(self) -> str:
        """Get appropriate database URL based on environment"""
        if self.test_mode:
            return self.mongodb_test_uri
        return self.mongodb_uri
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"
    
    def get_ai_config(self) -> dict:
        """Get AI service configuration"""
        return {
            "mistral_api_key": self.mistral_api_key,
            "groq_api_key": self.groq_api_key,
            "openai_api_key": self.openai_api_key,
            "primary_model": self.primary_ai_model,
            "fallback_model": self.fallback_ai_model,
            "temperature": self.ai_temperature,
            "max_tokens": self.ai_max_tokens
        }
    
    def get_platform_config(self, platform: str) -> dict:
        """Get platform-specific configuration"""
        platform_configs = {
            "reddit": {
                "client_id": self.reddit_client_id,
                "client_secret": self.reddit_client_secret,
                "user_agent": self.reddit_user_agent,
                "username": self.reddit_username,
                "password": self.reddit_password,
                "rate_limit_delay": self.reddit_rate_limit_delay,
                "max_retries": self.reddit_max_retries
            },
            "twitter": {
                "bearer_token": self.twitter_bearer_token,
                "api_key": self.twitter_api_key,
                "api_secret": self.twitter_api_secret,
                "access_token": self.twitter_access_token,
                "access_token_secret": self.twitter_access_token_secret,
                "client_id": self.twitter_client_id,
                "client_secret": self.twitter_client_secret,
                "rate_limit_delay": self.twitter_rate_limit_delay,
                "max_retries": self.twitter_max_retries
            },
            "stackoverflow": {
                "key": self.stackoverflow_key,
                "access_token": self.stackoverflow_access_token,
                "rate_limit": self.stackoverflow_rate_limit
            },
            "webmd": {
                "request_delay": self.webmd_request_delay,
                "max_retries": self.webmd_max_retries
            }
        }
        
        return platform_configs.get(platform, {})
    
    def get_subscription_config(self, tier: str) -> dict:
        """Get subscription tier configuration"""
        tier_configs = {
            "free": {
                "platforms": self.free_tier_platforms,
                "monthly_actions": self.free_tier_monthly_actions,
                "price": 0.0
            },
            "pro": {
                "platforms": self.pro_tier_platforms,
                "monthly_actions": self.pro_tier_monthly_actions,
                "price": self.pro_tier_price
            },
            "gold": {
                "platforms": self.gold_tier_platforms,
                "monthly_actions": self.gold_tier_monthly_actions,
                "price": self.gold_tier_price
            },
            "diamond": {
                "platforms": self.diamond_tier_platforms,
                "monthly_actions": self.diamond_tier_monthly_actions,
                "price": self.diamond_tier_price
            }
        }
        
        return tier_configs.get(tier, tier_configs["free"])


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    
    Returns:
        Settings instance with configuration loaded from environment
    """
    try:
        settings = Settings()
        logger.info("Settings loaded successfully")
        return settings
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        raise


# Development and testing utilities
def get_test_settings() -> Settings:
    """Get settings configured for testing"""
    return Settings(
        environment="testing",
        test_mode=True,
        debug=True,
        mongodb_uri="mongodb://localhost:27017/automation_platform_test",
        mock_ai_responses=True,
        mock_platform_apis=True
    )


def validate_env_file(env_path: str = ".env") -> dict:
    """
    Validate .env file and return missing required variables
    
    Args:
        env_path: Path to .env file
        
    Returns:
        Dictionary with validation results
    """
    required_vars = [
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "MONGODB_URI",
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET",
        "REDDIT_USERNAME",
        "REDDIT_PASSWORD"
    ]
    
    recommended_vars = [
        "MISTRAL_API_KEY",
        "GROQ_API_KEY",
        "TWITTER_BEARER_TOKEN",
        "STACKOVERFLOW_KEY"
    ]
    
    missing_required = []
    missing_recommended = []
    
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        
        for var in required_vars:
            if not os.getenv(var):
                missing_required.append(var)
        
        for var in recommended_vars:
            if not os.getenv(var):
                missing_recommended.append(var)
        
        return {
            "valid": len(missing_required) == 0,
            "missing_required": missing_required,
            "missing_recommended": missing_recommended,
            "message": "Environment validation completed"
        }
        
    except FileNotFoundError:
        return {
            "valid": False,
            "error": f"Environment file {env_path} not found",
            "missing_required": required_vars,
            "missing_recommended": recommended_vars
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Environment validation failed: {e}",
            "missing_required": [],
            "missing_recommended": []
        }


def generate_env_template() -> str:
    """Generate .env template with all configuration options"""
    template = """# ==============================================
# Multi-Platform Automation System Configuration
# ==============================================

# ==============================================
# CORE APPLICATION SETTINGS
# ==============================================
DEBUG=True
ENVIRONMENT=development
API_HOST=localhost
API_PORT=8000
SECRET_KEY=your_super_secret_key_here_32_chars_minimum
JWT_SECRET_KEY=your_jwt_secret_key_here_32_chars_minimum
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ==============================================
# AI SERVICES (REQUIRED - At least one)
# ==============================================
MISTRAL_API_KEY=your_mistral_api_key_here
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# ==============================================
# REDDIT API (REQUIRED)
# ==============================================
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=IndianAutomationPlatform/1.0
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# ==============================================
# TWITTER API (OPTIONAL)
# ==============================================
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret

# ==============================================
# STACK OVERFLOW API (OPTIONAL)
# ==============================================
STACKOVERFLOW_KEY=your_stackoverflow_api_key
STACKOVERFLOW_ACCESS_TOKEN=your_stackoverflow_access_token

# ==============================================
# DATABASE CONFIGURATION
# ==============================================
MONGODB_URI=mongodb://localhost:27017/automation_platform
MONGODB_TEST_URI=mongodb://localhost:27017/automation_platform_test
REDIS_URL=redis://localhost:6379/0

# ==============================================
# VOICE PROCESSING (OPTIONAL)
# ==============================================
GOOGLE_CLOUD_TTS_KEY=your_google_cloud_tts_key
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_region

# ==============================================
# SELENIUM/BROWSER AUTOMATION
# ==============================================
WEBDRIVER_PATH=/usr/local/bin/chromedriver
SELENIUM_HEADLESS=True
SELENIUM_TIMEOUT=30

# ==============================================
# MONITORING & LOGGING
# ==============================================
SENTRY_DSN=your_sentry_dsn_here
LOG_LEVEL=INFO

# ==============================================
# RATE LIMITING
# ==============================================
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# ==============================================
# CORS ORIGINS (Development)
# ==============================================
CORS_ORIGINS=http://localhost:3000,http://localhost:8501,http://127.0.0.1:3000,http://127.0.0.1:8501
"""
    return template


if __name__ == "__main__":
    """
    Command line utility for configuration management
    """
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Configuration management utility")
    parser.add_argument("--validate", action="store_true", help="Validate environment file")
    parser.add_argument("--generate-template", action="store_true", help="Generate .env template")
    parser.add_argument("--test-config", action="store_true", help="Test configuration loading")
    parser.add_argument("--env-file", default=".env", help="Path to environment file")
    
    args = parser.parse_args()
    
    if args.generate_template:
        print("Generating .env template...")
        template = generate_env_template()
        with open("env.template", "w") as f:
            f.write(template)
        print("Template saved to env.template")
    
    elif args.validate:
        print(f"Validating environment file: {args.env_file}")
        result = validate_env_file(args.env_file)
        
        if result["valid"]:
            print("✅ Environment validation passed!")
        else:
            print("❌ Environment validation failed!")
            
            if result.get("missing_required"):
                print(f"Missing required variables: {', '.join(result['missing_required'])}")
            
            if result.get("missing_recommended"):
                print(f"Missing recommended variables: {', '.join(result['missing_recommended'])}")
            
            if result.get("error"):
                print(f"Error: {result['error']}")
    
    elif args.test_config:
        print("Testing configuration loading...")
        try:
            settings = get_settings()
            print("✅ Configuration loaded successfully!")
            print(f"Environment: {settings.environment}")
            print(f"Debug mode: {settings.debug}")
            print(f"AI Services configured: {bool(settings.mistral_api_key or settings.groq_api_key)}")
            print(f"Reddit configured: {bool(settings.reddit_client_id)}")
            print(f"Twitter configured: {bool(settings.twitter_bearer_token)}")
        except Exception as e:
            print(f"❌ Configuration loading failed: {e}")
            sys.exit(1)
    
    else:
        parser.print_help()