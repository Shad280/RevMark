# RevMark AWS S3 & Stripe Connect Setup Guide

## 🎉 Features Added

Your RevMark platform now includes:

### ✅ AWS S3 File Uploads
- Secure file attachments in messages
- Support for images, PDFs, and documents
- Private file storage with temporary access URLs
- File size and type validation

### ✅ Stripe Connect Escrow Payments  
- Secure escrow payment system
- Automatic platform fee collection (5% default)
- Seller onboarding with Stripe Connect
- Payment release and refund capabilities

## 🛠️ Setup Instructions

### 1. Set Up AWS S3

1. **Create AWS Account & S3 Bucket:**
   - Go to [AWS Console](https://console.aws.amazon.com/) → S3
   - Click "Create bucket"
   - Bucket name: `revmark-uploads` (or your preferred name)
   - Region: Choose one close to your users (e.g., `us-east-1`)
   - **Keep "Block public access" ON** ✅ (we use signed URLs)

2. **Create IAM User:**
   - Go to AWS Console → IAM → Users → Add user
   - Username: `revmark-uploader`
   - Access type: Programmatic access
   - Permissions: Attach policy `AmazonS3FullAccess` (narrow down later for security)
   - **Save the Access Key ID and Secret Access Key** 🔑

### 2. Set Up Stripe Connect

1. **Create Stripe Account:**
   - Go to [Stripe Dashboard](https://dashboard.stripe.com/)
   - Navigate to Settings → Connect
   - Enable "Platform or Marketplace" mode
   - Choose "Express accounts" (recommended)

2. **Get API Keys:**
   - Go to Developers → API keys
   - Copy your Publishable key and Secret key
   - For webhooks: Developers → Webhooks → Add endpoint

### 3. Configure Environment Variables

Create a `.env` file in your project root:

```env
# Database Configuration
DATABASE_URL=your_database_url_here
SECRET_KEY=your_secret_key_here

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=AKIA...your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=us-east-1
AWS_S3_BUCKET=revmark-uploads

# Stripe Configuration
STRIPE_PUBLIC_KEY=pk_test_...your_public_key
STRIPE_SECRET_KEY=sk_test_...your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_...your_webhook_secret

# Platform Settings
PLATFORM_FEE_PERCENTAGE=5.0

# App Settings (for production)
BASE_URL=https://your-domain.com
```

### 4. Install Dependencies

The required packages are already in your `requirements.txt`:
- `boto3` for AWS S3
- `stripe` for payments
- `python-dotenv` for environment variables

Run:
```bash
pip install -r requirements.txt
```

### 5. Database Migration

✅ **Already completed!** Your database now includes:
- New user fields for Stripe Connect accounts
- Enhanced request model with payment status
- Message attachments table
- Escrow payments tracking table

## 🚀 How It Works

### File Uploads
1. Users can attach files when sending messages
2. Files are uploaded to your private S3 bucket
3. Temporary signed URLs are generated for access
4. Only message participants can download files

### Escrow Payments
1. **Buyer funds a request** → Money held in escrow
2. **Seller completes work** → Provides deliverables
3. **Buyer approves work** → Payment released to seller
4. **Platform fee deducted** → Your revenue (5% default)

### User Flow
1. **Sellers** must complete Stripe Connect onboarding
2. **Buyers** can fund requests with credit/debit cards
3. **Communication** happens through enhanced messaging
4. **Payments** are released when work is approved

## 🔗 New URLs Available

- `/payment/<request_id>` - Fund/manage request payments
- `/api/upload` - File upload endpoint
- `/api/seller/connect` - Create seller account
- `/api/payment/create-intent` - Create payment
- `/api/payment/release` - Release payment to seller
- `/api/payment/refund` - Refund payment to buyer

## 🛡️ Security Features

- **Private S3 storage** with temporary access
- **File type validation** (images, PDFs, docs only)
- **File size limits** (16MB default)
- **Secure payment processing** via Stripe
- **Platform fee protection** (automatic deduction)
- **Access control** (users can only see their files/payments)

## 📱 New UI Elements

- ✅ File attachment in messaging
- ✅ Payment status badges
- ✅ Escrow payment forms
- ✅ Seller onboarding flow
- ✅ Payment history tracking

## 🧪 Testing

1. **Test File Uploads:**
   - Send a message with an image attachment
   - Verify file appears in S3 bucket
   - Check download links work

2. **Test Payments:**
   - Create a test request
   - Fund it with Stripe test card: `4242 4242 4242 4242`
   - Complete seller onboarding
   - Release payment and verify transfer

## 🚨 Production Checklist

Before going live:

- [ ] Replace Stripe test keys with live keys
- [ ] Set up Stripe webhooks for production
- [ ] Configure proper S3 bucket policies
- [ ] Set up monitoring and alerts
- [ ] Test the complete payment flow
- [ ] Configure backup strategy
- [ ] Set up SSL/HTTPS
- [ ] Update BASE_URL in .env

## 💰 Revenue Model

With 5% platform fee:
- $100 transaction = $5 to platform, $95 to seller
- Automatic fee collection via Stripe Connect
- No manual intervention required

## 🆘 Troubleshooting

**AWS Issues:**
- Check IAM permissions for S3 access
- Verify bucket name and region
- Test AWS credentials

**Stripe Issues:**
- Verify API keys are correct
- Check Connect account status
- Test with Stripe CLI for webhooks

**File Upload Issues:**
- Check file size limits
- Verify allowed file extensions
- Check S3 connectivity

Your RevMark platform is now ready for secure escrow payments and file sharing! 🚀