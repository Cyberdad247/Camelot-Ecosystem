from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from contract_runtime import ContractRejected, full_object_digest, validate_schema, verify_signed


RISK_RANK = {f"T{i}": i for i in range(5)}
COGNITION_RANK = {f"L{i}": i for i in range(6)}


@dataclass(frozen=True)
class LoadedKnight:
    package_id: str
    persona_id: str
    persona_class: str
    tenant_id: str
    workspace_id: str
    max_risk_tier: str
    max_cognition_ceiling: str
    allowed_effect_classes: tuple[str, ...]
    allowed_runes: tuple[str, ...]
    allowed_pills: tuple[str, ...]


def load_knight_package(
    package: dict,
    soul: dict,
    persona: dict,
    enterprise_role: dict,
    *,
    keyring: Mapping[str, Ed25519PublicKey],
    expected_tenant_id: str,
    expected_workspace_id: str,
    revoked_object_ids: set[str],
    policy_max_risk_tier: str,
    policy_max_cognition_ceiling: str,
    now: datetime,
) -> LoadedKnight:
    verify_signed(
        package,
        "knight-package.schema.json",
        keyring,
        now=now,
        accepted_lifecycles={"ACTIVE"},
    )
    verify_signed(
        soul,
        "soul.schema.json",
        keyring,
        now=now,
        accepted_lifecycles={"ACTIVE"},
    )
    verify_signed(
        enterprise_role,
        "enterprise-role.schema.json",
        keyring,
        now=now,
        accepted_lifecycles={"ACTIVE"},
    )
    validate_schema(persona, "persona.schema.json")

    for obj in (package, soul, enterprise_role):
        if obj["tenant_id"] != expected_tenant_id or obj["workspace_id"] != expected_workspace_id:
            raise ContractRejected("package component scope mismatch")
        if obj["object_id"] in revoked_object_ids:
            raise ContractRejected("revoked package component")

    if package["package_id"] in revoked_object_ids:
        raise ContractRejected("revoked knight package")

    if package["soul_ref"] != soul["object_id"]:
        raise ContractRejected("soul reference mismatch")
    if package["enterprise_role_ref"] != enterprise_role["object_id"]:
        raise ContractRejected("enterprise role reference mismatch")

    if package["soul_digest"] != full_object_digest(soul):
        raise ContractRejected("immutable Soul digest mismatch")
    if package["persona_digest"] != full_object_digest(persona):
        raise ContractRejected("persona digest mismatch")
    if package["enterprise_role_digest"] != full_object_digest(enterprise_role):
        raise ContractRejected("enterprise role digest mismatch")

    persona_id = package["persona_id"]
    if persona["persona_id"] != persona_id or enterprise_role["persona_id"] != persona_id:
        raise ContractRejected("persona identity mismatch")
    if package["persona_class"] != persona["class"] or package["persona_class"] != soul["persona_class"]:
        raise ContractRejected("persona class mismatch")
    if enterprise_role["soul_ref"] != soul["object_id"]:
        raise ContractRejected("enterprise role not bound to Soul")

    prohibited = set(package["prohibited_capabilities"])
    persona_prohibited = set(persona["competence_map"]["prohibited"])
    required_guardrails = {
        "policy_decision","lease_issuance","direct_main_branch_write","secret_handling",
        "unrestricted_network_access","auto_merge","auto_deploy","promotion_issue","epoch_increment",
    }
    if not required_guardrails.issubset(persona_prohibited):
        raise ContractRejected("persona missing mandatory authority prohibitions")
    if not {
        "policy_decision","lease_issuance","epoch_increment"
    }.issubset(prohibited):
        raise ContractRejected("Knight package weakens authority prohibitions")

    if RISK_RANK[package["max_risk_tier"]] > RISK_RANK[policy_max_risk_tier]:
        raise ContractRejected("Knight package exceeds policy risk ceiling")
    if COGNITION_RANK[package["max_cognition_ceiling"]] > COGNITION_RANK[policy_max_cognition_ceiling]:
        raise ContractRejected("Knight package exceeds policy cognition ceiling")

    return LoadedKnight(
        package_id=package["package_id"],
        persona_id=persona_id,
        persona_class=package["persona_class"],
        tenant_id=package["tenant_id"],
        workspace_id=package["workspace_id"],
        max_risk_tier=package["max_risk_tier"],
        max_cognition_ceiling=package["max_cognition_ceiling"],
        allowed_effect_classes=tuple(package["allowed_effect_classes"]),
        allowed_runes=tuple(package["allowed_runes"]),
        allowed_pills=tuple(package["allowed_pills"]),
    )
