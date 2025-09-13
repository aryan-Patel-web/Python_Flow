"""
Configuration module for Multi-Platform Automation System
Handles environment variables, settings validation, and configuration management
Updated for Reddit OAuth support and Pydantic V2
"""

import os
from typing import List, Optional
from functools import lru_cache
import logging
from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings with validation and type checking
    """
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

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
        "http://127.0.0.1:8501",
        "http://localhost:5173"
    ]

    # ==============================================
    # AI SERVICES CONFIGURATION - USING ENV VARS
    # ==============================================
    mistral_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    @field_validator('mistral_api_key', 'groq_api_key', 'openai_api_key', mode='before')
    @classmethod
    def validate_ai_keys(cls, v, info):
        """Load from environment if not provided"""
        if v is None:
            field_name = info.field_name
            env_key = field_name.upper()
            env_value = os.getenv(env_key)
            if env_value:
                logger.info(f"Loaded {field_name} from environment")
            return env_value
        return v

    # ==============================================
    # REDDIT API CONFIGURATION - USING ENV VARS
    # ==============================================
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "IndianAutomationPlatform/1.0"
    reddit_redirect_uri: str = "http://localhost:8000/api/oauth/reddit/callback"
    token_encryption_key: Optional[str] = None

    # Legacy username/password (optional)
    reddit_username: Optional[str] = None
    reddit_password: Optional[str] = None

    @field_validator('reddit_client_id', 'reddit_client_secret', mode='before')
    @classmethod
    def validate_reddit_credentials(cls, v, info):
        """Load from environment if not provided"""
        if v is None:
            field_name = info.field_name
            env_key = field_name.upper()
            env_value = os.getenv(env_key)
            if env_value:
                logger.info(f"Loaded {field_name} from environment")
            return env_value
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
    # DATABASE CONFIGURATION
    # ==============================================
    mongodb_uri: str = "mongodb://localhost:27017/socialMedia"
    mongodb_test_uri: str = "mongodb://localhost:27017/socialMedia_test"
    redis_url: str = "redis://localhost:6379/0"

    @field_validator('mongodb_uri')
    @classmethod
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
    # PLATFORM SPECIFIC SETTINGS
    # ==============================================
    reddit_rate_limit_delay: int = 2
    reddit_max_retries: int = 3

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
    # FEATURE FLAGS
    # ==============================================
    enable_voice_processing: bool = True
    enable_web_scraping: bool = True
    enable_ai_content_generation: bool = True
    enable_multi_language: bool = True
    enable_analytics: bool = True

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
        """Enhanced validation with better error messages"""
        ai_keys_available = any([self.mistral_api_key, self.groq_api_key, self.openai_api_key])
        
        if not ai_keys_available:
            logger.warning("No AI service API keys configured. AI features will be limited.")
        else:
            available_services = []
            if self.mistral_api_key:
                available_services.append("Mistral")
            if self.groq_api_key:
                available_services.append("Groq")
            if self.openai_api_key:
                available_services.append("OpenAI")
            logger.info(f"AI services configured: {', '.join(available_services)}")
        
        if not self.reddit_client_id or not self.reddit_client_secret:
            logger.warning("Reddit OAuth credentials not configured. Reddit features will be limited.")
        else:
            logger.info("Reddit OAuth credentials configured successfully")

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
            "REDDIT_CLIENT_ID": self.reddit_client_id,
            "REDDIT_CLIENT_SECRET": self.reddit_client_secret,
            "REDDIT_USER_AGENT": self.reddit_user_agent,
            "REDDIT_REDIRECT_URI": self.reddit_redirect_uri,
            "TOKEN_ENCRYPTION_KEY": self.token_encryption_key,
            "rate_limit_delay": self.reddit_rate_limit_delay,
            "max_retries": self.reddit_max_retries,
            "username": self.reddit_username,
            "password": self.reddit_password
        }


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