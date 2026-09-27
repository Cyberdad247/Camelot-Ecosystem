# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import sys
import types
from pathlib import Path

import uvicorn

# 🛡️ CONFIGURATION
KERNEL_ROOT = Path(r"C:\Users\vizio\CAMELOT_OS\01_KERNEL")
SQUIRES_ROOT = KERNEL_ROOT / "Squires"
NOTEBOOK_ROOT = SQUIRES_ROOT / "Notebook_Brain"

# 1. Set PYTHONPATH to include Squires so 'open_notebook' is found
sys.path.insert(0, str(SQUIRES_ROOT))

# 2. Inject Environment Variables (The Sovereign's Keys)
os.environ["SURREAL_URL"] = "ws://localhost:8000/rpc"
os.environ["SURREAL_USER"] = "root"
os.environ["SURREAL_PASS"] = "root"
os.environ["SURREAL_NAMESPACE"] = "camelot"  # Corrected Key
os.environ["SURREAL_DATABASE"] = "notebook"  # Corrected Key
os.environ["GOOGLE_API_KEY"] = "PLACEHOLDER_KEY_REMOVED_BY_SIR_SENTINEL"
os.environ["API_BASE_URL"] = "http://127.0.0.1:5055"

# 3. Patch 'api' module to point to Notebook_Brain
api_module = types.ModuleType("api")
api_module.__path__ = [str(NOTEBOOK_ROOT)]
sys.modules["api"] = api_module

# 4. Integrate Morgana Logger
sys.path.insert(0, str(KERNEL_ROOT / "tools"))
from morgana_logger import MorganaLogger  # noqa: E402

m_logger = MorganaLogger(actor="Notebook_Brain_Igniter")

if __name__ == "__main__":
    m_logger.log("IGNITION_START", "Notebook Brain")
    print("🧠 [MERLIN] Igniting Notebook Brain...")

    # CHANGE WORKING DIRECTORY TO SQUIRES
    os.chdir(SQUIRES_ROOT)
    print(f"   - Context Switched to: {os.getcwd()}")

    try:
        sys.path.insert(0, str(NOTEBOOK_ROOT))  # Add inner root too

        from main import app

        m_logger.log("IGNITION_SUCCESS", "Notebook Brain", context={"port": 5055})
        print("✅ [MERLIN] Ignition Successful. Hosting on Port 5055.")
        uvicorn.run(app, host="127.0.0.1", port=5055, log_level="info")

    except Exception as e:
        m_logger.log("IGNITION_FAILURE", "Notebook Brain", status="FAILURE", context={"error": str(e)})
        print(f"❌ [CRITICAL] Ignition Failed: {e}")
        import traceback

        traceback.print_exc()