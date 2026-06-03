#!/bin/bash

echo "🏗️  Creating MediTrack+ Project Structure..."
echo "================================================"

# Create directory structure
mkdir -p backend
mkdir -p frontend/assets
mkdir -p src
mkdir -p data/input
mkdir -p data/vector_store
mkdir -p data/mongodb_backup
mkdir -p tests
mkdir -p logs
mkdir -p credentials

# Create backend files
touch backend/__init__.py
touch backend/api.py
touch backend/models.py
touch backend/dependencies.py
touch backend/requirements.txt
touch backend/run.py

# Create enhanced .env file with all configurations
cat > backend/.env << 'ENVEOF'
# ============================================
# MediTrack+ Environment Configuration
# ============================================

# API Configuration
API_VERSION=v1
DEBUG=true
HOST=0.0.0.0
PORT=8000
RELOAD=true

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production-$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================================
# MongoDB Configuration
# ============================================
# Local MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USER=meditrack_user
MONGODB_PASSWORD=secure_password_here
MONGODB_DATABASE=meditrack_db
MONGODB_AUTH_SOURCE=admin

# MongoDB Atlas (Cloud)
MONGODB_ATLAS_URI=mongodb+srv://username:password@cluster.mongodb.net/meditrack_db?retryWrites=true&w=majority
MONGODB_USE_ATLAS=false

# Collections
MONGODB_USERS_COLLECTION=users
MONGODB_PRESCRIPTIONS_COLLECTION=prescriptions
MONGODB_CHAT_HISTORY_COLLECTION=chat_history
MONGODB_OTC_COLLECTION=otc_medicines

# ============================================
# Google Cloud Vision API
# ============================================
# Path to service account JSON key file
GOOGLE_APPLICATION_CREDENTIALS=./credentials/google_vision_key.json

# Google Cloud Project
GCP_PROJECT_ID=meditrack-project
GCP_LOCATION=us-central1

# Vision API Features
GCP_VISION_FEATURES=DOCUMENT_TEXT_DETECTION,TEXT_DETECTION
GCP_VISION_MODEL=builtin/latest

# ============================================
# RAG & Vector Store Configuration
# ============================================
# Vector Database Type: chromadb, faiss, pinecone
VECTOR_DB_TYPE=chromadb

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=./data/vector_store
CHROMA_COLLECTION_NAME=prescription_embeddings

# FAISS Configuration
FAISS_INDEX_PATH=./data/vector_store/faiss_index

# Pinecone (Optional - Cloud)
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=meditrack

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_MODEL_DIMENSION=384

# Chunking Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# ============================================
# LLM Configuration
# ============================================
# Options: openai, groq, ollama, huggingface
LLM_PROVIDER=openai

# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.3
OPENAI_MAX_TOKENS=1000

# Groq (Alternative)
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=mixtral-8x7b-32768

# Ollama (Local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Hugging Face
HUGGINGFACE_API_KEY=your-huggingface-api-key
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.1

# ============================================
# OCR Configuration
# ============================================
# OCR Engine: google_vision, tesseract, aws_textract
OCR_ENGINE=google_vision

# Tesseract (Fallback)
TESSERACT_PATH=/usr/bin/tesseract
TESSERACT_LANG=eng

# AWS Textract (Optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1

# ============================================
# Database Configuration (SQLite Fallback)
# ============================================
DATABASE_URL=sqlite:///./data/meditrack.db
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_MAX_OVERFLOW=20

# ============================================
# File Upload Configuration
# ============================================
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=.pdf,.png,.jpg,.jpeg,.heic
UPLOAD_DIR=./data/input
TEMP_DIR=./data/temp

# ============================================
# Redis Configuration (For Caching)
# ============================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
CACHE_TTL=3600  # 1 hour

# ============================================
# Logging Configuration
# ============================================
LOG_LEVEL=INFO
LOG_FILE=./logs/meditrack.log
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=5

# ============================================
# Rate Limiting
# ============================================
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60  # seconds

# ============================================
# Email Configuration (For Notifications)
# ============================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ADMIN_EMAIL=admin@meditrack.com

# ============================================
# Frontend Configuration
# ============================================
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# ============================================
# Monitoring & Analytics
# ============================================
SENTRY_DSN=your-sentry-dsn
ENABLE_METRICS=true
PROMETHEUS_PORT=9090

ENVEOF

# Create frontend files
cat > frontend/index.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MediTrack+ | AI Healthcare Assistant</title>
    <link rel="stylesheet" href="styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <div id="app">
        <div class="loading">Loading MediTrack+...</div>
    </div>
    <script src="app.js"></script>
</body>
</html>
HTMLEOF

# Create basic CSS file
cat > frontend/styles.css << 'CSSEOF'
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    font-size: 1.5rem;
    color: white;
}
CSSEOF

# Create basic JS file
cat > frontend/app.js << 'JSEOF'
console.log('MediTrack+ Frontend Loaded');
// Your full app.js code here
JSEOF

# Create backend requirements.txt
cat > backend/requirements.txt << 'TXTEOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
email-validator==2.1.0

# MongoDB
motor==3.3.2
pymongo==4.5.0

# Google Cloud
google-cloud-vision==3.4.0
google-cloud-storage==2.10.0
google-auth==2.23.4

# RAG & Vector Store
langchain==0.1.0
langchain-community==0.0.10
chromadb==0.4.22
faiss-cpu==1.7.4
sentence-transformers==2.2.2

# LLM
openai==1.3.0
groq==0.4.2

# OCR & Processing
pdfplumber==0.10.3
Pillow==10.1.0
pytesseract==0.3.10
opencv-python==4.8.1.78

# Database
sqlalchemy==2.0.23
alembic==1.12.1

# Caching
redis==5.0.1

# Monitoring
sentry-sdk==1.38.0
prometheus-client==0.19.0

# Utilities
requests==2.31.0
numpy==1.24.3
pandas==2.1.4
tiktoken==0.5.1
TXTEOF

# Create backend run.py
cat > backend/run.py << 'PYEOF'
#!/usr/bin/env python3
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
PYEOF

# Create main requirements.txt
cat > requirements.txt << 'TXTEOF'
# Core dependencies
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# MongoDB
motor==3.3.2
pymongo==4.5.0

# Google Cloud
google-cloud-vision==3.4.0
google-cloud-storage==2.10.0

# RAG & AI
langchain==0.1.0
langchain-community==0.0.10
chromadb==0.4.22
faiss-cpu==1.7.4
sentence-transformers==2.2.2
openai==1.3.0

# OCR
pdfplumber==0.10.3
Pillow==10.1.0
pytesseract==0.3.10

# Database
sqlalchemy==2.0.23

# Utilities
requests==2.31.0
numpy==1.24.3
pandas==2.1.4
TXTEOF

# Create .gitignore
cat > .gitignore << 'GITEOF'
# Python
__pycache__/
*.py[cod]
*.so
.Python
env/
venv/
ENV/

# Credentials
credentials/
*.json
*.key
*.pem

# Environment
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite
*.sqlite3

# Data files
data/input/*
data/vector_store/*
data/mongodb_backup/*
!data/input/.gitkeep
!data/vector_store/.gitkeep

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Secrets
secrets/
config/
GITEOF

# Create README
cat > README.md << 'MDEOF'
# MediTrack+ - AI Healthcare Assistant

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
