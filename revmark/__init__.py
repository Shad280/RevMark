from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login"

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Import and register blueprints
    from revmark import routes, models
    app.register_blueprint(routes.bp)

    # Create tables only when appropriate
    # In production, tables should be created via migration or manual setup
    if not os.environ.get('DATABASE_URL'):
        # Local development - safe to auto-create tables
        with app.app_context():
            try:
                db.create_all()
            except Exception as e:
                app.logger.error(f"Could not create database tables: {e}")
    
    return app
