from datetime import datetime
from revmark.models import Message, User

def get_unread_message_count(user_id):
    """Get the count of unread messages for a user"""
    return Message.query.filter_by(receiver_id=user_id).count()

def format_timestamp(timestamp):
    """Format timestamp for display"""
    now = datetime.utcnow()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}h ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}m ago"
    else:
        return "Just now"

def get_conversation_partner(message, current_user_id):
    """Get the other user in a conversation"""
    if message.sender_id == current_user_id:
        return User.query.get(message.receiver_id)
    else:
        return User.query.get(message.sender_id)
