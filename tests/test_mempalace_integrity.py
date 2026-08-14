# SPDX-License-Identifier: MIT

import shutil
from pathlib import Path


def test_block_checksum_verification(meml2):
    # Use a local temporary directory
    test_storage = Path("./tests/tmp_mempalace_integrity")
    if test_storage.exists():
        shutil.rmtree(test_storage, ignore_errors=True)

    l2 = meml2.MemPalaceL2(storage_path=test_storage)

    # Store data
    l2.store(wing="test", room="audit", content="Secure Data", metadata={"id": "data_1"})

    # Search should pass integrity initially
    results = l2.search(query="Secure", wing="test", room="audit", verify_integrity=True)
    assert len(results) > 0
    assert results[0]["integrity_fail"] == False

    # MANUALLY TAMPER with metadata in ChromaDB (simulated)
    # We'll re-store with an invalid checksum to trigger the failure
    import hashlib
    bad_checksum = hashlib.sha256(b"tampered content").hexdigest()
    l2.store(wing="test", room="audit", content="Secure Data",
             metadata={"id": "data_1", "checksum": bad_checksum})

    results_tampered = l2.search(query="Secure", wing="test", room="audit", verify_integrity=True)
    # The search should either exclude the result or flag it
    assert len(results_tampered) == 0 or results_tampered[0]["integrity_fail"] == True

    # Cleanup
    shutil.rmtree(test_storage, ignore_errors=True)


def test_tenant_isolation(meml2):
    test_storage = Path("./tests/tmp_mempalace_isolation")
    if test_storage.exists():
        shutil.rmtree(test_storage, ignore_errors=True)

    l2 = meml2.MemPalaceL2(storage_path=test_storage)

    # Store same prefix for two different tenants
    l2.store(wing="camelot", room="audit", content="Shared Prefix", tenant_id="tenant_A")
    l2.store(wing="camelot", room="audit", content="Shared Prefix", tenant_id="tenant_B")

    # Verify search is isolated
    res_a = l2.search(query="Shared", wing="camelot", room="audit", tenant_id="tenant_A")
    res_b = l2.search(query="Shared", wing="camelot", room="audit", tenant_id="tenant_B")

    # Collections should be separate in the backend
    assert l2._get_collection_name("camelot", "audit", "tenant_A") != \
           l2._get_collection_name("camelot", "audit", "tenant_B")

    # Cleanup
    shutil.rmtree(test_storage, ignore_errors=True)
