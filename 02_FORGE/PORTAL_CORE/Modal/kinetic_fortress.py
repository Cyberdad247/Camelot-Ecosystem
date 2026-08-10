# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
from datetime import datetime

import modal

# 1. FORGE DEFINITION
app = modal.App("camelot-kinetic-fortress")
# 2. THE IMAGE (Standardizing the Knight's Armor)
image = modal.Image.debian_slim().pip_install(
    "google-generativeai", 
    "replicate", 
    "pydantic",
    "fastapi",
    "appwrite"
)

# 2. THE ANYA VIEWPORT (The Sovereign Interface)
@app.function(image=image, secrets=[modal.Secret.from_name("my-sovereign-secrets")])
@modal.web_endpoint()
def anya_viewport(task: str):
    import google.generativeai as genai
    from appwrite.client import Client
    from appwrite.id import ID
    from appwrite.services.databases import Databases

    # 🛡️ GATE I: ANCHOR THE HANDSHAKE
    client = Client()
    client.set_endpoint(os.environ["APPWRITE_ENDPOINT"])
    client.set_project(os.environ["APPWRITE_PROJECT_ID"])
    client.set_key(os.environ["APPWRITE_API_KEY"])
    db = Databases(client)

    # 🧠 GATE II: THE THINKING PHASE (Gemini)
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(task)
    
    # 💎 GATE III: THE MEMORY PHASE (Appwrite Vault)
    # We save the results into the attributes we created: task_name, result_data, timestamp
    try:
        db.create_document(
            database_id='Memory', # Make sure this matches your DB name
            collection_id='Sovereign_Logs', # Make sure this matches your Collection ID
            document_id=ID.unique(),
            data={
                "task_name": task[:250],
                "result_data": response.text[:4990],
                "timestamp": datetime.now().isoformat()
            }
        )
        persistence_status = "✅ Memory Anchored."
    except Exception as e:
        persistence_status = f"🐙 Anchor Failure: {str(e)}"

    return {
        "anya_voice": "Sovereign, the task is complete.",
        "thought": response.text,
        "vault_status": persistence_status
    }