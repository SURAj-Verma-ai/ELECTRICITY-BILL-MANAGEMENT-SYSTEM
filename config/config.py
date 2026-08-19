# Configuration Management for EBMS
import os
from datetime import timedelta

class BaseConfig:
    """Base configuration for all environments"""

    # Application
    APP_NAME = os.getenv('APP_NAME', 'EBMS')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Pagination
    ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100

    # JWT
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRY = int(os.getenv('JWT_EXPIRY', 3600))
    JWT_REFRESH_EXPIRY = timedelta(days=30)

    # Caching
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')

    # Security
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')


class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""

    DEBUG = True
    TESTING = False
    ENV = 'development'

    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'


class TestingConfig(BaseConfig):
    """Testing environment configuration"""

    DEBUG = True
    TESTING = True
    ENV = 'testing'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    CACHE_REDIS_URL = 'redis://localhost:6379/2'


class ProductionConfig(BaseConfig):
    """Production environment configuration"""

    DEBUG = False
    TESTING = False
    ENV = 'production'

    # Enhanced security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv('APP_ENV', 'development')
    return config.get(env, config['default'])
