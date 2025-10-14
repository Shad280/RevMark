from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from revmark import db
from revmark.models import Message, MessageAttachment, Request, User, EscrowPayment
from revmark.utils.email_utils import send_email
from revmark.s3_utils import s3_manager
from revmark.stripe_utils import stripe_manager
import logging
import os

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")

# ---------- FILE UPLOAD ENDPOINTS ----------

@api_bp.route("/upload", methods=["POST"])
@login_required
def upload_file():
    """Upload file to S3 and return file info"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check if AWS S3 is configured
        if not current_app.config.get('AWS_ACCESS_KEY_ID'):
            return jsonify({"error": "File upload not available (AWS S3 not configured)"}), 503
        
        # Upload to S3
        file_info = s3_manager.upload_file(file, folder="message-attachments")
        
        # Generate temporary URL for immediate preview
        preview_url = s3_manager.generate_presigned_url(file_info['s3_key'], expiration=3600)
        
        return jsonify({
            "success": True,
            "file": {
                "s3_key": file_info['s3_key'],
                "original_filename": file_info['original_filename'],
                "file_size": file_info['file_size'],
                "content_type": file_info['content_type'],
                "preview_url": preview_url
            }
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return jsonify({"error": "File upload service unavailable"}), 503

@api_bp.route("/file/<int:attachment_id>/download", methods=["GET"])
@login_required
def download_file(attachment_id):
    """Generate download URL for a message attachment"""
    try:
        attachment = MessageAttachment.query.get_or_404(attachment_id)
        
        # Check if user has access to this file
        message = Message.query.get(attachment.message_id)
        if message.sender_id != current_user.id and message.receiver_id != current_user.id:
            return jsonify({"error": "Access denied"}), 403
        
        # Generate presigned URL
        download_url = s3_manager.generate_presigned_url(
            attachment.s3_key, 
            expiration=3600  # 1 hour
        )
        
        return jsonify({
            "download_url": download_url,
            "filename": attachment.original_filename,
            "expires_in": 3600
        })
        
    except Exception as e:
        logger.error(f"File download error: {str(e)}")
        return jsonify({"error": "Failed to generate download URL"}), 500

# ---------- STRIPE CONNECT ENDPOINTS ----------

@api_bp.route("/seller/connect", methods=["POST"])
@login_required
def create_seller_account():
    """Create Stripe Connect account for seller"""
    try:
        if current_user.stripe_account_id:
            return jsonify({"error": "Seller account already exists"}), 400
        
        # Check if Stripe is configured
        if not current_app.config.get('STRIPE_SECRET_KEY'):
            return jsonify({"error": "Payment processing not available (Stripe not configured)"}), 503
        
        account_info = stripe_manager.create_connect_account(
            current_user.id, 
            current_user.email
        )
        
        return jsonify({
            "success": True,
            "onboarding_url": account_info['onboarding_url'],
            "account_id": account_info['account_id']
        })
        
    except Exception as e:
        logger.error(f"Seller account creation error: {str(e)}")
        return jsonify({"error": "Payment service unavailable"}), 503

@api_bp.route("/seller/status", methods=["GET"])
@login_required
def get_seller_status():
    """Get seller account status"""
    try:
        if not current_user.stripe_account_id:
            return jsonify({
                "connected": False,
                "onboarding_complete": False
            })
        
        status = stripe_manager.get_account_status(current_user.stripe_account_id)
        
        if status:
            # Update user onboarding status
            current_user.stripe_onboarding_complete = (
                status['charges_enabled'] and 
                status['payouts_enabled'] and 
                status['details_submitted']
            )
            db.session.commit()
        
        return jsonify({
            "connected": True,
            "onboarding_complete": current_user.stripe_onboarding_complete,
            "account_status": status
        })
        
    except Exception as e:
        logger.error(f"Seller status error: {str(e)}")
        return jsonify({"error": "Failed to get seller status"}), 500

# ---------- ESCROW PAYMENT ENDPOINTS ----------

@api_bp.route("/payment/create-intent", methods=["POST"])
@login_required
def create_payment_intent():
    """Create payment intent for escrow payment"""
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        amount = float(data.get('amount', 0))
        seller_id = data.get('seller_id')
        
        if not request_id or amount <= 0:
            return jsonify({"error": "Invalid request or amount"}), 400
        
        # Verify request exists and user is the buyer
        request_obj = Request.query.get_or_404(request_id)
        if request_obj.buyer_id != current_user.id:
            return jsonify({"error": "Access denied"}), 403
        
        if request_obj.status != 'open':
            return jsonify({"error": "Request is not open for funding"}), 400
        
        # Create payment intent
        payment_info = stripe_manager.create_payment_intent(
            request_id=request_id,
            buyer_id=current_user.id,
            amount=amount,
            seller_id=seller_id
        )
        # Notify seller if an offer was made (seller_id provided)
        try:
            if seller_id:
                seller = User.query.get(seller_id)
                if seller and seller.email:
                    subject = f"Your offer was selected for request #{request_id}" 
                    body = f"Good news! The buyer has created a payment for Request #{request_id}.\n\nAmount: ${amount:.2f}\n\nLog in to RevMark to view details and message the buyer."
                    send_email(subject, [seller.email], body)
        except Exception:
            logger.exception("Failed to send offer-made email to seller")
        
        return jsonify({
            "success": True,
            "client_secret": payment_info['client_secret'],
            "amount": payment_info['amount'],
            "platform_fee": payment_info['platform_fee']
        })
        
    except Exception as e:
        logger.error(f"Payment intent creation error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route("/payment/release", methods=["POST"])
@login_required
def release_payment():
    """Release escrow payment to seller"""
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        
        if not request_id:
            return jsonify({"error": "Request ID required"}), 400
        
        # Verify request and user permissions
        request_obj = Request.query.get_or_404(request_id)
        if request_obj.buyer_id != current_user.id:
            return jsonify({"error": "Access denied"}), 403
        
        if request_obj.status != 'funded':
            return jsonify({"error": "Request is not funded"}), 400
        
        if not request_obj.seller_id:
            return jsonify({"error": "No seller assigned"}), 400
        
        # Get seller account
        seller = User.query.get(request_obj.seller_id)
        if not seller or not seller.stripe_account_id:
            return jsonify({"error": "Seller account not configured"}), 400
        
        # Release payment
        transfer_info = stripe_manager.release_payment_to_seller(
            request_obj.stripe_payment_intent_id,
            seller.stripe_account_id
        )

        # Notify buyer and seller about completion
        try:
            buyer = User.query.get(request_obj.buyer_id) if request_obj else None
            seller = User.query.get(request_obj.seller_id) if request_obj and request_obj.seller_id else None
            if buyer and buyer.email:
                send_email(f"Payment released for Request #{request_id}", [buyer.email], f"Your payment for Request #{request_id} has been released to the seller.")
            if seller and seller.email:
                send_email(f"You received payment for Request #{request_id}", [seller.email], f"A payment for Request #{request_id} has been released to your account. Amount: ${transfer_info['amount_transferred']:.2f}")
        except Exception:
            logger.exception("Failed to send payment released emails")
        
        return jsonify({
            "success": True,
            "transfer_id": transfer_info['transfer_id'],
            "amount_transferred": transfer_info['amount_transferred'],
            "platform_fee": transfer_info['platform_fee']
        })
        
    except Exception as e:
        logger.error(f"Payment release error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route("/payment/refund", methods=["POST"])
@login_required
def refund_payment():
    """Refund escrow payment to buyer"""
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        reason = data.get('reason', 'requested_by_customer')
        
        if not request_id:
            return jsonify({"error": "Request ID required"}), 400
        
        # Verify request and user permissions
        request_obj = Request.query.get_or_404(request_id)
        if request_obj.buyer_id != current_user.id:
            return jsonify({"error": "Access denied"}), 403
        
        if request_obj.status not in ['funded', 'in_progress']:
            return jsonify({"error": "Cannot refund this request"}), 400
        
        # Process refund
        refund_info = stripe_manager.refund_payment(
            request_obj.stripe_payment_intent_id,
            reason=reason
        )
        
        return jsonify({
            "success": True,
            "refund_id": refund_info['refund_id'],
            "amount_refunded": refund_info['amount_refunded'],
            "status": refund_info['status']
        })
        
    except Exception as e:
        logger.error(f"Payment refund error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route("/payment/history/<int:request_id>", methods=["GET"])
@login_required
def get_payment_history(request_id):
    """Get payment history for a request"""
    try:
        # Verify request and user permissions
        request_obj = Request.query.get_or_404(request_id)
        if request_obj.buyer_id != current_user.id and request_obj.seller_id != current_user.id:
            return jsonify({"error": "Access denied"}), 403
        
        # Get escrow payments
        payments = EscrowPayment.query.filter_by(request_id=request_id).all()
        
        payment_history = []
        for payment in payments:
            payment_history.append({
                "id": payment.id,
                "amount": payment.amount,
                "platform_fee": payment.platform_fee,
                "seller_amount": payment.seller_amount,
                "status": payment.status,
                "created_at": payment.created_at.isoformat(),
                "completed_at": payment.completed_at.isoformat() if payment.completed_at else None,
                "stripe_payment_intent_id": payment.stripe_payment_intent_id,
                "stripe_transfer_id": payment.stripe_transfer_id
            })
        
        return jsonify({
            "success": True,
            "payments": payment_history,
            "request_status": request_obj.status
        })
        
    except Exception as e:
        logger.error(f"Payment history error: {str(e)}")
        return jsonify({"error": "Failed to get payment history"}), 500

# ---------- ERROR HANDLERS ----------

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500