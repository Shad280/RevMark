import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Railway sets this automatically if you added a Postgres plugin
DATABASE_URL = os.getenv("DATABASE_URL")

# Fix for psycopg2 / SQLAlchemy compatibility
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "revmark-secret-key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Ensure instance directory exists for local SQLite
    if not DATABASE_URL:
        instance_dir = os.path.join(BASE_DIR, 'instance')
        os.makedirs(instance_dir, exist_ok=True)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'revmark.db')}"
