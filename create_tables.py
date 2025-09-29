#!/usr/bin/env python3
"""
Direct PostgreSQL database initialization for Railway
"""

import os
import sys
from sqlalchemy import create_engine, text

# PostgreSQL connection details from Railway
DATABASE_URL = "postgresql://postgres:CAxURJFzItKFLjAvOnIdmeJltIYtclRW@yamabiko.proxy.rlwy.net:50386/railway"

def create_tables():
    """Create all database tables directly with SQL"""
    print(f"🔗 Connecting to Railway PostgreSQL...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            print("✅ Connected to PostgreSQL!")
            
            # Create user table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS "user" (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(64) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    password VARCHAR(200) NOT NULL
                );
            """))
            
            # Create request table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS request (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT NOT NULL,
                    budget FLOAT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    buyer_id INTEGER NOT NULL,
                    FOREIGN KEY (buyer_id) REFERENCES "user" (id)
                );
            """))
            
            # Create message table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS message (
                    id SERIAL PRIMARY KEY,
                    body TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE NOT NULL,
                    FOREIGN KEY (sender_id) REFERENCES "user" (id),
                    FOREIGN KEY (receiver_id) REFERENCES "user" (id)
                );
            """))
            
            conn.commit()
            
            print("✅ All tables created successfully!")
            
            # Verify tables exist
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
            """))
            
            tables = [row[0] for row in result]
            print(f"🔍 Tables in database: {sorted(tables)}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_tables()
