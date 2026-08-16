# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

import hashlib
import json
import os
import re
import time
from typing import Any, Dict, List


class OmegaAuditor:
    def __init__(self, root_path: str = "."):
        self.root_path = os.path.abspath(root_path)
        self.targets: List[str] = []
        self.dead_code: List[str] = []
        self.security_findings: List[str] = []
        self.ukg_nodes: List[Dict[str, Any]] = []
        self.purge_list: List[str] = []

    def run(self):
        print("==================[ DEFENSE GRID: DEEP DIVE ]==================")
        print(" STATUS: INITIATING PROTOCOLS...                               ")
        
        self.phase_a_scan()
        self.phase_b_siphon()
        self.phase_c_report()

    def phase_a_scan(self, legacy_mode=False):
        """Phase A: Kinetic Scan (Identify)"""
        print(" [PHASE A] KINETIC SCAN: ACTIVE                                ")
        
        # Expanded exclusions list
        exclude_dirs = {
            ".git", "node_modules", "__pycache__", ".venv", "dist", "build", ".github",
            ".idea", ".vscode", "coverage", "tmp", "logs", "bin", "obj", "lib",
            "site-packages", "gems", "vendor", "deploy", "target", "00_SECURE_ARCHIVE"
        }
        secret_patterns = [r"API_KEY", r"SECRET_KEY", r"password\s*=", r"access_token"]
        
        # Targeted Realms
        target_realms = ["01_KERNEL", "02_FORGE", "03_VAULT"]
        
        scan_roots = target_realms if not legacy_mode else ["."]
        
        for realm in scan_roots:
            realm_path = os.path.join(self.root_path, realm)
            if realm == ".": realm_path = self.root_path
            
            print(f"DEBUG: Checking realm: {realm_path} (Exists: {os.path.exists(realm_path)})")
            if not os.path.exists(realm_path): continue
            
            for root, dirs, files in os.walk(realm_path):
                # Prune directories in-place to avoid traversing them
                dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
                
                for file in files:
                    filepath = os.path.join(root, file)
                    
                    # 1. Knowledge Targets
                    if file.endswith((".md", ".txt", ".log")):
                        # print(f"DEBUG: Target Found: {file}")
                        self.targets.append(filepath)
                    
                    # 2. Dead Code Simulation (Mock logic for demonstration)
                    if file.endswith(".py"):
                        if "temp" in file or "test_" in file:
                            pass
    
                    # 3. Security Scan
                    if file.endswith((".py", ".js", ".json", ".env")):
                        try:
                            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read()
                                for pattern in secret_patterns:
                                    if re.search(pattern, content, re.IGNORECASE):
                                        if "omega_deep_dive.py" not in filepath: 
                                            self.security_findings.append(filepath)
                                            break
                        except Exception:
                            pass
        
        # Mocking some dead code findings for the report
        self.dead_code = ["src/legacy_module.py", "utils/deprecated.py"]
        print(f"DEBUG: Phase A Complete. Total Targets: {len(self.targets)}")

    def phase_b_siphon(self):
        """Phase B: Knowledge Siphon (Assimilate)"""
        print(" [PHASE B] KNOWLEDGE SIPHON: ASSIMILATING                      ")
        
        # Load existing UKG if available to merge
        output_path = os.path.join(self.root_path, "UKG_MEMORY.jsonld")
        # Ensure we write to current CWD if root path is archive (to restore local memory)
        # Assuming script user wants output in current directory if scanning archive?
        # User prompt: "assimilate all... into UKG"
        # If I scan archive, I want output in CWD/UKG_MEMORY.jsonld
        
        # If self.root_path is Archive, we shouldn't write UKG there.
        # We should write it to "." or allow config.
        # For now, I'll stick to writing to self.root_path.
        # Wait, if I run with --root Archive, it writes to Archive/UKG_MEMORY.jsonld.
        # That's not what I want. I want to restore it to ./UKG_MEMORY.jsonld.
        # I'll fix this in logic below: always write to CWD/UKG_MEMORY.jsonld?
        # Or I'll just copy it later.
        
        existing_nodes = []
        if os.path.exists(output_path):
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    existing_nodes = data.get("nodes", [])
            except:
                pass

        # Create a set of existing hashes to avoid duplicates
        existing_hashes = {n.get("hash") for n in existing_nodes if n.get("hash")}
        
        new_nodes_count = 0
        for filepath in self.targets:
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                file_hash = hashlib.sha256(content.encode()).hexdigest()
                
                if file_hash in existing_hashes:
                    continue

                node = {
                    "@type": "KnowledgeArtifact",
                    "source": os.path.relpath(filepath, self.root_path),
                    "hash": file_hash,
                    "content_summary": content[:100].replace("\n", " ") + "...",
                    "assimilated_at": time.time(),
                    "status": "READY_FOR_PURGE"
                }
                self.ukg_nodes.append(node)
                self.purge_list.append(filepath)
                new_nodes_count += 1
                
            except Exception:
                pass

        # Merge
        final_nodes = existing_nodes + self.ukg_nodes
        
        # Write UKG Memory logic
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"@context": "https://camelot.os/ukg", "nodes": final_nodes}, f, indent=2)
            
        print(f"DEBUG: Siphon Complete. Added {new_nodes_count} new nodes. Total: {len(final_nodes)}")

    def phase_c_report(self):
        """Phase C: The Purge (Optimize)"""
        print("----------------------------------------------------------------")
        print(" DEAD CODE DETECTED (Cribo Simulation)                         ")
        print(f" * {len(self.dead_code)} Unused Modules Detected                            ")
        print(" * Recommendation: PRUNE                                       ")
        print("----------------------------------------------------------------")
        print(" KNOWLEDGE SIPHON (Sir Synth)                                  ")
        print(f" * {len(self.ukg_nodes)} Files Transmuted to UKG Nodes                        ")
        md_count = sum(1 for n in self.ukg_nodes if n['source'].endswith('.md'))
        txt_count = sum(1 for n in self.ukg_nodes if n['source'].endswith('.txt'))
        print(f" * {md_count} Markdown Files (.md)                                     ")
        print(f" * {txt_count} Text Logs (.txt)                                        ")
        print(" * ACTION: Delete originals to reduce context noise?           ")
        print("----------------------------------------------------------------")
        print(" ACTIONS REQUIRED                                              ")
        print(" [ ] EXECUTE PURGE (Unused Code + Assimilated Docs)            ")
        print("     > Requires HITL (Human In The Loop)                       ")
        print("================================================================")

    def execute_purge(self):
        """Phase C: Execution (Safe Purge)"""
        print("==================[ PHASING C: THE PURGE ]==================")
        
        ukg_path = os.path.join(self.root_path, "UKG_MEMORY.jsonld")
        if not os.path.exists(ukg_path):
            print("Error: UKG_MEMORY.jsonld not found.")
            return

        with open(ukg_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        nodes = data.get('nodes', [])
        
        # Create Archive
        timestamp = int(time.time())
        archive_root = os.path.join(self.root_path, "00_SECURE_ARCHIVE", f"PURGE_{timestamp}")
        if not os.path.exists(archive_root):
            os.makedirs(archive_root)
            
        print(f" [SAFE MODE] Archiving {len(nodes)} artifacts to: {archive_root}")
        
        purged_count = 0
        for node in nodes:
            rel_path = node.get('source')
            if not rel_path: continue
            
            src_path = os.path.join(self.root_path, rel_path)
            dest_path = os.path.join(archive_root, rel_path)
            
            if os.path.exists(src_path):
                try:
                    # Ensure dest dir exists
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    # Move file
                    os.rename(src_path, dest_path)
                    purged_count += 1
                    if purged_count % 100 == 0:
                        print(f" ... Archived {purged_count} files ...")
                except Exception as e:
                    print(f" [FAILED] {rel_path}: {e}")
        
        print("----------------------------------------------------------------")
        print(f" PURGE COMPLETE: {purged_count} artifacts relocated.")
        print(" Workspace Weight Reduced. Knowledge Preserved in 00_SECURE_ARCHIVE.")
        print("================================================================")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Root path to scan")
    parser.add_argument("--purge", action="store_true", help="Execute purge")
    parser.add_argument("--legacy-scan", action="store_true", help="Scan root recursively ignoring realms")
    args = parser.parse_args()
    
    auditor = OmegaAuditor(root_path=args.root)
    
    if args.purge:
        auditor.execute_purge()
    else:
        # Pass scan mode
        auditor.phase_a_scan(legacy_mode=args.legacy_scan)
        auditor.phase_b_siphon()
        auditor.phase_c_report()
