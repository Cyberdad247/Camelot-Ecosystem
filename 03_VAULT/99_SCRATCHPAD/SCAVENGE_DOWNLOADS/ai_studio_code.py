# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
from fastapi import FastAPI, UploadFile, File, Form
import tempfile, os, json
from app.models.schemas import SynergyAnalysisResponse
from app.services import analysis

app = FastAPI(title="Sonic Blueprint: Synergy_Analyzer")

@app.post("/analyze", response_model=SynergyAnalysisResponse)
async def analyze_synergy(instrument_data_str: str = Form(...), audio_file: UploadFile = File(...)):
    instrument_data = json.loads(instrument_data_str)
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await audio_file.read())
            tmp_path = tmp.name
        synergy_data = analysis.perform_full_analysis(tmp_path, instrument_data)
        return synergy_data
    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)