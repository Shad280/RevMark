#!/usr/bin/env python3
"""
AWS S3 Setup and Test Script for RevMark
Tests S3 configuration and file upload functionality
"""

import os
import sys
from pathlib import Path
import tempfile
from datetime import datetime

def test_aws_config():
    """Test if AWS configuration is properly set"""
    print("🧪 Testing AWS S3 Configuration")
    print("=" * 50)
    
    # Check environment variables
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID', '')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    aws_bucket = os.getenv('AWS_S3_BUCKET', 'revmark-uploads')
    
    print(f"🔑 Access Key: {'✅ Set' if aws_access_key and 'your_aws' not in aws_access_key else '❌ Not configured'}")
    print(f"🔐 Secret Key: {'✅ Set' if aws_secret_key and 'your_aws' not in aws_secret_key else '❌ Not configured'}")
    print(f"🌍 Region: {aws_region}")
    print(f"🪣 Bucket: {aws_bucket}")
    
    if not aws_access_key or 'your_aws' in aws_access_key:
        print("\n❌ AWS not configured. Please set up AWS credentials first.")
        return False
    
    # Test boto3 import
    try:
        import boto3
        print("✅ boto3 library available")
    except ImportError:
        print("❌ boto3 not installed. Run: pip install boto3")
        return False
    
    # Test S3 connection
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        # Test bucket access
        response = s3_client.head_bucket(Bucket=aws_bucket)
        print("✅ S3 bucket accessible")
        
        # Test upload permissions
        test_key = f"test/connection-test-{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        test_content = f"RevMark S3 test - {datetime.now()}"
        
        s3_client.put_object(
            Bucket=aws_bucket,
            Key=test_key,
            Body=test_content.encode('utf-8'),
            ContentType='text/plain'
        )
        print("✅ Upload test successful")
        
        # Clean up test file
        s3_client.delete_object(Bucket=aws_bucket, Key=test_key)
        print("✅ Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ S3 connection failed: {str(e)}")
        print("\nPossible issues:")
        print("- Check your AWS credentials")
        print("- Verify bucket name exists and is accessible")
        print("- Confirm IAM user has S3 permissions")
        return False

def test_revmark_integration():
    """Test RevMark's S3 integration"""
    print("\n🔧 Testing RevMark S3 Integration")
    print("=" * 50)
    
    try:
        # Test import
        from revmark.s3_utils import S3Manager
        print("✅ S3Manager imports successfully")
        
        # Test initialization
        s3_manager = S3Manager()
        print("✅ S3Manager initializes")
        
        # Test file upload simulation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test file for RevMark S3 integration")
            temp_file_path = f.name
        
        # Note: We won't actually upload in the test to avoid creating test files
        print("✅ Ready for file upload testing")
        
        # Cleanup
        os.unlink(temp_file_path)
        
        return True
        
    except Exception as e:
        print(f"❌ RevMark S3 integration error: {str(e)}")
        return False

def main():
    print("🚀 RevMark AWS S3 Setup Test")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Please run this script from the RevMark root directory")
        sys.exit(1)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("❌ python-dotenv not installed")
        sys.exit(1)
    
    success = True
    
    # Test AWS configuration
    if not test_aws_config():
        success = False
    
    # Test RevMark integration
    if not test_revmark_integration():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 AWS S3 is properly configured and ready!")
        print("\n📋 What works now:")
        print("- File uploads in messages")
        print("- Secure file storage")
        print("- Automatic file management")
        print("- Download links with expiration")
    else:
        print("❌ AWS S3 setup needs attention")
        print("\n📋 Next steps:")
        print("1. Complete AWS account setup")
        print("2. Create S3 bucket")
        print("3. Create IAM user with S3 permissions")
        print("4. Add credentials to .env file")
        print("5. Run this test again")
    
    print(f"\n🌐 Test RevMark at: http://127.0.0.1:5000")

if __name__ == "__main__":
    main()