"""MemPalace L2 tenant-isolation and secret-handling tests.

The isolation primitives are exercised directly (``_generate_salted_id`` and
``_get_collection_name``) because those hold the security property and work
without a vector backend. The end-to-end store/search test needs chromadb and
skips cleanly when it is absent — it previously failed with ``IndexError`` on an
empty result list, which looked like a collision bug rather than a missing
dependency.

Regression: tenant and content were concatenated into HMAC with no delimiter, so
the field boundary was ambiguous and distinct tenants could produce identical
IDs. The collection name had the same flaw, which is worse — two tenants sharing
one ChromaDB collection.
"""
import importlib.util
from pathlib import Path

import pytest


def _load_mempalace():
    repo_root = Path(__file__).resolve().parent.parent
    module_path = repo_root / "01_KERNEL" / "memory" / "mempalace_l2.py"
    spec = importlib.util.spec_from_file_location("mempalace_l2", module_path)
    mempalace = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mempalace)
    return mempalace


@pytest.fixture()
def l2(tmp_path):
    return _load_mempalace().MemPalaceL2(storage_path=tmp_path)


# ── Salted ID: injective framing ─────────────────────────────────────────────

def test_distinct_tenants_get_distinct_ids(l2):
    content = "Sensitive content that should be salted"
    assert l2._generate_salted_id(content, "tenant_a") != \
           l2._generate_salted_id(content, "tenant_b")


def test_same_tenant_and_content_is_stable(l2):
    """IDs must be deterministic — the persistent index is keyed by them."""
    assert l2._generate_salted_id("payload", "tenant_a") == \
           l2._generate_salted_id("payload", "tenant_a")


def test_ambiguous_field_split_does_not_collide(l2):
    """('a','bc') and ('ab','c') must not share an ID.

    Without length-prefixed framing both hash the bytes ``abc`` and collide,
    letting one tenant confirm another tenant's cached content.
    """
    assert l2._generate_salted_id("bc", "a") != l2._generate_salted_id("c", "ab")


@pytest.mark.parametrize(("t1", "c1", "t2", "c2"), [
    ("a", "bc", "ab", "c"),
    ("acme", "_secret", "acme_", "secret"),
    ("x", "yz", "xy", "z"),
    ("", "ab", "a", "b"),
])
def test_no_cross_tenant_id_collisions(l2, t1, c1, t2, c2):
    assert l2._generate_salted_id(c1, t1) != l2._generate_salted_id(c2, t2)


# ── Collection name: injective framing ───────────────────────────────────────

def test_ambiguous_split_does_not_share_a_collection(l2):
    """Two tenants must never resolve to the same ChromaDB collection."""
    assert l2._get_collection_name("sec_ops", "notes", "acme") != \
           l2._get_collection_name("ops", "notes", "acme_sec")


def test_collection_name_is_stable_and_chroma_valid(l2):
    name = l2._get_collection_name("sec/ops", "notes.v1", "acme-corp")
    assert name == l2._get_collection_name("sec/ops", "notes.v1", "acme-corp")
    assert 3 <= len(name) <= 63
    assert name[0].isalnum() and name[-1].isalnum()
    assert all(ch.isalnum() or ch in "_-" for ch in name)


def test_distinct_tenants_get_distinct_collections(l2):
    assert l2._get_collection_name("w", "r", "tenant_a") != \
           l2._get_collection_name("w", "r", "tenant_b")


# ── Secret handling ──────────────────────────────────────────────────────────

def test_missing_secret_is_refused(monkeypatch, tmp_path):
    """Absent secret must raise, not silently fall back to a public key."""
    mempalace = _load_mempalace()
    monkeypatch.delenv("MEMPALACE_SECRET", raising=False)
    monkeypatch.delenv("MEMPALACE_ALLOW_INSECURE_SECRET", raising=False)
    with pytest.raises(mempalace.MemPalaceSecretError):
        mempalace.MemPalaceL2(storage_path=tmp_path)


def test_known_public_default_is_refused_even_if_set(monkeypatch, tmp_path):
    mempalace = _load_mempalace()
    monkeypatch.setenv("MEMPALACE_SECRET", mempalace._INSECURE_DEFAULT_SECRET)
    with pytest.raises(mempalace.MemPalaceSecretError):
        mempalace.MemPalaceL2(storage_path=tmp_path)


def test_explicit_dev_optin_is_allowed(monkeypatch, tmp_path):
    mempalace = _load_mempalace()
    monkeypatch.delenv("MEMPALACE_SECRET", raising=False)
    monkeypatch.setenv("MEMPALACE_ALLOW_INSECURE_SECRET", "1")
    assert mempalace.MemPalaceL2(storage_path=tmp_path) is not None


def test_distinct_secrets_produce_distinct_ids(monkeypatch, tmp_path):
    """The HMAC key must actually key the output."""
    mempalace = _load_mempalace()
    monkeypatch.setenv("MEMPALACE_SECRET", "secret-one")
    first = mempalace.MemPalaceL2(storage_path=tmp_path)._generate_salted_id("x", "t")
    monkeypatch.setenv("MEMPALACE_SECRET", "secret-two")
    second = mempalace.MemPalaceL2(storage_path=tmp_path)._generate_salted_id("x", "t")
    assert first != second


# ── End-to-end (needs a vector backend) ──────────────────────────────────────

def test_cache_salting_collision_resistance(l2):
    """Two tenants storing identical content must round-trip to distinct IDs."""
    pytest.importorskip("chromadb", reason="L2 runs in DARK mode without chromadb")

    wing, room = "security", "test"
    content = "Sensitive content that should be salted"

    l2.store(wing, room, content, tenant_id="tenant_a")
    l2.store(wing, room, content, tenant_id="tenant_b")

    results_a = l2.search(content, wing, room, tenant_id="tenant_a")
    results_b = l2.search(content, wing, room, tenant_id="tenant_b")
    assert results_a and results_b, "store/search round-trip returned nothing"

    assert results_a[0]["id"] != results_b[0]["id"]


def test_tenant_search_does_not_return_another_tenants_content(l2):
    pytest.importorskip("chromadb", reason="L2 runs in DARK mode without chromadb")

    wing, room = "security", "isolation"
    l2.store(wing, room, "tenant a private note", tenant_id="tenant_a")

    leaked = l2.search("tenant a private note", wing, room, tenant_id="tenant_b")
    assert not leaked, f"tenant_b saw tenant_a content: {leaked}"


if __name__ == "__main__":
    pytest.main([__file__])
