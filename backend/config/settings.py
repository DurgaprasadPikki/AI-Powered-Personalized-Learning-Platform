import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/learning_platform'
    JWT_SECRET = os.environ.get('JWT_SECRET') or 'jwt-secret-key-change-in-production'
    JWT_EXPIRATION = timedelta(days=30)
    
    # ML Model settings
    ML_MODEL_PATH = os.path.join(os.path.dirname(__file__), '../ml_engine/models')
    DIFFICULTY_LEVELS = ['Beginner', 'Intermediate', 'Advanced']
    
    # Quiz settings
    DIFFICULTY_ADJUSTMENT_THRESHOLD = 0.75  # 75% accuracy to increase difficulty
    MIN_QUESTIONS_FOR_RECOMMENDATION = 5
    
    # API settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    MONGODB_URI = 'mongodb://localhost:27017/learning_platform_test'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
