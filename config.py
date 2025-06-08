import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'lantercar-secret-key-2024'
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Fallback para PostgreSQL
        DB_USERNAME = os.environ.get('DB_USERNAME') or 'postgres'
        DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'password'
        DB_HOST = os.environ.get('DB_HOST') or 'localhost'
        DB_PORT = os.environ.get('DB_PORT') or '5432'
        DB_NAME = os.environ.get('DB_NAME') or 'lantercar'
        
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Login
    LOGIN_VIEW = 'auth.login'
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

