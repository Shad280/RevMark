from revmark import create_app
import os

# 🔍 DEBUG: Check what Railway is providing
print("=" * 60)
print("🚂 RAILWAY POSTGRESQL DEBUG INFO:")
print("DATABASE_URL:", os.getenv("DATABASE_URL"))
print("DATABASE_PUBLIC_URL:", os.getenv("DATABASE_PUBLIC_URL"))
print("RAILWAY_ENVIRONMENT:", os.getenv("RAILWAY_ENVIRONMENT"))
print("RAILWAY_PRIVATE_DOMAIN:", os.getenv("RAILWAY_PRIVATE_DOMAIN"))
print("PGUSER:", os.getenv("PGUSER"))
print("POSTGRES_USER:", os.getenv("POSTGRES_USER"))
print("PGHOST:", os.getenv("PGHOST"))
print("PGPORT:", os.getenv("PGPORT"))
print("PGDATABASE:", os.getenv("PGDATABASE"))
print("POSTGRES_DB:", os.getenv("POSTGRES_DB"))
print("PGPASSWORD:", '***' if os.getenv("PGPASSWORD") else None)
print("POSTGRES_PASSWORD:", '***' if os.getenv("POSTGRES_PASSWORD") else None)
print("=" * 60)

app = create_app()

if __name__ == '__main__':
    # For local development only
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
