from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
import os, uuid, shutil

from src.config import Config
from src.extractor import PrescriptionExtractor
from src.graph import RAGGraph
from src.auth import AuthManager
from src.utils import ensure_directory
from src.db_manager import DBManager
from src.vector_store import VectorStoreManager

from backend.dependencies import verify_token, create_access_token

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= INIT =================

db = DBManager()
extractor = PrescriptionExtractor()
rag_graph = RAGGraph().build_graph()
auth_manager = AuthManager()
vector_store = VectorStoreManager()

# ================= MODELS =================

class AuthRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    question: str
    prescription_id: str
    session_id: str

class OTCCheckRequest(BaseModel):
    prescription_id: str
    session_id: str

# ================= AUTH =================

@app.post("/api/register")
def register(req: AuthRequest):
    success, msg = auth_manager.register_user(req.username, req.password)
    if not success:
        raise HTTPException(400, msg)
    return {"success": True, "message": msg}

@app.post("/api/login")
def login(req: AuthRequest):
    success, msg = auth_manager.login_user(req.username, req.password)
    if not success:
        raise HTTPException(401, msg)

    token = create_access_token({"sub": req.username})
    return {"success": True, "token": token, "username": req.username}

# ================= UPLOAD =================

@app.post("/api/upload-prescription")
def upload(
    file: UploadFile = File(...),
    username: str = Form(...),
    current_user: str = Depends(verify_token)
):
    if username != current_user:
        raise HTTPException(403, "User mismatch")

    ensure_directory(Config.INPUT_DIR)
    path = os.path.join(Config.INPUT_DIR, file.filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    data = extractor.extract_data(path)
    file_id = str(uuid.uuid4())

    # Save in MongoDB
    db.prescriptions.insert_one({
        "id": file_id,
        "username": username,
        "filename": file.filename,
        "data": data,
        "created_at": datetime.utcnow()
    })

    # Save in Pinecone
    if data and "medicines" in data:
        texts = []
        metadatas = []

        for med in data["medicines"]:
            text = f"""
            Medicine: {med.get('name')}
            Dosage: {med.get('dosage')}
            Frequency: {med.get('frequency')}
            Timing: {med.get('timing')}
            """

            texts.append(text)
            metadatas.append({
                "text": text,
                "prescription_id": file_id
            })

        vector_store.add_texts(
            texts=texts,
            metadata_list=metadatas,
            namespace="prescriptions"
        )

    return {"success": True, "prescription_id": file_id}

# ================= GET PRESCRIPTIONS =================

@app.get("/api/user-prescriptions")
def get_prescriptions(username: str, current_user: str = Depends(verify_token)):
    if username != current_user:
        raise HTTPException(403, "User mismatch")

    prescriptions = list(db.prescriptions.find({"username": username}, {"_id": 0}))
    
    # Format for frontend (match what frontend expects)
    formatted_prescriptions = []
    for p in prescriptions:
        formatted_prescriptions.append({
            "id": p.get("id"),
            "title": p.get("filename", "Prescription"),
            "created_at": p.get("created_at")
        })
    
    return {"success": True, "prescriptions": formatted_prescriptions}

# ================= 🔥 ADD THIS MISSING ENDPOINT =================

@app.get("/api/prescription-details")
def prescription_details(id: str, username: str, current_user: str = Depends(verify_token)):
    """Get detailed information about a specific prescription"""
    if username != current_user:
        raise HTTPException(403, "User mismatch")
    
    prescription = db.prescriptions.find_one({"id": id, "username": username}, {"_id": 0})
    
    if not prescription:
        raise HTTPException(404, "Prescription not found")
    
    # Format medicine details as HTML
    details_html = "<ul style='margin: 0; padding-left: 1.5rem;'>"
    
    if prescription.get("data") and prescription["data"].get("medicines"):
        for med in prescription["data"]["medicines"]:
            details_html += f"""
            <li style='margin-bottom: 1rem;'>
                <strong>{med.get('name', 'Unknown')}</strong><br>
                 Dosage: {med.get('dosage', 'N/A')}<br>
                 Timing: {med.get('timing', 'N/A')}<br>
                 Frequency: {med.get('frequency', 'N/A')}
            </li>
            """
    else:
        details_html += "<li>No medicine details found</li>"
    
    details_html += "</ul>"
    
    # Create a session ID for chat
    session_id = str(uuid.uuid4())
    
    return {
        "success": True,
        "title": prescription.get("filename", "Prescription"),
        "details": details_html,
        "session_id": session_id
    }

# =================  ADD THIS MISSING ENDPOINT =================

@app.get("/api/otc-list")
def otc_list(search: Optional[str] = None):
    """Get list of OTC medicines"""
    # Comprehensive OTC medicines list
    all_medicines = [
        {"name": "Paracetamol (Acetaminophen)", "type": "Pain Relief & Fever"},
        {"name": "Ibuprofen", "type": "Anti-inflammatory & Pain Relief"},
        {"name": "Aspirin", "type": "Pain Relief & Blood Thinner"},
        {"name": "Cetirizine", "type": "Antihistamine/Allergy"},
        {"name": "Loratadine", "type": "Antihistamine/Allergy"},
        {"name": "Fexofenadine", "type": "Antihistamine/Allergy"},
        {"name": "Omeprazole", "type": "Antacid/Acid Reducer"},
        {"name": "Vitamin C", "type": "Supplement"},
        {"name": "Vitamin D3", "type": "Supplement"},
        {"name": "Calcium", "type": "Supplement"},
        {"name": "Multivitamins", "type": "Supplement"},
        {"name": "Cough Syrup", "type": "Cough & Cold"},
        {"name": "Loperamide", "type": "Anti-diarrheal"},
        {"name": "Hydrocortisone Cream", "type": "Topical/Skin"},
        {"name": "Antacid Tablets", "type": "Digestive Health"},
        {"name": "Diphenhydramine", "type": "Antihistamine/Sleep Aid"},
        {"name": "Naproxen Sodium", "type": "Pain Relief"},
        {"name": "Bandages & First Aid", "type": "First Aid"},
        {"name": "Antiseptic Cream", "type": "First Aid"},
        {"name": "Saline Nasal Spray", "type": "Cold & Allergy"},
        {"name": "Artificial Tears", "type": "Eye Care"},
        {"name": "Zinc Supplements", "type": "Supplement"},
        {"name": "Probiotics", "type": "Digestive Health"},
        {"name": "Melatonin", "type": "Sleep Aid"},
    ]
    
    # Filter by search if provided
    if search:
        search_lower = search.lower()
        medicines = [m for m in all_medicines if search_lower in m['name'].lower()]
    else:
        medicines = all_medicines
    
    return {"success": True, "medicines": medicines}

# =================  ADD THIS MISSING ENDPOINT =================

@app.post("/api/check-otc")
def check_otc(req: OTCCheckRequest, current_user: str = Depends(verify_token)):
    """Check which medicines in prescription are OTC"""
    # Get prescription
    prescription = db.prescriptions.find_one({"id": req.prescription_id}, {"_id": 0})
    
    if not prescription:
        raise HTTPException(404, "Prescription not found")
    
    # OTC medicine keywords
    otc_keywords = [
        "paracetamol", "acetaminophen", "tylenol", "ibuprofen", "advil", "motrin",
        "aspirin", "cetirizine", "zyrtec", "loratadine", "claritin", "fexofenadine",
        "allegra", "omeprazole", "prilosec", "vitamin", "calcium", "cough", 
        "loperamide", "imodium", "hydrocortisone", "antacid", "diphenhydramine", 
        "benadryl", "naproxen", "aleve", "bandage", "antiseptic", "saline", 
        "artificial tears", "zinc", "probiotic", "melatonin"
    ]
    
    result = {
        "otc_medicines": [],
        "consult_medicines": []
    }
    
    # Check each medicine
    if prescription.get("data") and prescription["data"].get("medicines"):
        for med in prescription["data"]["medicines"]:
            med_name = med.get('name', '').lower()
            
            # Check if medicine is OTC
            is_otc = any(keyword in med_name for keyword in otc_keywords)
            
            if is_otc:
                result["otc_medicines"].append({
                    "name": med.get('name', 'Unknown'),
                    "reason": "This medicine is generally available over the counter. Follow the recommended dosage on the package."
                })
            else:
                result["consult_medicines"].append({
                    "name": med.get('name', 'Unknown'),
                    "reason": "This medicine typically requires a prescription. Please consult with a doctor or pharmacist before use."
                })
    
    return {"success": True, "result": result}

# ================= CHAT =================

@app.post("/api/chat")
def chat(req: ChatRequest, current_user: str = Depends(verify_token)):
    result = rag_graph.invoke({
        "question": req.question,
        "prescription_id": req.prescription_id,
        "session_id": req.session_id,
        "context": [],
        "answer": ""
    })

    print(" GRAPH RESULT:", result)

    answer = result.get("answer", "")

    if not answer or str(answer).lower() == "none":
        answer = "I couldn't generate a proper answer. Try again."

    db.chats.insert_many([
        {"session_id": req.session_id, "role": "user", "content": req.question},
        {"session_id": req.session_id, "role": "ai", "content": answer}
    ])

    return {"success": True, "answer": answer}

# ================= CHAT HISTORY =================

@app.get("/api/chat-history")
def history(session_id: str, current_user: str = Depends(verify_token)):
    msgs = list(db.chats.find({"session_id": session_id}, {"_id": 0}))
    return {"success": True, "messages": msgs}

# ================= HEALTH CHECK =================

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}