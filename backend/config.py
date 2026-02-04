import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    # Use SQLite for easy local testing, PostgreSQL for production
    # Render uses DATABASE_URL, fix for SQLAlchemy 1.4+ (postgres:// -> postgresql://)
    database_url = os.getenv('DATABASE_URL', 'sqlite:///gamescout.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    
    # RAWG API
    RAWG_API_KEY = os.getenv('RAWG_API_KEY', '')
    RAWG_BASE_URL = 'https://api.rawg.io/api'
    
    # Cache Configuration
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 21600  # 6 hours
