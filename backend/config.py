#!/usr/bin/env python3
"""
Configuration file for API keys and database credentials.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env.local (for development) or .env (for production)
load_dotenv('.env.local')  # Try local first
load_dotenv()  # Then try .env

class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # CORS settings
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Logging
    LOG_LEVEL = "INFO"
    
    # Server settings
    HOST = "0.0.0.0"
    PORT = 5001
    
    # API Keys - Load from environment variables for security
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    
    # Platform API URLs
    YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
    COURSERA_API_BASE = "https://api.coursera.org/api/courses.v1"
    EDX_API_BASE = "https://courses.edx.org/api/courses/v1/courses"
    GITHUB_API_BASE = "https://api.github.com"
    
    # MongoDB Configuration (for future caching)
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'learning_roadmap')
    
    # Request settings
    REQUEST_TIMEOUT = 10
    MAX_CONCURRENT_REQUESTS = 5
    
    # Cache settings
    CACHE_DURATION_HOURS = 24
    
    # Groq AI settings
    GROQ_MODEL = "llama-3.1-8b-instant"
    GROQ_MAX_TOKENS = 4000
    GROQ_TEMPERATURE = 0.7


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Production CORS origins
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else ["http://localhost:3000"]


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = "DEBUG"


def get_config():
    """Get configuration class based on environment."""
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig