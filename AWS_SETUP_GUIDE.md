# 🚀 AWS S3 Setup Guide for RevMark

## Overview
AWS S3 enables file uploads in RevMark messages and requests. Users can attach documents, images, and other files.

## 📋 Step-by-Step Setup

### 1. Create AWS Account
- Go to: https://aws.amazon.com
- Click "Create an AWS Account"
- Complete registration (credit card required, but S3 free tier is generous)

### 2. Create S3 Bucket
1. **Login to AWS Console**: https://console.aws.amazon.com
2. **Search for "S3"** and click the service
3. **Click "Create bucket"**
4. **Configure bucket**:
   ```
   Bucket name: revmark-uploads-yourusername
   Region: US East (N. Virginia) us-east-1
   Block all public access: ✅ CHECKED
   Bucket versioning: Disabled
   Default encryption: Enabled (recommended)
   ```
5. **Click "Create bucket"**

### 3. Create IAM User
1. **Search for "IAM"** in AWS Console
2. **Users → Create user**
3. **User details**:
   ```
   Username: revmark-s3-user
   Access type: Programmatic access
   ```
4. **Permissions**:
   - Click "Attach existing policies directly"
   - Search and select: **AmazonS3FullAccess**
5. **Create user**

### 4. Get Access Keys
1. **Click on the created user**
2. **Security credentials tab**
3. **Create access key**
4. **Choose "Application running outside AWS"**
5. **Copy the credentials**:
   - Access Key ID: `AKIA...`
   - Secret Access Key: `(long string - only shown once)`

### 5. Update RevMark Configuration
Update your `.env` file:
```bash
AWS_ACCESS_KEY_ID=AKIA1234567890EXAMPLE
AWS_SECRET_ACCESS_KEY=your-actual-secret-key-here
AWS_REGION=us-east-1
AWS_S3_BUCKET=revmark-uploads-yourusername
```

### 6. Install AWS Dependencies
```bash
pip install boto3
```

### 7. Test the Setup
```bash
python aws_setup_test.py
```

## 🧪 Testing File Uploads

Once configured, you can test:

1. **Send a message** with file attachment
2. **Upload profile pictures** (future feature)
3. **Attach documents** to requests

## 📊 AWS Costs

**S3 Free Tier (first 12 months):**
- 5 GB storage
- 20,000 GET requests
- 2,000 PUT requests

**After free tier:**
- Storage: ~$0.023 per GB/month
- Requests: ~$0.0004 per 1,000 requests

For a small marketplace, costs are typically under $5/month.

## 🔒 Security Features

- **Private uploads**: Files not publicly accessible
- **Presigned URLs**: Temporary download links
- **IAM permissions**: Restricted access
- **File type validation**: Only allowed formats
- **Size limits**: Prevents abuse

## 🚨 Troubleshooting

### Common Issues:
1. **"Access Denied"**: Check IAM permissions
2. **"Bucket not found"**: Verify bucket name and region
3. **"Credentials not found"**: Check .env file values
4. **"Import error"**: Run `pip install boto3`

### Debug Commands:
```bash
# Test AWS credentials
python aws_setup_test.py

# Check environment variables
python -c "import os; print(f'AWS Key: {os.getenv(\"AWS_ACCESS_KEY_ID\", \"Not set\")[:8]}...')"

# Test S3 connection
python -c "import boto3; print(boto3.client('s3').list_buckets())"
```

## 🎯 What This Enables

**Message Attachments:**
- Users can attach files to messages
- Automatic file type validation
- Secure download links

**Request Enhancement:**
- Attach project files
- Share design mockups
- Include requirement documents

**Future Features:**
- User profile pictures
- Portfolio uploads
- File sharing between users

---

**Ready to set up AWS? Follow the steps above, then run the test script!** 🚀