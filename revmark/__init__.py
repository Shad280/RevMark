from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache
from flask_mail import Mail
from flask_migrate import Migrate
from config import Config
from scaling_config import ScalingConfig
import os
from urllib.parse import urlparse, urlunparse

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login"
cache = Cache()
mail = Mail()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)
    app.config.from_object(ScalingConfig)
    
    # 🔍 CRITICAL DEBUG: Log a masked SQLAlchemy URI (do NOT print credentials)
    raw_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if raw_uri:
        try:
            parsed = urlparse(raw_uri)
            # Build a netloc without username/password
            netloc = parsed.hostname or ''
            if parsed.port:
                netloc = f"{netloc}:{parsed.port}"
            masked = urlunparse((parsed.scheme, netloc, parsed.path or '', '', '', ''))
            app.logger.info(f"🔍 SQLAlchemy will use: {masked}")
        except Exception:
            app.logger.info("🔍 SQLAlchemy will use: [REDACTED]")
    else:
        app.logger.info("🔍 SQLAlchemy will use: NOT_SET")
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Initialize admin panel
    from revmark.admin import init_admin
    init_admin(app, db)

    # Import and register blueprints
    from revmark import routes, models
    from revmark.api_routes import api_bp
    app.register_blueprint(routes.bp)
    app.register_blueprint(api_bp)

    # Create tables only when appropriate
    # In production, tables should be created via migration or manual setup
    if not os.environ.get('DATABASE_URL'):
        # Local development - safe to auto-create tables
        with app.app_context():
            try:
                db.create_all()
            except Exception as e:
                app.logger.error(f"Could not create database tables: {e}")

    # Lightweight health endpoint for platform healthchecks
    @app.route('/__status')
    def __status():
        # Keep this minimal and fast: return 200 if the app process is up.
        return {"status": "ok"}, 200
    
    return app
