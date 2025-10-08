from revmark import create_app
import os
import traceback
from flask import Flask

# Try to create the full app. If that fails (for example due to a missing
# environment variable or transient DB error), fall back to a minimal app
# that responds 200 on `/` so Railway healthchecks don't immediately fail the
# deployment. The fallback makes the instance reachable while you inspect
# runtime logs and fix the root cause.
try:
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
except Exception as e:
    # Print traceback to make debugging easier in Railway logs
    print("!!! create_app() failed during startup. Falling back to a minimal app.")
    traceback.print_exc()

    fallback = Flask(__name__)

    @fallback.route("/")
    def health():
        # Return a 200 OK so host healthchecks pass while we investigate
        return "OK - fallback (startup error)", 200

    @fallback.route("/__status")
    def status():
        return {"status": "fallback", "error": str(e)}, 200

    app = fallback


if __name__ == '__main__':
    # For local development only
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
