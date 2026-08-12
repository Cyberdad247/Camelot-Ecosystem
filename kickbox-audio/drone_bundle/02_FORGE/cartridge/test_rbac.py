# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Test Suite — Cartridge Lifecycle RBAC
(role resolution, deny-wins, least-privilege, OMEGA bridge, fabrication guard,
authorized+audited trust ops, HITL approval authorization).

Run:  python 02_FORGE/cartridge/test_rbac.py
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["CAMELOT_CARTRIDGE_HMAC_KEY"] = "rbac-test-secret"

from cartridge import cartridge_crypto as cc
from cartridge.cartridge_rbac import (
    RBACPolicy, AuthorizationError, make_rbac_approval,
    CAP_FABRICATE, CAP_SIGN, CAP_APPROVE, CAP_CARTRIDGE_REVOKE, CAP_KEY_REVOKE,
)
from cartridge.cartridge_trust import TrustStore, RevocationList, AuditLog, TrustManager
from cartridge.cartridge_schemas import CartridgeManifest
from cartridge.sandbox import CartridgeSandbox, TrustMode
from cartridge.fabrication_engine import CartridgeFabricator


def _tmp(name):
    return os.path.join(tempfile.mkdtemp(prefix="camelot_rbac_"), name)


def _policy(**principals) -> RBACPolicy:
    pol = RBACPolicy(path=_tmp("rbac.json"))
    for name, spec in principals.items():
        pol.assign(name, spec.get("roles", []),
                   grants=spec.get("grants"), deny=spec.get("deny"))
    return pol


def test_role_resolution():
    print("\n=== RBAC: default role → capabilities ===")
    pol = _policy(bot={"roles": ["release-engineer"]})
    assert pol.authorize("bot", CAP_FABRICATE)[0]
    assert pol.authorize("bot", CAP_SIGN)[0]
    ok, reason = pol.authorize("bot", CAP_CARTRIDGE_REVOKE)
    assert not ok, reason
    print("✅ release-engineer can fabricate+sign, not revoke:", reason)


def test_deny_wins():
    print("\n=== RBAC: explicit deny beats a granted role ===")
    pol = _policy(contractor={"roles": ["release-engineer"], "deny": [CAP_SIGN]})
    assert pol.authorize("contractor", CAP_FABRICATE)[0]
    ok, reason = pol.authorize("contractor", CAP_SIGN)
    assert not ok and "explicitly denied" in reason, reason
    print("✅ deny wins:", reason)


def test_unknown_principal_least_privilege():
    print("\n=== RBAC: unknown principal has no capabilities ===")
    pol = _policy(known={"roles": ["auditor"]})
    ok, reason = pol.authorize("ghost", CAP_FABRICATE)
    assert not ok, reason
    ok2, reason2 = pol.authorize(None, CAP_FABRICATE)
    assert not ok2, reason2
    print("✅ unknown/None principal denied:", reason)


def test_extra_grant():
    print("\n=== RBAC: per-principal grant adds a capability ===")
    pol = _policy(alice={"roles": ["release-engineer"], "grants": [CAP_APPROVE]})
    assert pol.authorize("alice", CAP_APPROVE)[0]
    print("✅ grant supplements role")


def test_omega_bridge():
    print("\n=== RBAC: OMEGA-tier knight bridges to admin (all caps) ===")
    pol = RBACPolicy(path=_tmp("rbac.json"))  # empty overlay
    # sir_boris is OMEGA tier in access_matrix.json
    ok, reason = pol.authorize("sir_boris", CAP_KEY_REVOKE)
    if pol._omega_knights:
        assert ok, reason
        print("✅ OMEGA knight sir_boris bridged to admin:", reason)
    else:
        print("⚠ access_matrix.json not found in this checkout — bridge skipped (non-fatal)")


def test_fabrication_guard():
    print("\n=== RBAC: fabrication requires fabricate+sign ===")
    pol = _policy(builder={"roles": ["release-engineer"]},
                  viewer={"roles": ["auditor"]})
    # Authorized principal
    fab = CartridgeFabricator(output_dir="temp_rbac_fab", rbac=pol, principal="builder")
    m = fab.fabricate({"cartridge_id": "RBAC_OK", "tools": ["CodeGen"]})
    assert m.signature.split(":")[0] in ("hmac", "ed25519"), m.signature
    print("✅ authorized builder fabricated a signed cartridge")
    # Unauthorized principal
    try:
        fab.fabricate({"cartridge_id": "RBAC_NO"}, principal="viewer")
        assert False, "auditor must not be able to fabricate"
    except AuthorizationError as e:
        print("✅ unauthorized fabrication blocked:", e)
    import shutil
    shutil.rmtree(os.path.join(os.path.dirname(__file__), "temp_rbac_fab"), ignore_errors=True)


def test_guarded_trust_ops_are_audited():
    print("\n=== RBAC: privileged trust ops authorized + audited ===")
    pol = _policy(secoff={"roles": ["security-officer"]},
                  builder={"roles": ["release-engineer"]})
    audit = AuditLog(_tmp("a.log"))
    tm = TrustManager(TrustStore(_tmp("ts.json")), RevocationList(_tmp("r.json")), audit, rbac=pol)

    # Authorized revoke
    tm.revoke_cartridge("BAD", principal="secoff", reason="malware")
    assert "BAD" in tm.revocations.cartridges
    # Unauthorized revoke
    try:
        tm.revoke_cartridge("OTHER", principal="builder", reason="nope")
        assert False, "release-engineer lacks cartridge:revoke"
    except AuthorizationError as e:
        print("✅ unauthorized revoke blocked:", e)

    ok, msg = audit.verify_chain()
    assert ok, msg
    lines = [l for l in open(audit.path, encoding="utf-8").read().splitlines() if l]
    import json
    events = [json.loads(l) for l in lines]
    decisions = [(e["event"], e["decision"]) for e in events]
    assert ("authz", "allow") in decisions
    assert ("authz", "deny") in decisions
    assert ("cartridge_revoke", "done") in decisions
    print(f"✅ authz allow+deny and the op are all in the tamper-evident log ({msg})")


def test_hitl_approval_authorization():
    print("\n=== RBAC: HITL gate honors cartridge:approve ===")
    pol = _policy(manager={"roles": ["approver"]},
                  intern={"roles": ["auditor"]})

    # approver_resolver decides who is approving; here it's fixed per sandbox.
    def resolver_for(principal):
        return lambda cid, tool, params: principal

    m = CartridgeManifest(cartridge_id="HITL_C", description="d", signature="pending",
                          governance={"allowed_tools": ["*"], "HITL_required": True})
    m.signature = cc.sign(m)

    sb_ok = CartridgeSandbox(trust_mode=TrustMode.STRICT,
                             approval_callback=make_rbac_approval(pol, resolver_for("manager")))
    assert sb_ok.run_cartridge_tool(m, "CodeGen", {})["status"] == "success"

    sb_no = CartridgeSandbox(trust_mode=TrustMode.STRICT,
                             approval_callback=make_rbac_approval(pol, resolver_for("intern")))
    res = sb_no.run_cartridge_tool(m, "CodeGen", {})
    assert res["violation"] == "HITLRequired", res
    print("✅ approver satisfies HITL; non-approver is rejected at the gate")


ALL_TESTS = [
    test_role_resolution,
    test_deny_wins,
    test_unknown_principal_least_privilege,
    test_extra_grant,
    test_omega_bridge,
    test_fabrication_guard,
    test_guarded_trust_ops_are_audited,
    test_hitl_approval_authorization,
]

if __name__ == "__main__":
    print("🧪 Cartridge Lifecycle RBAC")
    failures = 0
    for t in ALL_TESTS:
        try:
            t()
        except AssertionError as e:
            failures += 1
            print(f"❌ {t.__name__} FAILED: {e}")
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"❌ {t.__name__} ERROR: {e}")
            import traceback
            traceback.print_exc()
    print(f"\n{'🏆 ALL PASSED' if failures == 0 else f'❌ {failures} FAILURE(S)'} "
          f"({len(ALL_TESTS) - failures}/{len(ALL_TESTS)})")
    raise SystemExit(1 if failures else 0)
