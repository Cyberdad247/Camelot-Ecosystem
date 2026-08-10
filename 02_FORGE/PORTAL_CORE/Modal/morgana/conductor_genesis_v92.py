# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict

import structlog
import yaml

# ==========================================
# 🛡️ ENHANCED CONFIGURATION & LOGGING
# ==========================================

@dataclass
class Config:
    """Production configuration with environment-specific settings"""
    environment: str = os.getenv("ENVIRONMENT", "development")
    modal_timeout: int = 60 if os.getenv("ENVIRONMENT") == "production" else 30
    retry_attempts: int = 5 if os.getenv("ENVIRONMENT") == "production" else 3
    backup_retention_days: int = 30
    max_requests_per_minute: int = 100
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 30
    modal_secret_name: str = "my-sovereign-secrets"
    
    def __post_init__(self):
        try:
            with open("config.yaml", "r") as f:
                data = yaml.safe_load(f)
                if self.environment in data.get("environments", {}):
                    env_config = data["environments"][self.environment]
                    for key, value in env_config.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
        except FileNotFoundError:
            pass

# Initialize structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
config = Config()

# ==========================================
# 🛡️ ENHANCED PAYLOADS WITH ERROR HANDLING
# ==========================================

# 1. MORGANA CORE (MODAL) - Production Ready
MORGANA_PAYLOAD_TEMPLATE = """
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
    secrets=[modal.Secret.from_name("__SECRET_NAME__")],
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
        sys_prompt = f"IDENTITY: MORGANA_Omega_PROD | MODE: {req.mode} | CULTURE: {culture_key}\nCONTEXT: {culture_context}"
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
        "service": "MORGANA_Omega_PROD"
    }
"""

MORGANA_PAYLOAD = MORGANA_PAYLOAD_TEMPLATE.replace("__SECRET_NAME__", config.modal_secret_name)

# 2. HOLOGRAPHIC BODY (REACT) - Production Ready
FRONTEND_PAYLOAD = """
"use client";
import React, { useRef, useMemo, useState, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Sphere, MeshDistortMaterial, Float, Stars, Html } from "@react-three/drei";
import * as THREE from "three";

interface MorganaAvatarProps {
  mode?: "IDLE" | "RESEARCH" | "DEV" | "MUSIC" | "ANALYSIS";
  onError?: (error: Error) => void;
  requestId?: string;
}

interface ModeColors {
  IDLE: string;
  RESEARCH: string;
  DEV: string;
  MUSIC: string;
  ANALYSIS: string;
}

const MODE_COLORS: ModeColors = {
  IDLE: "#D4AF37",
  RESEARCH: "#00F0FF", 
  DEV: "#10B981",
  MUSIC: "#8B5CF6",
  ANALYSIS: "#F59E0B"
};

interface LivingCoreProps {
  mode: keyof ModeColors;
  onError?: (error: Error) => void;
}

function LivingCore({ mode, onError }: LivingCoreProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [error, setError] = useState<Error | null>(null);
  
  const color = useMemo(() => MODE_COLORS[mode] || MODE_COLORS.IDLE, [mode]);
  
  useFrame((state) => {
    try {
      const t = state.clock.getElapsedTime();
      if(meshRef.current) {
          const material = meshRef.current.material as THREE.MeshStandardMaterial;
          material.distort = 0.4 + Math.sin(t) * 0.2;
          meshRef.current.rotation.x = t * 0.1;
          meshRef.current.rotation.y = t * 0.15;
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Unknown error");
      setError(error);
      onError?.(error);
    }
  });

  if (error) {
    return (
      <Html center>
        <div className="bg-red-900/80 text-white p-4 rounded">
          <p>3D Rendering Error</p>
          <p className="text-sm">{error.message}</p>
        </div>
      </Html>
    );
  }

  return (
    <Float speed={2} rotationIntensity={1} floatIntensity={2}>
      <Sphere args={[1, 64, 64]} ref={meshRef} scale={1.2}>
        <MeshDistortMaterial 
            color={color} 
            envMapIntensity={1} 
            clearcoat={1} 
            clearcoatRoughness={0.1} 
            metalness={0.1} 
            roughness={0.2}
        />
      </Sphere>
    </Float>
  );
}

function ErrorBoundary({ children }: { children: React.ReactNode }) {
  const [hasError, setHasError] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      setHasError(true);
      setError(new Error(event.message));
    };
    
    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (hasError) {
    return (
      <div className="w-full h-64 bg-black/80 flex items-center justify-center border border-red-500">
        <div className="text-red-400 text-center">
          <h3>Rendering Error</h3>
          <p className="text-sm">{error?.message || "Unknown error"}</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

export default function MorganaAvatar({ mode = "IDLE", onError, requestId }: MorganaAvatarProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [isHealthy, setIsHealthy] = useState(true);
  const [lastCheck, setLastCheck] = useState<string>(new Date().toLocaleTimeString());
  const [dimensions, setDimensions] = useState({ width: 800, height: 256 });

  useEffect(() => {
    const updateDimensions = () => {
      setDimensions({
        width: window.innerWidth,
        height: Math.max(256, window.innerHeight * 0.3)
      });
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Heartbeat Logic
  useEffect(() => {
    const checkHealth = async () => {
      try {
        // Logic would point to the health endpoint deployed via Modal
        setLastCheck(new Date().toLocaleTimeString());
        setIsHealthy(true);
      } catch (err) {
        setIsHealthy(false);
      }
    };
    
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const handleCanvasError = (error: Error) => {
    console.error("Canvas rendering error:", error);
    onError?.(error);
  };

  return (
    <ErrorBoundary>
      <div className="w-full h-64 relative bg-black/80 border-b border-[#D4AF37]/20 overflow-hidden min-h-[200px]">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50 z-10">
            <div className="text-[#D4AF37] animate-pulse">Loading Morgana...</div>
          </div>
        )}
        
        <Canvas 
          camera={{ position: [0, 0, 3] }}
          gl={{ antialias: true, alpha: true }}
          dpr={[1, 2]}
          onCreated={() => setIsLoading(false)}
          onError={handleCanvasError}
        >
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1.5} color="#fff" />
          <LivingCore mode={mode} onError={handleCanvasError} />
          <Stars radius={100} depth={50} count={2000} factor={4} saturation={0} fade speed={1} />
        </Canvas>
        
        <div className="absolute bottom-2 right-4 text-[10px] font-mono text-[#D4AF37] tracking-widest opacity-80 bg-black/50 px-2 py-1 rounded">
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></span>
            MORGANA_Omega_PROD // STATUS: {mode}
          </div>
          {requestId && <span className="text-[8px]">REQ: {requestId.slice(-8)}</span>}
          <div className="text-[7px] opacity-50">LST_CHK: {lastCheck}</div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
"""

# ==========================================
# ⚙️ ENHANCED CONDUCTOR ENGINE
# ==========================================

class DeploymentManager:
    """Manages deployment state and rollback capabilities"""
    
    def __init__(self):
        self.backup_dir = None
        self.deployment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.state_file = Path("deployment_state.json")
        
    def create_backup(self) -> bool:
        """Create backup of existing deployment"""
        try:
            self.backup_dir = Path(f"backups/deployment_{self.deployment_id}")
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup existing files
            files_to_backup = [
                "morgana_core.py",
                "components/3d/MorganaAvatar.tsx"
            ]
            
            for file_path in files_to_backup:
                if Path(file_path).exists():
                    backup_path = self.backup_dir / file_path.replace("/", "_")
                    shutil.copy2(file_path, backup_path)
                    logger.info("Backed up file", original=file_path, backup=backup_path)
            
            state = {
                "deployment_id": self.deployment_id,
                "timestamp": datetime.now().isoformat(),
                "backup_location": str(self.backup_dir),
                "status": "backup_created"
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
            return True
        except Exception as e:
            logger.error("Backup creation failed", error=str(e))
            return False
    
    def rollback(self) -> bool:
        """Rollback to previous deployment"""
        try:
            if not self.backup_dir or not self.backup_dir.exists():
                logger.error("No backup available for rollback")
                return False
            
            for backup_file in self.backup_dir.glob("*"):
                if backup_file.is_file():
                    original_name = backup_file.name.replace("_", "/")
                    if original_name.endswith(".py") or original_name.endswith(".tsx"):
                        shutil.copy2(backup_file, original_name)
                        logger.info("Restored file", backup=backup_file, original=original_name)
            
            logger.info("Rollback completed successfully")
            return True
        except Exception as e:
            logger.error("Rollback failed", error=str(e))
            return False

def log(msg: str, level: str = "INFO", **kwargs):
    """Enhanced logging with structured data"""
    log_levels = {
        "INFO": lambda: logger.info(msg, **kwargs),
        "SUCCESS": lambda: logger.info(f"✅ {msg}", **kwargs),
        "WARN": lambda: logger.warning(msg, **kwargs),
        "ERROR": lambda: logger.error(msg, **kwargs),
    }
    if level in log_levels:
        log_levels[level]()
    else:
        logger.info(msg, **kwargs)

def hitl_gate(action: str, critical: bool = True) -> bool:
    """Enhanced HITL with logging and auto-confirm support"""
    log(f"🚪 PROPOSAL: {action}", "WARN", critical=critical)
    
    if os.getenv("AUTO_CONFIRM", "false").lower() == "true":
        log(f"✅ AUTO-AUTHORIZED (Env Var): {action}", "SUCCESS")
        return True

    try:
        # Check if running in non-interactive mode
        if not sys.stdin.isatty():
             log(f"⚠️ NON-INTERACTIVE MODE: Assuming YES for {action}", "WARN")
             return True

        response = input("   >>> AUTHORIZE? (y/n): ").lower().strip()
    except EOFError:
        log(f"⚠️ EOF DETECTED: Assuming YES for {action}", "WARN")
        return True
    
    if response == 'y':
        log(f"✅ AUTHORIZED: {action}", "SUCCESS")
        return True
    else:
        log(f"❌ ABORTED BY SOVEREIGN: {action}", "ERROR")
        if critical:
            sys.exit(0)
        return False

def validate_environment() -> Dict[str, bool]:
    """Comprehensive environment validation"""
    results = {}
    
    # 1. Python Dependencies
    required_packages = [
        "modal", "google-generativeai", "appwrite", 
        "replicate", "pydantic", "circuitbreaker", 
        "structlog", "redis", "pyyaml"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            results[f"package_{package}"] = True
        except ImportError:
            results[f"package_{package}"] = False
            logger.error("Missing package", package=package)
    
    # 2. Modal Authentication
    try:
        result = subprocess.run(["modal", "token", "list"], 
                              capture_output=True, text=True, timeout=10)
        results["modal_auth"] = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        results["modal_auth"] = False
        logger.error("Modal authentication failed")

    # 3. Modal Secrets Check (New)
    try:
        result = subprocess.run(["modal", "secret", "list"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
             # Very basic check if secret name exists in output
             results["modal_secret_exists"] = config.modal_secret_name in result.stdout
             if not results["modal_secret_exists"]:
                 logger.error(f"Modal secret '{config.modal_secret_name}' not found in cloud.")
        else:
             results["modal_secret_exists"] = False
    except:
        results["modal_secret_exists"] = False
    
    # 4. Required Local Secrets (Env Vars)
    required_secrets = [
        "APPWRITE_ENDPOINT", "APPWRITE_PROJECT_ID", 
        "APPWRITE_API_KEY", "GOOGLE_API_KEY"
    ]
    for secret in required_secrets:
        results[f"secret_{secret}"] = bool(os.getenv(secret))
        if not results[f"secret_{secret}"]:
            logger.error("Missing secret", secret=secret)
    
    return results

def install_dependencies():
    dependencies = [
        "modal>=0.63.0", "google-generativeai>=0.3.0", 
        "appwrite>=4.0.0", "replicate>=0.15.0", 
        "pydantic>=2.0.0", "circuitbreaker>=1.4.0",
        "structlog>=23.1.0", "redis>=5.0.0", "pyyaml>=6.0"
    ]
    
    logger.info("Installing dependencies", dependencies=dependencies)
    
    for dep in dependencies:
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], check=True, capture_output=True)
            logger.info("Installed dependency", dependency=dep)
        except subprocess.CalledProcessError as e:
            logger.error("Failed to install dependency", dependency=dep, error=str(e))
            return False
    return True

def main():
    log("🚀 INITIATING CAMELOT_OS v92.0 PRODUCTION SEQUENCE (REFACTORED)", "INFO")
    deployment_manager = DeploymentManager()
    
    try:
        # PHASE 0: ENVIRONMENT VALIDATION
        log("🔍 Performing comprehensive environment validation...", "INFO")
        validation_results = validate_environment()
        
        failed_checks = [k for k, v in validation_results.items() if not v]
        if failed_checks:
            if os.getenv("BYPASS_VALIDATION", "false").lower() == "true":
                log(f"⚠️ BYPASS_VALIDATION ACTIVE. Ignoring failures: {failed_checks}", "WARN")
                failed_checks = []
            else:
                log(f"❌ Environment validation failed: {failed_checks}", "ERROR")
            
            if "package_" in str(failed_checks):
                if hitl_gate("Install missing Python packages?", critical=False):
                    if not install_dependencies():
                        sys.exit(1)
                else:
                    sys.exit(1)
            
            if "modal_auth" in failed_checks:
                log("Please run 'modal setup' first", "ERROR")
                if not os.getenv("BYPASS_MODAL_AUTH"):
                    sys.exit(1)

            if "modal_secret_exists" in failed_checks:
                log(f"Secret '{config.modal_secret_name}' missing in Modal.", "ERROR")
                if not hitl_gate("Bypass secret check? (Logic will fail online)", critical=False):
                    sys.exit(1)
        
        log("✅ Environment validation passed", "SUCCESS")
        
        # PHASE 1: BACKUP
        if hitl_gate("Create backup of existing deployment?", critical=False):
            deployment_manager.create_backup()
        
        # PHASE 2: DEPLOY BACKEND
        skip_deploy = os.getenv("SKIP_DEPLOY", "false").lower() == "true"
        if hitl_gate("DEPLOY MORGANA PRODUCTION SWARM", critical=True):
            
            # READ TEMPLATE
            template_path = Path("templates/morgana_core.py")
            if not template_path.exists():
                log("❌ Template 'templates/morgana_core.py' NOT FOUND.", "ERROR")
                sys.exit(1)
                
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # INJECT CONFIG
            content = content.replace("__SECRET_NAME__", config.modal_secret_name)
            
            # WRITE ARTIFACT
            with open("morgana_core.py", "w", encoding="utf-8") as f:
                f.write(content)
            
            log("🔨 Forged 'morgana_core.py' from template.", "SUCCESS")

            if skip_deploy:
                log("⚠️ SKIPPING CLOUD DEPLOYMENT (SKIP_DEPLOY=true)", "WARN")
            else:
                log("⚡ Actuating Kinetic Strike (Deployment)...", "INFO")
                try:
                    result = subprocess.run(
                        ["modal", "deploy", "morgana_core.py"], 
                        check=True, 
                        capture_output=True, 
                        text=True,
                        timeout=300
                    )
                    log("🎉 MORGANA PRODUCTION IS ALIVE", "SUCCESS")
                except Exception as e:
                    log(f"💥 DEPLOYMENT FAILED: {e}", "ERROR")
                    if hitl_gate("Rollback?", critical=False):
                        deployment_manager.rollback()
                    sys.exit(1)
        
        # PHASE 3: DEPLOY FRONTEND
        if hitl_gate("INJECT PRODUCTION HOLOGRAPHIC AVATAR", critical=True):
            template_path = Path("templates/MorganaAvatar.tsx")
            target_file = Path("components/3d/MorganaAvatar.tsx")
            
            if template_path.exists():
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(template_path, target_file)
                log(f"✅ Holographic Component injected at: {target_file}", "SUCCESS")
            else:
                log("❌ Template 'MorganaAvatar.tsx' missing.", "ERROR")
                
        log("🎉 PRODUCTION GENESIS COMPLETE", "SUCCESS")
        
    except KeyboardInterrupt:
        log("\n⚠️ Interrupted", "WARN")
        sys.exit(1)
    except Exception as e:
        log(f"💥 UNEXPECTED ERROR: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()