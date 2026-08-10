# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Phase 2 Cartridge V2 test suite
================================

Covers:
  * CartridgeManifestV2 schema validation (V1 fields preserved, V2 fields added).
  * .cartridge archive roundtrip (pack -> unpack -> manifest matches).
  * Tamper detection (modified payload.zip, modified manifest.json).
  * V1 -> V2 adapter (legacy shim with V1_LEGACY_SHA256 magic).
  * PublisherRegistry (add, resolve, kid ownership).
  * TrustManager V2 verify path (publisher gate + crypto).
  * cartridge_cli pack/verify (smoke).

These tests are run by the existing test harness via ``python -m pytest``.
They do NOT touch disk outside a tmp dir; the existing cartridge package is
read-only for the duration of the suite.
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import pytest

# Make the package importable when running from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cartridge import cartridge_archive as ca
from cartridge import cartridge_cli
from cartridge import cartridge_crypto as cc
from cartridge.cartridge_schemas import (
    V1_HOST_API_VERSION,
    V1_LEGACY_SHA256,
    V2_HOST_API_VERSION,
    CartridgeManifest,
    CartridgeManifestV2,
)
from cartridge.cartridge_trust import (
    PublisherRegistry,
    TrustManager,
    TrustStore,
    install_publisher_registry,
)
from cartridge.cartridge_v2_adapter import (
    is_legacy_v1,
    upgrade_v1_manifest,
)


# ── Fixtures ────────────────────────────────────────────────────────────────
@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def v1_manifest_dict():
    """A minimal V1 manifest dict (matches the seven cockpit cartridges)."""
    return {
        "cartridge_id": "TEST_CART",
        "version": "1.0.0",
        "description": "Phase 2 test cartridge",
        "agents": ["Sir_Test"],
        "tools": [],
        "protocols": [],
        "capabilities": ["test.capability"],
        "resource_budget": {
            "max_tokens": 8000,
            "max_memory_mb": 256,
            "max_latency_ms": 300,
        },
        "risk_profile": "low",
        "governance": {
            "HITL_required": False,
            "allowed_tools": [],
            "denied_operations": [],
        },
        "hooks": {"on_load": [], "on_unload": [], "health_check": []},
        "embeddings": {"static_docs": [], "symbolic_snippets": []},
        "signature": "ed25519:default:dGVzdA==",  # placeholder, will be re-signed
        "created_at": "2026-07-10T00:00:00",
        "created_by": "test_suite",
    }


@pytest.fixture
def signed_v1_manifest(v1_manifest_dict, monkeypatch):
    """A V1 manifest signed with a fresh in-memory ed25519 key.

    The public key is registered in the TrustStore via env so the verify
    path can resolve it.
    """
    priv_b64, pub_b64 = cc.generate_keypair(save=False)
    monkeypatch.setenv("CAMELOT_CARTRIDGE_PRIVATE_KEY", priv_b64)
    monkeypatch.setenv("CAMELOT_CARTRIDGE_PUBLIC_KEY", pub_b64)
    # Canonicalize the dict-like manifest (pydantic v1 -> v2 transition)
    manifest = CartridgeManifest.model_validate(v1_manifest_dict)
    sig = cc.sign(manifest)
    v1_manifest_dict["signature"] = sig
    return v1_manifest_dict, pub_b64, priv_b64


@pytest.fixture
def resign(signed_v1_manifest):
    """Re-sign a manifest with the same keypair as signed_v1_manifest.

    V2-only fields (hostApiVersion, publisher_id, sha256, entry, routes,
    resourceBudget) change the canonical bytes produced by
    cartridge_crypto.canonical_bytes, so a signature computed against
    the V1 form will not verify against the V2 form. Every V2 verify
    test must therefore re-sign AFTER adding V2 fields. This fixture
    reuses the keypair from signed_v1_manifest so the public key
    registered in the trust store still resolves the signature.
    """
    _manifest_dict, _pub_b64, priv_b64 = signed_v1_manifest

    def _resign(manifest):
        sig = cc.sign(manifest, private_key_b64=priv_b64)
        if isinstance(manifest, dict):
            return {**manifest, "signature": sig}
        return manifest.model_copy(update={"signature": sig})

    return _resign


@pytest.fixture
def publisher_registry_dir(tmp_path, monkeypatch):
    """Per-test PublisherRegistry stored in a tmp dir so tests don't collide."""
    reg_path = tmp_path / "publishers.json"
    monkeypatch.setenv("CAMELOT_CARTRIDGE_PUBLISHERS", str(reg_path))
    return reg_path


# ── Schema ──────────────────────────────────────────────────────────────────
def test_v2_schema_inherits_v1_fields():
    """V2 must keep every V1 field (so a V1 dict validates)."""
    base = {
        "cartridge_id": "X",
        "description": "d",
        "agents": [],
        "tools": [],
        "protocols": [],
        "capabilities": [],
        "resource_budget": {"max_tokens": 1, "max_memory_mb": 1, "max_latency_ms": 1},
        "governance": {"HITL_required": False, "allowed_tools": [], "denied_operations": []},
        "hooks": {"on_load": [], "on_unload": [], "health_check": []},
        "embeddings": {"static_docs": [], "symbolic_snippets": []},
        "signature": "ed25519:default:dGVzdA==",
    }
    m = CartridgeManifestV2.model_validate(base)
    # V1 fields preserved
    assert m.cartridge_id == "X"
    assert m.description == "d"
    assert m.resource_budget.max_tokens == 1
    # V2 fields have defaults
    assert m.hostApiVersion == V2_HOST_API_VERSION
    assert m.publisher_id == "legacy-v1"
    # sha256 default is "" (empty); V1->V2 adapter and pack() set it explicitly.
    assert m.sha256 == ""
    assert m.entry == "./index.js"
    assert m.routes == []


def test_v2_schema_requires_publisher_id_override():
    """V2 must accept arbitrary publisher_id; the registry is what gates it."""
    base = {"cartridge_id": "X", "description": "d", "signature": "ed25519:default:dGVzdA=="}
    m = CartridgeManifestV2.model_validate({**base, "publisher_id": "acme-cartridge-works"})
    assert m.publisher_id == "acme-cartridge-works"


def test_v2_routes_and_resource_budget_camel_case():
    m = CartridgeManifestV2.model_validate({
        "cartridge_id": "X",
        "description": "d",
        "signature": "ed25519:default:dGVzdA==",
        "routes": [
            {"mount": "/cartridges/x", "component": "./x-cartridge", "prefetch": ["./a.js"]}
        ],
        "resourceBudget": {"maxTokens": 500, "maxMemoryMb": 100, "maxLatencyMs": 50},
    })
    assert len(m.routes) == 1
    assert m.routes[0].mount == "/cartridges/x"
    assert m.routes[0].prefetch == ["./a.js"]
    assert m.resourceBudget.maxTokens == 500


def test_v2_v1_legacy_helper():
    # sha256 default is "" (empty), so we must set V1_LEGACY_SHA256
    # explicitly to exercise the v1_legacy() shortcut.
    m = CartridgeManifestV2.model_validate({
        "cartridge_id": "X",
        "description": "d",
        "signature": "ed25519:default:dGVzdA==",
        "sha256": V1_LEGACY_SHA256,
    })
    assert m.v1_legacy() is True
    m2 = m.model_copy(update={"sha256": "a" * 64})
    assert m2.v1_legacy() is False


# ── Archive: pack / unpack / tamper ─────────────────────────────────────────
def _write_source_dir(path: Path, files: dict[str, str]) -> None:
    for rel, content in files.items():
        full = path / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")


# Tests that need to pre-set manifest.sha256 (so pack() does NOT overwrite it)
# call ca.compute_payload_sha256() — the canonical implementation lives in
# cartridge_archive.py so this test helper cannot silently diverge from the
# production writer.


def test_archive_pack_unpack_roundtrip(tmp_dir, signed_v1_manifest):
    manifest_dict, _pub, _priv = signed_v1_manifest
    manifest_v1 = CartridgeManifest.model_validate(manifest_dict)
    manifest = CartridgeManifestV2.model_validate({
        **manifest_v1.model_dump(mode="json"),
        "hostApiVersion": V2_HOST_API_VERSION,
        "publisher_id": "acme-test",
        "entry": "./src/index.tsx",
        "routes": [{"mount": "/cartridges/x", "component": "./src/index.tsx", "prefetch": []}],
    })
    src = tmp_dir / "src"
    _write_source_dir(src, {"index.tsx": "// hello", "lib/util.ts": "export const v = 1;"})

    archive_path = tmp_dir / "out.cartridge"
    written = ca.pack(src, manifest, archive_path)
    assert Path(written) == archive_path
    assert archive_path.is_file()

    m2, payload, _meta = ca.unpack(archive_path)
    assert m2.cartridge_id == manifest.cartridge_id
    # pack() overwrites V1_LEGACY_SHA256 (and any blank hash) with the real
    # payload hash, so the archive's manifest carries the actual hash, not
    # the stale V1_LEGACY_SHA256 still in the caller's local `manifest`
    # variable. Compare against the real payload hash instead.
    expected_sha = ca.sha256_bytes(payload)
    assert m2.sha256 == expected_sha
    assert m2.sha256 != V1_LEGACY_SHA256
    # payload.zip should be a valid zip with our two source files
    with zipfile.ZipFile(io.BytesIO(payload), "r") as zf:
        names = sorted(zf.namelist())
    assert names == ["index.tsx", "lib/util.ts"]


def test_archive_unpack_rejects_non_zip(tmp_dir):
    bogus = tmp_dir / "bogus.cartridge"
    bogus.write_text("not a zip file", encoding="utf-8")
    with pytest.raises(ca.ArchiveError):
        ca.unpack(bogus)


def test_archive_unpack_rejects_wrong_members(tmp_dir):
    archive = tmp_dir / "wrong.cartridge"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("readme.txt", "hi")
    with pytest.raises(ca.ArchiveError):
        ca.unpack(archive)


def test_archive_unpack_detects_payload_tamper(tmp_dir, signed_v1_manifest):
    manifest_dict, _pub, _priv = signed_v1_manifest
    manifest = CartridgeManifestV2.model_validate({
        **manifest_dict,
        "hostApiVersion": V2_HOST_API_VERSION,
        "publisher_id": "acme-test",
        "entry": "./src/index.tsx",
    })
    src = tmp_dir / "src"
    _write_source_dir(src, {"index.tsx": "// hello"})

    archive_path = tmp_dir / "out.cartridge"
    ca.pack(src, manifest, archive_path)

    # Surgically rewrite the payload.zip inside the outer archive to a
    # different byte string; the outer envelope stays valid but the inner
    # hash no longer matches.
    outer_buf = io.BytesIO(archive_path.read_bytes())
    payload_buf = io.BytesIO()
    with zipfile.ZipFile(outer_buf, "r") as outer:
        manifest_json = outer.read("manifest.json")
        with zipfile.ZipFile(payload_buf, "w", compression=zipfile.ZIP_STORED) as inner:
            inner.writestr("evil.txt", "tampered")
    new_payload = payload_buf.getvalue()

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_STORED) as outer:
        outer.writestr("manifest.json", manifest_json)
        outer.writestr("payload.zip", new_payload)

    with pytest.raises(ca.ArchiveError, match="sha256 mismatch"):
        ca.unpack(archive_path)


def test_archive_legacy_v1_skips_payload_check(tmp_dir, signed_v1_manifest):
    """V1 legacy shims (sha256 == V1_LEGACY_SHA256) are accepted when unpacked
    directly without going through pack() — pack() deliberately overwrites
    V1_LEGACY_SHA256 with the real payload hash because a packed archive IS
    a real archive (it has a payload.zip) and the V1_LEGACY_SHA256 sentinel
    only applies to the runtime hydrator's V1 shim path. This test covers the
    unpack-only V1 shim path that the V1 trusted loader exercises."""
    manifest_dict, _pub, _priv = signed_v1_manifest
    manifest = CartridgeManifestV2.model_validate({
        **manifest_dict,
        "hostApiVersion": V1_HOST_API_VERSION,
        "publisher_id": "legacy-v1",
        "entry": "src/cartridges/x/x-cartridge.tsx",
        "sha256": V1_LEGACY_SHA256,
    })
    # Build the archive by hand (not via pack()) so the manifest keeps its
    # V1_LEGACY_SHA256 sentinel.
    archive_path = tmp_dir / "legacy.cartridge"
    payload_buf = io.BytesIO()
    with zipfile.ZipFile(payload_buf, "w", compression=zipfile.ZIP_STORED) as inner:
        inner.writestr("index.tsx", "// (not used; legacy)")
    manifest_json = manifest.model_dump_json(indent=2).encode("utf-8")
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_STORED) as outer:
        outer.writestr("manifest.json", manifest_json)
        outer.writestr("payload.zip", payload_buf.getvalue())

    m2, _payload, _meta = ca.unpack(archive_path)
    # Lock the full V1 shim contract: the unpacked manifest preserves the
    # V1 fields and the V1_LEGACY_SHA256 sentinel survives the round-trip.
    assert m2.v1_legacy() is True
    assert m2.cartridge_id == manifest.cartridge_id
    assert m2.publisher_id == "legacy-v1"
    assert m2.hostApiVersion == V1_HOST_API_VERSION
    assert m2.sha256 == V1_LEGACY_SHA256


# ── V1 -> V2 adapter ────────────────────────────────────────────────────────
def test_v1_to_v2_adapter_fills_v2_fields(v1_manifest_dict):
    v2 = upgrade_v1_manifest(v1_manifest_dict)
    assert v2.cartridge_id == v1_manifest_dict["cartridge_id"]
    assert v2.hostApiVersion == V1_HOST_API_VERSION
    assert v2.publisher_id == "legacy-v1"
    assert v2.entry == "src/cartridges/TEST_CART/TEST_CART-cartridge.tsx"
    assert v2.sha256 == V1_LEGACY_SHA256
    assert len(v2.routes) == 1
    assert v2.routes[0].mount == "/cartridges/TEST_CART"
    # V1 fields preserved
    assert v2.agents == v1_manifest_dict["agents"]
    assert v2.capabilities == v1_manifest_dict["capabilities"]
    # resource_budget is preserved AND mirrored
    assert v2.resource_budget.max_tokens == 8000
    assert v2.resourceBudget.maxTokens == 8000


def test_v1_to_v2_adapter_rejects_missing_id():
    with pytest.raises(ValueError, match="cartridge_id"):
        upgrade_v1_manifest({"description": "no id"})


def test_is_legacy_v1_helper():
    v2 = upgrade_v1_manifest({"cartridge_id": "X", "description": "d", "signature": "ed25519:default:dGVzdA=="})
    assert is_legacy_v1(v2) is True


# ── PublisherRegistry ───────────────────────────────────────────────────────
def test_publisher_registry_roundtrip(publisher_registry_dir):
    reg = PublisherRegistry()
    reg.add_publisher("acme", kids=["kid-2025", "kid-2026"], note="initial")
    assert reg.resolve("acme").kids == ["kid-2025", "kid-2026"]

    # Reload from disk
    reg2 = PublisherRegistry()
    assert reg2.resolve("acme").kids == ["kid-2025", "kid-2026"]
    assert reg2.is_kid_owned_by("acme", "kid-2026") is True
    assert reg2.is_kid_owned_by("acme", "kid-2099") is False
    assert reg2.is_kid_owned_by("ghost-publisher", "kid-2026") is False


def test_publisher_registry_rotation(publisher_registry_dir):
    reg = PublisherRegistry()
    reg.add_publisher("acme", kids=["kid-2025"])
    reg.add_kid_to_publisher("acme", "kid-2026")
    assert reg.resolve("acme").kids == ["kid-2025", "kid-2026"]


def test_publisher_registry_duplicate_rejected(publisher_registry_dir):
    reg = PublisherRegistry()
    reg.add_publisher("acme", kids=["kid-2025"])
    with pytest.raises(ValueError, match="already registered"):
        reg.add_publisher("acme", kids=["kid-2026"])


def test_publisher_registry_add_public_key(publisher_registry_dir):
    """Phase 3: add_public_key_to_publisher stores a base64 Ed25519 public key
    for a kid and round-trips through the registry."""
    reg = PublisherRegistry()
    reg.add_publisher("acme", kids=["kid-2025"])
    reg.add_public_key_to_publisher("acme", "kid-2025", "AbCdEf123==")
    # Reload from disk to confirm persistence.
    reg2 = PublisherRegistry()
    entry = reg2.resolve("acme")
    assert entry is not None
    assert entry.public_keys == {"kid-2025": "AbCdEf123=="}


def test_publisher_registry_add_public_key_rejects_unknown_kid(publisher_registry_dir):
    """Adding a public key for a kid the publisher doesn't own must fail loud."""
    reg = PublisherRegistry()
    reg.add_publisher("acme", kids=["kid-2025"])
    with pytest.raises(ValueError, match="not owned by publisher"):
        reg.add_public_key_to_publisher("acme", "kid-9999", "AbCdEf123==")


def test_publisher_registry_add_public_key_rejects_unknown_publisher(publisher_registry_dir):
    reg = PublisherRegistry()
    with pytest.raises(KeyError, match="unknown publisher"):
        reg.add_public_key_to_publisher("ghost", "kid-2025", "AbCdEf123==")


def test_publisher_registry_to_bundle_dict(publisher_registry_dir):
    """to_bundle_dict emits the browser bundle shape (camelCase, versioned)."""
    reg = PublisherRegistry()
    reg.add_publisher(
        "acme", kids=["kid-2025", "kid-2026"], note="Acme Cartridge Works",
    )
    reg.add_public_key_to_publisher("acme", "kid-2025", "AbC==")
    reg.add_public_key_to_publisher("acme", "kid-2026", "DeF==")
    bundle = reg.to_bundle_dict()
    # Versioned + timestamped envelope.
    assert bundle["version"] == "1"
    assert isinstance(bundle["exported_at"], str) and "T" in bundle["exported_at"]
    # camelCase publisher entries matching the TypeScript PublisherInfo type.
    assert len(bundle["publishers"]) == 1
    pub = bundle["publishers"][0]
    assert pub["publisherId"] == "acme"
    assert pub["trustedKids"] == ["kid-2025", "kid-2026"]
    assert pub["publicKeys"] == {"kid-2025": "AbC==", "kid-2026": "DeF=="}
    assert pub["active"] is True
    assert pub["note"] == "Acme Cartridge Works"


def test_publisher_registry_to_bundle_dict_always_excludes_legacy_v1(publisher_registry_dir):
    """The deterministic legacy-v1 seed is unconditionally filtered out of
    the bundle (no opt-in flag). The seed is browser-side and never
    belongs in the bundle; operators should never need to include it."""
    reg = PublisherRegistry()
    reg.add_publisher("acme", kids=["kid-2025"])
    # Even if the operator explicitly adds the seed to the Python registry,
    # to_bundle_dict() must still exclude it from the bundle.
    reg.add_publisher("legacy-v1", kids=["default", "legacy"])
    bundle = reg.to_bundle_dict()
    publisher_ids = [p["publisherId"] for p in bundle["publishers"]]
    assert "legacy-v1" not in publisher_ids
    assert "acme" in publisher_ids


# ── TrustManager V2 verify path ─────────────────────────────────────────────
def test_trust_manager_v2_verify_happy_path(tmp_dir, signed_v1_manifest, publisher_registry_dir, monkeypatch, resign):
    manifest_dict, pub_b64, _priv = signed_v1_manifest
    monkeypatch.setenv("CAMELOT_CARTRIDGE_TRUST_STORE", str(tmp_dir / "trust.json"))
    monkeypatch.setenv("CAMELOT_CARTRIDGE_REVOCATIONS", str(tmp_dir / "revocations.json"))
    monkeypatch.setenv("CAMELOT_CARTRIDGE_AUDIT_LOG", str(tmp_dir / "audit.log"))

    store = TrustStore()
    store.add_key("default", scheme=cc.SCHEME_ED25519, public_key_b64=pub_b64)

    reg = PublisherRegistry()
    reg.add_publisher("acme-test", kids=["default"])

    manager = TrustManager()
    install_publisher_registry(manager, reg)

    manifest_v2 = CartridgeManifestV2.model_validate({
        **manifest_dict,
        "hostApiVersion": V2_HOST_API_VERSION,
        "publisher_id": "acme-test",
        # sha256 default is "" (empty); trust manager rejects empty as
        # "not yet packed". Set a real 64-char hex string to exercise the
        # V2 verify happy path.
        "sha256": "a" * 64,
    })
    # V2-only fields change canonical bytes; re-sign after adding them.
    manifest_v2 = resign(manifest_v2)
    ok, why = manager.verify_v2(manifest_v2)
    assert ok is True, why
    assert "default" in why


def test_trust_manager_v2_verify_rejects_unknown_publisher(tmp_dir, signed_v1_manifest, publisher_registry_dir, monkeypatch, resign):
    manifest_dict, pub_b64, _priv = signed_v1_manifest
    monkeypatch.setenv("CAMELOT_CARTRIDGE_TRUST_STORE", str(tmp_dir / "trust.json"))
    monkeypatch.setenv("CAMELOT_CARTRIDGE_REVOCATIONS", str(tmp_dir / "revocations.json"))
    monkeypatch.setenv("CAMELOT_CARTRIDGE_AUDIT_LOG", str(tmp_dir / "audit.log"))

    store = TrustStore()
    store.add_key("default", scheme=cc.SCHEME_ED25519, public_key_b64=pub_b64)
    reg = PublisherRegistry()
    manager = TrustManager()
    install_publisher_registry(manager, reg)

    manifest_v2 = CartridgeManifestV2.model_validate({
        **manifest_dict,
        "hostApiVersion": V2_HOST_API_VERSION,
        "publisher_id": "unknown-publisher",
        # V2 sha256 default is V1_LEGACY_SHA256, which would trigger the V1
        # legacy short-circuit in _trust_manager_verify_v2 and skip the
        # publisher check. Set a real 64-char hex string to exercise the
        # V2 publisher path.
        "sha256": "a" * 64,
    })
    # V2-only fields change canonical bytes; re-sign after adding them.
    manifest_v2 = resign(manifest_v2)
    ok, why = manager.verify_v2(manifest_v2)
    assert ok is False
    assert "unknown publisher" in why


def test_trust_manager_v2_verify_rejects_wrong_kid(tmp_dir, signed_v1_manifest, publisher_registry_dir, monkeypatch, resign):
    manifest_dict, pub_b64, _priv = signed_v1_manifest
    monkeypatch.setenv("CAMELOT_CARTRIDGE_TRUST_STORE", str(tmp_dir / "trust.json"))
    monkeypatch.setenv("CAMELOT_CARTRIDGE_REVOCATIONS", str(tmp_dir / "revocations.json"))
    monkeypatch.setenv("CAMELOT_CARTRIDGE_AUDIT_LOG", str(tmp_dir / "audit.log"))

    store = TrustStore()
    store.add_key("default", scheme=cc.SCHEME_ED25519, public_key_b64=pub_b64)
    reg = PublisherRegistry()
    reg.add_publisher("acme-test", kids=["some-other-kid"])  # not "default"
    manager = TrustManager()
    install_publisher_registry(manager, reg)

    manifest_v2 = CartridgeManifestV2.model_validate({
        **manifest_dict,
        "hostApiVersion": V2_HOST_API_VERSION,
        "publisher_id": "acme-test",
        # V2 sha256 default is V1_LEGACY_SHA256, which would trigger the V1
        # legacy short-circuit in _trust_manager_verify_v2 and skip the
        # publisher check. Set a real 64-char hex string to exercise the
        # V2 publisher path.
        "sha256": "a" * 64,
    })
    # V2-only fields change canonical bytes; re-sign after adding them.
    manifest_v2 = resign(manifest_v2)
    ok, why = manager.verify_v2(manifest_v2)
    assert ok is False
    assert "does not own kid" in why


def test_trust_manager_v2_legacy_v1_skips_publisher_gate(tmp_dir, signed_v1_manifest, publisher_registry_dir, monkeypatch, resign):
    manifest_dict, pub_b64, _priv = signed_v1_manifest
    monkeypatch.setenv("CAMELOT_CARTRIDGE_TRUST_STORE", str(tmp_dir / "trust.json"))
    monkeypatch.setenv("CAMELOT_CARTRIDGE_REVOCATIONS", str(tmp_dir / "revocations.json"))
    monkeypatch.setenv("CAMELOT_CARTRIDGE_AUDIT_LOG", str(tmp_dir / "audit.log"))

    store = TrustStore()
    store.add_key("default", scheme=cc.SCHEME_ED25519, public_key_b64=pub_b64)
    reg = PublisherRegistry()
    manager = TrustManager()
    install_publisher_registry(manager, reg)

    # V1 legacy shim: publisher_id is "legacy-v1", no publisher in registry.
    manifest_v2 = CartridgeManifestV2.model_validate({
        **manifest_dict,
        "hostApiVersion": V1_HOST_API_VERSION,
        "publisher_id": "legacy-v1",
        "sha256": V1_LEGACY_SHA256,
    })
    # V2-only fields change canonical bytes; re-sign after adding them.
    manifest_v2 = resign(manifest_v2)
    ok, why = manager.verify_v2(manifest_v2)
    # The V1 verify path (signature check) still runs; this is the legacy bridge.
    assert ok is True, why


# ── CLI smoke ───────────────────────────────────────────────────────────────
def test_cli_pack_and_verify(tmp_dir, signed_v1_manifest, publisher_registry_dir, monkeypatch, resign):
    manifest_dict, pub_b64, _priv = signed_v1_manifest
    monkeypatch.setenv("CAMELOT_CARTRIDGE_TRUST_STORE", str(tmp_dir / "trust.json"))
    monkeypatch.setenv("CAMELOT_CARTRIDGE_REVOCATIONS", str(tmp_dir / "revocations.json"))
    monkeypatch.setenv("CAMELOT_CARTRIDGE_AUDIT_LOG", str(tmp_dir / "audit.log"))
    monkeypatch.setenv("CAMELOT_CARTRIDGE_PUBLISHERS", str(tmp_dir / "publishers.json"))

    # Set up trust + publisher
    store = TrustStore()
    store.add_key("default", scheme=cc.SCHEME_ED25519, public_key_b64=pub_b64)
    reg = PublisherRegistry()
    reg.add_publisher("acme-test", kids=["default"])

    src = tmp_dir / "src"
    _write_source_dir(src, {"index.tsx": "// hello"})

    manifest_path = tmp_dir / "manifest.json"
    manifest_v2 = CartridgeManifestV2.model_validate({
        **manifest_dict,
        "hostApiVersion": V2_HOST_API_VERSION,
        "publisher_id": "acme-test",
        # Pre-compute the expected payload sha256 so pack() does NOT overwrite
        # it (pack() overwrites V1_LEGACY_SHA256 and blank values; any other
        # mismatch raises ArchiveError). This keeps the signature valid because
        # the in-archive manifest matches what we signed.
        "sha256": ca.compute_payload_sha256(src),
    })
    # V2-only fields change canonical bytes; re-sign after adding them.
    manifest_v2 = resign(manifest_v2)
    manifest_path.write_text(manifest_v2.model_dump_json(indent=2), encoding="utf-8")

    archive_path = tmp_dir / "out.cartridge"
    rc = cartridge_cli.main([
        "pack",
        "--source", str(src),
        "--manifest", str(manifest_path),
        "--output", str(archive_path),
    ])
    assert rc == 0
    assert archive_path.is_file()

    rc = cartridge_cli.main(["verify", str(archive_path)])
    assert rc == 0


def test_cli_verify_rejects_tampered(tmp_dir, signed_v1_manifest, publisher_registry_dir, monkeypatch, resign):
    manifest_dict, pub_b64, _priv = signed_v1_manifest
    monkeypatch.setenv("CAMELOT_CARTRIDGE_TRUST_STORE", str(tmp_dir / "trust.json"))
    monkeypatch.setenv("CAMELOT_CARTRIDGE_REVOCATIONS", str(tmp_dir / "revocations.json"))
    monkeypatch.setenv("CAMELOT_CARTRIDGE_AUDIT_LOG", str(tmp_dir / "audit.log"))
    monkeypatch.setenv("CAMELOT_CARTRIDGE_PUBLISHERS", str(tmp_dir / "publishers.json"))

    store = TrustStore()
    store.add_key("default", scheme=cc.SCHEME_ED25519, public_key_b64=pub_b64)
    reg = PublisherRegistry()
    reg.add_publisher("acme-test", kids=["default"])

    src = tmp_dir / "src"
    _write_source_dir(src, {"index.tsx": "// hello"})

    manifest_path = tmp_dir / "manifest.json"
    manifest_v2 = CartridgeManifestV2.model_validate({
        **manifest_dict,
        "hostApiVersion": V2_HOST_API_VERSION,
        "publisher_id": "acme-test",
        # Pre-compute the expected payload sha256 so pack() does NOT overwrite
        # it (pack() overwrites V1_LEGACY_SHA256 and blank values; any other
        # mismatch raises ArchiveError). This keeps the signature valid because
        # the in-archive manifest matches what we signed.
        "sha256": ca.compute_payload_sha256(src),
    })
    # V2-only fields change canonical bytes; re-sign after adding them.
    manifest_v2 = resign(manifest_v2)
    manifest_path.write_text(manifest_v2.model_dump_json(indent=2), encoding="utf-8")

    archive_path = tmp_dir / "out.cartridge"
    cartridge_cli.main([
        "pack", "--source", str(src), "--manifest", str(manifest_path), "--output", str(archive_path),
    ])

    # Tamper with the inner payload
    outer_buf = io.BytesIO(archive_path.read_bytes())
    manifest_json = None
    with zipfile.ZipFile(outer_buf, "r") as outer:
        manifest_json = outer.read("manifest.json")
    payload_buf = io.BytesIO()
    with zipfile.ZipFile(payload_buf, "w", compression=zipfile.ZIP_STORED) as inner:
        inner.writestr("evil.txt", "tampered")
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_STORED) as outer:
        outer.writestr("manifest.json", manifest_json)
        outer.writestr("payload.zip", payload_buf.getvalue())

    rc = cartridge_cli.main(["verify", str(archive_path)])
    assert rc == 1  # archive error


# ── Phase 3 public key distribution ───────────────────────────────────────
def test_cli_add_publisher_with_public_key(tmp_dir, monkeypatch):
    """`cartridge_cli add-publisher --public-key KID:PUBKEY_B64` stores the
    public key and the subsequent `export-bundle` emits it in the browser
    bundle shape. Closes the Phase 3 ship-blocker for production Ed25519."""
    monkeypatch.setenv("CAMELOT_CARTRIDGE_PUBLISHERS", str(tmp_dir / "publishers.json"))

    # Register a publisher with one kid + one Ed25519 public key.
    rc = cartridge_cli.main([
        "add-publisher", "acme-cartridge-works",
        "--kids", "kid-2026",
        "--public-key", "kid-2026:AbCdEf123==",
        "--note", "Phase 3 test publisher",
    ])
    assert rc == 0, f"add-publisher returned {rc}"

    # Export the bundle and verify the public key round-trips.
    bundle_path = tmp_dir / "publishers.json"
    rc = cartridge_cli.main([
        "export-bundle", "--output", str(bundle_path),
    ])
    assert rc == 0, f"export-bundle returned {rc}"
    assert bundle_path.is_file()

    import json as _json
    bundle = _json.loads(bundle_path.read_text(encoding="utf-8"))
    assert bundle["version"] == "1"
    assert len(bundle["publishers"]) == 1
    pub = bundle["publishers"][0]
    assert pub["publisherId"] == "acme-cartridge-works"
    assert pub["trustedKids"] == ["kid-2026"]
    assert pub["publicKeys"] == {"kid-2026": "AbCdEf123=="}
    assert pub["active"] is True
    assert pub["note"] == "Phase 3 test publisher"


def test_cli_add_publisher_public_key_rejects_invalid_format(tmp_dir, monkeypatch):
    """`--public-key` without the `KID:PUBKEY_B64` separator must fail loud
    (exit code 3) rather than silently dropping the key."""
    monkeypatch.setenv("CAMELOT_CARTRIDGE_PUBLISHERS", str(tmp_dir / "publishers.json"))
    rc = cartridge_cli.main([
        "add-publisher", "acme",
        "--kids", "kid-2026",
        "--public-key", "no-separator-here",
    ])
    assert rc == 3
    # Publisher should NOT be registered (fail-loud before save).
    assert not (tmp_dir / "publishers.json").exists()


def test_cli_add_publisher_public_key_rejects_unknown_kid(tmp_dir, monkeypatch):
    """`--public-key` for a kid not in `--kids` must fail loud (exit code 3)."""
    monkeypatch.setenv("CAMELOT_CARTRIDGE_PUBLISHERS", str(tmp_dir / "publishers.json"))
    rc = cartridge_cli.main([
        "add-publisher", "acme",
        "--kids", "kid-2025",
        "--public-key", "kid-9999:AbC==",
    ])
    assert rc == 3


def test_cli_export_bundle_roundtrip(tmp_dir, monkeypatch):
    """`export-bundle` writes a versioned JSON file that matches
    `loadTrustedPublishers` input shape on the browser side."""
    monkeypatch.setenv("CAMELOT_CARTRIDGE_PUBLISHERS", str(tmp_dir / "publishers.json"))

    # Register two publishers with different key sets.
    cartridge_cli.main([
        "add-publisher", "acme",
        "--kids", "kid-a", "kid-b",
        "--public-key", "kid-a:PUBKEY_A", "kid-b:PUBKEY_B",
    ])
    cartridge_cli.main([
        "add-publisher", "lisa",
        "--kids", "kid-x",
    ])

    bundle_path = tmp_dir / "bundle.json"
    rc = cartridge_cli.main(["export-bundle", "--output", str(bundle_path)])
    assert rc == 0
    assert bundle_path.is_file()

    import json as _json
    bundle = _json.loads(bundle_path.read_text(encoding="utf-8"))
    assert bundle["version"] == "1"
    assert "exported_at" in bundle
    by_id = {p["publisherId"]: p for p in bundle["publishers"]}
    assert by_id["acme"]["publicKeys"] == {"kid-a": "PUBKEY_A", "kid-b": "PUBKEY_B"}
    # Publisher with no public keys still appears in the bundle with an
    # empty publicKeys map (the browser will trust via kids alone if the
    # V1 legacy short-circuit applies, or fail at Ed25519 verify time).
    assert by_id["lisa"]["publicKeys"] == {}
