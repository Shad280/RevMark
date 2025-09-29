# Create database indexes for better performance
# Run this script once to add indexes to your existing database

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from revmark import create_app, db

def add_indexes():
    app = create_app()
    with app.app_context():
        try:
            # Add indexes for better query performance
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_user_username ON "user" (username);')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_user_email ON "user" (email);')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_request_title ON request (title);')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_request_timestamp ON request (timestamp);')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_request_buyer_id ON request (buyer_id);')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_message_timestamp ON message (timestamp);')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_message_sender_id ON message (sender_id);')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_message_receiver_id ON message (receiver_id);')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_message_is_read ON message (is_read);')
            
            print("✅ Database indexes created successfully!")
            
        except Exception as e:
            print(f"❌ Error creating indexes: {e}")

if __name__ == "__main__":
    add_indexes()
