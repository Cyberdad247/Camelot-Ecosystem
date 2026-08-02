# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Sovereign Seeding Utility: Hydrate the Titan Omega Memory Stack
Usage: py seed_knowledge.py --dir <directory_path>
"""

import argparse
import os
import sys

# Ensure memory modules are reachable
sys.path.insert(0, os.path.dirname(__file__))

from memory.seeder import TitanSeeder
from memory.titan_omega import TitanOmega


def main():
    parser = argparse.ArgumentParser(description="Seed knowledge into Camelot-OS Titan Omega memory stack.")
    parser.add_argument("--dir", type=str, help="Directory containing documents to seed (e.g., .md, .txt)")
    parser.add_argument("--manifest", type=str, help="Single agent manifest JSON to seed")
    
    args = parser.parse_args()
    
    titan = TitanOmega()
    seeder = TitanSeeder(titan)
    
    if args.dir:
        print(f"[*] Starting Directory Seeding Pipeline: {args.dir}")
        seeder.run_directory_pipeline(args.dir)
        print("[+] Directory seeding complete.")
        
    if args.manifest:
        import json
        with open(args.manifest, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            seeder.seed_agent_cartridge(manifest)
        print(f"[+] Seeded manifest: {args.manifest}")

    if not args.dir and not args.manifest:
        # Default: Seed the project documentation itself
        project_docs = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
        if os.path.exists(project_docs):
            print(f"[*] Seeding project documentation from: {project_docs}")
            seeder.run_directory_pipeline(project_docs)
            print("[+] Project docs seeding complete.")
        else:
            print("[!] No seeding parameters provided and docs/ not found. Use --help")

if __name__ == "__main__":
    main()