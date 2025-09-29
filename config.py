import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 🔍 Railway PostgreSQL Detection
DATABASE_URL = os.getenv("DATABASE_URL")

# Try alternative Railway PostgreSQL variable names if DATABASE_URL is missing
if not DATABASE_URL:
    DATABASE_URL = (
        os.getenv("DATABASE_PUBLIC_URL") or
        os.getenv("RAILWAY_POSTGRES_URL") or
        os.getenv("POSTGRES_URL") or 
        os.getenv("PGURL")
    )

# ⚠️ Fix postgres:// to postgresql:// for SQLAlchemy compatibility
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print(f"🔧 Fixed postgres:// to postgresql:// for SQLAlchemy")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "revmark-secret-key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 🔍 Database Configuration with Fallback
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        print(f"✅ Using PostgreSQL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configured'}")
    else:
        # Local development fallback
        instance_dir = os.path.join(BASE_DIR, 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'revmark.db')}"
        print("🏠 Using SQLite for local development")
        
    # 🚨 Railway Production Check
    if os.getenv("RAILWAY_ENVIRONMENT") and not DATABASE_URL:
        raise RuntimeError("❌ Railway PostgreSQL plugin not configured. Add PostgreSQL plugin to your Railway project.")
