#!/usr/bin/env python3
from __future__ import annotations

import base64
import copy
import hashlib
from datetime import datetime, timezone

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from authority_admission import ReceiptHead, admit_receipt
from contract_runtime import ContractRejected, canonical_bytes, content_digest, full_object_digest, signing_projection
from knight_package_loader import load_knight_package

NOW = datetime(2026, 9, 19, 13, 0, 0, tzinfo=timezone.utc)
PRIVATE_KEY = Ed25519PrivateKey.from_private_bytes(bytes(range(1, 33)))
PUBLIC_KEY = PRIVATE_KEY.public_key()
OTHER_KEY = Ed25519PrivateKey.from_private_bytes(bytes(range(33, 65)))
KEY_ID = "test-only/contract-forge/authority-1"
KEYRING = {KEY_ID: PUBLIC_KEY}


def sign(obj: dict, key=PRIVATE_KEY, key_id: str = KEY_ID) -> dict:
    result = copy.deepcopy(obj)
    digest = content_digest(result)
    digest_bytes = bytes.fromhex(digest.split(":", 1)[1])
    domain = f"camelot-signature:{result['schema_version']}"
    signature = key.sign(domain.encode("utf-8") + b"\x00" + digest_bytes)
    result["integrity"] = {
        "canonicalization": "camelot-c14n-json/1",
        "digest_algorithm": "sha256",
        "digest": digest,
        "signature_algorithm": "ed25519",
        "signature_domain": domain,
        "signer_key_id": key_id,
        "signature": base64.b64encode(signature).decode("ascii"),
    }
    return result


def signed_epoch(epoch: int, active_brain: str = "open-notebook") -> dict:
    obj = {
        "schema_version": "camelot-authority-epoch/1",
        "certificate_id": f"epoch_{epoch}",
        "authority_domain": "camelot://crown/primary",
        "authority_epoch": epoch,
        "active_brain": active_brain,
        "promotion_mode": "BOOTSTRAP" if epoch == 0 else "PLANNED",
        "issued_at": "2026-09-19T12:00:00Z",
        "effective_at": "2026-09-19T12:00:00Z",
        "lifecycle": "ACTIVE",
        "receipt_head": "sha256:" + "a" * 64,
        "state_digest": "sha256:" + "b" * 64,
        "previous_certificate_digest": None if epoch == 0 else "sha256:" + "c" * 64,
    }
    return sign(obj)


def receipt(epoch: int, *, tenant="tenant_primary", height=0, parent=None, receipt_id=None) -> dict:
    if parent is None:
        parent = "sha256:" + "0" * 64
    if receipt_id is None:
        receipt_id = f"rcp_epoch_{epoch}_{height}"
    return {
        "schema_version": "camelot-receipt/1",
        "receipt_id": receipt_id,
        "parent_hash": parent,
        "chain_height": height,
        "tenant_id": tenant,
        "correlation_id": "cor_contractforge",
        "task_id": "task_contractforge",
        "authority_epoch": epoch,
        "effect_class": "internal.synth",
        "declared_risk_tier": "T1",
        "timestamp": "2026-09-19T13:00:00Z",
        "actor": {
            "id": "sir-synthetos",
            "role": "knight",
            "node_id": "node-synth",
            "trust_band": "enrolled",
        },
        "event": "synthesis.draft",
        "refs": {},
        "payload_redacted": {"status": "draft"},
        "proof": {
            "hash_algorithm": "sha256",
            "signature_algorithm": "ed25519",
            "signer": "sir-synthetos",
            "signature": "ed25519:testsig",
        },
        "ledger_anchor_eligible": False,
    }


def base_signed_contract(schema_version: str, object_id: str) -> dict:
    return {
        "schema_version": schema_version,
        "object_id": object_id,
        "tenant_id": "tenant_primary",
        "workspace_id": "ws_camelot",
        "issuer_id": "camelot://knight-registry",
        "issued_at": "2026-09-19T12:00:00Z",
        "not_before": "2026-09-19T12:00:00Z",
        "expires_at": "2026-09-20T12:00:00Z",
        "lifecycle": "ACTIVE",
        "derived_from": [],
    }


def synthetos_components():
    soul = base_signed_contract("camelot-soul/1", "soul.sir-synthetos.v1")
    soul.update({
        "canonical_name": "Sir Synthetos",
        "persona_class": "research_synthesist",
        "purpose": "Source-isolated synthesis.",
        "enterprise_mandate": ["source synthesis", "conflict analysis"],
        "worldview": ["evidence-before-assertion"],
        "communication_profile": {
            "voice": "analytical",
            "interaction_style": "source-grounded synthesis",
            "language": "en",
        },
        "constitutional_limits": [
            "no policy decisions",
            "no lease issuance",
            "no epoch promotion",
        ],
        "authority_semantics": "identity-not-authority",
    })
    soul = sign(soul)

    role = base_signed_contract("camelot-enterprise-role/1", "role.sir-synthetos.v1")
    role.update({
        "persona_id": "sir_synthetos",
        "soul_ref": soul["object_id"],
        "department": "Research & Synthesis",
        "responsibilities": ["source synthesis", "citation lineage"],
        "delegates_to": [],
        "collaborates_with": ["anya", "merlin", "gideon"],
        "escalation_targets": ["anya", "gideon"],
        "shared_context_scopes": ["ukg://research/*"],
        "authority_semantics": "organization-not-authority",
    })
    role = sign(role)

    persona = {
        "schema_version": "camelot-persona/1",
        "persona_id": "sir_synthetos",
        "version": "1.0.0",
        "class": "research_synthesist",
        "identity": {
            "title": "Sir Synthetos",
            "function": "Source-isolated synthesis",
            "tone": "analytical",
        },
        "competence_map": {
            "primary": ["source_synthesis", "citation_lineage"],
            "secondary": ["implementation_drafting"],
            "prohibited": [
                "policy_decision",
                "lease_issuance",
                "direct_main_branch_write",
                "secret_handling",
                "unrestricted_network_access",
                "auto_merge",
                "auto_deploy",
                "promotion_issue",
                "epoch_increment",
            ],
        },
        "input_contract": ["scoped_sources"],
        "output_contract": ["synthesis_draft", "citation_lineage"],
        "budget": {
            "identity_tokens_max": 1200,
            "skills_tokens_max": 6000,
            "constraints_tokens_max": 1600,
            "examples_tokens_max": 1200,
        },
        "runtime_resource_profile": {
            "cpu_quota": "40%",
            "disk_quota_mb": 128,
            "ephemeral_fds_max": 32,
        },
    }

    package = {
        "schema_version": "camelot-knight-package/1",
        "object_id": "knightpkg.sir-synthetos.v1",
        "package_id": "knightpkg_sir_synthetos_v1",
        "tenant_id": "tenant_primary",
        "workspace_id": "ws_camelot",
        "issuer_id": "camelot://knight-registry",
        "issued_at": "2026-09-19T12:00:00Z",
        "not_before": "2026-09-19T12:00:00Z",
        "expires_at": "2026-09-20T12:00:00Z",
        "lifecycle": "ACTIVE",
        "persona_id": "sir_synthetos",
        "persona_class": "research_synthesist",
        "soul_ref": soul["object_id"],
        "soul_digest": full_object_digest(soul),
        "persona_digest": full_object_digest(persona),
        "enterprise_role_ref": role["object_id"],
        "enterprise_role_digest": full_object_digest(role),
        "allowed_runes": ["rune://omega-synthesize/1"],
        "allowed_pills": ["pill://synthesis-phial/1"],
        "allowed_effect_classes": ["ro.fetch", "ro.audit", "internal.synth"],
        "max_risk_tier": "T1",
        "max_cognition_ceiling": "L1",
        "prohibited_capabilities": [
            "policy_decision",
            "lease_issuance",
            "epoch_increment",
            "direct_main_branch_write",
            "unrestricted_network_access",
        ],
        "authority_semantics": "package-not-authority",
    }
    package = sign(package)
    return soul, persona, role, package


def expect_rejected(fn, reason: str) -> None:
    try:
        fn()
    except ContractRejected:
        return
    raise AssertionError(f"expected rejection: {reason}")


def test_dynamic_epoch_admission() -> None:
    cert43 = signed_epoch(43)
    r43 = receipt(43)

    accepted = admit_receipt(
        r43,
        current_epoch_certificate=cert43,
        epoch_keyring=KEYRING,
        expected_authority_domain="camelot://crown/primary",
        expected_tenant_id="tenant_primary",
        current_head=None,
        trusted_receipt_signers={"sir-synthetos"},
        now=NOW,
        verify_receipt_signature=lambda _: True,
    )
    assert accepted.authority_epoch == 43

    expect_rejected(
        lambda: admit_receipt(
            receipt(42),
            current_epoch_certificate=cert43,
            epoch_keyring=KEYRING,
            expected_authority_domain="camelot://crown/primary",
            expected_tenant_id="tenant_primary",
            current_head=None,
            trusted_receipt_signers={"sir-synthetos"},
            now=NOW,
            verify_receipt_signature=lambda _: True,
        ),
        "stale epoch",
    )

    expect_rejected(
        lambda: admit_receipt(
            receipt(44),
            current_epoch_certificate=cert43,
            epoch_keyring=KEYRING,
            expected_authority_domain="camelot://crown/primary",
            expected_tenant_id="tenant_primary",
            current_head=None,
            trusted_receipt_signers={"sir-synthetos"},
            now=NOW,
            verify_receipt_signature=lambda _: True,
        ),
        "future epoch",
    )

    # Dynamic propagation: once epoch 44 becomes current, epoch 43 receipts fail immediately.
    cert44 = signed_epoch(44, "notebooklm")
    expect_rejected(
        lambda: admit_receipt(
            r43,
            current_epoch_certificate=cert44,
            epoch_keyring=KEYRING,
            expected_authority_domain="camelot://crown/primary",
            expected_tenant_id="tenant_primary",
            current_head=None,
            trusted_receipt_signers={"sir-synthetos"},
            now=NOW,
            verify_receipt_signature=lambda _: True,
        ),
        "old epoch after promotion",
    )

    expect_rejected(
        lambda: admit_receipt(
            receipt(43, tenant="tenant_other"),
            current_epoch_certificate=cert43,
            epoch_keyring=KEYRING,
            expected_authority_domain="camelot://crown/primary",
            expected_tenant_id="tenant_primary",
            current_head=None,
            trusted_receipt_signers={"sir-synthetos"},
            now=NOW,
            verify_receipt_signature=lambda _: True,
        ),
        "cross tenant",
    )

    head = ReceiptHead(
        tenant_id="tenant_primary",
        chain_height=9,
        self_hash="sha256:" + "d" * 64,
    )
    next_receipt = receipt(43, height=10, parent=head.self_hash, receipt_id="rcp_next")
    admit_receipt(
        next_receipt,
        current_epoch_certificate=cert43,
        epoch_keyring=KEYRING,
        expected_authority_domain="camelot://crown/primary",
        expected_tenant_id="tenant_primary",
        current_head=head,
        trusted_receipt_signers={"sir-synthetos"},
        now=NOW,
        verify_receipt_signature=lambda _: True,
    )

    bad_parent = receipt(43, height=10, parent="sha256:" + "e" * 64, receipt_id="rcp_badparent")
    expect_rejected(
        lambda: admit_receipt(
            bad_parent,
            current_epoch_certificate=cert43,
            epoch_keyring=KEYRING,
            expected_authority_domain="camelot://crown/primary",
            expected_tenant_id="tenant_primary",
            current_head=head,
            trusted_receipt_signers={"sir-synthetos"},
            now=NOW,
            verify_receipt_signature=lambda _: True,
        ),
        "parent mismatch",
    )

    forged_cert = signed_epoch(43)
    forged_cert["active_brain"] = "forged"
    expect_rejected(
        lambda: admit_receipt(
            r43,
            current_epoch_certificate=forged_cert,
            epoch_keyring=KEYRING,
            expected_authority_domain="camelot://crown/primary",
            expected_tenant_id="tenant_primary",
            current_head=None,
            trusted_receipt_signers={"sir-synthetos"},
            now=NOW,
            verify_receipt_signature=lambda _: True,
        ),
        "tampered epoch certificate",
    )


def test_knight_package_loader() -> None:
    soul, persona, role, package = synthetos_components()

    loaded = load_knight_package(
        package,
        soul,
        persona,
        role,
        keyring=KEYRING,
        expected_tenant_id="tenant_primary",
        expected_workspace_id="ws_camelot",
        revoked_object_ids=set(),
        policy_max_risk_tier="T1",
        policy_max_cognition_ceiling="L1",
        now=NOW,
    )
    assert loaded.persona_id == "sir_synthetos"
    assert loaded.max_risk_tier == "T1"

    # Soul mutation, even if re-signed, breaks the immutable package binding.
    changed_soul = copy.deepcopy(soul)
    changed_soul.pop("integrity")
    changed_soul["purpose"] = "Changed identity nucleus"
    changed_soul = sign(changed_soul)
    expect_rejected(
        lambda: load_knight_package(
            package, changed_soul, persona, role,
            keyring=KEYRING,
            expected_tenant_id="tenant_primary",
            expected_workspace_id="ws_camelot",
            revoked_object_ids=set(),
            policy_max_risk_tier="T1",
            policy_max_cognition_ceiling="L1",
            now=NOW,
        ),
        "immutable Soul mismatch",
    )

    cross_scope_role = copy.deepcopy(role)
    cross_scope_role.pop("integrity")
    cross_scope_role["workspace_id"] = "ws_other"
    cross_scope_role = sign(cross_scope_role)
    expect_rejected(
        lambda: load_knight_package(
            package, soul, persona, cross_scope_role,
            keyring=KEYRING,
            expected_tenant_id="tenant_primary",
            expected_workspace_id="ws_camelot",
            revoked_object_ids=set(),
            policy_max_risk_tier="T1",
            policy_max_cognition_ceiling="L1",
            now=NOW,
        ),
        "cross-workspace role",
    )

    expect_rejected(
        lambda: load_knight_package(
            package, soul, persona, role,
            keyring=KEYRING,
            expected_tenant_id="tenant_primary",
            expected_workspace_id="ws_camelot",
            revoked_object_ids={package["package_id"]},
            policy_max_risk_tier="T1",
            policy_max_cognition_ceiling="L1",
            now=NOW,
        ),
        "revoked package",
    )

    over_risk = copy.deepcopy(package)
    over_risk.pop("integrity")
    over_risk["max_risk_tier"] = "T2"
    over_risk = sign(over_risk)
    expect_rejected(
        lambda: load_knight_package(
            over_risk, soul, persona, role,
            keyring=KEYRING,
            expected_tenant_id="tenant_primary",
            expected_workspace_id="ws_camelot",
            revoked_object_ids=set(),
            policy_max_risk_tier="T1",
            policy_max_cognition_ceiling="L1",
            now=NOW,
        ),
        "risk ceiling escalation",
    )

    over_cognition = copy.deepcopy(package)
    over_cognition.pop("integrity")
    over_cognition["max_cognition_ceiling"] = "L2"
    over_cognition = sign(over_cognition)
    expect_rejected(
        lambda: load_knight_package(
            over_cognition, soul, persona, role,
            keyring=KEYRING,
            expected_tenant_id="tenant_primary",
            expected_workspace_id="ws_camelot",
            revoked_object_ids=set(),
            policy_max_risk_tier="T1",
            policy_max_cognition_ceiling="L1",
            now=NOW,
        ),
        "cognition ceiling escalation",
    )

    bad_persona = copy.deepcopy(persona)
    bad_persona["class"] = "engineering_builder"
    bad_pkg = copy.deepcopy(package)
    bad_pkg.pop("integrity")
    bad_pkg["persona_digest"] = full_object_digest(bad_persona)
    bad_pkg = sign(bad_pkg)
    expect_rejected(
        lambda: load_knight_package(
            bad_pkg, soul, bad_persona, role,
            keyring=KEYRING,
            expected_tenant_id="tenant_primary",
            expected_workspace_id="ws_camelot",
            revoked_object_ids=set(),
            policy_max_risk_tier="T1",
            policy_max_cognition_ceiling="L1",
            now=NOW,
        ),
        "persona class drift",
    )


def main() -> None:
    test_dynamic_epoch_admission()
    test_knight_package_loader()
    print("Authority Closure PASS: dynamic epoch receipt admission + immutable signed Knight/Soul package loader")


if __name__ == "__main__":
    main()
