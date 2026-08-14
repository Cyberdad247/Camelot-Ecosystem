# SPDX-License-Identifier: MIT

"""Camelot-OS Interactive Onboarding and Ignition System.

Serves the onboarding dashboard web app and runs local CLI diagnostic checks.
"""

from __future__ import annotations

import http.server
import json
import os
import socketserver
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
PORT = 8099


def run_command_silent(args: list[str]) -> str | None:
    try:
        res = subprocess.run(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3.0
        )
        return res.stdout.strip() if res.returncode == 0 else None
    except Exception:
        return None


def gather_system_diagnostics() -> dict[str, Any]:
    # Check environments
    python_ver = sys.version.split()[0]
    in_venv = sys.prefix != sys.base_prefix

    # Appwrite connection status
    appwrite_endpoint = os.environ.get("APPWRITE_ENDPOINT", "https://appwrite.local/v1")
    appwrite_ok = os.environ.get("APPWRITE_API_KEY") is not None

    # Redis configuration
    redis_ok = os.environ.get("REDIS_URL") is not None

    # CLI version queries
    node_ver = run_command_silent(["node", "--version"])
    rust_ver = run_command_silent(["rustc", "--version"])
    git_ver = run_command_silent(["git", "--version"])

    # Path existences
    vfs_ok = (REPO_ROOT / "vfs").exists()
    nukg_store_ok = (REPO_ROOT / "03_VAULT" / "firnflow" / "nukg_crystals.json").exists()
    tests_ok = (REPO_ROOT / "tests" / "test_firnflow.py").exists()

    return {
        "status": "ready",
        "env": {
            "python": python_ver,
            "in_venv": in_venv,
            "node": node_ver or "missing",
            "rust": rust_ver or "missing",
            "git": git_ver or "missing",
        },
        "integrations": {
            "appwrite": {
                "endpoint": appwrite_endpoint,
                "configured": appwrite_ok,
                "label": "Online" if appwrite_ok else "Offline (using fallback)",
            },
            "redis": {
                "configured": redis_ok,
                "label": "Configured" if redis_ok else "Placeholder Keys Only",
            },
        },
        "vfs": {
            "scaffolded": vfs_ok,
            "nukg_store": nukg_store_ok,
            "tests_present": tests_ok,
        },
    }


class OnboardingHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve from REPO_ROOT
        super().__init__(*args, directory=str(REPO_ROOT), **kwargs)

    def do_GET(self):
        if self.path == "/api/diagnostics":
            diagnostics = gather_system_diagnostics()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(diagnostics).encode("utf-8"))
        elif self.path in ("/", "/index.html", "/onboarding"):
            self.path = "/onboarding.html"
            super().do_GET()
        else:
            super().do_GET()


def main():
    print("=================================================================")
    print("       🏰 CAMELOT-OS :: System Ignition & Onboarding 🏰          ")
    print("=================================================================")
    print("Starting diagnostics microserver...")

    # Print current diagnostic state to stdout
    diag = gather_system_diagnostics()
    print(f"- Python: {diag['env']['python']} (In Venv: {diag['env']['in_venv']})")
    print(f"- Node: {diag['env']['node']} | Rust: {diag['env']['rust']}")
    print(f"- Appwrite Sync: {diag['integrations']['appwrite']['label']}")
    print(f"- VFS Scaffolding: {'Mounted' if diag['vfs']['scaffolded'] else 'Missing'}")

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), OnboardingHandler) as httpd:
        url = f"http://localhost:{PORT}/onboarding.html"
        print(f"\nIgniting Interactive Dashboard at: {url}")
        print("Press Ctrl+C to stop the server.")

        # Open in default browser automatically
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down ignition microserver.")


if __name__ == "__main__":
    main()
