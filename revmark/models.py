from datetime import datetime
from revmark import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    
    # Stripe Connect Account ID for sellers
    stripe_account_id = db.Column(db.String(100), nullable=True)
    stripe_onboarding_complete = db.Column(db.Boolean, default=False)
    
    # Define relationships with explicit foreign_keys to avoid ambiguity
    messages_sent = db.relationship("Message", foreign_keys="Message.sender_id", backref="sender", lazy=True)
    messages_received = db.relationship("Message", foreign_keys="Message.receiver_id", backref="receiver", lazy=True)
    
    def unread_message_count(self):
        """Count unread messages for this user"""
        return Message.query.filter_by(receiver_id=self.id, is_read=False).count()
    
    @property
    def is_verified_seller(self):
        """Check if user is a verified seller with completed Stripe onboarding"""
        return self.stripe_account_id is not None and self.stripe_onboarding_complete
    
    @property
    def can_receive_payments(self):
        """Check if user can receive payments (alias for is_verified_seller)"""
        return self.is_verified_seller

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    
    # Escrow payment fields
    status = db.Column(db.String(20), default='open', index=True)  # open, funded, in_progress, completed, cancelled
    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)
    stripe_payment_intent_id = db.Column(db.String(100), nullable=True)
    stripe_transfer_id = db.Column(db.String(100), nullable=True)
    escrow_amount = db.Column(db.Float, nullable=True)  # Amount held in escrow
    platform_fee = db.Column(db.Float, nullable=True)   # Platform fee amount
    
    # Relationships with explicit foreign keys to avoid ambiguity
    buyer = db.relationship("User", foreign_keys=[buyer_id], backref="bought_requests")
    seller = db.relationship("User", foreign_keys=[seller_id], backref="sold_requests")
    payments = db.relationship("EscrowPayment", backref="request", lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)

    # Offer-related fields
    is_offer = db.Column(db.Boolean, default=False, nullable=False, index=True)
    offer_approved = db.Column(db.Boolean, default=False, nullable=False, index=True)
    offer_rejected = db.Column(db.Boolean, default=False, nullable=False, index=True)

    # File attachments
    attachments = db.relationship("MessageAttachment", backref="message", lazy=True, cascade="all, delete-orphan")

    def mark_as_read(self):
        """Mark this message as read"""
        self.is_read = True
        db.session.commit()

class MessageAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey("message.id"), nullable=False, index=True)
    filename = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(200), nullable=False)
    s3_key = db.Column(db.String(500), nullable=False)  # S3 object key
    file_size = db.Column(db.Integer, nullable=False)   # File size in bytes
    content_type = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class EscrowPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("request.id"), nullable=False, index=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)
    
    # Payment details
    amount = db.Column(db.Float, nullable=False)
    platform_fee = db.Column(db.Float, nullable=False)
    seller_amount = db.Column(db.Float, nullable=False)  # Amount after platform fee
    
    # Stripe IDs
    stripe_payment_intent_id = db.Column(db.String(100), nullable=False, unique=True)
    stripe_transfer_id = db.Column(db.String(100), nullable=True)
    
    # Status tracking
    status = db.Column(db.String(20), default='pending', index=True)  # pending, completed, failed, refunded
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships with explicit foreign keys
    buyer = db.relationship("User", foreign_keys=[buyer_id], backref="buyer_payments")
    seller = db.relationship("User", foreign_keys=[seller_id], backref="seller_payments")
