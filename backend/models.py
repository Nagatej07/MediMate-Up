from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class ChatRequest(BaseModel):
    question: str
    prescription_id: str
    session_id: str

class OTCRequest(BaseModel):
    prescription_id: str
    session_id: str

class PrescriptionResponse(BaseModel):
    id: str
    title: str
    filename: str
    details: Optional[str] = None

class MessageResponse(BaseModel):
    role: str
    content: str