# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import modal
import os
import time
import logging
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("resonance-bridge")

# 1. DEFINE THE FASTAPI APP WITH CORS
web_app = FastAPI()

# THIS IS THE KEY: Allow ALL origins to talk to this backend
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows V0, Localhost, Vercel deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = modal.App("resonance-bridge-v56")

image = modal.Image.debian_slim().pip_install(
    "gradio_client", 
    "pydantic", 
    "requests", 
    "fastapi" 
)

class ResonanceRequest(BaseModel):
    audio_url: str
    prompt: str
    shard_id: int = 1

# 2. MOUNT THE WEB APP
@app.function(
    image=image, 
    timeout=900, # 15 minutes max
    secrets=[
        modal.Secret.from_name("github-token"),
        modal.Secret.from_name("hf-secret")
    ]
)
@modal.asgi_app()
def fastapi_app():
    return web_app

# 3. DEFINE THE ENDPOINT ON THE APP
@web_app.post("/")
async def actuate_resonance(request: ResonanceRequest):
    from gradio_client import Client
    
    token = os.environ["HF_TOKEN"]
    SPACE_ID = "Wan-AI/Wan2.1"
    
    logger.info(f"Connecting to {SPACE_ID} for Shard_{request.shard_id}")
    
    try:
        client = Client(SPACE_ID, token=token)
        
        logger.info("Triggering async video generation")
        trigger_result = client.predict(
            prompt=request.prompt,
            size="1280*720",      
            watermark_wan=True,   
            seed=-1,              
            api_name="/t2v_generation_async"
        )
        
        logger.info(f"Job queued — estimated wait: {trigger_result[1]}s")
        
        start_time = time.time()
        video_url = None
        
        # POLLING LOOP
        while time.time() - start_time < 600:
            status_result = client.predict(api_name="/status_refresh")
            video_data = status_result[0]
            
            if video_data and 'video' in video_data and video_data['video']:
                video_url = video_data['video']
                logger.info(f"Video generation complete: {video_url}")
                break
            
            # Keep Modal alive
            time.sleep(5)
            
        if not video_url:
            return {"status": "ERROR", "message": "Timed out waiting for video generation."}
        
        return {
            "status": "SUCCESS",
            "shard_id": request.shard_id,
            "video_url": video_url,
            "message": "Asset successfully rendered."
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Resonance bridge error: {error_msg}")
        return {"status": "ERROR", "message": error_msg}