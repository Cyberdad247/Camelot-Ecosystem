import subprocess
import os
import sys

def run_trivy_scan(target_dir):
    print(f"🛡️ [VERITAS] Starting Trivy Security Scan for: {target_dir}")
    
    # Attempt to run via docker (common for local trivy usage)
    # Alternatively: trivy fs target_dir
    try:
        # Check if trivy is installed locally first
        cmd = ["trivy", "fs", "--severity", "HIGH,CRITICAL", target_dir]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ [VERITAS] Scan Complete. No critical vulnerabilities found.")
            print(result.stdout)
        else:
            print("⚠️ [VERITAS] Scan found potential issues or failed.")
            print(result.stdout)
            print(result.stderr)
            
    except FileNotFoundError:
        print("❌ [VERITAS] Trivy not found in PATH. Please install Trivy or run via Docker.")
        print("Suggested command: docker run --rm -v ${PWD}:/tmp aquasec/trivy fs /tmp/01_KERNEL")

if __name__ == "__main__":
    kernel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "01_KERNEL"))
    run_trivy_scan(kernel_path)
