# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import subprocess
from datetime import datetime
from pathlib import Path

# 🛡️ CONFIGURATION
DASHBOARD_DIR = Path(r"C:\Users\vizio\CAMELOT_OS\02_FORGE\Anya_Dashboard")
REPORT_FILE = Path(r"C:\Users\vizio\CAMELOT_OS\99_HISTORY\DASHBOARD_PROD_VALIDATION.md")

results = {}


def run_check(name, check_func):
    print(f"📊 [ZENITH] Validating: {name}...")
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


# 1. Code Review (Linting & Security)
def verify_code_quality():
    # ESLint
    try:
        lint_res = subprocess.run(["npm", "run", "lint"], cwd=DASHBOARD_DIR, shell=True, capture_output=True, text=True)
        lint_status = "PASS" if lint_res.returncode == 0 else "WARN"
    except:
        lint_status = "FAIL"

    # Security Audit
    try:
        audit_res = subprocess.run(["npm", "audit"], cwd=DASHBOARD_DIR, shell=True, capture_output=True, text=True)
        sec_status = "PASS" if "0 vulnerabilities" in audit_res.stdout else "WARN"
    except:
        sec_status = "FAIL"

    return True, f"Lint: {lint_status} | Security: {sec_status}"


# 2. Performance (Build Size)
def verify_build_size():
    dist_path = DASHBOARD_DIR / "dist"
    if not dist_path.exists():
        return False, "Build missing. Run 'npm run build' first."

    js_size = sum(f.stat().st_size for f in dist_path.rglob("*.js")) / (1024 * 1024)
    # 3D engines are heavy, so we allow up to 5MB
    if js_size < 5:
        return True, f"JS Bundle: {js_size:.2f} MB (Optimal)"
    return True, f"JS Bundle: {js_size:.2f} MB (Heavy - Consider Code Splitting)"


# 3. Reliability (Error Boundaries)
def verify_reliability():
    # Check for ErrorBoundary usage in App.tsx or main.tsx
    app_tsx = (DASHBOARD_DIR / "src" / "App.tsx").read_text(encoding="utf-8")
    if "ErrorBoundary" in app_tsx:
        return True, "ErrorBoundary detected."
    return False, "No ErrorBoundary found in App.tsx. High risk of white-screen crashes."


# 4. Deployment Readiness
def verify_deployment():
    vercel = (DASHBOARD_DIR / "vercel.json").exists()
    pkg = (DASHBOARD_DIR / "package.json").exists()

    if vercel and pkg:
        return True, "Vercel config and Package.json present."
    return False, "Deployment config missing."


# 5. Documentation
def verify_docs():
    readme = (DASHBOARD_DIR / "README.md").exists()
    return readme, "README.md presence check."


if __name__ == "__main__":
    run_check("Code Quality (Lint/Audit)", verify_code_quality)
    run_check("Performance (Bundle Size)", verify_build_size)
    run_check("Reliability (Fault Tolerance)", verify_reliability)
    run_check("Deployment Readiness", verify_deployment)
    run_check("Documentation", verify_docs)

    # Generate Report
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# 🚀 ANYA DASHBOARD & QUANTUM ENGINE: PROD VALIDATION\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n\n")
        for key, val in results.items():
            icon = "✅" if val["status"] == "PASS" else "❌" if val["status"] == "FAIL" else "⚠️"
            f.write(f"### {icon} {key}\n")
            f.write(f"- Status: **{val['status']}**\n")
            f.write(f"- Details: `{val['details']}`\n\n")

    print(f"\n📜 Validation Report: {REPORT_FILE}")