# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
DEPRECATED: This stub is superseded by the full Resonance Bridge at
  02_FORGE/Modal/bridge.py (app: resonance-bridge-v56)

That implementation provides:
  - Wan-AI/Wan2.1 video generation via HuggingFace Spaces
  - FastAPI + CORS endpoint at POST /
  - Requires Modal secrets: github-token, hf-secret
  - Deploy: modal deploy CAMELOT_OS/02_FORGE/Modal/bridge.py

This file is retained for backwards compatibility only.
"""

import warnings

warnings.warn(
    "excalibur-resonance/proxy/bridge.py is deprecated. "
    "Use 02_FORGE/Modal/bridge.py (resonance-bridge-v56) instead.",
    DeprecationWarning,
    stacklevel=2,
)


def bootstrap():
    return {
        "status": "deprecated",
        "message": "Use 02_FORGE/Modal/bridge.py (resonance-bridge-v56) instead",
        "deploy_cmd": "modal deploy CAMELOT_OS/02_FORGE/Modal/bridge.py",
    }


if __name__ == "__main__":
    print(bootstrap())
