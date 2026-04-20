# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Tier 1 launcher (blueprint-compatible)
#
# Equivalent to the blueprint's:
#     cd local_brain && python main.py
#
# Delegates to the real kernel at 01_KERNEL/EXCALIBUR/core/excalibur.py
# and binds to port 8001 per Tier 1 spec.
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_KERNEL = _REPO / "01_KERNEL"
for _p in [_KERNEL, _KERNEL / "EXCALIBUR" / "core",
           _KERNEL / "agora", _KERNEL / "forge", _KERNEL / "iron_gate",
           _KERNEL / "merlin", _KERNEL / "senses", _KERNEL / "titan"]:
    sys.path.insert(0, str(_p))

import uvicorn  # noqa: E402

from excalibur import app  # noqa: E402

if __name__ == "__main__":
    port = int(os.getenv("LOCAL_BRAIN_PORT", "8001"))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
