#!/usr/bin/env python3
"""
Merge and integrate 3D Spatial UI, HTMX Center, and Architecture Assets
from camelot-os/main into the Camelot-Ecosystem monorepo.
"""

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def main():
    print("[MERGE] Querying git objects from camelot-os/main...")
    files = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", "camelot-os/main"],
        text=True,
        cwd=REPO_ROOT
    ).splitlines()

    transfers = []
    
    # 1. 3D Spatial UI & Holographic HUD -> apps/spatial-hud/
    for f in files:
        if f.startswith("src/") or f in [
            "index.html", "vite.config.ts", "tailwind.config.js",
            "postcss.config.js", "metadata.json", "tsconfig.json"
        ]:
            target = REPO_ROOT / "apps" / "spatial-hud" / f
            transfers.append((f, target))
        elif f == "package.json":
            # Will be customized as apps/spatial-hud/package.json
            transfers.append((f, REPO_ROOT / "apps" / "spatial-hud" / "package.json"))
        # 2. HTMX Center -> opt/camelot/htmx-center/
        elif f.startswith("opt/camelot/htmx-center/"):
            transfers.append((f, REPO_ROOT / f))
        # 3. Missing Docs -> docs/
        elif f.startswith("docs/architecture/") or f.startswith("docs/reference/") or f.startswith("docs/threat-models/"):
            transfers.append((f, REPO_ROOT / f))

    print(f"[MERGE] Extracting {len(transfers)} files from camelot-os/main...")
    
    for src_git_path, dest_path in transfers:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        content_bytes = subprocess.check_output(
            ["git", "show", f"camelot-os/main:{src_git_path}"],
            cwd=REPO_ROOT
        )
        
        # If writing package.json for apps/spatial-hud, customize workspace name
        if src_git_path == "package.json" and "apps/spatial-hud" in str(dest_path).replace("\\", "/"):
            pkg_data = json.loads(content_bytes.decode("utf-8"))
            pkg_data["name"] = "@sovereign/spatial-hud"
            pkg_data["version"] = "0.1.0"
            dest_path.write_text(json.dumps(pkg_data, indent=2) + "\n", encoding="utf-8")
        else:
            dest_path.write_bytes(content_bytes)

    print(f"[MERGE] Successfully transferred {len(transfers)} files.")
    print("[MERGE] Workspace apps/spatial-hud established.")
    print("[MERGE] Architecture documents and opt/camelot/htmx-center populated.")

if __name__ == "__main__":
    main()
