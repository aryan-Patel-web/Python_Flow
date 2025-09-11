"""
Configuration module for Multi-Platform Automation System
Handles environment variables, settings validation, and configuration management
Updated for Reddit OAuth support
"""

import os
from typing import List, Optional
from functools import lru_cache
import logging
from pydantic_settings import BaseSettings
from pydantic import validator

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
    secret_key: str = "your_super_secret_key_here_32_chars_minimum"
    jwt_secret_key: str = "your_jwt_secret_key_here_32_chars_minimum"
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
    # REDDIT API CONFIGURATION (UPDATED FOR OAUTH)
    # ==============================================
    reddit_client_id: str = "your_reddit_client_id"
    reddit_client_secret: str = "your_reddit_client_secret"
    reddit_user_agent: str = "IndianAutomationPlatform/1.0"

    # OAuth-specific settings
    reddit_redirect_uri: str = "http://localhost:8000/api/oauth/reddit/callback"
    token_encryption_key: Optional[str] = None

    # Legacy username/password (optional for backward compatibility)
    reddit_username: Optional[str] = None
    reddit_password: Optional[str] = None

    @validator('reddit_client_id', 'reddit_client_secret')
    def validate_reddit_credentials(cls, v):
        if not v or v == "your_reddit_client_id" or v == "your_reddit_client_secret":
            logger.warning("Reddit credentials not configured properly")
            return v
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
    # DATABASE CONFIGURATION (UPDATED FOR socialMedia)
    # ==============================================
    mongodb_uri: str = "mongodb://localhost:27017/socialMedia"
    mongodb_test_uri: str = "mongodb://localhost:27017/socialMedia_test"
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
    reddit_rate_limit_delay: int = 2
    reddit_max_retries: int = 3
    twitter_rate_limit_delay: int = 1
    twitter_max_retries: int = 3
    webmd_request_delay: int = 3
    webmd_max_retries: int = 2
    stackoverflow_rate_limit: int = 300

    # ==============================================
    # CONTENT GENERATION SETTINGS
    # ==============================================
    max_content_length: int = 2000
    min_content_length: int = 50
    default_tone: str = "professional"
    default_language: str = "en"

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
    free_tier_platforms: int = 1
    free_tier_monthly_actions: int = 50
    pro_tier_platforms: int = 3
    pro_tier_monthly_actions: int = 500
    pro_tier_price: float = 999.0
    gold_tier_platforms: int = 5
    gold_tier_monthly_actions: int = 2000
    gold_tier_price: float = 2499.0
    diamond_tier_platforms: int = -1
    diamond_tier_monthly_actions: int = -1
    diamond_tier_price: float = 4999.0
    qa_commission_rate: float = 0.30
    min_payout_amount: float = 500.0

    # ==============================================
    # CACHE SETTINGS
    # ==============================================
    cache_ttl_short: int = 300
    cache_ttl_medium: int = 1800
    cache_ttl_long: int = 3600
    cache_ttl_daily: int = 86400

    # ==============================================
    # FILE UPLOAD SETTINGS
    # ==============================================
    max_file_size: int = 10 * 1024 * 1024
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

    min_password_length: int = 8
    require_password_numbers: bool = True
    require_password_symbols: bool = True
    require_password_uppercase: bool = True
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

    test_mode: bool = False
    mock_ai_responses: bool = False
    mock_platform_apis: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"   # ✅ FIX: ignore unknown fields like max_workers, reload

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_configuration()
        self._setup_encryption()

    def _setup_encryption(self):
        if not self.token_encryption_key:
            try:
                from cryptography.fernet import Fernet
                self.token_encryption_key = Fernet.generate_key().decode()
                logger.info("Generated new token encryption key")
            except ImportError:
                logger.warning("Cryptography not available, token encryption disabled")
                self.token_encryption_key = None

    def _validate_configuration(self):
        if not any([self.mistral_api_key, self.groq_api_key, self.openai_api_key]):
            logger.warning("No AI service API keys configured. AI features limited.")
        if self.environment == "production":
            if "localhost" in self.mongodb_uri:
                logger.warning("Using localhost MongoDB in production")
            if "localhost" in self.redis_url:
                logger.warning("Using localhost Redis in production")
        if self.environment == "production" and self.debug:
            logger.warning("Debug mode enabled in production")
        if len(self.secret_key) < 32:
            logger.warning("Secret key should be >= 32 chars")

    @property
    def database_url(self) -> str:
        return self.mongodb_test_uri if self.test_mode else self.mongodb_uri

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    def get_ai_config(self) -> dict:
        return {
            "mistral_api_key": self.mistral_api_key,
            "groq_api_key": self.groq_api_key,
            "openai_api_key": self.openai_api_key,
            "primary_model": self.primary_ai_model,
            "fallback_model": self.fallback_ai_model,
            "temperature": self.ai_temperature,
            "max_tokens": self.ai_max_tokens
        }

    def get_reddit_config(self) -> dict:
        return {
            "client_id": self.reddit_client_id,
            "client_secret": self.reddit_client_secret,
            "user_agent": self.reddit_user_agent,
            "redirect_uri": self.reddit_redirect_uri,
            "token_encryption_key": self.token_encryption_key,
            "rate_limit_delay": self.reddit_rate_limit_delay,
            "max_retries": self.reddit_max_retries,
            "username": self.reddit_username,
            "password": self.reddit_password
        }

    def get_platform_config(self, platform: str) -> dict:
        platform_configs = {
            "reddit": self.get_reddit_config(),
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
    try:
        settings = Settings()
        logger.info("Settings loaded successfully")
        return settings
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        return Settings()


def get_test_settings() -> Settings:
    return Settings(
        environment="testing",
        test_mode=True,
        debug=True,
        mongodb_uri="mongodb://localhost:27017/socialMedia_test",
        mock_ai_responses=True,
        mock_platform_apis=True
    )
