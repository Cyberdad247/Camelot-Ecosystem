import shutil
import json
import importlib.util
from pathlib import Path
from control_plane.provenance import ProvenanceManager, VerificationRun

def test_provenance_mempalace_integration():
    repo_root = Path(__file__).resolve().parent.parent
    module_path = repo_root / "01_KERNEL" / "memory" / "mempalace_l2.py"
    spec = importlib.util.spec_from_file_location("mempalace_l2", module_path)
    mempalace_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mempalace_mod)
    MemPalaceL2 = mempalace_mod.MemPalaceL2

    test_vault = Path("./tests/tmp_vault_integration")
    if test_vault.exists():
        shutil.rmtree(test_vault, ignore_errors=True)
        
    # ProvenanceManager will use its default MemPalaceL2 which uses default path
    # For testing, we want to control the path.
    # I'll temporarily patch the manager or just use a dedicated test.
    mgr = ProvenanceManager(vault_path=test_vault)
    # Patch the mempalace instance to use a test path
    test_l2_path = Path("./tests/tmp_l2_integration")
    if test_l2_path.exists():
        shutil.rmtree(test_l2_path, ignore_errors=True)
    mgr.mempalace = MemPalaceL2(storage_path=test_l2_path)
    
    run = VerificationRun(
        run_id="int_test_1",
        operator="sir_helio",
        command="//AUDIT ARCHITECTURE",
        results={"nodes": 12, "integrity": "HIGH"},
        success=True
    )
    
    mgr.log_verification(run)
    
    # Now check if it's in MemPalace (using the operator as tenant_id)
    results = mgr.mempalace.search(query="AUDIT", wing="camelot", room="audit", tenant_id="sir_helio")
    
    assert len(results) > 0
    assert "int_test_1" in results[0]["content"]
    assert results[0]["metadata"]["run_id"] == "int_test_1"
    
    print("Integration Verified: Provenance -> MemPalace L2 Flow Active.")

    # Cleanup
    shutil.rmtree(test_vault, ignore_errors=True)
    shutil.rmtree(test_l2_path, ignore_errors=True)

if __name__ == "__main__":
    test_provenance_mempalace_integration()
