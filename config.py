import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "revmark-secret-key"
    
    # Database - Use PostgreSQL in production, SQLite locally
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if DATABASE_URL:
        # Fix for various postgres:// URL formats
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Local development - create instance directory if it doesn't exist
        instance_dir = os.path.join(BASE_DIR, "instance")
        if not os.path.exists(instance_dir):
            os.makedirs(instance_dir)
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance/revmark.db")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
