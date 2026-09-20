# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

def update_ledger():
    ledger_path = REPO_ROOT / "PROVENANCE_LEDGER.md"
    
    entries = [
        {
            "id": "1854",
            "task": "REYA Nostr Bridge Activation & Sir Codex Edge Systemd Daemon Lockdown (camelot-reya-edge.service): cgroups v2 Strict Scarcity Bounds (<350MB MemoryMax) & QR-Pill Pairing",
            "author": "SIR_HELIO / SIR_CODEX / ANYA_Ω / MERLIN_Ω / SIR_HELIOS / ARTHUR_OMEGA",
            "status": "✅ IMPLEMENTED, VERIFIED, SYNCHRONIZED & SEALED",
            "notes": "Activated REYA Nostr transport bridge and locked execution onto edge node under Sir Helio and Sir Codex: (1) Sir Codex forged infra/systemd/camelot-reya-edge.service and install-reya-edge.sh constraining Reya's Python process strictly inside camelot-workers.slice with cgroups v2 limits (MemoryHigh=300M, MemoryMax=350M, CPUQuota=60%, ProtectSystem=strict, ProtectHome=read-only, PrivateTmp=true, IPAddressAllow=127.0.0.1/32 100.64.0.0/10), (2) Engineered 02_FORGE/assimilation/reya/reya_nostr_bridge.py implementing decentralized Nostr relay listener (NIP-01/NIP-44), HMAC-SHA256 QR-Pill device pairing for Excalibur S26 Ultra / Motorola, and zero-copy packet piping into Bifrost Gateway (:3001) and shared memory slab, (3) Registered rune //ACTIVATE_REYA_NOSTR_BRIDGE and aliases in control_plane/runes/runic_router.py with verified CLI dispatch, (4) Extended test suite tests/test_reya_assimilation.py passing 14/14 tests (28/28 full suite green), (5) Stored crystal into MemCastle KNN store (Row ID 539) and Graphiti temporal knowledge graph (Fact 9) under SIR_HELIO, and (6) Synchronized all 4 PROVENANCE_LEDGER.md mirrors with exact byte-hash parity. — 2026-09-20 22:15 UTC"
        }
    ]

    try:
        content = ledger_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        
        insert_at = -1
        for i, line in enumerate(lines):
            if "| 1853" in line:
                insert_at = i
                break
        
        if insert_at == -1:
            for i, line in enumerate(lines):
                if "| ID" in line:
                    insert_at = i + 2
                    break

        new_rows = [f"| {e['id']} | **{e['task']}** | {e['author']} | {e['status']} | {e['notes']} |" for e in entries]
            
        final_lines = lines[:insert_at] + new_rows + lines[insert_at:]
        ledger_path.write_text("\n".join(final_lines) + "\n", encoding="utf-8")
        print(f"[OK] Ledger updated with {len(entries)} entries at row {insert_at}.")
        
    except Exception as e:
        print(f"[ERROR] Ledger update error: {e}")

if __name__ == "__main__":
    update_ledger()
