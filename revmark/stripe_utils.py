import stripe
import os
from flask import current_app
from revmark.models import User, EscrowPayment, Request
from revmark import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StripeManager:
    def __init__(self):
        self.api_key = None
    
    def _initialize_stripe(self):
        """Initialize Stripe with API key"""
        if self.api_key is None:
            try:
                self.api_key = current_app.config['STRIPE_SECRET_KEY']
                stripe.api_key = self.api_key
            except Exception as e:
                logger.error(f"Failed to initialize Stripe: {str(e)}")
        return self.api_key is not None
    
    def create_connect_account(self, user_id, email, country='US'):
        """
        Create a Stripe Connect Express account for a seller
        
        Args:
            user_id: User ID
            email: User email
            country: Country code (default US)
            
        Returns:
            dict: Contains account_id and onboarding_url
        """
        if not self._initialize_stripe():
            raise Exception("Stripe not initialized")
            
        try:
            # Create Express account
            account = stripe.Account.create(
                type='express',
                country=country,
                email=email,
                capabilities={
                    'transfers': {'requested': True},
                },
                settings={
                    'payouts': {
                        'schedule': {
                            'interval': 'daily'
                        }
                    }
                }
            )
            
            # Create account link for onboarding
            account_link = stripe.AccountLink.create(
                account=account.id,
                refresh_url=f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/seller/onboarding/refresh",
                return_url=f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/seller/onboarding/complete",
                type='account_onboarding',
            )
            
            # Update user with Stripe account ID
            user = User.query.get(user_id)
            if user:
                user.stripe_account_id = account.id
                db.session.commit()
            
            return {
                'account_id': account.id,
                'onboarding_url': account_link.url
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating connect account: {str(e)}")
            raise Exception(f"Failed to create seller account: {str(e)}")
    
    def create_payment_intent(self, request_id, buyer_id, amount, seller_id=None):
        """
        Create a PaymentIntent for escrow payment with optional Connect account
        
        Args:
            request_id: Request ID
            buyer_id: Buyer user ID
            amount: Payment amount in dollars
            seller_id: Seller user ID (optional)
            
        Returns:
            dict: Contains client_secret and payment_intent_id
        """
        if not self._initialize_stripe():
            raise Exception("Stripe not initialized")
            
        try:
            amount_cents = int(amount * 100)  # Convert to cents
            platform_fee_cents = int(amount_cents * (current_app.config['PLATFORM_FEE_PERCENTAGE'] / 100))
            
            # Build PaymentIntent parameters
            intent_params = {
                'amount': amount_cents,
                'currency': 'usd',
                'automatic_payment_methods': {'enabled': True},
                'metadata': {
                    'request_id': str(request_id),
                    'buyer_id': str(buyer_id),
                    'seller_id': str(seller_id) if seller_id else '',
                    'platform_fee': str(platform_fee_cents)
                },
                'description': f"RevMark Request #{request_id} Payment"
            }
            
            # If seller has a connected account, set up for Connect payments
            seller = None
            if seller_id:
                seller = User.query.get(seller_id)
                if seller and seller.stripe_account_id and seller.stripe_onboarding_complete:
                    # Use application fee for Connect accounts
                    intent_params['application_fee_amount'] = platform_fee_cents
                    intent_params['on_behalf_of'] = seller.stripe_account_id
                    intent_params['transfer_data'] = {
                        'destination': seller.stripe_account_id,
                    }
            
            # Create PaymentIntent
            intent = stripe.PaymentIntent.create(**intent_params)
            
            # Create escrow payment record
            escrow_payment = EscrowPayment(
                request_id=request_id,
                buyer_id=buyer_id,
                seller_id=seller_id,
                amount=amount,
                platform_fee=platform_fee_cents / 100,  # Convert back to dollars
                seller_amount=amount - (platform_fee_cents / 100),
                stripe_payment_intent_id=intent.id,
                status='pending'
            )
            db.session.add(escrow_payment)
            
            # Update request with payment info
            request_obj = Request.query.get(request_id)
            if request_obj:
                request_obj.stripe_payment_intent_id = intent.id
                request_obj.escrow_amount = amount
                request_obj.platform_fee = platform_fee_cents / 100
                # Don't mark as funded until payment is confirmed
                if seller_id:
                    request_obj.seller_id = seller_id
            
            db.session.commit()
            
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': amount,
                'platform_fee': platform_fee_cents / 100,
                'uses_connect': bool(seller and seller.stripe_account_id and seller.stripe_onboarding_complete)
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {str(e)}")
            db.session.rollback()
            raise Exception(f"Failed to create payment: {str(e)}")
    
    def release_payment_to_seller(self, payment_intent_id, seller_account_id):
        """
        Transfer funds from platform to seller account
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID
            seller_account_id: Seller's Stripe Connect account ID
            
        Returns:
            dict: Transfer details
        """
        if not self._initialize_stripe():
            raise Exception("Stripe not initialized")
            
        try:
            # Get escrow payment record
            escrow_payment = EscrowPayment.query.filter_by(
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
            if not escrow_payment:
                raise Exception("Escrow payment not found")
            
            if escrow_payment.status != 'pending':
                raise Exception(f"Payment already {escrow_payment.status}")
            
            # Create transfer to seller
            transfer = stripe.Transfer.create(
                amount=int(escrow_payment.seller_amount * 100),  # Convert to cents
                currency='usd',
                destination=seller_account_id,
                transfer_group=payment_intent_id,
                metadata={
                    'request_id': str(escrow_payment.request_id),
                    'buyer_id': str(escrow_payment.buyer_id),
                    'seller_id': str(escrow_payment.seller_id)
                }
            )
            
            # Update escrow payment record
            escrow_payment.stripe_transfer_id = transfer.id
            escrow_payment.status = 'completed'
            escrow_payment.completed_at = datetime.utcnow()
            
            # Update request status
            request_obj = Request.query.get(escrow_payment.request_id)
            if request_obj:
                request_obj.stripe_transfer_id = transfer.id
                request_obj.status = 'completed'
            
            db.session.commit()
            
            return {
                'transfer_id': transfer.id,
                'amount_transferred': escrow_payment.seller_amount,
                'platform_fee': escrow_payment.platform_fee
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error releasing payment: {str(e)}")
            db.session.rollback()
            raise Exception(f"Failed to release payment: {str(e)}")
    
    def refund_payment(self, payment_intent_id, reason='requested_by_customer'):
        """
        Refund a payment to the buyer
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID
            reason: Refund reason
            
        Returns:
            dict: Refund details
        """
        if not self._initialize_stripe():
            raise Exception("Stripe not initialized")
            
        try:
            # Create refund
            refund = stripe.Refund.create(
                payment_intent=payment_intent_id,
                reason=reason
            )
            
            # Update escrow payment record
            escrow_payment = EscrowPayment.query.filter_by(
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
            if escrow_payment:
                escrow_payment.status = 'refunded'
                escrow_payment.completed_at = datetime.utcnow()
                
                # Update request status
                request_obj = Request.query.get(escrow_payment.request_id)
                if request_obj:
                    request_obj.status = 'cancelled'
                
                db.session.commit()
            
            return {
                'refund_id': refund.id,
                'amount_refunded': refund.amount / 100,  # Convert from cents
                'status': refund.status
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error processing refund: {str(e)}")
            db.session.rollback()
            raise Exception(f"Failed to process refund: {str(e)}")
    
    def get_account_status(self, account_id):
        """
        Get the status of a Stripe Connect account
        
        Args:
            account_id: Stripe Connect account ID
            
        Returns:
            dict: Account status and capabilities
        """
        if not self._initialize_stripe():
            raise Exception("Stripe not initialized")
            
        try:
            account = stripe.Account.retrieve(account_id)
            
            return {
                'charges_enabled': account.charges_enabled,
                'payouts_enabled': account.payouts_enabled,
                'details_submitted': account.details_submitted,
                'requirements': account.requirements,
                'capabilities': account.capabilities
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error getting account status: {str(e)}")
            return None
    
    def create_account_link(self, account_id, return_url, refresh_url):
        """
        Create an account link for Stripe Connect onboarding
        
        Args:
            account_id: Stripe account ID
            return_url: URL to redirect after successful onboarding
            refresh_url: URL to redirect if user needs to retry onboarding
            
        Returns:
            dict: Contains the onboarding URL
        """
        if not self._initialize_stripe():
            raise Exception("Stripe not initialized")
            
        try:
            account_link = stripe.AccountLink.create(
                account=account_id,
                refresh_url=refresh_url,
                return_url=return_url,
                type='account_onboarding',
            )
            
            logger.info(f"Created account link for account {account_id}")
            return {
                'url': account_link.url,
                'expires_at': account_link.expires_at
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating account link: {str(e)}")
            raise Exception(f"Failed to create onboarding link: {str(e)}")
    
    def get_account(self, account_id):
        """
        Get Stripe account details
        
        Args:
            account_id: Stripe account ID
            
        Returns:
            dict: Account details
        """
        if not self._initialize_stripe():
            raise Exception("Stripe not initialized")
            
        try:
            account = stripe.Account.retrieve(account_id)
            return {
                'id': account.id,
                'email': account.email,
                'details_submitted': account.details_submitted,
                'charges_enabled': account.charges_enabled,
                'payouts_enabled': account.payouts_enabled,
                'requirements': account.requirements.to_dict_recursive() if account.requirements else None,
                'capabilities': account.capabilities.to_dict_recursive() if account.capabilities else None
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving account: {str(e)}")
            raise Exception(f"Failed to retrieve account: {str(e)}")
    
    def verify_webhook(self, payload, signature):
        """
        Verify and construct Stripe webhook event
        
        Args:
            payload: Raw request payload
            signature: Stripe signature header
            
        Returns:
            dict: Verified webhook event
        """
        if not self._initialize_stripe():
            raise Exception("Stripe not initialized")
            
        webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
        if not webhook_secret:
            raise Exception("Webhook secret not configured")
            
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            return event
            
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {str(e)}")
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {str(e)}")
            raise stripe.error.SignatureVerificationError("Invalid signature")
    
    def create_transfer(self, amount, destination_account, application_fee=None, metadata=None):
        """
        Create a transfer to a connected account
        
        Args:
            amount: Amount in cents
            destination_account: Stripe account ID to transfer to
            application_fee: Platform fee in cents (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            dict: Transfer details
        """
        if not self._initialize_stripe():
            raise Exception("Stripe not initialized")
            
        try:
            transfer_data = {
                'amount': amount,
                'currency': 'usd',
                'destination': destination_account,
            }
            
            if application_fee:
                transfer_data['application_fee_amount'] = application_fee
                
            if metadata:
                transfer_data['metadata'] = metadata
            
            transfer = stripe.Transfer.create(**transfer_data)
            
            logger.info(f"Created transfer {transfer.id} for ${amount/100:.2f} to {destination_account}")
            return {
                'id': transfer.id,
                'amount': transfer.amount,
                'destination': transfer.destination,
                'created': transfer.created,
                'status': 'succeeded'  # Transfers are typically instant
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating transfer: {str(e)}")
            raise Exception(f"Failed to create transfer: {str(e)}")

# Initialize global Stripe manager instance
stripe_manager = StripeManager()