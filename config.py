import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "revmark-secret-key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    def __init__(self):
        # Debug: Print environment info
        print("=== DATABASE CONFIGURATION DEBUG ===", file=sys.stderr)
        print(f"DATABASE_URL exists: {bool(os.environ.get('DATABASE_URL'))}", file=sys.stderr)
        print(f"Railway environment: {bool(os.environ.get('RAILWAY_ENVIRONMENT'))}", file=sys.stderr)
        
        # Set database configuration
        self._setup_database()
    
    def _setup_database(self):
        database_url = os.environ.get("DATABASE_URL")
        
        if database_url:
            print("Using PostgreSQL from DATABASE_URL", file=sys.stderr)
            # Force PostgreSQL connection string format
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql://", 1)
            
            self.SQLALCHEMY_DATABASE_URI = database_url
            self.SQLALCHEMY_ENGINE_OPTIONS = {
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'pool_timeout': 20,
                'pool_size': 10,
                'max_overflow': 20
            }
            print(f"PostgreSQL URI set: {database_url[:50]}...", file=sys.stderr)
            
        # Check if we're in Railway environment (production)
        elif os.environ.get('RAILWAY_ENVIRONMENT'):
            print("ERROR: In Railway but no DATABASE_URL found!", file=sys.stderr)
            # This should not happen, but let's be explicit
            raise RuntimeError("Production environment detected but no DATABASE_URL provided")
            
        else:
            print("Using local development database", file=sys.stderr)
            # Local development
            postgres_local = os.environ.get("POSTGRES_LOCAL")
            if postgres_local:
                self.SQLALCHEMY_DATABASE_URI = postgres_local
                self.SQLALCHEMY_ENGINE_OPTIONS = {
                    'pool_pre_ping': True,
                    'pool_recycle': 300,
                }
            else:
                # SQLite fallback for local development only
                instance_dir = os.path.join(BASE_DIR, "instance")
                if not os.path.exists(instance_dir):
                    os.makedirs(instance_dir)
                self.SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance/revmark.db")
                self.SQLALCHEMY_ENGINE_OPTIONS = {}
        
        print(f"Final database URI: {getattr(self, 'SQLALCHEMY_DATABASE_URI', 'NOT SET')[:50]}...", file=sys.stderr)
        print("=== END DATABASE DEBUG ===", file=sys.stderr)
