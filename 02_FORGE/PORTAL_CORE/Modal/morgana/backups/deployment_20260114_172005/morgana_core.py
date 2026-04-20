# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import modal
import os
import random
import time
from datetime import datetime
from pydantic import BaseModel, field_validator
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
from circuitbreaker import circuit
import structlog
from functools import lru_cache
import redis
from typing import Optional

# Configure logging
logger = structlog.get_logger()

# DEFINITION
app = modal.App("morgana-research-agency-prod")
image = modal.Image.debian_slim().pip_install(
    "google-generativeai==0.3.0", 
    "appwrite==4.0.0", 
    "replicate==0.15.0", 
    "pydantic>=2.0.0",
    "circuitbreaker==1.4.0",
    "structlog==23.1.0",
    "redis==5.0.0"
)

# DATA MODEL WITH VALIDATION
class MorganaRequest(BaseModel):
    task: str
    mode: str = "RESEARCH" 
    force_culture: Optional[str] = None
    request_id: str = None
    mock_mode: bool = False
    
    @field_validator('task')
    @classmethod
    def validate_task(cls, v: str) -> str:
        if len(v) > 10000:
            raise ValueError('Task too long')
        if not v.strip():
            raise ValueError('Task cannot be empty')
        return v.strip()
    
    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v: str) -> str:
        allowed = {"RESEARCH", "DEV", "MUSIC", "ANALYSIS"}
        if v not in allowed:
            raise ValueError(f'Mode must be one of {allowed}')
        return v

# CULTURAL MATRIX
CULTURES = {
    "MEMPHIS": "Authentic, gritty, rhythmic, soulful. Focus on vibe and history.",
    "SILICON": "Efficient, scalable, ROI-focused. Focus on growth and metrics.",
    "ACADEMIC": "Rigorous, cited, structural. Focus on data accuracy.",
    "CYBERPUNK": "Disruptive, technical, encrypted. Focus on future-tech."
}

# CACHE CULTURE SELECTION
@lru_cache(maxsize=100)
def get_culture_context(culture_key: str) -> str:
    return CULTURES.get(culture_key, CULTURES["SILICON"])

# CIRCUIT BREAKER FOR EXTERNAL SERVICES
@circuit(failure_threshold=5, recovery_timeout=30)
def call_gemini_api(prompt: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(prompt)
    return response.text

# RATE LIMITING
class RateLimiter:
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
    
    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        
        # Clean old requests
        self.requests = [(ts, cid) for ts, cid in self.requests if ts > cutoff]
        
        # Count recent requests from this client
        client_requests = sum(1 for ts, cid in self.requests if cid == client_id)
        
        if client_requests >= self.max_requests:
            return False
        
        self.requests.append((now, client_id))
        return True

rate_limiter = RateLimiter()

@app.function(
    image=image, 
    secrets=[modal.Secret.from_name("my-sovereign-secrets")],
    timeout=300,  # 5 minute timeout
    memory=512,   # 512MB memory allocation
)
@modal.web_endpoint(method="POST")
def morgana_brain(req: MorganaRequest):
    start_time = time.time()
    
    # === MOCK MODE BYPASS ===
    if req.mock_mode:
        logger.info("EXECUTING IN MOCK MODE", request_id=req.request_id)
        time.sleep(1.5) # Simulate latency
        return {
            "morgana": f"[MOCK_REPLY] Processed task: '{req.task}' in mode {req.mode}",
            "meta": {
                "mode": req.mode,
                "culture": "MOCK_CULTURE",
                "vault": "Simulated",
                "processing_time_ms": 1500,
                "request_id": req.request_id or "mock-id"
            }
        }
    # ========================
    
    try:
        # RATE LIMITING CHECK
        client_id = req.request_id or "anonymous"
        if not rate_limiter.is_allowed(client_id):
            logger.warning("Rate limit exceeded", client_id=client_id)
            return {
                "status": "Rate Limited",
                "error": "Too many requests",
                "retry_after": 60
            }
        
        # VALIDATION
        if not req.task.strip():
            return {"status": "Invalid Request", "error": "Task cannot be empty"}
        
        # CULTURE SELECTION
        culture_key = req.force_culture or random.choice(list(CULTURES.keys()))
        culture_context = get_culture_context(culture_key)
        
        # APPWRITE CONNECTION WITH RETRY
        vault_status = "Disconnected"
        db = None
        try:
            client = Client()
            client.set_endpoint(os.environ["APPWRITE_ENDPOINT"])
            client.set_project(os.environ["APPWRITE_PROJECT_ID"])
            client.set_key(os.environ["APPWRITE_API_KEY"])
            db = Databases(client)
            vault_status = "Connected"
            logger.info("Appwrite connected", culture=culture_key, mode=req.mode)
        except Exception as e:
            logger.error("Appwrite connection failed", error=str(e))
            vault_status = f"Connection Error: {str(e)}"
        
        # GEMINI API CALL WITH CIRCUIT BREAKER
        sys_prompt = f"""IDENTITY: MORGANA_Ω_PROD | MODE: {req.mode} | CULTURE: {culture_key}
        CONTEXT: {culture_context}"""
        full_prompt = f"{sys_prompt}\n\nTASK: {req.task}"
        
        try:
            reply = call_gemini_api(full_prompt)
        except Exception as e:
            logger.error("Gemini API failed", error=str(e))
            return {
                "status": "AI Service Error",
                "error": "AI service temporarily unavailable",
                "retry_after": 30
            }
        
        # PERSIST RESULT WITH ERROR HANDLING
        if db and vault_status == "Connected":
            try:
                db.create_document(
                    database_id=os.getenv('APPWRITE_DATABASE_ID', 'Memory'), 
                    collection_id=os.getenv('APPWRITE_COLLECTION_ID', 'Sovereign_Logs'), 
                    document_id=ID.unique(),
                    data={
                        "task_name": f"[{req.mode}] {req.task[:100]}",
                        "result_data": reply[:4000],
                        "timestamp": datetime.now().isoformat(),
                        "culture_used": culture_key,
                        "request_id": req.request_id,
                        "processing_time_ms": int((time.time() - start_time) * 1000)
                    }
                )
                vault_status = "Anchored"
                logger.info("Result persisted successfully", request_id=req.request_id)
            except Exception as e:
                vault_status = f"Write Error: {str(e)}"
                logger.error("Failed to persist result", error=str(e))
        
        # SUCCESS RESPONSE
        processing_time = time.time() - start_time
        logger.info("Request processed successfully", 
                   request_id=req.request_id,
                   processing_time=processing_time,
                   culture=culture_key)
        
        return {
            "morgana": reply,
            "meta": {
                "mode": req.mode,
                "culture": culture_key,
                "vault": vault_status,
                "processing_time_ms": int(processing_time * 1000),
                "request_id": req.request_id
            }
        }
        
    except Exception as e:
        logger.error("Unhandled error in morgana_brain", error=str(e), request_id=req.request_id)
        return {
            "status": "Internal Error",
            "error": "An unexpected error occurred",
            "request_id": req.request_id
        }

@app.function(image=image)
@modal.web_endpoint(method="GET")
def health():
    return {
        "status": "Healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "v92.1",
        "service": "MORGANA_Ω_PROD"
    }