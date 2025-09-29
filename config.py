import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "revmark-secret-key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Railway DATABASE_URL detection with debugging
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Check all Railway PostgreSQL environment variables
    if not DATABASE_URL:
        # Try alternative Railway PostgreSQL variable names
        DATABASE_URL = (
            os.getenv("RAILWAY_POSTGRES_URL") or
            os.getenv("POSTGRES_URL") or 
            os.getenv("PGURL") or
            os.getenv("DATABASE_PRIVATE_URL")
        )
    
    # Fix postgres:// to postgresql:// for SQLAlchemy compatibility
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Force PostgreSQL in production environment (when Railway sets RAILWAY_ENVIRONMENT)
    if os.getenv("RAILWAY_ENVIRONMENT") and not DATABASE_URL:
        # If we're on Railway but no DATABASE_URL is found, this is an error
        raise RuntimeError("Railway PostgreSQL plugin not configured. Add PostgreSQL plugin to your Railway project.")
    
    # Set the database URI
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        print(f"Using PostgreSQL database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configured'}")
    else:
        # Local development with SQLite
        instance_dir = os.path.join(BASE_DIR, 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'revmark.db')}"
        print("Using SQLite database for local development")
