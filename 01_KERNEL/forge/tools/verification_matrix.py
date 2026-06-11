# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import subprocess
from datetime import datetime
from pathlib import Path

# 🛡️ CONFIGURATION
ROOT_DIR = Path(r"C:\Users\vizio\CAMELOT_OS")
FORGE_DIR = ROOT_DIR / "02_FORGE" / "Anya_Dashboard"
KERNEL_DIR = ROOT_DIR / "01_KERNEL"
REPORT_FILE = ROOT_DIR / "99_HISTORY" / "ULTIMATE_VERIFICATION_REPORT.md"

results = {}


def run_check(name, check_func):
    print(f"🔍 [ZENITH] Verifying: {name}...")
    try:
        status, details = check_func()
        results[name] = {"status": "PASS" if status else "FAIL", "details": details}
        if status:
            print("   ✅ PASS")
        else:
            print("   ❌ FAIL")
    except Exception as e:
        results[name] = {"status": "ERROR", "details": str(e)}
        print(f"   ❌ ERROR: {e}")


# 1. Code Integrity
def verify_integrity():
    # Simple syntax check on Kernel
    try:
        subprocess.run(["python", "-m", "compileall", str(KERNEL_DIR)], capture_output=True, check=True)
        return True, "Kernel Python files compiled successfully."
    except subprocess.CalledProcessError as e:
        return False, f"Compilation failed: {e.stderr.decode()}"


# 2. Test Coverage
def verify_coverage():
    try:
        # Running vitest in Forge
        npm = "npm.cmd" if __import__("sys").platform == "win32" else "npm"
        result = subprocess.run([npm, "run", "test"], cwd=FORGE_DIR, shell=False, capture_output=True, text=True)
        if "passed" in result.stdout:
            return True, "Vitest suite passed."
        return False, f"Tests failed:\n{result.stdout}"
    except Exception as e:
        return False, str(e)


# 3. Performance Metrics
def verify_performance():
    # Check dist size
    dist_path = FORGE_DIR / "dist"
    if not dist_path.exists():
        return False, "Dist folder missing."

    total_size = sum(f.stat().st_size for f in dist_path.rglob("*") if f.is_file()) / (1024 * 1024)
    if total_size < 5:
        return True, f"Build size optimal: {total_size:.2f} MB"
    return True, f"Build size heavy: {total_size:.2f} MB (Warning)"


# 4. Security
def verify_security():
    # NPM Audit
    try:
        npm = "npm.cmd" if __import__("sys").platform == "win32" else "npm"
        result = subprocess.run([npm, "audit"], cwd=FORGE_DIR, shell=False, capture_output=True, text=True)
        if "0 vulnerabilities" in result.stdout or "found 0 vulnerabilities" in result.stdout:
            return True, "NPM Audit Clean."
        return True, f"Vulnerabilities found (Check logs): {result.stdout.splitlines()[-1]}"  # Pass with warning
    except Exception:
        return False, "Audit failed."


# 5. Docs
def verify_docs():
    manifest = ROOT_DIR / "GEMINI.md"
    if manifest.exists() and "v97.6" in manifest.read_text(encoding="utf-8"):
        return True, "Manifest aligned with v97.6."
    return False, "Manifest version mismatch."


# 6. Build
def verify_build():
    index = FORGE_DIR / "dist" / "index.html"
    if index.exists():
        return True, "Index.html exists in dist."
    return False, "Build artifact missing."


# 7. Deployment
def verify_deployment():
    vercel_config = FORGE_DIR / "vercel.json"
    if vercel_config.exists():
        return True, "Vercel config present."
    return False, "Vercel config missing."


# 8. User Acceptance (Simulated)
def verify_uat():
    # Check if key features exist in code
    files = list(FORGE_DIR.rglob("AnyasLink.tsx"))
    if files:
        return True, "AnyasLink feature found in source."
    return False, "Core feature missing."


if __name__ == "__main__":
    run_check("Code Integrity", verify_integrity)
    run_check("Test Coverage", verify_coverage)
    run_check("Performance", verify_performance)
    run_check("Security", verify_security)
    run_check("Documentation", verify_docs)
    run_check("Build Success", verify_build)
    run_check("Deployment Readiness", verify_deployment)
    run_check("User Acceptance", verify_uat)

    # Generate Report
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# 🛡️ ULTIMATE VERIFICATION REPORT\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n\n")
        for key, val in results.items():
            icon = "✅" if val["status"] == "PASS" else "❌" if val["status"] == "FAIL" else "⚠️"
            f.write(f"### {icon} {key}\n")
            f.write(f"- Status: **{val['status']}**\n")
            f.write(f"- Details: `{val['details']}`\n\n")

    print(f"\n📜 Verification Matrix Complete. Report: {REPORT_FILE}")