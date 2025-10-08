#!/usr/bin/env python3
"""
Standalone FastAPI Escrow Application

Run this directly to avoid conflicts with Flask app.
"""
import os
import sys

# Add the current directory to Python path to ensure our app module is found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    print("🚀 Starting RevMark FastAPI Escrow System...")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🔧 Interactive API: http://localhost:8001/redoc")
    print("❤️  Health Check: http://localhost:8001/health")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,  # Different port to avoid conflict with Flask
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )