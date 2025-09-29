import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "revmark-secret-key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database configuration - Production first
    DATABASE_URL = os.environ.get("DATABASE_URL")
    
    if DATABASE_URL:
        # Production: Use PostgreSQL exclusively
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        # PostgreSQL specific engine options
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': 20,
            'pool_size': 10,
            'max_overflow': 20
        }
    else:
        # Development: Use PostgreSQL or SQLite as fallback
        POSTGRES_LOCAL = os.environ.get("POSTGRES_LOCAL")
        if POSTGRES_LOCAL:
            SQLALCHEMY_DATABASE_URI = POSTGRES_LOCAL
            SQLALCHEMY_ENGINE_OPTIONS = {
                'pool_pre_ping': True,
                'pool_recycle': 300,
            }
        else:
            # SQLite fallback for local development only
            instance_dir = os.path.join(BASE_DIR, "instance")
            if not os.path.exists(instance_dir):
                os.makedirs(instance_dir)
            SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance/revmark.db")
            SQLALCHEMY_ENGINE_OPTIONS = {}
