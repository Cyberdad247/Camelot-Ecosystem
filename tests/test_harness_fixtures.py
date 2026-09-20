# SPDX-License-Identifier: MIT

"""Harness fixture coverage gate.

Wires the 29 ``harness/fixtures/*/README.md`` security-behavior specs into
machine-checked test coverage. Each README is a fixture spec with a
``Verify:`` clause naming the production gate it must back. This module
enforces three layers:

1. STRUCTURE — every fixture directory has a well-formed README (title
   matching the directory, a scenario, a ``Verify:`` clause, and at least
   one ``§x.y`` section reference). A malformed README fails the gate.
2. MANIFEST — every fixture is classified into an evidence class with an
   explicit wiring target:

   - ``confirmed``: the fixture's Verify clause is exercised in this module
     against real code (today: the §11.3 receipt chain).
   - ``planned``: a real implementation exists in the tree but the exact
     verify gate is not yet wired into this module.
   - ``aspirational``: the README is a spec only — no implementation
     exists in the tree yet.

   Nothing is silently dropped: the manifest must cover exactly the
   fixture directories on disk.
3. WIRING — confirmed fixtures execute their Verify clause against
   ``harness/contracts/verify_receipt_chain.py`` (the pinned-key §11.3
   chain: self_hash, ed25519 signature, height continuity, parent linkage,
   epoch freshness, tenant binding via canonical serialization).

Evidence-class discipline follows the repository constitution: a fixture
is never claimed tested unless this module actually runs its check against
live code.
"""

from __future__ import annotations

import copy
import importlib.util
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = REPO_ROOT / "harness" / "fixtures"
VERIFY_RECEIPT_CHAIN = REPO_ROOT / "harness" / "contracts" / "verify_receipt_chain.py"

# ---------------------------------------------------------------------------
# Fixture discovery
# ---------------------------------------------------------------------------

EXPECTED_FIXTURES: tuple[str, ...] = (
    "VFS_path_escape",
    "VPS_network_partition",
    "cached_epoch_across_policy_bump",
    "cartridge_exceeding_risk_tier_invariant_cap",
    "cross_policy_namespace_cache_hit",
    "cross_tenant_cache_key",
    "cross_tenant_event_query",
    "duplicate_provider_webhook",
    "equota_promotion_with_witness_unreachable",
    "expired_effect_manifest",
    "forged_node_receipt",
    "forged_operator_request",
    "local_twin_promotion",
    "malformed_symbolect_tree",
    "mobile_epoch_window_expired",
    "mobile_permission_denied",
    "network_call_without_lease",
    "operator-console-approval",
    "operator-console-cancellation",
    "operator-console-integrity-failure",
    "operator-console-readonly-audit",
    "prohibited_process_execution",
    "prompt_injection_document",
    "receipt_parent_hash_tamper",
    "single_operator_t3_approval_attempt",
    "stale_authority_epoch",
    "unauthorized_persona_capability",
    "unauthorized_secret_handle",
    "untrusted_memory_promotion",
)

# Evidence manifest: fixture -> (evidence_class, wiring_target, reason).
# The wiring target names the check in this module (or the on-disk code)
# that backs the fixture's Verify clause.
FIXTURE_MANIFEST: dict[str, tuple[str, str, str]] = {
    "forged_node_receipt": (
        "confirmed",
        "check_forged_signature",
        "verify_chain rejects bad ed25519 signature / self_hash mismatch (§11.3)",
    ),
    "forged_operator_request": (
        "confirmed",
        "check_forged_operator_request",
        "verify_operator_request denies forged signature, stale cookie, replayed "
        "nonce, and missing MFA (§12.2, §13.1, §19.2)",
    ),
    "receipt_parent_hash_tamper": (
        "confirmed",
        "check_parent_hash_tamper",
        "verify_chain detects parent_hash rewrite via re-derivation + linkage (§11.3)",
    ),
    "stale_authority_epoch": (
        "confirmed",
        "check_stale_epoch",
        "verify_chain rejects authority_epoch below trusted (§6.3, §11.3 D-4)",
    ),
    "cross_tenant_event_query": (
        "planned",
        "check_tenant_binding",
        "receipt chain enforces tenant binding via canonical serialization (S-3); "
        "retrieval-denial layer is not implemented — chain side wired here",
    ),
    "malformed_symbolect_tree": (
        "planned",
        "01_KERNEL/merlin/Engines/symbolect_transpiler/symbolect.py",
        "SymbolectTranspiler exists (encode/decode/parse) but has no "
        "validation/rejection path; §17.3 gate not implemented",
    ),
    "operator-console-approval": (
        "confirmed",
        "check_operator_console_approval",
        "operator_console_gate.py ApprovalGate mirrors sentinel.ts verifyManifest/"
        "issueLease: approve issues lease, deny records denial (AC10–AC13)",
    ),
    "operator-console-cancellation": (
        "confirmed",
        "check_operator_console_cancellation",
        "operator_console_gate.py TaskController.cancel: cancellation receipt, "
        "lease revoked, workers stopped, workspace cleaned (AC20)",
    ),
    "operator-console-integrity-failure": (
        "confirmed",
        "check_operator_console_integrity_failure",
        "operator_console_gate.py detect_integrity_failure: INTEGRITY FAILED "
        "alert, approval disabled, record preserved (AC17–AC18)",
    ),
    "operator-console-readonly-audit": (
        "confirmed",
        "check_operator_console_readonly_audit",
        "operator_console_gate.py run_readonly_audit: real state, no-write "
        "receipt, no approval path (AC19)",
    ),
    "VFS_path_escape": (
        "aspirational",
        "",
        "no VFSGuardian / path-escape guard implementation in tree (§14.1, §14.3)",
    ),
    "VPS_network_partition": (
        "aspirational",
        "",
        "no failover/twin promotion implementation in tree (§6.4, §25.1)",
    ),
    "cached_epoch_across_policy_bump": (
        "aspirational",
        "",
        "no mobile epoch-cache implementation in tree (§10.3, §6.3)",
    ),
    "cartridge_exceeding_risk_tier_invariant_cap": (
        "aspirational",
        "",
        "no risk-tier invariant derivation in tree (§13.3, §8.2)",
    ),
    "cross_policy_namespace_cache_hit": (
        "aspirational",
        "",
        "no HMAC cache namespace implementation in tree (§15.6, §25.1)",
    ),
    "cross_tenant_cache_key": (
        "aspirational",
        "",
        "no HMAC cache namespace implementation in tree (§15.6)",
    ),
    "duplicate_provider_webhook": (
        "aspirational",
        "",
        "no provider webhook signature/dedupe implementation in tree (§20.x)",
    ),
    "equota_promotion_with_witness_unreachable": (
        "aspirational",
        "",
        "no witness-quorum failover implementation in tree (§6.5)",
    ),
    "expired_effect_manifest": (
        "aspirational",
        "",
        "no effect-manifest expiry enforcement in tree (§13.2)",
    ),

    "local_twin_promotion": (
        "aspirational",
        "",
        "no promotion/fencing controller implementation in tree (§6.4, §6.5)",
    ),
    "mobile_epoch_window_expired": (
        "aspirational",
        "",
        "no mobile epoch-window enforcement in tree (§10.3)",
    ),
    "mobile_permission_denied": (
        "aspirational",
        "",
        "no Android permission broker in tree (§10.1)",
    ),
    "network_call_without_lease": (
        "aspirational",
        "",
        "no network lease / egress boundary implementation in tree (§13.3)",
    ),
    "prohibited_process_execution": (
        "aspirational",
        "",
        "no native process supervisor in tree (§14.1)",
    ),
    "prompt_injection_document": (
        "aspirational",
        "",
        "no context-compiler stripping path in tree (§15.3)",
    ),
    "single_operator_t3_approval_attempt": (
        "aspirational",
        "",
        "no two-person-rule approval gate in tree (§5.5)",
    ),
    "unauthorized_persona_capability": (
        "aspirational",
        "",
        "no persona prohibited-capability compile gate in tree (§16, §13.3)",
    ),
    "unauthorized_secret_handle": (
        "aspirational",
        "",
        "no secret-broker handle authorization in tree (§14.3)",
    ),
    "untrusted_memory_promotion": (
        "aspirational",
        "",
        "no memory-promotion VFS/lease gate in tree (§15.1, §15.3)",
    ),
}

_CONFIRMED = {n for n, (cls, _, _) in FIXTURE_MANIFEST.items() if cls == "confirmed"}
_PLANNED = {n for n, (cls, _, _) in FIXTURE_MANIFEST.items() if cls == "planned"}
_ASPIRATIONAL = {n for n, (cls, _, _) in FIXTURE_MANIFEST.items() if cls == "aspirational"}

VERIFY_OPERATOR_REQUEST = REPO_ROOT / "harness" / "contracts" / "verify_operator_request.py"
OPERATOR_CONSOLE_GATE = REPO_ROOT / "harness" / "contracts" / "operator_console_gate.py"

_VERIFY_TOKEN_RE = re.compile(r"Verify:\s*(.+)$", re.MULTILINE)
# §x.y / §x.y.z section refs, the spec shorthand §x.y.z.k, and Operator
# Console acceptance-criteria refs (AC10–AC13, AC20, …).
_SECTION_RE = re.compile(r"§\d+(?:\.\d+|\.[A-Za-z])+|AC\d+(?:–AC\d+)?")


def read_fixture_readme(name: str) -> str:
    """Return the raw README text for a fixture, or raise on absence."""
    readme = FIXTURES_DIR / name / "README.md"
    if not readme.is_file():
        raise FileNotFoundError(f"fixture {name!r} has no README.md at {readme}")
    return readme.read_text(encoding="utf-8")


def parse_fixture(name: str) -> dict[str, str]:
    """Parse a fixture README into {title, scenario, verify, sections}."""
    text = read_fixture_readme(name)
    title_m = re.search(r"^# Fixture:\s*(.+)$", text, re.MULTILINE)
    verify_m = _VERIFY_TOKEN_RE.search(text)
    scenario = " ".join(text.splitlines()[2:]) if text.splitlines() else ""
    sections = _SECTION_RE.findall(text)
    return {
        "title": title_m.group(1).strip() if title_m else "",
        "scenario": scenario,
        "verify": verify_m.group(1).strip() if verify_m else "",
        "sections": sections,
    }


# ---------------------------------------------------------------------------
# Layer 1 — structural validation (all 29 fixtures)
# ---------------------------------------------------------------------------

def test_all_expected_fixture_dirs_exist() -> None:
    on_disk = sorted(p.name for p in FIXTURES_DIR.iterdir() if p.is_dir())
    missing = [n for n in EXPECTED_FIXTURES if n not in on_disk]
    extra = [n for n in on_disk if n not in EXPECTED_FIXTURES]
    assert not missing, f"fixture dirs missing: {missing}"
    assert not extra, f"unexpected fixture dirs (update EXPECTED_FIXTURES): {extra}"


@pytest.mark.parametrize("name", EXPECTED_FIXTURES)
def test_fixture_readme_is_wellformed(name: str) -> None:
    parsed = parse_fixture(name)
    assert parsed["title"] == name, (
        f"{name}: README title {parsed['title']!r} does not match fixture dir name"
    )
    assert len(parsed["scenario"]) > 40, f"{name}: scenario prose missing or too short"
    assert parsed["verify"], f"{name}: missing 'Verify:' clause"
    assert parsed["sections"], f"{name}: missing §x.y section reference(s)"


# ---------------------------------------------------------------------------
# Layer 2 — evidence manifest completeness
# ---------------------------------------------------------------------------

def test_manifest_covers_every_fixture_exactly_once() -> None:
    on_disk = {p.name for p in FIXTURES_DIR.iterdir() if p.is_dir()}
    assert on_disk == set(FIXTURE_MANIFEST), (
        "FIXTURE_MANIFEST must cover exactly the on-disk fixtures"
    )


def test_evidence_class_totals() -> None:
    """Guard against silent classification drift as fixtures get wired."""
    assert len(_CONFIRMED) == 8, f"confirmed set changed: {sorted(_CONFIRMED)}"
    assert len(_PLANNED) == 2, f"planned set changed: {sorted(_PLANNED)}"
    assert len(_ASPIRATIONAL) == 19, f"aspirational set changed: {sorted(_ASPIRATIONAL)}"
    assert len(FIXTURE_MANIFEST) == 29


def test_aspirational_fixtures_have_no_impl_ref() -> None:
    """Aspirational fixtures must not claim a wiring target."""
    for name, (cls, target, reason) in FIXTURE_MANIFEST.items():
        if cls == "aspirational":
            assert not target, f"{name}: aspirational fixture must have empty wiring target"
            assert reason, f"{name}: aspirational fixture needs a reason"


def test_planned_fixtures_reference_real_code() -> None:
    """Planned fixtures must point at code that exists on disk, or at a
    check function defined in this module (a real, runnable wiring)."""
    for name, (cls, target, _reason) in FIXTURE_MANIFEST.items():
        if cls != "planned":
            continue
        assert target, f"{name}: planned fixture needs a wiring target"
        target_path = REPO_ROOT / target
        if target in globals():
            continue  # a check function defined in this module
        assert target_path.exists(), (
            f"{name}: planned wiring target {target!r} does not exist on disk"
        )


# ---------------------------------------------------------------------------
# Layer 3 — confirmed wiring against the §11.3 receipt chain
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def receipt_chain():
    """Load harness/contracts/verify_receipt_chain.py (standalone script)."""
    spec = importlib.util.spec_from_file_location(
        "verify_receipt_chain_under_test", VERIFY_RECEIPT_CHAIN
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _signed_chain(receipt_chain):
    """A clean 4-receipt chain (genesis + 3) + its signer public key."""
    chain, priv = receipt_chain.build_chain()
    return chain, priv.public_key()


def test_confirmed_fixtures_have_checks() -> None:
    """Every confirmed fixture maps to a check function defined in this module."""
    expected_checks = {
        "forged_node_receipt": "check_forged_signature",
        "forged_operator_request": "check_forged_operator_request",
        "operator-console-approval": "check_operator_console_approval",
        "operator-console-cancellation": "check_operator_console_cancellation",
        "operator-console-integrity-failure": "check_operator_console_integrity_failure",
        "operator-console-readonly-audit": "check_operator_console_readonly_audit",
        "receipt_parent_hash_tamper": "check_parent_hash_tamper",
        "stale_authority_epoch": "check_stale_epoch",
    }
    for name, (cls, target, _reason) in FIXTURE_MANIFEST.items():
        if cls == "confirmed":
            assert name in expected_checks, f"{name}: no expected check mapping"
            assert target == expected_checks[name]
            assert target in globals(), f"{name}: check {target!r} not defined"


def check_forged_signature(receipt_chain) -> None:
    """Fixture: forged_node_receipt — forged signer/bad signature must fail.

    Verify: receipt_signature_verified fails; chain linkage refused; no
    chain discontinuity introduced (§11.3).
    """
    chain, pubkey = _signed_chain(receipt_chain)
    # Valid chain verifies first (sanity).
    ok, msg = receipt_chain.verify_chain(chain, pubkey)
    assert ok, f"sanity: clean chain must verify, got: {msg}"
    # Forge rcp_0002's signature (S-4 analogue).
    forged = copy.deepcopy(chain)
    forged[2]["proof"]["signature"] = "ed25519:" + "0" * 128
    ok, msg = receipt_chain.verify_chain(forged, pubkey)
    assert not ok, "forged signature must fail verification"
    assert "signature" in msg.lower(), f"failure must cite signature, got: {msg}"


def test_forged_node_receipt(receipt_chain) -> None:
    check_forged_signature(receipt_chain)


def check_parent_hash_tamper(receipt_chain) -> None:
    """Fixture: receipt_parent_hash_tamper — parent_hash rewrite must break
    the chain link.

    Verify: tamper_detection_verified catches the rewrite;
    receipt_chain_verified fails at the broken link (§11.3).
    """
    chain, pubkey = _signed_chain(receipt_chain)
    tampered = copy.deepcopy(chain)
    tampered[2]["parent_hash"] = "sha256:" + "f" * 64
    ok, msg = receipt_chain.verify_chain(tampered, pubkey)
    assert not ok, "parent_hash rewrite must fail verification"
    # parent_hash is part of canonical serialization, so detection may fire
    # as self_hash mismatch OR as the explicit parent_hash linkage break.
    assert ("parent_hash" in msg.lower()) or ("self_hash" in msg.lower()), (
        f"failure must cite parent_hash/self_hash, got: {msg}"
    )


def test_receipt_parent_hash_tamper(receipt_chain) -> None:
    check_parent_hash_tamper(receipt_chain)


def check_stale_epoch(receipt_chain) -> None:
    """Fixture: stale_authority_epoch — message signed under an epoch below
    the trusted epoch must be rejected.

    Verify: stale_epoch_rejection_tested passes; stale leases and control
    messages denied (§6.3, §13.1).
    """
    chain, pubkey = _signed_chain(receipt_chain)
    trusted = receipt_chain.TRUSTED_EPOCH
    stale = copy.deepcopy(chain)
    stale[2]["authority_epoch"] = trusted - 1
    # Re-sign so only the epoch rule can fail (isolates the conjunct).
    stale[2]["self_hash"] = receipt_chain.sha256_hex(receipt_chain.canonical(stale[2]))
    stale[2]["proof"]["signature"] = "ed25519:" + (
        _priv_from_chain(receipt_chain).sign(receipt_chain.canonical(stale[2])).hex()
    )
    ok, msg = receipt_chain.verify_chain(stale, pubkey, trusted_epoch=trusted)
    assert not ok, "stale epoch must fail verification"
    assert "epoch" in msg.lower(), f"failure must cite epoch, got: {msg}"


def test_stale_authority_epoch(receipt_chain) -> None:
    check_stale_epoch(receipt_chain)


def _priv_from_chain(receipt_chain):
    """The pinned TEST-ONLY signer private key (same deterministic key the
    harness uses; used only to re-sign an isolated tamper case)."""
    return receipt_chain.signer_key()


def check_tenant_binding(receipt_chain) -> None:
    """Chain-side tenant binding (S-3) — tenant_id is part of canonical
    serialization, so a cross-tenant injection breaks self_hash/signature
    even without touching the linkage fields.

    Backs fixture: cross_tenant_event_query (chain side). Retrieval-denial
    layer is aspirational.
    """
    chain, pubkey = _signed_chain(receipt_chain)
    injected = copy.deepcopy(chain)
    injected[1]["tenant_id"] = "tenant_other"
    ok, msg = receipt_chain.verify_chain(injected, pubkey)
    assert not ok, "cross-tenant injection must fail verification"
    assert "self_hash" in msg.lower() or "signature" in msg.lower(), (
        f"failure must cite self_hash/signature, got: {msg}"
    )


def test_cross_tenant_chain_binding(receipt_chain) -> None:
    check_tenant_binding(receipt_chain)


# ---------------------------------------------------------------------------
# Operator-request gate (§12.2 replay window / §13.1 signature / §19.2 MFA)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def operator_request_gate():
    """Load harness/contracts/verify_operator_request.py (standalone script)."""
    spec = importlib.util.spec_from_file_location(
        "verify_operator_request_under_test", VERIFY_OPERATOR_REQUEST
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _signed_operator_request(gate, operator_id="op_alice", nonce="nonce-0001", now=None):
    """A valid signed operator request + its signer public key."""
    import time
    key = gate.signer_key()
    now = time.time() if now is None else now
    req = gate.build_operator_request(
        key,
        request_id="op_req_0001",
        operator_id=operator_id,
        effect="payment.capture",
        declared_risk_tier="T4",
        nonce=nonce,
        issued_at=now,
    )
    return req, key.public_key()


def check_forged_operator_request(gate) -> None:
    """Fixture: forged_operator_request — forged/replayed/stale session proof
    must be denied before any policy evaluation or effect path.

    Verify: request denied with `operator_request_signature_verified` failing;
    no lease issued; replay window (60s, §12.2) enforced; MFA required for
    operators (§13.1, §19.2).
    """
    import copy
    import time

    req, pubkey = _signed_operator_request(gate)

    # Valid request passes (sanity), and the gate token is the fixture's token.
    ok, msg = gate.verify_operator_request(req, pubkey)
    assert ok, f"sanity: valid operator request must pass, got: {msg}"
    assert gate.GATE_TOKEN in msg

    # The request shape validates against operator-evidence.schema.json.
    ok_shape, shape_msg = gate.request_validates_against_schema(req)
    assert ok_shape, f"valid request must conform to operator-evidence schema: {shape_msg}"
    assert req["schemaVersion"] == "operator-evidence/1"

    # Shape violation (missing required field) must be rejected before any
    # signature/replay check — even with a valid signature.
    bad_shape = copy.deepcopy(req)
    del bad_shape["schemaVersion"]
    ok, msg = gate.verify_operator_request(bad_shape, pubkey)
    assert not ok, "non-conformant shape must be rejected"
    assert "schema violation" in msg.lower(), f"must cite schema, got: {msg}"

    # Forged signature (S-4): bad ed25519 signature must be rejected.
    forged = copy.deepcopy(req)
    forged["proof"]["signature"] = "ed25519:" + "0" * 128
    ok, msg = gate.verify_operator_request(forged, pubkey)
    assert not ok, "forged operator signature must be rejected"
    assert "signature" in msg.lower(), f"must cite signature, got: {msg}"

    # Stale cookie (§12.2): 60s replay window — a 120s-old proof must fail
    # even with a valid signature (re-sign isolates the window conjunct).
    stale = copy.deepcopy(req)
    stale["timestamp"] = gate._iso_from_epoch(time.time() - 120)
    stale["proof"]["signature"] = "ed25519:" + (
        gate.signer_key().sign(gate.canonical(stale)).hex()
    )
    ok, msg = gate.verify_operator_request(stale, pubkey)
    assert not ok, "stale session proof must be rejected (60s replay window)"
    assert "stale" in msg.lower(), f"must cite stale window, got: {msg}"

    # Replayed nonce: same nonce seen before must be rejected.
    seen: set[str] = set()
    ok, _ = gate.verify_operator_request(req, pubkey, seen_nonces=seen)
    assert ok
    replayed = copy.deepcopy(req)
    replayed["eventId"] = "op_req_9999"
    replayed["proof"]["signature"] = "ed25519:" + (
        gate.signer_key().sign(gate.canonical(replayed)).hex()
    )
    ok, msg = gate.verify_operator_request(replayed, pubkey, seen_nonces=seen)
    assert not ok, "replayed nonce must be rejected"
    assert "nonce" in msg.lower(), f"must cite nonce, got: {msg}"

    # MFA required (§13.1, §19.2): operator without verified MFA is denied
    # even with a perfect signature + fresh nonce.
    no_mfa = copy.deepcopy(req)
    no_mfa["mfa_verified"] = False
    no_mfa["proof"]["signature"] = "ed25519:" + (
        gate.signer_key().sign(gate.canonical(no_mfa)).hex()
    )
    ok, msg = gate.verify_operator_request(no_mfa, pubkey)
    assert not ok, "operator without MFA must be rejected"
    assert "mfa" in msg.lower(), f"must cite MFA, got: {msg}"


def test_forged_operator_request(operator_request_gate) -> None:
    check_forged_operator_request(operator_request_gate)


# ---------------------------------------------------------------------------
# Operator-console gate (Python mirror of the TS operator plane)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def operator_console_gate():
    """Load harness/contracts/operator_console_gate.py (standalone script)."""
    spec = importlib.util.spec_from_file_location(
        "operator_console_gate_under_test", OPERATOR_CONSOLE_GATE
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _good_manifest(gate, now: float, nonce: str = "nonce-a", **overrides):
    m = gate.build_effect_manifest(
        manifest_id="manifest_0001",
        task_id="task_0001",
        correlation_id="cor_0001",
        kind="workspace.patch",
        base_revision="git-sha-base",
        candidate_revision="git-sha-candidate",
        diff_sha256="sha256:" + "a" * 64,
        policy_class="standard",
        expires_at=now + 3600,
        one_time_nonce=nonce,
        effect_class="workspace.patch",
        declared_risk_tier="T2",
        required_evidence=["receipt://t"],
    )
    m.update(overrides)
    return m


_EVIDENCE = {"receipt://t"}


def check_operator_console_approval(gate) -> None:
    """Fixture: operator-console-approval — approve issues a lease, deny
    records a denial; controls require a valid session + all gates green.

    Verify: controls enabled only with valid operator session + all evidence
    gates green (AC10–AC13).
    """
    import time
    now = time.time()
    gate_mod = gate  # module under test
    gate_mod.ApprovalGate  # noqa: B018 — confirm symbol exists
    console = gate_mod.ApprovalGate(now=now)

    manifest = _good_manifest(gate_mod, now)
    # The manifest shape validates against effect-manifest.schema.json.
    ok_shape, shape_msg = gate_mod.manifest_validates_against_schema(manifest)
    assert ok_shape, f"manifest must conform to effect-manifest.schema.json: {shape_msg}"
    assert manifest["schemaVersion"] == "effect-manifest/1"
    assert manifest["declarationHash"].startswith("sha256:")

    # All gates green + valid session -> approve.
    ok, reasons = console.verify_manifest(manifest, evidence_present=_EVIDENCE)
    assert ok and not reasons, f"approve expected, got: {reasons}"

    # Invalid operator session alone must deny.
    bad_session = _good_manifest(gate_mod, now, nonce="nonce-s")
    bad_session["operatorSessionValid"] = False
    ok2, reasons2 = console.verify_manifest(bad_session, evidence_present=_EVIDENCE)
    assert not ok2 and "operator_session_invalid" in reasons2

    # Gideon fail must deny with the reason recorded.
    bad_gideon = _good_manifest(gate_mod, now, nonce="nonce-g")
    bad_gideon["gideonVerdict"] = "fail"
    ok3, reasons3 = console.verify_manifest(bad_gideon, evidence_present=_EVIDENCE)
    assert not ok3 and "gideon_verdict_not_pass" in reasons3

    # Missing required evidence must deny (schema-string refs).
    ok4, reasons4 = console.verify_manifest(
        _good_manifest(gate_mod, now, nonce="nonce-e")
    )
    assert not ok4 and "required_evidence_missing" in reasons4

    # Approve issues a lease; deny records a denial (no lease).
    lease = console.issue_lease(
        _good_manifest(gate_mod, now, nonce="nonce-l"), evidence_present=_EVIDENCE
    )
    assert console.get_lease(lease["leaseId"]) is not None, "lease must be active"
    denial = console.record_denial(
        _good_manifest(gate_mod, now, nonce="nonce-d"), ["gideon_verdict_not_pass"]
    )
    assert denial["decision"] == "deny"


def test_operator_console_approval(operator_console_gate) -> None:
    check_operator_console_approval(operator_console_gate)


def check_operator_console_cancellation(gate) -> None:
    """Fixture: operator-console-cancellation — cancel an active task.

    Verify: cancellation receipt, lease revoked, workers stopped, VFS
    workspace cleaned (AC20).
    """
    import time
    now = time.time()
    console = gate.ApprovalGate(now=now)
    chain = gate.EvidenceChain()
    ctrl = gate.TaskController(chain, console)

    lease = console.issue_lease(
        _good_manifest(gate, now, nonce="nonce-x"), evidence_present=_EVIDENCE
    )
    ctrl.start("task_c", ["w1", "w2"])
    evt = ctrl.cancel("task_c", lease["leaseId"])

    assert evt["kind"] == "task.cancelled"
    assert evt["payload"]["lease_revoked"] is True
    assert evt["payload"]["workers_stopped"] is True
    assert evt["payload"]["workspace_cleaned"] is True
    assert console.get_lease(lease["leaseId"]) is None, "lease must be revoked"


def test_operator_console_cancellation(operator_console_gate) -> None:
    check_operator_console_cancellation(operator_console_gate)


def check_operator_console_integrity_failure(gate) -> None:
    """Fixture: operator-console-integrity-failure — forged receipt hash.

    Verify: INTEGRITY FAILED alert, approval disabled, record preserved for
    investigation (AC17–AC18).
    """
    chain = gate.EvidenceChain()
    chain.append(
        event_id="evt_1", task_id="task_i", kind="snapshot",
        actor="gideon", integrity="integrity_failed",
        payload={"receipt_hash": "sha256:" + "f" * 64},
    )
    alert = gate.detect_integrity_failure(chain, "task_i")
    assert alert["alert"] == "INTEGRITY FAILED"
    assert alert["integrity"] == "integrity_failed"
    assert alert["approval_disabled"] is True
    assert alert["preserved_record"] is not None, "record must be preserved"

    # A clean chain raises no alert.
    clean = gate.EvidenceChain()
    clean.append(event_id="evt_1", task_id="task_ok", kind="snapshot",
                 actor="gideon")
    assert gate.detect_integrity_failure(clean, "task_ok")["alert"] is None


def test_operator_console_integrity_failure(operator_console_gate) -> None:
    check_operator_console_integrity_failure(operator_console_gate)


def check_operator_console_readonly_audit(gate) -> None:
    """Fixture: operator-console-readonly-audit — deterministic read-only task.

    Verify: all six panels render real state, no fabricated content, no-write
    receipt (AC19).
    """
    chain = gate.EvidenceChain()
    chain.append(event_id="evt_1", task_id="task_r", kind="audit.readonly",
                 actor="owl-auditor", payload={"worker": "owl-auditor"})
    audit = gate.run_readonly_audit(chain, "task_r")

    # The audit result IS an operator-task-snapshot/1 and must validate.
    ok_snap, snap_msg = gate.snapshot_validates_against_schema(audit)
    assert ok_snap, f"snapshot must conform to operator-task-snapshot.schema.json: {snap_msg}"
    assert audit["schemaVersion"] == "operator-task-snapshot/1"
    assert audit["integrity"] == "verified"

    assert audit["no_write_receipt"]["write_path_exercised"] is False
    assert audit["no_write_receipt"]["kind"] == "audit.readonly"
    assert "approval" not in audit, "no approval path in read-only audit"
    assert audit["taskGraph"][0]["id"] == "ant-mapper"
    assert audit["receipts"][0]["kind"] == "audit.readonly"


def test_operator_console_readonly_audit(operator_console_gate) -> None:
    check_operator_console_readonly_audit(operator_console_gate)


# ---------------------------------------------------------------------------
# Summary surface — the gate reports the wiring map on demand
# ---------------------------------------------------------------------------

def test_fixture_wiring_summary(capsys) -> None:
    """Print the evidence-class map so CI logs show coverage at a glance."""
    lines = ["harness fixture coverage map:"]
    for name in EXPECTED_FIXTURES:
        cls, target, reason = FIXTURE_MANIFEST[name]
        lines.append(f"  {name:45s} {cls:12s} {target or '(spec only)'}")
    print("\n".join(lines))
