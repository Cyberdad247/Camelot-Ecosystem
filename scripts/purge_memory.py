# -*- coding: utf-8 -*-
"""
Purge Memory — System-wide memory zero-out utility.
Clears ChromaDB L2 indices, Redis Agent Memory (L1.5), JSON-LD (L4), and project memory files.
"""

import sys
# Reconfigure stdout to use UTF-8 to prevent encoding crashes on Windows console output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import shutil
import json
import sqlite3
from pathlib import Path

# Setup paths relative to script
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT / "01_KERNEL"))

from memory.mempalace_l2 import MemPalaceL2
from memory.agent_memory import agent_memory

PROVENANCE_LEDGER = REPO_ROOT / "PROVENANCE_LEDGER.md"

def log_to_ledger(notes: str):
    """Log an entry to the PROVENANCE_LEDGER.md."""
    if not PROVENANCE_LEDGER.exists():
        return
    # Find last ID
    last_id = 2000
    try:
        content = PROVENANCE_LEDGER.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if l.startswith("|") and not l.startswith("| ID")]
        if lines:
            ids = []
            for line in lines:
                parts = line.split("|")
                if len(parts) > 1:
                    try:
                        ids.append(int(parts[1].strip()))
                    except ValueError:
                        continue
            if ids:
                last_id = max(ids)
    except Exception:
        pass

    new_id = last_id + 1
    from datetime import datetime, timezone
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"| {new_id} | **Memory Purge** | SYSTEM | ✅ COMPLETED | {notes} — {timestamp} |"
    
    try:
        content = PROVENANCE_LEDGER.read_text(encoding="utf-8")
        header_end = 0
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("| :--") or line.startswith("|--"):
                header_end = i + 1
                break
        
        if header_end:
            new_lines = lines[:header_end] + [entry] + lines[header_end:]
        else:
            new_lines = [entry] + lines
        PROVENANCE_LEDGER.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    except Exception as e:
        with open(PROVENANCE_LEDGER, "a", encoding="utf-8") as f:
            f.write(entry + "\n")

def purge_chromadb():
    """Delete all collections in ChromaDB or remove database files directly."""
    print("[1/4] Purging ChromaDB L2 Vector Indices...")
    l2_dir = REPO_ROOT / "03_VAULT" / "memory" / "l2_index"
    
    # 1. Attempt programmatic purge via client
    purged_ok = False
    try:
        l2 = MemPalaceL2(storage_path=l2_dir)
        if l2.client:
            colls = l2.client.list_collections()
            print(f"  Found {len(colls)} collections to delete.")
            for coll in colls:
                l2.client.delete_collection(coll.name)
                print(f"  Deleted collection: {coll.name}")
            purged_ok = True
    except Exception as e:
        print(f"  Programmatic ChromaDB purge failed: {e}. Falling back to file removal.")

    # 2. Programmatic sqlite3 cleanup & file sweep fallback
    try:
        # Close any open connections by deleting client
        if 'l2' in locals():
            del l2
        
        # Safe deletion of chroma.sqlite3 and subdirectories
        if l2_dir.exists():
            for item in l2_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                    print(f"  Removed folder: {item.name}")
                elif item.name == "chroma.sqlite3":
                    # Truncate sqlite database first to release file lock, then delete
                    try:
                        conn = sqlite3.connect(str(item))
                        conn.close()
                    except Exception:
                        pass
                    item.unlink()
                    print("  Deleted chroma.sqlite3 database file.")
            purged_ok = True
    except Exception as e:
        print(f"  ChromaDB file removal failed: {e}")
    
    if purged_ok:
        print("  ✅ ChromaDB successfully zeroed-out.")
    else:
        print("  ❌ ChromaDB purge failed.")

def purge_agent_memory():
    """Purge L1.5 Redis Agent Memory if configured."""
    print("[2/4] Purging L1.5 Redis Agent Memory...")
    if agent_memory.is_configured():
        success = agent_memory.purge_all()
        if success:
            print("  ✅ Redis Agent Memory successfully zeroed-out.")
        else:
            print("  ❌ Redis Agent Memory purge failed.")
    else:
        print("  ℹ️ Redis Agent Memory not configured. Skipping.")

def purge_jsonld_store():
    """Clear L4 UKG JSON-LD Memory Graph file."""
    print("[3/4] Purging L4 JSON-LD Memory Graph...")
    jsonld_path = REPO_ROOT / "03_VAULT" / "UKG" / "UKG_MEMORY.jsonld"
    if jsonld_path.exists():
        empty_graph = {
            "@context": {
                "@vocab": "https://kickbox.audio/schema/knight#",
                "name": "https://schema.org/name",
                "description": "https://schema.org/description"
            },
            "@type": "MemoryGraph",
            "@graph": []
        }
        try:
            jsonld_path.write_text(json.dumps(empty_graph, indent=2), encoding="utf-8")
            print("  ✅ Truncated UKG_MEMORY.jsonld to empty graph template.")
        except Exception as e:
            print(f"  ❌ Failed to truncate UKG_MEMORY.jsonld: {e}")
    else:
        print("  ℹ️ UKG_MEMORY.jsonld not found. Skipping.")

def purge_learned_aspects():
    """Remove learned aspect lines from project memory files."""
    print("[4/4] Purging learned aspects in memory.md...")
    targets = [
        REPO_ROOT / "audit-kickbox-audio" / "apps" / "pwa" / "public" / "memory.md",
        REPO_ROOT / "audit-kickbox-audio" / "memory.md"
    ]
    
    for t in targets:
        if t.exists():
            try:
                lines = t.read_text(encoding="utf-8").splitlines()
                # Keep comments/headers, remove lines starting with `- [`
                cleaned_lines = [l for l in lines if not l.strip().startswith("- [")]
                t.write_text("\n".join(cleaned_lines) + "\n", encoding="utf-8")
                print(f"  ✅ Cleaned learned aspects from {t.relative_to(REPO_ROOT)}")
            except Exception as e:
                print(f"  ❌ Failed to clean aspects from {t}: {e}")
        else:
            print(f"  ℹ️ File {t.name} not found. Skipping.")

def main():
    print("==================================================")
    print("🛡️ SOVEREIGN MEMORY PURGE SEQUENCE STARTING")
    print("==================================================")
    
    purge_chromadb()
    purge_agent_memory()
    purge_jsonld_store()
    purge_learned_aspects()
    
    log_to_ledger("Zeroed-out ChromaDB vector indices, L1.5 Redis Agent Memory, UKG_MEMORY.jsonld graph, and local memory.md learned aspects.")
    
    print("==================================================")
    print("✅ MEMORY PURGE COMPLETE")
    print("==================================================")

if __name__ == "__main__":
    main()
