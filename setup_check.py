#!/usr/bin/env python3
"""
RevMark Quick Setup Script
Helps configure environment variables and test the setup
"""

import os
import sys
from pathlib import Path

def main():
    print("🚀 RevMark Quick Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Please run this script from the RevMark root directory")
        sys.exit(1)
    
    # Check if .env exists
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("📋 Creating .env file from .env.example...")
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ Created .env file")
        else:
            print("❌ No .env.example found")
            return
    
    # Read current .env
    env_vars = {}
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    print("\n🔍 Checking configuration...")
    
    # Check Stripe configuration
    stripe_pk = env_vars.get('STRIPE_PUBLIC_KEY', '')
    stripe_sk = env_vars.get('STRIPE_SECRET_KEY', '')
    stripe_configured = all([
        stripe_pk.startswith('pk_') and 'your_stripe_public_key_here' not in stripe_pk,
        stripe_sk.startswith('sk_') and 'your_stripe_secret_key_here' not in stripe_sk,
    ])
    
    print(f"💳 Stripe: {'✅ Configured' if stripe_configured else '❌ Not configured'}")
    
    # Check AWS configuration  
    aws_configured = all([
        env_vars.get('AWS_ACCESS_KEY_ID', '').replace('your_', '') != 'aws_access_key_here',
        env_vars.get('AWS_SECRET_ACCESS_KEY', '').replace('your_', '') != 'aws_secret_key_here',
        env_vars.get('AWS_S3_BUCKET', '').replace('your-', '') != 'bucket-name'
    ])
    
    print(f"📁 AWS S3: {'✅ Configured' if aws_configured else '❌ Not configured (optional)'}")
    
    # Check database
    db_url = env_vars.get('DATABASE_URL', '')
    if 'postgresql' in db_url:
        print("🗄️  Database: ✅ PostgreSQL configured")
    else:
        print("🗄️  Database: ℹ️  Using SQLite (development)")
    
    print("\n📋 Next Steps:")
    
    if not stripe_configured:
        print("1. 💳 Set up Stripe (REQUIRED for payments):")
        print("   - Go to https://dashboard.stripe.com")
        print("   - Get your test API keys")
        print("   - Update STRIPE_PUBLIC_KEY and STRIPE_SECRET_KEY in .env")
        print("   - Set up webhook endpoint for payments")
    
    if not aws_configured:
        print("2. 📁 Set up AWS S3 (optional for file uploads):")
        print("   - Create AWS account and S3 bucket")
        print("   - Create IAM user with S3 permissions")
        print("   - Update AWS_* variables in .env")
    
    if 'postgresql' not in db_url:
        print("3. 🗄️  Set up PostgreSQL (for production):")
        print("   - Use Railway, AWS RDS, or local PostgreSQL")
        print("   - Update DATABASE_URL in .env")
        print("   - Run: python create_tables.py")
    
    print("\n🎯 Quick Test Commands:")
    print("   python app.py                    # Start the application")
    print("   python create_tables.py          # Set up database tables")
    print("   python -c 'import revmark; print(\"✅ Import successful\")'")
    
    print("\n📚 For detailed setup instructions, see:")
    print("   - NEXT_STEPS_SETUP.md")
    print("   - STRIPE_CONNECT_IMPLEMENTATION.md")
    
    # Test basic imports
    print("\n🧪 Testing basic functionality...")
    try:
        import revmark
        print("✅ RevMark imports successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Try: pip install -r requirements.txt")
    
    # Check database
    try:
        from revmark import db
        print("✅ Database connection available")
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    print("\n🚀 RevMark setup check complete!")
    print("   Visit http://127.0.0.1:5000 once the app is running")

if __name__ == "__main__":
    main()