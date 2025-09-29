#!/usr/bin/env python3
"""
Database initialization script for Railway PostgreSQL
This script creates all the database tables in production
"""

from revmark import create_app, db
from revmark.models import User, Request, Message
import os

def init_database():
    """Initialize the database with all tables"""
    # Force Railway environment to use PostgreSQL
    os.environ['RAILWAY_ENVIRONMENT'] = 'production'
    os.environ['DATABASE_URL'] = 'postgresql://postgres:CAxURJFzItKFLjAvOnIdmeJltIYtclRW@yamabiko.proxy.rlwy.net:50386/railway'
    
    app = create_app()
    
    with app.app_context():
        print(f"🔗 Connected to: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("🔨 Creating database tables...")
        
        # Create all tables
        db.create_all()
        
        print("✅ Database tables created successfully!")
        print(f"📊 Tables created:")
        print(f"   - user")
        print(f"   - request") 
        print(f"   - message")
        
        # Verify tables exist
        inspector = db.inspect(db.engine)
        table_names = inspector.get_table_names()
        print(f"🔍 Verified tables in database: {table_names}")

if __name__ == "__main__":
    init_database()
