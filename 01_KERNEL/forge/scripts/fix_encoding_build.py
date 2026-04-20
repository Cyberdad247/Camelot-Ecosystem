# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
import subprocess
import sys


def run_compileall():
    print("🛠️ [REPAIR] Forcing UTF-8 for compileall...")
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"

    # Run compileall on the root directory
    cmd = [sys.executable, "-m", "compileall", "."]

    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8")
        if result.returncode == 0:
            print("✅ [REPAIR] Compilation Successful.")
        else:
            print(f"⚠️ [REPAIR] Compilation had warnings/errors:\n{result.stderr}")
    except Exception as e:
        print(f"❌ [REPAIR] Compilation Failed: {e}")


if __name__ == "__main__":
    run_compileall()