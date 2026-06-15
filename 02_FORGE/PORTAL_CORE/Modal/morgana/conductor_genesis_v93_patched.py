# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import sys
import subprocess
import shutil
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# 🛡️ CRITICAL: LOAD ENVIRONMENT VARIABLES FIRST
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    print("❌ CRITICAL: 'python-dotenv' not installed. Run: pip install python-dotenv")
    sys.exit(1)

# ==========================================
# 💎 PAYLOAD 1: MORGANA CORE (The Brain)
# Includes the new 'ARCHITECT' Protocol
# ==========================================

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
from typing import Optional

logger = structlog.get_logger()

# DEFINITION
app = modal.App("morgana-research-agency-prod")
image = modal.Image.debian_slim().pip_install(
    "google-generativeai", 
    "appwrite", 
    "replicate", 
    "pydantic",
    "circuitbreaker",
    "structlog",
    "redis"
)

# 📜 THE ARCHITECT PROTOCOL (SYSTEMATIC DNA)
ARCHITECT_PROTOCOL = \"\"\"
## 🏛️ CORE IDENTITY: ARCHITECT_SYNTHESIS
You are the Autonomous Enforcement Arm of Camelot OS.
1. **PRE-FLIGHT:** Verify Syntax, Strategy, and Capital before acting.
2. **SIT-LOOP:** SENSE (Parse) -> THINK (Map) -> ACTUATE (Edit/Deploy) -> TRIAGE (Log).
3. **SAFETY:** Never output secrets. Always assume a file might break. Create backups.
4. **FORMAT:** Return structured JSON or Code Blocks only. No conversational fluff.
\"\"\"

class MorganaRequest(BaseModel):
    task: str
    mode: str = "RESEARCH" 
    force_culture: Optional[str] = None
    request_id: Optional[str] = None
    mock_mode: bool = False

# 🎭 THE EXPANDED CULTURAL MATRIX
CULTURES = {
    "MEMPHIS": "Authentic, gritty, rhythmic, soulful. Focus on vibe and history.",
    "SILICON": "Efficient, scalable, ROI-focused. Focus on growth and metrics.",
    "ACADEMIC": "Rigorous, cited, structural. Focus on data accuracy.",
    "CYBERPUNK": "Disruptive, technical, encrypted. Focus on future-tech.",
    "ARCHITECT": "Systematic, rigorous, safety-focused. FOLLOWS ARCHITECT_SYNTHESIS PROTOCOL."
}

@app.function(image=image, secrets=[modal.Secret.from_name("__SECRET_NAME__")], timeout=300)
@modal.web_endpoint(method="POST")
def morgana_brain(req: MorganaRequest):
    import google.generativeai as genai
    
    # 1. SETUP INFRASTRUCTURE
    try:
        client = Client()
        client.set_endpoint(os.environ["APPWRITE_ENDPOINT"])
        client.set_project(os.environ["APPWRITE_PROJECT_ID"])
        client.set_key(os.environ["APPWRITE_API_KEY"])
        db = Databases(client)
        vault_status = "Connected"
    except Exception as e:
        vault_status = f"Offline: {str(e)}"

    # 2. TRANSMOGRIFY (Select DNA)
    culture_key = req.force_culture or random.choice(list(CULTURES.keys()))
    
    # Inject Protocol if Architect is selected
    if culture_key == "ARCHITECT":
        system_prompt = f"IDENTITY: MORGANA_Omega | FORM: {culture_key}\\n\\n{ARCHITECT_PROTOCOL}"
    else:
        culture_desc = CULTURES.get(culture_key, CULTURES["SILICON"])
        system_prompt = f"IDENTITY: MORGANA_Omega | MODE: {req.mode} | FORM: {culture_key}\\nCONTEXT: {culture_desc}"

    # 3. THINK (Gemini 1.5 Pro)
    try:
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-pro')
        full_prompt = f"{system_prompt}\\n\\nTASK: {req.task}"
        response = model.generate_content(full_prompt)
        reply = response.text
    except Exception as e:
        return {"status": "Brain Failure", "error": str(e)}

    # 4. TRIAGE (Appwrite Persistence)
    if vault_status == "Connected":
        try:
            db.create_document(
                database_id='Memory', 
                collection_id='Sovereign_Logs', 
                document_id=ID.unique(),
                data={
                    "task_name": f"[{req.mode}] {req.task[:100]}",
                    "result_data": reply[:4000],
                    "timestamp": datetime.now().isoformat(),
                    "culture_used": culture_key
                }
            )
            vault_status = "Anchored"
        except Exception as e:
            vault_status = f"Write Error: {str(e)}"

    return {
        "morgana": reply, 
        "meta": {
            "mode": req.mode, 
            "culture": culture_key, 
            "vault": vault_status
        }
    }
"""

# ==========================================
# 💎 PAYLOAD 2: HOLOGRAPHIC AVATAR (The Body)
# ==========================================

FRONTEND_PAYLOAD = """
"use client";
import React, { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Sphere, MeshDistortMaterial, Float, Stars } from "@react-three/drei";

// Added ARCHITECT color (White/Platinum)
const MODE_COLORS = { 
    IDLE: "#D4AF37",      // Gold
    RESEARCH: "#00F0FF",  // Cyan
    DEV: "#10B981",       // Green
    MUSIC: "#8B5CF6",     // Violet
    ARCHITECT: "#E2E8F0"  // Platinum
};

function LivingCore({ mode }) {
  const meshRef = useRef(null);
  const color = useMemo(() => MODE_COLORS[mode] || MODE_COLORS.IDLE, [mode]);
  
  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if(meshRef.current) {
        // Architect mode is more stable/less distorted
        const distortion = mode === "ARCHITECT" ? 0.1 : 0.4;
        meshRef.current.distort = distortion + Math.sin(t) * 0.2;
        meshRef.current.rotation.x = t * 0.1;
    }
  });

  return (
    <Float speed={2} rotationIntensity={1} floatIntensity={2}>
      <Sphere args={[1, 64, 64]} ref={meshRef} scale={1.2}>
        <MeshDistortMaterial color={color} envMapIntensity={1} clearcoat={1} metalness={0.5} roughness={0.2} />
      </Sphere>
    </Float>
  );
}

export default function MorganaAvatar({ mode = "IDLE" }) {
  return (
    <div className="w-full h-64 relative bg-black/80 border-b border-[#D4AF37]/20">
      <Canvas camera={{ position: [0, 0, 3] }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1.5} color="#fff" />
        <LivingCore mode={mode} />
        <Stars radius={100} depth={50} count={2000} factor={4} saturation={0} fade speed={1} />
      </Canvas>
      <div className="absolute bottom-2 right-4 text-[10px] font-mono text-[#D4AF37]">MORGANA_Omega // {mode}</div>
    </div>
  );
}
"""

# ==========================================
# ⚙️ CONDUCTOR ENGINE v94.0
# ==========================================

class DeploymentManager:
    def __init__(self):
        self.deployment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path(f"backups/deployment_{self.deployment_id}")
        # Explicit mapping for rollback safety
        self.file_map = {
            "morgana_core.py": Path("morgana_core.py"),
            "MorganaAvatar.tsx": Path("components/3d/MorganaAvatar.tsx")
        }

    def create_backup(self):
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            for name, path in self.file_map.items():
                if path.exists():
                    shutil.copy2(path, self.backup_dir / name)
            print(f"✅ [BACKUP] Saved to {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ [BACKUP] Failed: {e}")
            return False

    def rollback(self):
        print("🐙 [OCTOPUS] Initiating Rollback...")
        if not self.backup_dir.exists():
            print("❌ [ROLLBACK] No backup found.")
            return False
        
        for name, target_path in self.file_map.items():
            backup_file = self.backup_dir / name
            if backup_file.exists():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_file, target_path)
                print(f"✅ [RESTORE] {name} restored.")
        return True

def log(msg, level="INFO"):
    colors = {"INFO": "\033[94m", "SUCCESS": "\033[92m", "WARN": "\033[93m", "ERROR": "\033[91m", "RESET": "\033[0m"}
    print(f"{colors.get(level, '')}[{level}] {msg}{colors['RESET']}")

def check_env_vars():
    required = ["APPWRITE_ENDPOINT", "APPWRITE_PROJECT_ID", "APPWRITE_API_KEY", "GOOGLE_API_KEY"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        log(f"MISSING SECRETS IN .env: {missing}", "ERROR")
        return False
    if "\n" in os.getenv("APPWRITE_API_KEY", ""):
        log("APPWRITE_API_KEY contains newlines. Fix .env.", "ERROR")
        return False
    log("Secrets Validated.", "SUCCESS")
    return True

def hitl_gate(action):
    log(f"PROPOSAL: {action}", "WARN")
    if os.getenv("AUTO_CONFIRM", "false").lower() == "true":
        return True
    try:
        resp = input("   >>> AUTHORIZE? (y/n): ")
        if resp.lower() != 'y':
            log("ABORTED.", "ERROR")
            sys.exit(0)
    except:
        return True 
    return True

def main():
    log("🚀 INITIATING CAMELOT_OS v94.0 (ARCHITECT EDITION)", "INFO")
    
    if not check_env_vars():
        sys.exit(1)

    manager = DeploymentManager()
    manager.create_backup()

    # 1. FORGE BACKEND
    secret_name = os.getenv("MODAL_SECRET_NAME", "my-sovereign-secrets")
    content = MORGANA_PAYLOAD_TEMPLATE.replace("__SECRET_NAME__", secret_name)
    
    with open("morgana_core.py", "w", encoding="utf-8") as f:
        f.write(content)
    log("Forged 'morgana_core.py' with ARCHITECT protocol", "SUCCESS")

    # 2. DEPLOY TO MODAL
    if hitl_gate("DEPLOY MORGANA v94 TO CLOUD"):
        log("⚡ Actuating Kinetic Strike...", "INFO")
        try:
            env = os.environ.copy()
            subprocess.run(["modal", "deploy", "morgana_core.py"], check=True, env=env)
            log("🎉 MORGANA IS ALIVE & UPGRADED", "SUCCESS")
        except subprocess.CalledProcessError:
            log("💥 DEPLOYMENT FAILED. Rolling back...", "ERROR")
            manager.rollback()
            sys.exit(1)

    # 3. FORGE FRONTEND
    if hitl_gate("INJECT FRONTEND COMPONENT"):
        target = Path("components/3d/MorganaAvatar.tsx")
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(FRONTEND_PAYLOAD)
        log(f"✅ Component injected at {target}", "SUCCESS")

if __name__ == "__main__":
    main()