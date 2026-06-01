import json
import hashlib
from pathlib import Path
from control_plane.provenance import VerificationRun, ProvenanceManager

def backfill():
    mgr = ProvenanceManager()
    ledger_path = mgr.verification_ledger
    
    if not ledger_path.exists():
        print("No ledger found to backfill.")
        return

    print(f"Backfilling ledger: {ledger_path}")
    
    entries = []
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    
    print(f"Loaded {len(entries)} entries.")
    
    prev_hash = None
    new_entries = []
    entry_counter = 1
    
    for i, entry_data in enumerate(entries):
        # ... existing cleanup ...
        
        try:
            run = VerificationRun(**entry_data)
            run.entry_id = entry_counter
            run.parent_hash = prev_hash
            run.entry_hash = run.compute_hash()
            
            new_entries.append(run.model_dump())
            prev_hash = run.entry_hash
            entry_counter += 1
        except Exception as e:
            print(f"Skipping malformed entry at line {i+1}: {e}")
            continue

    # Write back to root ledger
    with open(ledger_path, "w", encoding="utf-8") as f:
        for entry in new_entries:
            f.write(json.dumps(entry) + "\n")
            
    print(f"Backfill complete. SHA-256 chain established for {len(new_entries)} entries.")
    
if __name__ == "__main__":
    backfill()
