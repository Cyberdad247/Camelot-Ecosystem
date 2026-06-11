# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from agents.coordinator_agent import coordinator_agent
from agno.agent import RunResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS to allow requests from your frontend
_ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",") if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Define the request body model
class AnalysisRequest(BaseModel):
    video_url: str

# Define the entry point
@app.get("/")
async def root():
    return {"message": "Welcome to the video analysis API!"}

# Define the analysis endpoint
@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    video_url = request.video_url
    prompt = f"Analyze the following video: {video_url}"
    response: RunResponse = coordinator_agent.run(prompt)

    # Assuming response.content is a Pydantic model or a dictionary
    json_compatible_response = jsonable_encoder(response.content)
    return JSONResponse(content=json_compatible_response)