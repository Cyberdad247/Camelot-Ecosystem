import json
from pathlib import Path

from control_plane.infra.provenance import ProvenanceManager, VerificationRun


def test_ledger_tamper_detection():
    # Use a local temporary directory for testing
    test_vault = Path("./tests/tmp_vault_audit")
    if test_vault.exists():
        import shutil
        shutil.rmtree(test_vault, ignore_errors=True)
    
    mgr = ProvenanceManager(vault_path=test_vault)
    
    # 1. Create a valid chain
    for i in range(5):
        run = VerificationRun(
            run_id=f"run_{i}",
            operator="sir_helio",
            command=f"cmd_{i}",
            results={},
            success=True
        )
        mgr.log_verification(run)
    
    # Verify initial integrity
    assert mgr.verify_integrity() == True
    
    # 2. Tamper with an entry
    entries = []
    with open(mgr.verification_ledger, "r", encoding="utf-8") as f:
        for line in f:
            entries.append(json.loads(line))
    
    # Modify result of entry index 2
    entries[2]["results"]["tampered"] = True
    
    with open(mgr.verification_ledger, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
            
    # Verify integrity fails
    assert mgr.verify_integrity() == False
    
    # 3. Tamper with hash chain (change parent_hash)
    entries[3]["parent_hash"] = "bogus_hash"
    with open(mgr.verification_ledger, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
            
    assert mgr.verify_integrity() == False

    # Cleanup
    import shutil
    shutil.rmtree(test_vault, ignore_errors=True)
