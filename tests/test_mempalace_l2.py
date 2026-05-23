import pytest
import os
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
