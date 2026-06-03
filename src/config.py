import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()
import os
from dotenv import load_dotenv

load_dotenv()

import os
from dotenv import load_dotenv

load_dotenv()

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI")

    # Gemini API
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # 🔥 USE THIS MODEL (STABLE)
    GEMINI_MODEL_NAME = "gemini-2.5-flash-lite"
    # Pinecone
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
    PINECONE_INDEX_NAME = "prescription-index"

    # Auth
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret123")

    # File path
    INPUT_DIR = "uploads"

    @staticmethod
    def validate():
        if not Config.MONGO_URI:
            raise ValueError("❌ MONGO_URI missing in .env")

        if not Config.GOOGLE_CREDENTIALS:
            raise ValueError("❌ GOOGLE_APPLICATION_CREDENTIALS missing in .env")