from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, flash
from revmark.models import User, Request, Message

class AdminAuthMixin:
    """Mixin to require admin authentication for admin views"""
    def is_accessible(self):
        # Check if user is logged in and is admin
        if current_user.is_authenticated:
            # For now, check if email is yours (replace with your email)
            return current_user.email == 'stamound1@outlook.com'
        return False
    
    def inaccessible_callback(self, name, **kwargs):
        flash('You need admin privileges to access this page.', 'danger')
        return redirect(url_for('main.login'))

class AdminHomeView(AdminAuthMixin, AdminIndexView):
    """Custom admin home page"""
    @expose('/')
    def index(self):
        # Get some basic stats
        user_count = User.query.count()
        request_count = Request.query.count()
        message_count = Message.query.count()
        
        return self.render('admin/index.html', 
                         user_count=user_count,
                         request_count=request_count, 
                         message_count=message_count)

class UserAdmin(AdminAuthMixin, ModelView):
    """Admin view for Users"""
    # Columns to display in list view
    column_list = ['id', 'username', 'email', 'requests']
    column_searchable_list = ['username', 'email']
    column_filters = ['username', 'email']
    
    # Don't show password hash
    form_excluded_columns = ['password', 'messages_sent', 'messages_received']
    
    # Custom column formatting
    def _requests_formatter(view, context, model, name):
        return len(model.requests)
    
    column_formatters = {
        'requests': _requests_formatter
    }

class RequestAdmin(AdminAuthMixin, ModelView):
    """Admin view for Requests"""
    column_list = ['id', 'title', 'buyer', 'budget', 'timestamp']
    column_searchable_list = ['title', 'description']
    column_filters = ['buyer.username', 'budget', 'timestamp']
    column_default_sort = ('timestamp', True)
    
    # Custom formatting for description preview
    def _description_formatter(view, context, model, name):
        if model.description:
            return model.description[:100] + '...' if len(model.description) > 100 else model.description
        return ''
    
    column_formatters = {
        'description': _description_formatter
    }

class MessageAdmin(AdminAuthMixin, ModelView):
    """Admin view for Messages"""
    column_list = ['id', 'sender', 'receiver', 'timestamp', 'is_read']
    column_searchable_list = ['body']
    column_filters = ['sender.username', 'receiver.username', 'is_read', 'timestamp']
    column_default_sort = ('timestamp', True)
    
    # Don't allow editing messages
    can_edit = False
    can_create = False
    
    # Custom formatting for message preview
    def _body_formatter(view, context, model, name):
        if model.body:
            return model.body[:50] + '...' if len(model.body) > 50 else model.body
        return ''
    
    column_formatters = {
        'body': _body_formatter
    }

def init_admin(app, db):
    """Initialize admin interface"""
    admin = Admin(
        app, 
        name='RevMark Admin',
        template_mode='bootstrap3',
        index_view=AdminHomeView(name='Dashboard')
    )
    
    # Add model views
    admin.add_view(UserAdmin(User, db.session, name='Users'))
    admin.add_view(RequestAdmin(Request, db.session, name='Requests'))
    admin.add_view(MessageAdmin(Message, db.session, name='Messages'))
    
    return admin
