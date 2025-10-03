from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from revmark import db, cache
from revmark.models import User, Request, Message

bp = Blueprint("main", __name__)

# ---------- PAGES ----------
@bp.route("/")
@cache.cached(timeout=60)  # Cache homepage for 1 minute
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
        
        # For now, just flash a success message
        # Later we'll add email sending functionality
        flash(f"Thank you {name}! Your message has been received. We'll get back to you at {email} soon.", "success")
        return redirect(url_for("main.contact"))
    
    return render_template("contact.html")
    return render_template("about.html")

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
        db.session.commit()
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
@cache.cached(timeout=120)  # Cache browse page for 2 minutes
def browse_requests():
    page = request.args.get('page', 1, type=int)
    requests = Request.query.order_by(Request.timestamp.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template("browse_requests.html", requests=requests)


@bp.route("/request/<int:request_id>")
@cache.cached(timeout=300)  # Cache individual requests for 5 minutes
def view_request(request_id):
    request_item = Request.query.get_or_404(request_id)
    return render_template("view_request.html", request=request_item)


# ---------- ACCOUNT MANAGEMENT ----------
@bp.route("/account")
@login_required
def account():
    user_requests = Request.query.filter_by(buyer_id=current_user.id).order_by(Request.timestamp.desc()).all()
    return render_template("account.html", requests=user_requests)


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
