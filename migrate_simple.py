"""
Simple database creation script for adding escrow payment and file attachment features
"""
import os
import sys
import sqlite3

def add_columns_to_sqlite():
    """Add new columns to existing SQLite database"""
    
    # Path to the SQLite database
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'revmark.db')
    
    if not os.path.exists(db_path):
        print("❌ Database not found. Please run the app first to create the database.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Adding new columns to existing tables...")
        
        # Add new columns to User table
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN stripe_account_id VARCHAR(100)")
            print("✅ Added stripe_account_id to user table")
        except sqlite3.Error:
            print("ℹ️ stripe_account_id column already exists in user table")
            
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN stripe_onboarding_complete BOOLEAN DEFAULT 0")
            print("✅ Added stripe_onboarding_complete to user table")
        except sqlite3.Error:
            print("ℹ️ stripe_onboarding_complete column already exists in user table")
        
        # Add new columns to Request table
        try:
            cursor.execute("ALTER TABLE request ADD COLUMN status VARCHAR(20) DEFAULT 'open'")
            print("✅ Added status to request table")
        except sqlite3.Error:
            print("ℹ️ status column already exists in request table")
            
        try:
            cursor.execute("ALTER TABLE request ADD COLUMN seller_id INTEGER")
            print("✅ Added seller_id to request table")
        except sqlite3.Error:
            print("ℹ️ seller_id column already exists in request table")
            
        try:
            cursor.execute("ALTER TABLE request ADD COLUMN stripe_payment_intent_id VARCHAR(100)")
            print("✅ Added stripe_payment_intent_id to request table")
        except sqlite3.Error:
            print("ℹ️ stripe_payment_intent_id column already exists in request table")
            
        try:
            cursor.execute("ALTER TABLE request ADD COLUMN stripe_transfer_id VARCHAR(100)")
            print("✅ Added stripe_transfer_id to request table")
        except sqlite3.Error:
            print("ℹ️ stripe_transfer_id column already exists in request table")
            
        try:
            cursor.execute("ALTER TABLE request ADD COLUMN escrow_amount FLOAT")
            print("✅ Added escrow_amount to request table")
        except sqlite3.Error:
            print("ℹ️ escrow_amount column already exists in request table")
            
        try:
            cursor.execute("ALTER TABLE request ADD COLUMN platform_fee FLOAT")
            print("✅ Added platform_fee to request table")
        except sqlite3.Error:
            print("ℹ️ platform_fee column already exists in request table")
        
        # Create MessageAttachment table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_attachment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                filename VARCHAR(200) NOT NULL,
                original_filename VARCHAR(200) NOT NULL,
                s3_key VARCHAR(500) NOT NULL,
                file_size INTEGER NOT NULL,
                content_type VARCHAR(100) NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES message (id)
            )
        """)
        print("✅ Created message_attachment table")
        
        # Create EscrowPayment table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS escrow_payment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                buyer_id INTEGER NOT NULL,
                seller_id INTEGER,
                amount FLOAT NOT NULL,
                platform_fee FLOAT NOT NULL,
                seller_amount FLOAT NOT NULL,
                stripe_payment_intent_id VARCHAR(100) NOT NULL UNIQUE,
                stripe_transfer_id VARCHAR(100),
                status VARCHAR(20) DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                FOREIGN KEY (request_id) REFERENCES request (id),
                FOREIGN KEY (buyer_id) REFERENCES user (id),
                FOREIGN KEY (seller_id) REFERENCES user (id)
            )
        """)
        print("✅ Created escrow_payment table")
        
        # Update existing requests with default status
        cursor.execute("UPDATE request SET status = 'open' WHERE status IS NULL")
        requests_updated = cursor.rowcount
        if requests_updated > 0:
            print(f"✅ Updated {requests_updated} requests with default status")
        
        conn.commit()
        conn.close()
        
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = add_columns_to_sqlite()
    if success:
        print("\n🎉 Database is ready for escrow payments and file uploads!")
        print("\nNext steps:")
        print("1. Set up your AWS S3 bucket and add credentials to .env")
        print("2. Set up your Stripe Connect account and add keys to .env")
        print("3. Restart your application")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)