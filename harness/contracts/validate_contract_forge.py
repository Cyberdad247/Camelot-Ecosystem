#!/usr/bin/env python3
from __future__ import annotations

import base64
import copy
import hashlib
import json
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "packages" / "contracts"

NEW_SCHEMAS = [
    "soul.schema.json",
    "enterprise-role.schema.json",
    "spark.schema.json",
    "rune.schema.json",
    "pill.schema.json",
    "memory-candidate.schema.json",
    "memory-object.schema.json",
    "effective-capability-set.schema.json",
]

FIXED_NOW = datetime(2026, 9, 19, 12, 0, 0, tzinfo=timezone.utc)
PRIVATE_KEY = Ed25519PrivateKey.from_private_bytes(bytes(range(1, 33)))
PUBLIC_KEY = PRIVATE_KEY.public_key()


def load_schema(name: str) -> dict:
    with (SCHEMA_DIR / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def normalize(value):
    if isinstance(value, float):
        raise TypeError("camelot-c14n-json/1 forbids floating-point values")
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [normalize(v) for v in value]
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            nk = unicodedata.normalize("NFC", k)
            out[nk] = normalize(v)
        return out
    return value


def canonical_bytes(value: dict) -> bytes:
    normalized = normalize(value)
    return json.dumps(
        normalized,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")


def signing_projection(obj: dict) -> dict:
    return {k: copy.deepcopy(v) for k, v in obj.items() if k != "integrity"}


def sign(obj: dict) -> dict:
    result = copy.deepcopy(obj)
    projection = signing_projection(result)
    digest_bytes = hashlib.sha256(canonical_bytes(projection)).digest()
    digest = "sha256:" + digest_bytes.hex()
    domain = f"camelot-signature:{result['schema_version']}"
    signature_input = domain.encode("utf-8") + b"\x00" + digest_bytes
    signature = PRIVATE_KEY.sign(signature_input)
    result["integrity"] = {
        "canonicalization": "camelot-c14n-json/1",
        "digest_algorithm": "sha256",
        "digest": digest,
        "signature_algorithm": "ed25519",
        "signature_domain": domain,
        "signer_key_id": "test-only/contract-forge/ed25519-1",
        "signature": base64.b64encode(signature).decode("ascii"),
    }
    return result


def validate_schema(obj: dict, schema_name: str) -> None:
    schema = load_schema(schema_name)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(obj)


def verify_signed(obj: dict, schema_name: str, accepted_lifecycles: set[str]) -> None:
    validate_schema(obj, schema_name)
    integ = obj["integrity"]
    projection = signing_projection(obj)
    digest_bytes = hashlib.sha256(canonical_bytes(projection)).digest()
    expected_digest = "sha256:" + digest_bytes.hex()
    assert integ["digest"] == expected_digest, "digest mismatch"

    expected_domain = f"camelot-signature:{obj['schema_version']}"
    assert integ["signature_domain"] == expected_domain, "signature domain mismatch"
    signature_input = expected_domain.encode("utf-8") + b"\x00" + digest_bytes
    PUBLIC_KEY.verify(base64.b64decode(integ["signature"]), signature_input)

    start = datetime.fromisoformat(obj["not_before"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(obj["expires_at"].replace("Z", "+00:00"))
    assert start <= FIXED_NOW < end, "object outside validity window"
    assert obj["lifecycle"] in accepted_lifecycles, "lifecycle not admissible"


def base(schema_version: str, object_id: str, lifecycle: str = "ACTIVE") -> dict:
    return {
        "schema_version": schema_version,
        "object_id": object_id,
        "tenant_id": "tenant_primary",
        "workspace_id": "ws_camelot",
        "issuer_id": "camelot://contract-forge/test-issuer",
        "issued_at": "2026-09-19T11:00:00Z",
        "not_before": "2026-09-19T11:00:00Z",
        "expires_at": "2026-09-20T11:00:00Z",
        "lifecycle": lifecycle,
        "derived_from": [],
    }


def synthetos_objects():
    soul = base("camelot-soul/1", "soul.sir-synthetos.v1")
    soul.update({
        "canonical_name": "Sir Synthetos",
        "persona_class": "research_synthesist",
        "purpose": "Source-isolated synthesis for implementation-oriented enterprise research.",
        "enterprise_mandate": [
            "isolate sources",
            "extract claims and provenance",
            "identify intersections and conflicts",
            "produce implementation-oriented synthesis drafts",
        ],
        "worldview": ["evidence-before-assertion", "human-agency-first", "authority-outside-models"],
        "communication_profile": {
            "voice": "analytical and implementation-oriented",
            "interaction_style": "source-grounded synthesis",
            "language": "en",
        },
        "constitutional_limits": [
            "no policy decisions",
            "no lease issuance",
            "no epoch promotion",
            "no canonical memory activation",
            "no external effects without Sentinel authorization",
        ],
        "authority_semantics": "identity-not-authority",
    })

    role = base("camelot-enterprise-role/1", "role.sir-synthetos.v1")
    role.update({
        "persona_id": "sir_synthetos",
        "soul_ref": "soul.sir-synthetos.v1",
        "department": "Research & Synthesis",
        "responsibilities": ["source synthesis", "conflict analysis", "citation lineage", "draft generation"],
        "delegates_to": [],
        "collaborates_with": ["anya", "merlin", "gideon"],
        "escalation_targets": ["anya", "gideon"],
        "shared_context_scopes": ["ukg://research/*", "ukg://architecture/*"],
        "authority_semantics": "organization-not-authority",
    })

    spark = base("camelot-spark/1", "spark.sir-synthetos.q1")
    spark.update({
        "persona_id": "sir_synthetos",
        "soul_ref": "soul.sir-synthetos.v1",
        "quest_ref": "quest://contract-forge/1",
        "task_ref": "task://synthesis/1",
        "context_sources": [
            {"ref": "ukg://architecture/camelot", "trust_class": "SIGNED_UKG"}
        ],
        "token_budget": {"total_tokens": 32000, "scratch_reserve_tokens": 4000},
        "allowed_runes": ["rune://omega-synthesize/1"],
        "allowed_pills": ["pill://synthesis-phial/1"],
        "cognition_ceiling": "L1",
        "authority_semantics": "context-not-authority",
    })

    rune = base("camelot-rune/1", "rune.omega-synthesize.v1")
    rune.update({
        "rune_id": "omega-synthesize",
        "name": "Ω_SYNTHESIZE",
        "steps": [
            {"id": "survey", "operation": "survey scoped sources", "requires": []},
            {"id": "isolate", "operation": "isolate sources", "requires": ["survey"]},
            {"id": "extract", "operation": "extract claims and provenance", "requires": ["isolate"]},
            {"id": "intersections", "operation": "analyze intersections", "requires": ["extract"]},
            {"id": "conflicts", "operation": "analyze conflicts", "requires": ["extract"]},
            {"id": "synthesize", "operation": "synthesize implementation draft", "requires": ["intersections", "conflicts"]},
        ],
        "expected_outputs": ["source lineage", "conflict map", "synthesis draft"],
        "failure_policy": "ESCALATE",
        "grants_capabilities": False,
        "authority_semantics": "procedure-not-authority",
    })

    pill = base("camelot-pill/1", "pill.synthesis-phial.v1")
    pill.update({
        "pill_id": "synthesis-phial",
        "name": "Synthesis Phial",
        "module_digest": None,
        "allowed_tools": ["ukg.retrieve", "source.read", "source.parse", "citation.extract", "draft.write.shadow"],
        "forbidden_tools": [
            "policy.write", "lease.issue", "epoch.promote", "memory.activate",
            "vfs.canonical.write", "network.unrestricted", "device.control",
        ],
        "resource_limits": {
            "max_actions": 64,
            "max_memory_mb": 384,
            "timeout_s": 600,
            "network_mode": "disabled",
        },
        "cognition_ceiling": "L1",
        "authority_semantics": "ceiling-not-grant",
    })

    candidate = base("camelot-memory-candidate/1", "memory-candidate.synthetos.lesson1", "CANDIDATE")
    candidate.update({
        "subject_ref": "persona://sir_synthetos",
        "memory_class": "enterprise",
        "content": {"lesson": "Keep source conflicts explicit until resolution."},
        "trust_class": "AGENT_GENERATED",
        "provenance_refs": ["quest://contract-forge/1", "receipt://draft/1"],
        "activation_allowed": False,
        "authority_semantics": "memory-never-authority",
    })

    memory = base("camelot-memory-object/1", "memory.synthetos.lesson1", "ACTIVE")
    memory.update({
        "subject_ref": "persona://sir_synthetos",
        "memory_class": "enterprise",
        "content_digest": "sha256:" + "1" * 64,
        "candidate_digest": "sha256:" + "2" * 64,
        "gideon_verdict_ref": "gideon://verdict/1",
        "arthur_resolution_ref": "arthur://resolution/1",
        "activation_receipt_ref": "receipt://memory/activation/1",
        "authority_semantics": "memory-never-authority",
    })

    effective = base("camelot-effective-capability-set/1", "caps.synthetos.q1")
    effective.update({
        "authority_epoch": 42,
        "lease_ref": "lease://synthetos/q1",
        "effect_manifest_hash": "sha256:" + "3" * 64,
        "subject_ref": "persona://sir_synthetos",
        "risk_tier": "T0",
        "cognition_ceiling": "L1",
        "capabilities": ["ukg.retrieve", "source.read", "source.parse", "citation.extract", "draft.write.shadow"],
        "resource_scopes": {
            "vfs_read": ["/ukg/architecture/*"],
            "vfs_write": ["/shadow/drafts/*"],
            "network": [],
        },
        "source_constraints": [
            {"kind": "policy", "ref": "policy://tenant-primary/current", "digest": "sha256:" + "4" * 64},
            {"kind": "persona", "ref": "persona://sir_synthetos", "digest": "sha256:" + "5" * 64},
            {"kind": "spark", "ref": "spark://sir-synthetos/q1", "digest": "sha256:" + "6" * 64},
            {"kind": "pill", "ref": "pill://synthesis-phial/1", "digest": "sha256:" + "7" * 64},
            {"kind": "lease", "ref": "lease://synthetos/q1", "digest": "sha256:" + "8" * 64},
            {"kind": "effect-manifest", "ref": "effect://synthetos/q1", "digest": "sha256:" + "9" * 64},
        ],
        "authority_semantics": "compiled-authority-not-source-of-authority",
    })

    return soul, role, spark, rune, pill, candidate, memory, effective


def validate_existing_persona_contract() -> None:
    persona = {
        "schema_version": "camelot-persona/1",
        "persona_id": "sir_synthetos",
        "version": "1.0.0",
        "class": "research_synthesist",
        "identity": {
            "title": "Sir Synthetos",
            "function": "Source-isolated synthesis and conflict/intersection analysis",
            "tone": "analytical and implementation-oriented",
        },
        "competence_map": {
            "primary": ["source_synthesis", "conflict_analysis", "citation_lineage"],
            "secondary": ["implementation_drafting"],
            "prohibited": [
                "policy_decision", "lease_issuance", "direct_main_branch_write",
                "secret_handling", "unrestricted_network_access", "auto_merge",
                "auto_deploy", "promotion_issue", "epoch_increment",
            ],
        },
        "input_contract": ["scoped_sources", "quest_context"],
        "output_contract": ["synthesis_draft", "citation_lineage", "conflict_map"],
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
    validate_schema(persona, "persona.schema.json")


def effective_ceiling(levels: list[str]) -> str:
    rank = {f"L{i}": i for i in range(6)}
    return min(levels, key=lambda x: rank[x])


def expect_validation_failure(obj: dict, schema_name: str) -> None:
    try:
        validate_schema(obj, schema_name)
    except ValidationError:
        return
    raise AssertionError(f"{schema_name}: expected schema rejection")


def main() -> None:
    for name in NEW_SCHEMAS:
        Draft202012Validator.check_schema(load_schema(name))

    validate_existing_persona_contract()

    objects = synthetos_objects()
    pairs = [
        (objects[0], "soul.schema.json", {"ACTIVE"}),
        (objects[1], "enterprise-role.schema.json", {"ACTIVE"}),
        (objects[2], "spark.schema.json", {"ACTIVE"}),
        (objects[3], "rune.schema.json", {"ACTIVE"}),
        (objects[4], "pill.schema.json", {"ACTIVE"}),
        (objects[5], "memory-candidate.schema.json", {"CANDIDATE"}),
        (objects[6], "memory-object.schema.json", {"ACTIVE"}),
        (objects[7], "effective-capability-set.schema.json", {"ACTIVE"}),
    ]

    signed = []
    for obj, schema_name, lifecycles in pairs:
        s = sign(obj)
        verify_signed(s, schema_name, lifecycles)
        signed.append((s, schema_name, lifecycles))

    # Deterministic canonicalization: dict insertion order does not matter.
    shuffled = dict(reversed(list(signing_projection(signed[0][0]).items())))
    assert canonical_bytes(shuffled) == canonical_bytes(signing_projection(signed[0][0]))

    # Any mutation invalidates digest/signature.
    mutated = copy.deepcopy(signed[0][0])
    mutated["canonical_name"] = "Tampered Synthetos"
    try:
        verify_signed(mutated, "soul.schema.json", {"ACTIVE"})
    except (AssertionError, InvalidSignature):
        pass
    else:
        raise AssertionError("content mutation was accepted")

    # Tenant/workspace substitution is cryptographically bound and must fail.
    cross_tenant = copy.deepcopy(signed[0][0])
    cross_tenant["tenant_id"] = "tenant_other"
    try:
        verify_signed(cross_tenant, "soul.schema.json", {"ACTIVE"})
    except (AssertionError, InvalidSignature):
        pass
    else:
        raise AssertionError("cross-tenant substitution was accepted")

    # Unknown schema family/version rejects by schema const.
    unknown = copy.deepcopy(signed[0][0])
    unknown["schema_version"] = "camelot-soul/999"
    expect_validation_failure(unknown, "soul.schema.json")

    # Validly signed but expired object is still rejected.
    expired = copy.deepcopy(objects[0])
    expired["expires_at"] = "2026-09-18T11:00:00Z"
    expired_signed = sign(expired)
    try:
        verify_signed(expired_signed, "soul.schema.json", {"ACTIVE"})
    except AssertionError:
        pass
    else:
        raise AssertionError("expired signed object was accepted")

    # Validly signed revoked object is still rejected by lifecycle admission.
    revoked = copy.deepcopy(objects[0])
    revoked["lifecycle"] = "REVOKED"
    revoked_signed = sign(revoked)
    try:
        verify_signed(revoked_signed, "soul.schema.json", {"ACTIVE"})
    except AssertionError:
        pass
    else:
        raise AssertionError("revoked signed object was accepted")

    # Signature from an untrusted/different key cannot verify under the pinned key.
    other_key = Ed25519PrivateKey.from_private_bytes(bytes(range(33, 65)))
    invalid_signer = copy.deepcopy(signed[0][0])
    digest_bytes = bytes.fromhex(invalid_signer["integrity"]["digest"].split(":", 1)[1])
    domain = invalid_signer["integrity"]["signature_domain"]
    invalid_signer["integrity"]["signature"] = base64.b64encode(
        other_key.sign(domain.encode("utf-8") + b"\x00" + digest_bytes)
    ).decode("ascii")
    try:
        verify_signed(invalid_signer, "soul.schema.json", {"ACTIVE"})
    except InvalidSignature:
        pass
    else:
        raise AssertionError("invalid signer was accepted")

    # Runes cannot become capability grants.
    bad_rune = copy.deepcopy(objects[3])
    bad_rune["grants_capabilities"] = True
    bad_rune["integrity"] = sign(bad_rune)["integrity"]
    expect_validation_failure(bad_rune, "rune.schema.json")

    # Candidate memory cannot masquerade as active memory.
    bad_candidate = copy.deepcopy(objects[5])
    bad_candidate["lifecycle"] = "ACTIVE"
    bad_candidate["integrity"] = sign(bad_candidate)["integrity"]
    expect_validation_failure(bad_candidate, "memory-candidate.schema.json")

    # Active memory structurally requires Gideon + Arthur + receipt lineage.
    bad_memory = sign(copy.deepcopy(objects[6]))
    del bad_memory["gideon_verdict_ref"]
    expect_validation_failure(bad_memory, "memory-object.schema.json")

    # Ceiling attenuation always chooses the most restrictive layer.
    assert effective_ceiling(["L4", "L1", "L3", "L2"]) == "L1"

    print("Contract Forge PASS: 8 new schemas + Synthetos persona continuity + signing/scope/lifecycle/attenuation/memory gates")


if __name__ == "__main__":
    main()
