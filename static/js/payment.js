// Payment form handling for RevMark escrow system
document.addEventListener('DOMContentLoaded', function() {
  // Check if we have the required configuration
  if (!window.paymentConfig) {
    console.error('Payment configuration not found');
    return;
  }

  const { stripePublicKey, platformFee, requestId } = window.paymentConfig;
  
  // Only initialize if we have Stripe public key and we're on payment form
  if (!stripePublicKey || !document.getElementById('payment-form')) {
    return;
  }

  // Initialize Stripe
  const stripe = Stripe(stripePublicKey);
  const elements = stripe.elements();

  // Create card element
  const cardElement = elements.create('card', {
    style: {
      base: {
        fontSize: '16px',
        color: '#424770',
        '::placeholder': {
          color: '#aab7c4',
        },
      },
    },
  });

  // Mount card element
  cardElement.mount('#card-element');

  // Get form elements
  const form = document.getElementById('payment-form');
  const amountInput = document.getElementById('amount');
  const submitButton = document.getElementById('submit-payment');
  const cardErrors = document.getElementById('card-errors');
  const paymentBreakdown = document.getElementById('payment-breakdown');

  // Update payment breakdown when amount changes
  amountInput.addEventListener('input', updatePaymentBreakdown);

  function updatePaymentBreakdown() {
    const amount = parseFloat(amountInput.value) || 0;
    const fee = amount * (platformFee / 100);
    const total = amount + fee;

    if (amount > 0) {
      document.getElementById('breakdown-amount').textContent = `$${amount.toFixed(2)}`;
      document.getElementById('breakdown-fee').textContent = `$${fee.toFixed(2)}`;
      document.getElementById('breakdown-total').textContent = `$${total.toFixed(2)}`;
      paymentBreakdown.style.display = 'block';
      submitButton.disabled = false;
    } else {
      paymentBreakdown.style.display = 'none';
      submitButton.disabled = true;
    }
  }

  // Handle card element changes
  cardElement.on('change', function(event) {
    if (event.error) {
      cardErrors.textContent = event.error.message;
    } else {
      cardErrors.textContent = '';
    }
  });

  // Handle form submission
  form.addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const amount = parseFloat(amountInput.value);
    if (!amount || amount <= 0) {
      cardErrors.textContent = 'Please enter a valid amount';
      return;
    }

    // Disable submit button and show loading state
    submitButton.disabled = true;
    submitButton.textContent = '🔄 Processing Payment...';

    try {
      // Create payment intent
      const response = await fetch('/api/payment/create-intent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount: amount,
          request_id: requestId,
          seller_id: document.getElementById('seller_id')?.value
        }),
      });

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Failed to create payment');
      }

      // Confirm payment with Stripe
      const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(data.client_secret, {
        payment_method: {
          card: cardElement,
        }
      });

      if (stripeError) {
        throw new Error(stripeError.message);
      }

      // Payment successful
      if (paymentIntent.status === 'succeeded') {
        // Redirect to success page or show success message
        window.location.href = `/request/${requestId}?payment=success`;
      }

    } catch (error) {
      console.error('Payment error:', error);
      cardErrors.textContent = error.message || 'An error occurred processing your payment';
      
      // Re-enable submit button
      submitButton.disabled = false;
      submitButton.textContent = '🔒 Fund Request Securely';
    }
  });

  // Initial breakdown update
  updatePaymentBreakdown();
});

// Payment action functions for funded requests
function releasePayment() {
  if (!confirm('Are you sure you want to release payment to the seller? This action cannot be undone.')) {
    return;
  }

  const requestId = window.paymentConfig?.requestId;
  if (!requestId) {
    alert('Error: Request ID not found');
    return;
  }

  fetch(`/api/payment/release`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      request_id: requestId
    }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert('Payment released successfully!');
      location.reload();
    } else {
      alert('Error releasing payment: ' + (data.error || 'Unknown error'));
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('Error releasing payment. Please try again.');
  });
}

function requestRefund() {
  const reason = prompt('Please provide a reason for the refund request:');
  if (!reason || reason.trim() === '') {
    return;
  }

  const requestId = window.paymentConfig?.requestId;
  if (!requestId) {
    alert('Error: Request ID not found');
    return;
  }

  fetch(`/api/payment/refund`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      request_id: requestId,
      reason: reason.trim()
    }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert('Refund request submitted successfully!');
      location.reload();
    } else {
      alert('Error submitting refund request: ' + (data.error || 'Unknown error'));
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('Error submitting refund request. Please try again.');
  });
}