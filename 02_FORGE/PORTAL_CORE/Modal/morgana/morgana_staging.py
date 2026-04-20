# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import modal
import os
from morgana_core import (
    image, MorganaRequest, CULTURES, get_culture_context,
    call_gemini_api, RateLimiter, morgana_brain
)

# SEPARATE APP: Shares the same API logic
app_staging = modal.App("morgana-research-agency-staging")

@app_staging.function(
    image=image,
    secrets=[modal.Secret.from_name("shared-api-keys")],
    timeout=300,
    memory=512,
)
@modal.fastapi_endpoint(method="POST")
def morgana_brain_staging(req: MorganaRequest):
    """Staging version of the same API"""
    return morgana_brain(req)

@app_staging.function(image=image)
@modal.fastapi_endpoint(method="GET")
def health_staging():
    return {
        "status": "Healthy (Staging)",
        "timestamp": "2026-01-14T22:45:00",
        "version": "v92.1-staging",
        "service": "MORGANA_Ω_STAGING"
    }</content>
<parameter name="filePath">c:\Users\vizio\Applications\chimera-os\Modal\morgana\morgana_staging.py