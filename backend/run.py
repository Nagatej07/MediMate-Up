#!/usr/bin/env python3
"""
MediTrack+ FastAPI Server Runner
Run this script to start the backend server
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
try:
    from dotenv import load_dotenv
    # Load from backend/.env
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)
    print(f" Loaded environment from {env_path}")
except ImportError:
    print("  python-dotenv not installed, using system environment")
except Exception as e:
    print(f"  Error loading .env: {e}")

# Configuration from environment variables
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
RELOAD = os.getenv("RELOAD", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

# Print startup configuration
print("\n" + "="*50)
print(" MediTrack+ Backend Server")
print("="*50)
print(f" Host: {HOST}")
print(f" Port: {PORT}")
print(f" Auto-reload: {RELOAD}")
print(f" Log Level: {LOG_LEVEL}")
print("="*50 + "\n")

if __name__ == "__main__":
    try:
        uvicorn.run(
            "backend.api:app",  # Path to your FastAPI app
            host=HOST,
            port=PORT,
            reload=RELOAD,
            log_level=LOG_LEVEL,
            # Optional: Add these for production
            # workers=int(os.getenv("WORKERS", 1)),
            # ssl_keyfile=os.getenv("SSL_KEYFILE"),
            # ssl_certfile=os.getenv("SSL_CERTFILE"),
        )
    except KeyboardInterrupt:
        print("\n\n Shutting down MediTrack+ server...")
    except Exception as e:
        print(f"\n Error starting server: {e}")
        print("\n Troubleshooting tips:")
        print("1. Make sure fastapi and uvicorn are installed: pip install fastapi uvicorn")
        print("2. Check that backend/api.py exists")
        print("3. Verify your .env file has all required variables")
        print("4. Try running: python -c 'import backend.api' to test import")
        sys.exit(1)