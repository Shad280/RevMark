#!/bin/bash
# Quick Heroku Deployment Script

echo "🚀 RevMark Heroku Deployment Script"
echo "=================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial RevMark commit"
else
    echo "✅ Git repository already initialized"
fi

# Get app name from user
read -p "Enter your Heroku app name (lowercase, no spaces): " app_name

if [ -z "$app_name" ]; then
    echo "❌ App name is required!"
    exit 1
fi

echo "🌐 Creating Heroku app: $app_name"
heroku create $app_name

echo "🗄️ Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:mini -a $app_name

echo "🔧 Setting environment variables..."
heroku config:set FLASK_APP=app.py -a $app_name
heroku config:set FLASK_ENV=production -a $app_name
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))") -a $app_name

echo "📤 Deploying to Heroku..."
git add .
git commit -m "Deploy to Heroku" || echo "No changes to commit"
git push heroku main

echo "🗄️ Initializing database..."
heroku run python -c "from app import app, db; app.app_context().push(); db.create_all()" -a $app_name

echo "🎉 Deployment complete!"
echo "Your app is live at: https://$app_name.herokuapp.com"
