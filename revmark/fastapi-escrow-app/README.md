# RevMark FastAPI Escrow System

A complete FastAPI backend implementing escrow-style payments with Stripe Connect, manual capture, transfers, and messaging with image uploads.

## 🚀 Features

- **User Authentication**: JWT-based auth with signup/login
- **Stripe Escrow Flow**: 
  - Seller onboarding via Stripe Express
  - Buyer payment authorization (manual capture)
  - Funds release with platform fee deduction
  - Automatic transfers to seller accounts
- **Messaging System**: Text messages with image upload support
- **Request Management**: Create, view, and manage service requests
- **Webhook Support**: Stripe event handling
- **File Uploads**: Local storage with easy S3 migration path

## 🛠️ Quick Setup

1. **Install Dependencies**:
   ```bash
   cd revmark/fastapi-escrow-app
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   copy .env.example .env
   # Edit .env with your Stripe keys
   ```

3. **Run Application**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. **Visit**: http://localhost:8000/docs for API documentation

## Project Structure

```
fastapi-escrow-app
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── escrow.py
│   │   ├── message.py
│   │   └── payment.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── v1
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── escrow.py
│   │       ├── messages.py
│   │       ├── payments.py
│   │       └── uploads.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── escrow.py
│   │   ├── message.py
│   │   └── payment.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── escrow.py
│   │   ├── stripe_service.py
│   │   ├── message.py
│   │   └── file_upload.py
│   └── utils
│       ├── __init__.py
│       ├── email.py
│       └── validators.py
├── alembic
│   ├── versions
│   ├── env.py
│   └── script.py.mako
├── tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_escrow.py
│   ├── test_messages.py
│   └── test_payments.py
├── requirements.txt
├── alembic.ini
├── .env.example
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/fastapi-escrow-app.git
   cd fastapi-escrow-app
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the environment variables by copying `.env.example` to `.env` and filling in the necessary values.

## Running the Application

To run the FastAPI application, use the following command:
```
uvicorn app.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

## API Documentation

The API documentation can be accessed at `http://127.0.0.1:8000/docs`.

## Testing

To run the tests, use:
```
pytest
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.