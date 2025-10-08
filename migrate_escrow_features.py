"""
Migration script to add escrow payment and file attachment features
Run this script to update your database schema
"""
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from revmark import create_app, db
from revmark.models import User, Request, Message, MessageAttachment, EscrowPayment

def migrate_database():
    """Add new columns and tables for escrow and file attachments"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting database migration...")
        
        try:
            # Create all new tables and columns
            db.create_all()
            print("✅ Database schema updated successfully!")
            
            # Update existing requests with default status
            requests_updated = db.session.execute(
                "UPDATE request SET status = 'open' WHERE status IS NULL"
            ).rowcount
            
            if requests_updated > 0:
                print(f"✅ Updated {requests_updated} requests with default status")
            
            db.session.commit()
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\n🎉 Database is ready for escrow payments and file uploads!")
        print("\nNext steps:")
        print("1. Set up your AWS S3 bucket and add credentials to .env")
        print("2. Set up your Stripe Connect account and add keys to .env")
        print("3. Restart your application")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)