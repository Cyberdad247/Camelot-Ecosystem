import pytest
import shutil
import importlib.util
from pathlib import Path

def test_mempalace_l2_init():
    # Setup local test directory to avoid permission issues
    test_storage = Path("./tests/tmp_mempalace_l2")
    if test_storage.exists():
        shutil.rmtree(test_storage, ignore_errors=True)
    
    # Dynamic import to handle non-existent module
    repo_root = Path(__file__).resolve().parent.parent
    module_path = repo_root / "01_KERNEL" / "memory" / "mempalace_l2.py"
    
    if not module_path.exists():
        pytest.fail(f"Module {module_path} not found. Implementation pending.")
    
    spec = importlib.util.spec_from_file_location("mempalace_l2", module_path)
    mempalace = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mempalace)
    
    l2 = mempalace.MemPalaceL2(storage_path=test_storage)
    
    assert l2.client is not None
    assert l2.storage_path == test_storage
    assert test_storage.exists()
    
    # Cleanup
    shutil.rmtree(test_storage, ignore_errors=True)

def test_scoped_search():
    test_storage = Path("./tests/tmp_mempalace_l2_scoped")
    if test_storage.exists():
        shutil.rmtree(test_storage, ignore_errors=True)
        
    repo_root = Path(__file__).resolve().parent.parent
    module_path = repo_root / "01_KERNEL" / "memory" / "mempalace_l2.py"
    spec = importlib.util.spec_from_file_location("mempalace_l2", module_path)
    mempalace = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mempalace)
    
    l2 = mempalace.MemPalaceL2(storage_path=test_storage)
    
    # Add to specific wing/room
    l2.store(
        wing="camelot", 
        room="audit", 
        content="Success Gene #1: Linear scaling verified.", 
        metadata={"id": "gene_1", "v1000": True}
    )
    
    l2.store(
        wing="luxora", 
        room="payment", 
        content="Success Gene #2: Stripe handshake hardened.", 
        metadata={"id": "gene_2"}
    )
    
    # Search within scope
    results = l2.search(query="Linear", wing="camelot", room="audit")
    assert len(results) > 0
    assert "scaling" in results[0]["content"]
    
    # Search outside room should be empty (or not match)
    results_other_room = l2.search(query="Linear", wing="camelot", room="other")
    assert len(results_other_room) == 0
    
    # Search outside wing should be empty
    results_other_wing = l2.search(query="Linear", wing="other_project")
    assert len(results_other_wing) == 0
    
    # Cleanup
    shutil.rmtree(test_storage, ignore_errors=True)
