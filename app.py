from revmark import create_app
import os

# 🔍 DEBUG: Check what Railway is providing
print("=" * 50)
print("RAILWAY DEBUG INFO:")
print("DATABASE_URL from Railway:", os.getenv("DATABASE_URL"))
print("RAILWAY_ENVIRONMENT:", os.getenv("RAILWAY_ENVIRONMENT"))
print("All DB-related env vars:")
for key, value in os.environ.items():
    if any(db_key in key.upper() for db_key in ['DATABASE', 'POSTGRES', 'PG']):
        print(f"  {key}: {'***' if 'PASSWORD' in key.upper() else value}")
print("=" * 50)

app = create_app()

if __name__ == '__main__':
    # For local development only
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
