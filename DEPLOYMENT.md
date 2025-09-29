# RevMark Deployment Guide

## 🚀 Deploy to Heroku (Recommended for beginners)

### Prerequisites:
1. Install Git: https://git-scm.com/downloads
2. Create Heroku account: https://heroku.com
3. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

### Steps:

1. **Initialize Git Repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create Heroku App:**
   ```bash
   heroku login
   heroku create your-app-name-here
   ```

3. **Configure Database:**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Set Environment Variables:**
   ```bash
   heroku config:set FLASK_APP=app.py
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key-here
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   ```

6. **Initialize Database:**
   ```bash
   heroku run python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

Your app will be live at: https://your-app-name-here.herokuapp.com

---

## 🌐 Alternative Options:

### 2. **Railway** (Modern, Easy)
- Cost: $5/month
- Website: railway.app
- Steps: Connect GitHub repo, auto-deploy

### 3. **DigitalOcean App Platform**
- Cost: $5-12/month
- Website: digitalocean.com/products/app-platform
- Good performance, easy scaling

### 4. **Render** (Free tier available)
- Cost: Free tier, paid from $7/month
- Website: render.com
- Very beginner-friendly

### 5. **AWS/Google Cloud** (Advanced)
- Cost: Variable, pay-as-you-use
- More complex setup but very scalable

---

## 📋 Production Checklist:

### Before Deployment:
- [ ] Add environment variables for production
- [ ] Set up proper database (PostgreSQL)
- [ ] Configure email service for notifications
- [ ] Set up domain name
- [ ] Add SSL certificate (usually automatic)
- [ ] Test all functionality
- [ ] Set up monitoring/logging

### Security Updates Needed:
1. **Environment Variables:** Move secret key to environment variable
2. **Database:** Switch from SQLite to PostgreSQL
3. **Email:** Configure email service for user notifications
4. **Logging:** Add proper error logging
5. **HTTPS:** Ensure SSL is enabled (usually automatic on platforms)

---

## 💰 Cost Breakdown:

| Platform | Free Tier | Paid Plans |
|----------|-----------|------------|
| Heroku | Limited hours | $7-25/month |
| Railway | No | $5/month |
| Render | Yes | $7/month |
| DigitalOcean | $200 credit | $5-12/month |

**Recommendation:** Start with Heroku free tier to test, then upgrade as needed.
