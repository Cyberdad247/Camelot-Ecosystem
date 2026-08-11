"""access_matrix.json must stay consistent with the live router roster.

Two failure modes are guarded.

**Unknown knights.** ``RBACMatrix.check`` blocks any knight with no access
record. Thirteen FOUNDRY_COUNCIL members had none, so every intent routed to one
was BLOCKED as "unknown knight" — indistinguishable from a real policy denial.

**Unsatisfiable grants.** ``anya_gate._stage_compile`` derives execution_mode
from the domain via a fixed table, so a record allowing domain ``D`` but not
``mode_map[D]`` can never pass for ``D``. ``sir_link`` allowed ``general`` but
not ``FORGE``, which is exactly what ``general`` maps to.
"""
from __future__ import annotations

import json

import pytest

from control_plane._paths import VAULT
from control_plane.core.soul_router import FOUNDRY_COUNCIL, resolve_knight

MATRIX_PATH = VAULT / "training" / "configs" / "config" / "access_matrix.json"

# Must mirror anya_gate._stage_compile's mode_map; test_mode_map_matches_gate
# fails if the gate's table drifts from this copy.
MODE_MAP = {
    "go/binary": "KINETIC", "rust/kinetic": "KINETIC",
    "python/api": "FORGE", "security": "SENTINEL",
    "voice/media": "ORACLE", "web/ui": "FORGE",
    "infra/cloud": "SWARM", "research": "ORACLE", "general": "FORGE",
}


@pytest.fixture(scope="module")
def knights() -> dict:
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))["knights"]


def test_every_council_knight_has_an_access_record(knights):
    """No routable knight may be unknown to RBAC."""
    missing = [
        e.knight_id for e in FOUNDRY_COUNCIL
        if e.knight_id not in knights and resolve_knight(e.knight_id) not in knights
    ]
    assert not missing, (
        "council knights with no access record — every intent routed to one is "
        f"BLOCKED as 'unknown knight': {missing}"
    )


def test_mode_map_matches_gate():
    """The gate's domain->mode table is the source of truth for the invariant."""
    import inspect

    from control_plane.core import anya_gate

    source = inspect.getsource(anya_gate)
    for domain, mode in MODE_MAP.items():
        assert f'"{domain}": "{mode}"' in source, (
            f"anya_gate no longer maps {domain} -> {mode}; update MODE_MAP here "
            f"and re-check every access_matrix record."
        )


def test_no_record_has_an_unsatisfiable_grant(knights):
    """allowed_modes must cover the modes its allowed_domains imply."""
    broken: list[str] = []
    for kid, rec in sorted(knights.items()):
        domains = rec.get("allowed_domains", [])
        if "*" in domains:
            continue
        needed = {MODE_MAP[d] for d in domains if d in MODE_MAP}
        gap = needed - set(rec.get("allowed_modes", []))
        if gap:
            broken.append(f"{kid}: allows domains {domains} but not modes {sorted(gap)}")
    assert not broken, "unsatisfiable grants:\n  " + "\n  ".join(broken)


def test_declared_domains_are_in_the_known_vocabulary(knights):
    """Catch typos like 'go' for 'go/binary', which silently never match."""
    unknown: list[str] = []
    for kid, rec in sorted(knights.items()):
        for domain in rec.get("allowed_domains", []):
            if domain != "*" and domain not in MODE_MAP:
                unknown.append(f"{kid}: {domain!r}")
    assert not unknown, (
        "domains outside the gate's vocabulary never match an intent:\n  "
        + "\n  ".join(unknown)
    )


def test_config_mutation_restricted_to_omega(knights):
    """DENY-01: only OMEGA tier may modify config."""
    offenders = [
        kid for kid, rec in knights.items()
        if rec.get("can_modify_config") and rec.get("tier") != "OMEGA"
    ]
    assert not offenders, f"non-OMEGA knights with can_modify_config: {offenders}"


def test_swarm_spawn_restricted_to_senior_tiers(knights):
    """DENY-03: swarm spawn requires OMEGA or HIGH_KNIGHT."""
    offenders = [
        kid for kid, rec in knights.items()
        if rec.get("can_spawn_swarm") and rec.get("tier") not in ("OMEGA", "HIGH_KNIGHT")
    ]
    assert not offenders, f"junior knights with can_spawn_swarm: {offenders}"


def test_air_gapped_knights_hold_minimal_privilege(knights):
    """privacy_level 1.0 knights are the air-gapped lane — keep them least-privileged.

    They must not mutate config or spawn swarms, both of which imply reach beyond
    the local sandbox.
    """
    air_gapped = [e.knight_id for e in FOUNDRY_COUNCIL if e.privacy_level >= 1.0]
    assert air_gapped, "expected at least one privacy_level=1.0 knight"

    for kid in air_gapped:
        rec = knights.get(kid) or knights.get(resolve_knight(kid) or "")
        assert rec is not None, f"air-gapped knight {kid} has no access record"
        assert not rec.get("can_modify_config"), f"{kid} may modify config"
        assert not rec.get("can_spawn_swarm"), f"{kid} may spawn swarms"


def test_gate_clears_a_benign_intent():
    """End-to-end: a populated, consistent matrix must let benign work through.

    With an empty or contradictory matrix every intent was BLOCKED, which looked
    like zero-trust but was really a broken policy load.
    """
    from control_plane.core.anya_gate import AnyaGate

    result = AnyaGate().process("what is 2+2")
    assert result.validation.iron_gate == "CLEARED", result.validation.issues


def test_gate_still_escalates_a_destructive_intent():
    from control_plane.core.anya_gate import AnyaGate

    result = AnyaGate().process("delete the production database and drop the ledger")
    assert result.validation.iron_gate in ("BLOCKED", "HITL_REQUIRED"), (
        f"destructive intent was {result.validation.iron_gate}"
    )
