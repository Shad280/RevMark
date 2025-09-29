import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "revmark-secret-key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 🔍 Railway PostgreSQL Detection with Manual Construction
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # 🚨 RAILWAY FIX: If DATABASE_URL contains template variables, construct manually
    if DATABASE_URL and "${{" in DATABASE_URL:
        print("🔧 Railway template variables detected, constructing DATABASE_URL manually...")
        # Get individual PostgreSQL components
        pguser = os.getenv("PGUSER") or os.getenv("POSTGRES_USER")
        pgpassword = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD")
        pghost = os.getenv("PGHOST") or os.getenv("RAILWAY_PRIVATE_DOMAIN")
        pgport = os.getenv("PGPORT", "5432")
        pgdatabase = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB")
        
        if all([pguser, pgpassword, pghost, pgdatabase]):
            DATABASE_URL = f"postgresql://{pguser}:{pgpassword}@{pghost}:{pgport}/{pgdatabase}"
            print(f"✅ Manually constructed PostgreSQL URL: postgresql://{pguser}:***@{pghost}:{pgport}/{pgdatabase}")
        else:
            print(f"❌ Missing PostgreSQL components: user={pguser}, host={pghost}, db={pgdatabase}")
            DATABASE_URL = None
    
    # Try alternative Railway PostgreSQL variable names if DATABASE_URL is still missing
    if not DATABASE_URL:
        DATABASE_URL = (
            os.getenv("DATABASE_PUBLIC_URL") or
            os.getenv("RAILWAY_POSTGRES_URL") or
            os.getenv("POSTGRES_URL") or 
            os.getenv("PGURL")
        )
    
    # ⚠️ CRITICAL: Fix postgres:// to postgresql:// for SQLAlchemy compatibility
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        print(f"🔧 Fixed postgres:// to postgresql:// for SQLAlchemy")
    
    # 🔍 Set Database URI
    if DATABASE_URL and not "${{" in DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        print(f"✅ Using PostgreSQL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configured'}")
    else:
        # Local development fallback
        instance_dir = os.path.join(BASE_DIR, 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'revmark.db')}"
        print("🏠 Using SQLite for local development")
    
    # 🚨 Railway Production Check (temporarily disabled for debugging)
    # if os.getenv("RAILWAY_ENVIRONMENT") and not DATABASE_URL:
    #     raise RuntimeError("❌ Railway PostgreSQL plugin not configured. Add PostgreSQL plugin to your Railway project.")
