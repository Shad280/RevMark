import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "revmark-secret-key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Performance optimizations - Updated Oct 1, 2025
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'  # 30 second query timeout
        }
    }
    
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
        # Check if this is Railway production without PostgreSQL
        if os.getenv("RAILWAY_ENVIRONMENT") == "production":
            print("❌ CRITICAL: PostgreSQL database not configured in Railway!")
            print("")
            print("🔧 SOLUTION: The PostgreSQL plugin is not connected to your web service.")
            print("Follow these steps in Railway dashboard:")
            print("1. Go to your project dashboard")
            print("2. Click on your PostgreSQL database service (should show a database icon)")
            print("3. Go to the 'Connect' or 'Variables' tab")
            print("4. Make sure your web service is listed in 'Connected Services'")
            print("5. If not, add your web service to connect the database")
            print("6. Redeploy your web service after connecting")
            print("")
            raise RuntimeError("PostgreSQL database not configured in Railway production environment")
        else:
            # Local development fallback
            instance_dir = os.path.join(BASE_DIR, 'instance')
            os.makedirs(instance_dir, exist_ok=True)
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'revmark.db')}"
            print("🏠 Using SQLite for local development")
