import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from a .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration class. Contains default configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-hard-to-guess-string'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/news_aggregator'
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'another-super-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    MONGO_URI = os.environ.get('DEV_MONGO_URI') or 'mongodb://localhost:27017/news_aggregator_dev'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    MONGO_URI = os.environ.get('TEST_MONGO_URI') or 'mongodb://localhost:27017/news_aggregator_test'
    # Use a different secret key for testing to ensure isolation
    SECRET_KEY = 'testing-secret-key'
    JWT_SECRET_KEY = 'testing-jwt-secret-key'


class ProductionConfig(Config):
    """Production configuration."""
    MONGO_URI = os.environ.get('PROD_MONGO_URI')
    # In production, ensure these keys are set in the environment
    if not MONGO_URI:
        raise ValueError("No PROD_MONGO_URI set for production")
    if not Config.SECRET_KEY or Config.SECRET_KEY == 'a-very-hard-to-guess-string':
         raise ValueError("No SECRET_KEY set for production")


# Dictionary to access config classes by name
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
