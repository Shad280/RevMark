from datetime import datetime
from revmark import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    requests = db.relationship("Request", backref="buyer", lazy=True)
    messages_sent = db.relationship("Message", foreign_keys="Message.sender_id", backref="sender", lazy=True)
    messages_received = db.relationship("Message", foreign_keys="Message.receiver_id", backref="receiver", lazy=True)
    
    def unread_message_count(self):
        """Count unread messages for this user"""
        return Message.query.filter_by(receiver_id=self.id, is_read=False).count()

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    buyer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    
    def mark_as_read(self):
        """Mark this message as read"""
        self.is_read = True
        db.session.commit()
