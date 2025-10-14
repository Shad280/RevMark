from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from revmark import db, cache
from revmark.utils.email_utils import send_email
from revmark.models import User, Request, Message, MessageAttachment, EscrowPayment

bp = Blueprint("main", __name__)

# ---------- PAGES ----------
@bp.route("/")
def index():
    page = request.args.get('page', 1, type=int)
    requests = Request.query.order_by(Request.timestamp.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    return render_template("index.html", requests=requests)

@bp.route("/about")
def about():
    return render_template("about.html")

@bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        # Send email to site admin (change recipient as needed)
        admin_email = current_app.config.get("MAIL_DEFAULT_SENDER", (None, "admin@example.com"))[1]
        body = f"Contact form submission from {name} <{email}>\n\nSubject: {subject}\n\nMessage:\n{message}"
        try:
            send_email(f"[RevMark Contact] {subject}", [admin_email], body)
            flash(f"Thank you {name}! Your message has been sent. We'll get back to you at {email} soon.", "success")
        except Exception as e:
            flash(f"Sorry, there was an error sending your message. Please try again later.", "danger")
        return redirect(url_for("main.contact"))

    return render_template("contact.html")

# ---------- AUTH ----------
@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("main.signup"))

        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("main.login"))

    return render_template("signup.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for("main.login"))

    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out.", "info")
    return redirect(url_for("main.index"))


# ---------- POST REQUEST ----------
@bp.route("/post_request", methods=["GET", "POST"])
@login_required
def post_request():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        budget = request.form.get("budget")

        # Prevent duplicate requests (title+description from same user)
        duplicate = Request.query.filter_by(
            title=title, description=description, buyer_id=current_user.id
        ).first()
        if duplicate:
            flash("You already posted this request.", "warning")
            return redirect(url_for("main.post_request"))

        new_request = Request(
            title=title,
            description=description,
            budget=float(budget) if budget else None,
            buyer=current_user
        )
        db.session.add(new_request)
        db.session.commit()
        flash("Request posted successfully!", "success")
        return redirect(url_for("main.index"))

    return render_template("post_request.html")


# ---------- INBOX ----------
@bp.route("/inbox")
@login_required
def inbox():
    # All messages where user is receiver
    messages = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.timestamp.desc()).all()
    
    # Mark all messages as read when user visits inbox
    unread_messages = Message.query.filter_by(receiver_id=current_user.id, is_read=False).all()
    for message in unread_messages:
        message.is_read = True
    if unread_messages:
        db.session.commit()
    
    return render_template("inbox.html", messages=messages)


@bp.route("/message/<int:receiver_id>", methods=["GET", "POST"])
@login_required
def message(receiver_id):
    receiver = User.query.get_or_404(receiver_id)

    if request.method == "POST":
        body = request.form["body"]
        msg = Message(body=body, sender=current_user, receiver=receiver)
        db.session.add(msg)
        db.session.flush()  # Get the message ID
        
        # Handle file attachments
        if 'attachments' in request.files:
            files = request.files.getlist('attachments')
            for file in files:
                if file and file.filename:
                    try:
                        # Check if AWS S3 is configured
                        if not current_app.config.get('AWS_ACCESS_KEY_ID'):
                            flash("File upload not available (AWS S3 not configured)", "warning")
                            continue
                            
                        # Upload to S3
                        from revmark.s3_utils import s3_manager
                        file_info = s3_manager.upload_file(file, folder="message-attachments")
                        
                        # Create attachment record
                        attachment = MessageAttachment(
                            message_id=msg.id,
                            filename=file_info['s3_key'].split('/')[-1],
                            original_filename=file_info['original_filename'],
                            s3_key=file_info['s3_key'],
                            file_size=file_info['file_size'],
                            content_type=file_info['content_type']
                        )
                        db.session.add(attachment)
                    except Exception as e:
                        flash(f"Failed to upload {file.filename}: File upload service unavailable", "warning")
        
        db.session.commit()
        # Send email notification to receiver
        try:
            recipient = receiver.email
            subject = f"New message from {current_user.username} on RevMark"
            body = f"You have a new message from {current_user.username}:\n\n{body}\n\nView the conversation in your RevMark inbox."
            send_email(subject, [recipient], body)
        except Exception:
            current_app.logger.exception("Failed to send message notification email")

        flash("Message sent!", "success")
        return redirect(url_for("main.message", receiver_id=receiver.id))

    # Conversation thread
    thread = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == receiver.id)) |
        ((Message.sender_id == receiver.id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()

    return render_template("thread.html", receiver=receiver, thread=thread)


# ---------- BROWSE & VIEW REQUESTS ----------
@bp.route("/browse")
def browse_requests():
    page = request.args.get('page', 1, type=int)
    requests = Request.query.order_by(Request.timestamp.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template("browse_requests.html", requests=requests)


@bp.route("/request/<int:request_id>")
def view_request(request_id):
    request_item = Request.query.get_or_404(request_id)
    return render_template("view_request.html", request=request_item)


# ---------- PAYMENT ROUTES ----------
@bp.route("/payment/<int:request_id>")
@login_required
def payment(request_id):
    """Show payment page for a request"""
    request_obj = Request.query.get_or_404(request_id)
    
    # Check if user is the buyer
    if request_obj.buyer_id != current_user.id:
        flash("Access denied. You can only fund your own requests.", "danger")
        return redirect(url_for("main.view_request", request_id=request_id))
    
    # Check if Stripe is configured
    if not current_app.config.get('STRIPE_PUBLIC_KEY'):
        flash("Payment processing not available. Please contact support.", "warning")
        return redirect(url_for("main.view_request", request_id=request_id))
    
    # Get seller if assigned
    seller = None
    if request_obj.seller_id:
        seller = User.query.get(request_obj.seller_id)
    
    return render_template("payment.html", 
                         request=request_obj, 
                         seller=seller,
                         stripe_public_key=current_app.config.get('STRIPE_PUBLIC_KEY'),
                         platform_fee=current_app.config.get('PLATFORM_FEE_PERCENTAGE', 5.0))

@bp.route("/seller/onboarding/complete")
@login_required
def seller_onboarding_complete():
    """Handle successful Stripe Connect onboarding"""
    if not current_user.stripe_account_id:
        flash("No seller account found. Please contact support.", "danger")
        return redirect(url_for("main.account"))
    
    # Update onboarding status
    from revmark.stripe_utils import stripe_manager
    try:
        status = stripe_manager.get_account_status(current_user.stripe_account_id)
        if status:
            current_user.stripe_onboarding_complete = (
                status['charges_enabled'] and 
                status['payouts_enabled'] and 
                status['details_submitted']
            )
            db.session.commit()
            
        if current_user.stripe_onboarding_complete:
            flash("Congratulations! Your seller account is now active. You can start receiving payments.", "success")
        else:
            flash("Your seller account is being reviewed. You'll be able to receive payments once approved.", "info")
            
    except Exception as e:
        flash("There was an issue verifying your account. Please try again later.", "warning")
    
    return redirect(url_for("main.account"))

@bp.route("/seller/onboarding/refresh")
@login_required
def seller_onboarding_refresh():
    """Handle Stripe Connect onboarding refresh"""
    flash("Please complete your seller account setup to start receiving payments.", "info")
    return redirect(url_for("main.account"))


# ---------- ACCOUNT MANAGEMENT ----------
@bp.route("/account")
@login_required
def account():
    tab = request.args.get('tab', 'profile')  # Default to profile tab
    user_requests = Request.query.filter_by(buyer_id=current_user.id).order_by(Request.timestamp.desc()).all()
    return render_template("account.html", requests=user_requests, active_tab=tab)


@bp.route("/delete_request/<int:request_id>", methods=["POST"])
@login_required
def delete_request(request_id):
    request_item = Request.query.get_or_404(request_id)
    
    # Check if user owns this request
    if request_item.buyer_id != current_user.id:
        flash("You can only delete your own requests!", "danger")
        return redirect(url_for("main.account"))
    
    # Delete the request
    db.session.delete(request_item)
    db.session.commit()
    flash("Request deleted successfully!", "success")
    return redirect(url_for("main.account"))


# ---------- SEO ROUTES ----------
@bp.route("/sitemap.xml")
def sitemap():
    from flask import make_response, send_from_directory
    import os
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    response = make_response(send_from_directory(static_dir, 'sitemap.xml'))
    response.headers["Content-Type"] = "application/xml"
    return response

@bp.route("/robots.txt")
def robots():
    from flask import make_response, send_from_directory
    import os
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    response = make_response(send_from_directory(static_dir, 'robots.txt'))
    response.headers["Content-Type"] = "text/plain"
    return response

@bp.route("/google02fb930af811e7de.html")
def google_verification():
    from flask import Response
    return Response("google-site-verification: google02fb930af811e7de.html", mimetype='text/html')

@bp.route("/BingSiteAuth.xml")
def bing_verification():
    from flask import Response
    xml_content = """<?xml version="1.0"?>
<users>
    <user>BING_VERIFICATION_CODE_HERE</user>
</users>"""
    return Response(xml_content, mimetype='application/xml')

# ---------- STRIPE CONNECT ----------
@bp.route("/seller/dashboard")
@login_required
def seller_dashboard():
    """Redirect to account page with seller tab active"""
    return redirect(url_for('main.account', tab='seller'))

@bp.route("/stripe/onboard", methods=["POST"])
@login_required
def onboard_seller():
    """Create Stripe Connect onboarding link for seller"""
    from revmark.stripe_utils import StripeManager
    import json
    
    try:
        stripe_manager = StripeManager()
        
        # Create or retrieve Stripe account
        if not current_user.stripe_account_id:
            # Create new connected account
            account = stripe_manager.create_connect_account(
                email=current_user.email,
                user_id=current_user.id
            )
            
            # Save account ID to user
            current_user.stripe_account_id = account['id']
            db.session.commit()
        
        # Create onboarding link
        account_link = stripe_manager.create_account_link(
            account_id=current_user.stripe_account_id,
            return_url=url_for('main.stripe_onboard_complete', _external=True),
            refresh_url=url_for('main.stripe_onboard_refresh', _external=True)
        )
        
        return {"success": True, "url": account_link['url']}
        
    except Exception as e:
        current_app.logger.error(f"Stripe onboarding error: {str(e)}")
        return {"success": False, "error": str(e)}, 400

@bp.route("/stripe/onboard/complete")
@login_required  
def stripe_onboard_complete():
    """Handle successful Stripe onboarding completion"""
    from revmark.stripe_utils import StripeManager
    
    try:
        stripe_manager = StripeManager()
        
        if current_user.stripe_account_id:
            # Check account status
            account = stripe_manager.get_account(current_user.stripe_account_id)
            
            # Update onboarding status based on account details
            if account.get('details_submitted') and account.get('charges_enabled'):
                current_user.stripe_onboarding_complete = True
                db.session.commit()
                flash("🎉 Stripe account connected successfully! You can now receive payments.", "success")
            else:
                flash("Please complete your Stripe account setup to receive payments.", "warning")
        
        return redirect(url_for('main.seller_dashboard'))
        
    except Exception as e:
        current_app.logger.error(f"Stripe onboarding completion error: {str(e)}")
        flash("There was an issue completing your Stripe setup. Please try again.", "danger")
        return redirect(url_for('main.seller_dashboard'))

@bp.route("/stripe/onboard/refresh")
@login_required
def stripe_onboard_refresh():
    """Handle Stripe onboarding refresh/retry"""
    flash("Let's try connecting your Stripe account again.", "info")
    return redirect(url_for('main.seller_dashboard'))


@bp.route('/admin/test-email')
@login_required
def admin_test_email():
    """Send a test email to the current user to verify SMTP is working."""
    try:
        recipient = current_user.email
        subject = "RevMark test email"
        body = f"Hello {current_user.username},\n\nThis is a test email from RevMark to verify outgoing email is configured correctly."
        send_email(subject, [recipient], body)
        flash("Test email sent — check your inbox.", "success")
    except Exception:
        current_app.logger.exception("Failed to send test email")
        flash("Failed to send test email. Check logs and SMTP settings.", "danger")
    return redirect(url_for('main.account'))

@bp.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhooks for payment and account events"""
    from revmark.stripe_utils import StripeManager
    import stripe
    
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    
    try:
        stripe_manager = StripeManager()
        event = stripe_manager.verify_webhook(payload, sig_header)
        
        current_app.logger.info(f"Received Stripe webhook: {event['type']}")
        
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            current_app.logger.info(f"💰 Payment successful for {payment_intent['id']}")
            
            # Update request and escrow payment status
            request_id = payment_intent['metadata'].get('request_id')
            if request_id:
                request_obj = Request.query.get(request_id)
                if request_obj:
                    request_obj.status = 'funded'
                    db.session.commit()
                    
                # Update escrow payment record
                escrow_payment = EscrowPayment.query.filter_by(
                    stripe_payment_intent_id=payment_intent['id']
                ).first()
                if escrow_payment:
                    escrow_payment.status = 'paid'
                    escrow_payment.paid_at = datetime.utcnow()
                    db.session.commit()
            
        elif event["type"] == "transfer.paid":
            transfer = event["data"]["object"]
            current_app.logger.info(f"✅ Transfer completed for {transfer['id']}")
            
            # Find and update related request status
            if 'metadata' in transfer and 'request_id' in transfer['metadata']:
                request_id = transfer['metadata']['request_id']
                request_obj = Request.query.get(request_id)
                if request_obj:
                    request_obj.status = 'completed'
                    db.session.commit()
            
        elif event["type"] == "account.updated":
            account = event["data"]["object"]
            current_app.logger.info(f"👤 Account updated: {account['id']}")
            
            # Update user's onboarding status
            user = User.query.filter_by(stripe_account_id=account['id']).first()
            if user:
                if account.get('details_submitted') and account.get('charges_enabled'):
                    user.stripe_onboarding_complete = True
                    db.session.commit()
                    
        elif event["type"] == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]
            current_app.logger.warning(f"❌ Payment failed for {payment_intent['id']}")
            
        return "Success", 200
        
    except ValueError as e:
        current_app.logger.error(f"Invalid webhook payload: {str(e)}")
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        current_app.logger.error(f"Invalid webhook signature: {str(e)}")
        return "Invalid signature", 400
    except Exception as e:
        current_app.logger.error(f"Webhook error: {str(e)}")
        return "Webhook error", 500
