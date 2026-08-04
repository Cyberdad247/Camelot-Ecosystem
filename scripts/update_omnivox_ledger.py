import sys
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

def update_ledger():
    ledger_path = REPO_ROOT / "PROVENANCE_LEDGER.md"
    
    entries = [
        {
            "id": "1623",
            "task": "OmniVox-Lattice Architecture Synthesis",
            "author": "SIR_BORIS",
            "status": "✅ ACTUATED",
            "notes": "Forged the OmniVox-Lattice core by synthesizing greater pieces from Multivoice-router and OmniRoute. Unified universal intent mapping with multi-persona vocal synthesis."
        },
        {
            "id": "1624",
            "task": "OmniVox Cartridge & UKG Node Deployment",
            "author": "SIR_BORIS",
            "status": "✅ DEPLOYED",
            "notes": "Created `omnivox.yaml` cartridge and registered `UKG_OMNIVOX_V1` node. Established L7 Ethereal dispatch layer for multi-agent swarm vocalization."
        }
    ]

    try:
        content = ledger_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        
        header_index = -1
        for i, line in enumerate(lines):
            if "| ID" in line:
                header_index = i
                break
        
        if header_index == -1: return  # noqa

        separator_index = header_index + 1
        new_rows = [f"| {e['id']} | **{e['task']}** | {e['author']} | {e['status']} | {e['notes']} |" for e in entries]
            
        final_lines = lines[:separator_index+1] + new_rows + lines[separator_index+1:]
        ledger_path.write_text("\n".join(final_lines), encoding="utf-8")
        print(f"✅ Ledger updated with {len(entries)} entries.")
        
    except Exception as e:
        print(f"❌ Ledger update error: {e}")

if __name__ == "__main__":
    update_ledger()
