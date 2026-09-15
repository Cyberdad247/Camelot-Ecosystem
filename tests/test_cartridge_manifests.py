# SPDX-License-Identifier: MIT

"""Cartridge-manifest suite — enforces the §8.2 / §8.3 manifest policy.

Every `cartridges/*/manifest.json` must:

1. Validate against the v1.2 `packages/contracts/cartridge.schema.json`.
2. Re-derive `artifact_hash` and verify the ed25519 `signature` against the
   shipped `signing_key.pub` (canonicalization shared with
   `scripts/sign_cartridge.py` — single source of truth).
3. Deny the authority capability set by construction (§8.2):
   `lease.issue, policy.admin, secret.export, unrestricted.network,
   direct_main_branch_write, auto_merge, auto_deploy`.
4. Honor §8.3: `customer-controlled` signer band cannot exceed T2.
"""

import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = ROOT / "packages" / "contracts"
CARTIDGES_DIR = ROOT / "cartridges"

# Load scripts/sign_cartridge.py by path (scripts/ is not a guaranteed package).
_spec = importlib.util.spec_from_file_location(
    "sign_cartridge", ROOT / "scripts" / "sign_cartridge.py"
)
sign_cartridge = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sign_cartridge)

MANIFESTS = sorted(CARTIDGES_DIR.glob("*/manifest.json"))
assert MANIFESTS, "cartridges/*/manifest.json must not be empty"

AUTHORITY_DENY_SET = {
    "lease.issue",
    "policy.admin",
    "secret.export",
    "unrestricted.network",
    "direct_main_branch_write",
    "auto_merge",
    "auto_deploy",
}


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def cartridge_schema() -> dict:
    return json.loads((CONTRACTS_DIR / "cartridge.schema.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.parent.name)
def test_manifest_validates_against_contract(cartridge_schema, path):
    validator = Draft202012Validator(cartridge_schema)
    errors = sorted(validator.iter_errors(load_manifest(path)), key=str)
    assert errors == [], f"{path.parent.name} failed contract: {errors}"


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.parent.name)
def test_manifest_signature_verifies(path):
    pub = (path.parent / "signing_key.pub").read_bytes()
    assert sign_cartridge.verify_manifest(path, pub), f"{path.parent.name} signature/artifact_hash invalid"


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.parent.name)
def test_manifest_denies_authority_capabilities(path):
    manifest = load_manifest(path)
    denied = set(manifest["denied_capabilities"])
    missing = AUTHORITY_DENY_SET - denied
    assert not missing, f"{path.parent.name} missing required denials: {sorted(missing)}"


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.parent.name)
def test_manifest_signer_band_caps_tier(path):
    manifest = load_manifest(path)
    if manifest["signer_trust_band"] == "customer-controlled":
        cap = manifest["risk_tier_invariant_cap"]
        assert cap in ("T0", "T1", "T2"), (
            f"{path.parent.name}: customer-controlled cap must be ≤ T2, got {cap}"
        )


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.parent.name)
def test_manifest_resource_profile_sane(path):
    profile = load_manifest(path)["resource_profile"]
    assert profile["memory_mb"] >= 64
    assert profile["timeout_s"] >= 1
    assert profile["max_workers"] >= 1


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.parent.name)
def test_manifest_risk_tier_is_valid(path):
    assert load_manifest(path)["risk_tier_invariant_cap"] in ("T0", "T1", "T2", "T3", "T4")


def test_tampered_manifest_is_rejected(tmp_path):
    """A manifest with an edited field must fail signature verification."""
    source = MANIFESTS[0]
    tampered_path = tmp_path / "manifest.json"
    manifest = load_manifest(source)
    manifest["resource_profile"]["timeout_s"] += 1  # edit after signing
    tampered_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    pub = (source.parent / "signing_key.pub").read_bytes()
    assert sign_cartridge.verify_manifest(tampered_path, pub) is False
