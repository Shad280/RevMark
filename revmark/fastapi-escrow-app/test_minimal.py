#!/usr/bin/env python3

# Simple test to see what's working
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

try:
    from fastapi import FastAPI
    print("✅ FastAPI imported successfully")
except Exception as e:
    print(f"❌ FastAPI import failed: {e}")

try:
    from pydantic import BaseModel
    print("✅ Pydantic imported successfully")
except Exception as e:
    print(f"❌ Pydantic import failed: {e}")

try:
    from sqlalchemy import create_engine
    print("✅ SQLAlchemy imported successfully")
except Exception as e:
    print(f"❌ SQLAlchemy import failed: {e}")

# Create a minimal FastAPI app
app = FastAPI(title="Test App")

@app.get("/")
def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting minimal test app on port 8002...")
    uvicorn.run(app, host="127.0.0.1", port=8002)