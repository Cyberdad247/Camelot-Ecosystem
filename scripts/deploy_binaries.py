#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path

def main():
    root_dir = Path(__file__).resolve().parent.parent
    
    # Define paths
    cribo_src = root_dir / "02_FORGE" / "kinetic" / "cribo" / "target" / "release" / "cribo.exe"
    rotel_src = root_dir / "02_FORGE" / "kinetic" / "rotel" / "target" / "release" / "rotel.exe"
    
    cribo_dest_dir = root_dir / "02_FORGE" / "KINETIC_ARMORY" / "Cribo" / "target" / "release"
    rotel_dest_dir = root_dir / "02_FORGE" / "KINETIC_ARMORY" / "Rotel" / "target" / "release"
    saltare_dest_dir = root_dir / "02_FORGE" / "KINETIC_ARMORY" / "Saltare"
    
    # 1. Create directories
    cribo_dest_dir.mkdir(parents=True, exist_ok=True)
    rotel_dest_dir.mkdir(parents=True, exist_ok=True)
    saltare_dest_dir.mkdir(parents=True, exist_ok=True)
    
    print("Created target directories in KINETIC_ARMORY.")

    # 2. Copy Rust binaries
    if cribo_src.exists():
        shutil.copy2(cribo_src, cribo_dest_dir / "cribo.exe")
        print(f"Copied cribo.exe to {cribo_dest_dir}")
    else:
        print(f"Warning: Compiled cribo.exe not found at {cribo_src}")

    if rotel_src.exists():
        shutil.copy2(rotel_src, rotel_dest_dir / "rotel.exe")
        print(f"Copied rotel.exe to {rotel_dest_dir}")
    else:
        print(f"Warning: Compiled rotel.exe not found at {rotel_src}")

    # 3. Build Go binaries (saltare and saltare-mcp)
    saltare_go_dir = root_dir / "kinetic_edge" / "saltare"
    if saltare_go_dir.exists():
        print("Compiling Saltare Go binaries...")
        try:
            # Build saltare.exe
            subprocess.run(
                ["go", "build", "-o", str(saltare_dest_dir / "saltare.exe"), "./cmd/saltare/main.go"],
                cwd=str(saltare_go_dir),
                check=True
            )
            print(f"Compiled and saved saltare.exe to {saltare_dest_dir}")
            
            # Build saltare-mcp.exe
            subprocess.run(
                ["go", "build", "-o", str(saltare_dest_dir / "saltare-mcp.exe"), "./cmd/saltare-mcp/main.go"],
                cwd=str(saltare_go_dir),
                check=True
            )
            print(f"Compiled and saved saltare-mcp.exe to {saltare_dest_dir}")
            
        except subprocess.CalledProcessError as e:
            print(f"Error compiling Go binaries: {e}")
    else:
        print(f"Warning: Go project folder not found at {saltare_go_dir}")

    # Verify everything
    expected_binaries = [
        ("saltare.exe", saltare_dest_dir / "saltare.exe"),
        ("saltare-mcp.exe", saltare_dest_dir / "saltare-mcp.exe"),
        ("cribo.exe", cribo_dest_dir / "cribo.exe"),
        ("rotel.exe", rotel_dest_dir / "rotel.exe"),
    ]
    
    print("\n--- Deployment Status Check ---")
    for name, path in expected_binaries:
        if path.exists():
            print(f"[OK] {name}: Present ({path.stat().st_size / (1024*1024):.2f} MB)")
        else:
            print(f"[MISSING] {name}: MISSING at {path}")

if __name__ == "__main__":
    main()
