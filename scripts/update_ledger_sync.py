# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

def update_ledger():
    ledger_path = REPO_ROOT / "PROVENANCE_LEDGER.md"
    
    entries = [
        {
            "id": "1866",
            "task": "MagSafe Cockpit PWA HUD & FastMCP CloudBrain Activation (Ω_MAGSAFE_COCKPIT_ACTIVATION): MagsafeRecorderCard UI, FastMCP Tools (magsafe_process_audio, magsafe_status), Cockpit Sub-Tab Integration & Strict Typecheck Verification",
            "author": "SIR_HELIOS / SIR_BORIS / SIR_CODEX / MERLIN_Ω / SIR_HELIO / ARTHUR_OMEGA",
            "status": "✅ IMPLEMENTED, VERIFIED, SYNCHRONIZED & SEALED",
            "notes": "Activated MagSafe edge ambient voice recording and kinetic dispatch into the PWA HUD and CloudBrain FastMCP server: (1) Engineered MagsafeRecorderCard in apps/pwa/src/components/voice/MagsafeRecorderCard.tsx rendering hardware snap status (SNAP_ON_ATTACHED 98%, cgroups <350MB RSS), Project Speculum WORM glass wall status, SecondBrain executive summary display, and real-time kinetic action item cards with interactive REYA Handshake approval toggles, (2) Mounted MagsafeRecorderCard as dedicated MAGSAFE_EDGE sub-navigation tab inside MultivoiceRouterCockpit in apps/pwa/src/components/MultivoiceRouterCockpit.tsx, (3) Exposed FastMCP tools magsafe_process_audio and magsafe_status on control_plane/mcp/cloudbrain_mcp_server.py allowing Antigravity and agent pantheon to trigger ambient ingestion and inspect cgroups limits, (4) Authored unit test test_fastmcp_magsafe_tools in tests/test_magsafe_voice_dispatcher.py passing 8/8 tests, (5) Verified clean TypeScript compilation (tsc --noEmit) across apps/pwa, verified parity gates (check_omnivoice_router_build.py, check_generated_artifact_parity.py), and (6) Synchronized all 4 PROVENANCE_LEDGER.md mirrors with exact byte-hash parity. — 2026-09-21 04:00 UTC"
        }
    ]

    try:
        content = ledger_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        
        insert_at = -1
        for i, line in enumerate(lines):
            if "| 1865" in line:
                insert_at = i
                break
        
        if insert_at == -1:
            for i, line in enumerate(lines):
                if "| ID" in line:
                    insert_at = i + 2
                    break
        if insert_at == -1:
            insert_at = 0

        new_rows = [f"| {e['id']} | **{e['task']}** | {e['author']} | {e['status']} | {e['notes']} |" for e in entries]
            
        final_lines = lines[:insert_at] + new_rows + lines[insert_at:]
        ledger_path.write_text("\n".join(final_lines) + "\n", encoding="utf-8")
        print(f"[OK] Ledger updated with {len(entries)} entries at row {insert_at}.")
        
    except Exception as e:
        print(f"[ERROR] Ledger update error: {e}")

if __name__ == "__main__":
    update_ledger()
