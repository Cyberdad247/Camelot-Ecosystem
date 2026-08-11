import json
from pathlib import Path

from control_plane.infra.provenance import ProvenanceManager, VerificationRun


def test_ledger_hash_chain_integrity():
    # Use a local temporary directory for testing
    test_vault = Path("./tests/tmp_vault")
    if test_vault.exists():
        import shutil
        shutil.rmtree(test_vault, ignore_errors=True)
    
    mgr = ProvenanceManager(vault_path=test_vault)
    
    # First run (should have no parent_hash or empty)
    run1 = VerificationRun(
        run_id="run_1",
        operator="sir_helio",
        command="//BOOT",
        results={"status": "OK"},
        success=True
    )
    mgr.log_verification(run1)
    
    # Second run (should have run1's hash as parent_hash)
    run2 = VerificationRun(
        run_id="run_2",
        operator="sir_helio",
        command="//SYNC",
        results={"status": "OK"},
        success=True
    )
    mgr.log_verification(run2)
    
    # Read the ledger and verify the chain
    entries = []
    with open(mgr.verification_ledger, "r", encoding="utf-8") as f:
        for line in f:
            entries.append(json.loads(line))
    
    assert len(entries) == 2
    # These will fail initially as we haven't implemented the logic
    assert "entry_id" in entries[0]
    assert entries[0]["entry_id"] == 1
    assert entries[1]["entry_id"] == 2
    assert entries[1]["parent_hash"] == entries[0]["entry_hash"]
    
    # Cleanup
    import shutil
    shutil.rmtree(test_vault, ignore_errors=True)
