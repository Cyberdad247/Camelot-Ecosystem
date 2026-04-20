# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import sys

# Ensure the 01_KERNEL directory is in path
kernel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(kernel_path)

try:
    from assimilation.core import handlers, types

    print("[SUCCESS] Imported assimilation.core.handlers")
    print("[SUCCESS] Imported assimilation.core.types")
except ImportError as e:
    print(f"[FAIL] Import failed: {e}")
    # print debug info
    print(f"Sys Path: {sys.path}")
    sys.exit(1)

# Check Pydantic
try:
    req = types.AssimilationRequest(repo_path="./test", tags=["test"])
    print(f"[SUCCESS] Pydantic Model instantiated: {req}")
except Exception as e:
    print(f"[FAIL] Pydantic check failed: {e}")
    sys.exit(1)