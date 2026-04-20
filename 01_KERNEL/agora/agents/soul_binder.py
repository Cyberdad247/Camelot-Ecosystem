# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
SOUL_BINDER: Phase 4 Neural Enrichment
Generates and injects Proteus MPI vectors into Knight configurations.
"""

import os
import json
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("soul_binder")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:1.7b"

# OCEAN Model Base Vectors
PERSONA_TEMPLATES = {
    "merlin": {"O": 0.95, "C": 1.00, "E": 0.35, "A": 0.45, "N": 0.01},
    "anya":   {"O": 0.90, "C": 0.95, "E": 0.80, "A": 0.60, "N": 0.05},
    "boris":  {"O": 0.85, "C": 1.00, "E": 0.30, "A": 0.40, "N": 0.01},
    "oracle": {"O": 0.98, "C": 0.90, "E": 0.20, "A": 0.50, "N": 0.10},
}

def generate_soul_prompt(knight_id, base_vector):
    """Refine the system prompt using the local model"""
    prompt = f"""
    Knight ID: {knight_id}
    Proteus MPI Vector: {json.dumps(base_vector)}
    
    Task: Refine the system prompt for this AI agent to embody these exact personality traits.
    Focus on: Professional tone, cognitive bias, and specific domain expertise.
    Output only the refined system instruction block.
    """
    
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        })
        return response.json().get("response", "")
    except Exception as e:
        logger.error(f"Ollama generation failed: {e}")
        return None

def bind_souls():
    """Iterate through knights and update their 'souls'"""
    for knight, vector in PERSONA_TEMPLATES.items():
        logger.info(f"Binding soul for {knight}...")
        soul = generate_soul_prompt(knight, vector)
        if soul:
            # Save to vault
            output_path = f"C:/Users/vizio/CAMELOT_OS/03_VAULT/Knights/souls/{knight}_soul.txt"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(soul)
            logger.info(f"Successfully bound {knight} soul.")

if __name__ == "__main__":
    bind_souls()
