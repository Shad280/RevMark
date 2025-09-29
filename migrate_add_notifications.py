"""
Database migration script to add is_read column to messages
Run this script to update your database with the new notification feature
"""

from revmark import create_app, db

def migrate_database():
    app = create_app()
    
    with app.app_context():
        # Add the is_read column to existing messages table
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE message ADD COLUMN is_read BOOLEAN DEFAULT FALSE'))
                conn.commit()
            print("✅ Successfully added is_read column to message table")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("ℹ️  Column is_read already exists - no migration needed")
            else:
                print(f"❌ Error adding column: {e}")
                
        # Update all existing messages to be marked as read (so users don't get overwhelmed)
        try:
            with db.engine.connect() as conn:
                result = conn.execute(db.text('UPDATE message SET is_read = 1 WHERE is_read IS NULL OR is_read = 0'))
                conn.commit()
            print("✅ Updated existing messages to read status")
        except Exception as e:
            print(f"⚠️  Warning updating existing messages: {e}")
            
        print("\n🎉 Database migration completed!")
        print("Users will now see notification badges for new unread messages!")

if __name__ == "__main__":
    migrate_database()
