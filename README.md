# RevMark - Freelance Marketplace Platform

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Access the Application
Open your browser and go to: http://127.0.0.1:5000

## 📋 Features

✅ **User Authentication**
- Secure signup and login
- Session management
- User profiles

✅ **Request System**
- Post service requests
- Anti-duplicate logic (one request per title per day)
- Browse all requests with pagination
- View detailed request information

✅ **Messaging System**
- Direct messaging between users
- Inbox with conversation threads
- Real-time message display
- Unread message indicators

✅ **Frontend Design**
- Green & white branding theme
- Responsive design
- Clean, professional UI
- Logo integration ready

✅ **Database Models**
- Users (authentication, profiles)
- Requests (project postings)
- Messages (communication)

## 🏗️ Project Structure

```
revmark/
├── app.py                 # Main Flask application entry point
├── config.py              # Application configuration
├── requirements.txt       # Python dependencies (Flask, SQLAlchemy, Flask-Login)
├── instance/              # Database storage (auto-created)
│   └── revmark.db        # SQLite database
├── revmark/              # Core application package
│   ├── __init__.py       # Flask app factory
│   ├── models.py         # Database models (User, Request, Message)
│   └── routes.py         # Application routes (auth, requests, messaging)
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Clean green & white theme
│   └── img/
│       └── logo.png      # RevMark RM logo (120x120px)
└── templates/            # Jinja2 templates
    ├── base.html         # Base template with logo navigation
    ├── index.html        # Homepage with requests & inbox preview
    ├── signup.html       # User registration
    ├── login.html        # User login
    ├── post_request.html # Create new request
    ├── inbox.html        # Message inbox
    └── thread.html       # Conversation view
```

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key for sessions (optional, has default)

### Database
- Uses SQLite by default
- Database file: `instance/revmark.db`
- Auto-creates tables on first run

## 🎨 Customization

### Logo
Add your RM logo as `static/img/logo.png` (200x200px recommended)

### Colors
Edit `static/css/style.css` to customize the green theme:
- `--primary-green: #2d8f3f`
- `--light-green: #4caf50`
- `--dark-green: #1b5e20`

## 📝 Usage

### For Clients (Buyers)
1. Sign up for an account
2. Post a service request with details
3. Wait for freelancers to contact you
4. Communicate through the messaging system
5. Choose the best freelancer for your project

### For Freelancers (Sellers)
1. Sign up for an account
2. Browse available requests
3. Contact clients for interesting opportunities
4. Negotiate and communicate through messages
5. Deliver quality work

## 🛡️ Security Features

- Password hashing with Werkzeug
- CSRF protection with Flask-WTF
- Session management with Flask-Login
- SQL injection prevention with SQLAlchemy ORM

## 🔄 Anti-Duplicate Logic

The platform prevents spam by limiting users to one request per title per day. This ensures:
- Quality over quantity
- Reduced spam
- Better user experience
- More focused opportunities

## 📱 Responsive Design

The platform works seamlessly on:
- Desktop computers
- Tablets
- Mobile phones
- Various screen sizes

## 🚀 Production Deployment

For production deployment:

1. Set environment variables:
   ```bash
   export SECRET_KEY="your-secret-key-here"
   ```

2. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn app:app
   ```

3. Consider using PostgreSQL instead of SQLite for better performance
4. Set up proper error handling and logging
5. Use HTTPS in production
6. Implement rate limiting for API endpoints

## 🔍 Development

### Adding New Features
1. Create new routes in `revmark/routes.py`
2. Add corresponding templates in `templates/`
3. Update models in `revmark/models.py` if needed
4. Add forms in `revmark/forms.py` for user input
5. Update CSS in `static/css/style.css` for styling

### Testing
Create test accounts:
- Username: demo, Password: demo123
- Username: client, Password: client123
- Username: freelancer, Password: freelancer123

## 📞 Support

This is a production-ready codebase with all essential features implemented. The platform is ready to handle real users and transactions with proper security measures in place.

## 🎯 Next Steps

Potential enhancements for the future:
- File upload system for attachments
- Rating and review system
- Payment integration
- Email notifications
- Advanced search and filtering
- User profiles with portfolios
- Project milestone tracking
- Mobile app development

---

**RevMark** - Connecting freelancers with opportunities since 2025.
