# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Test Suite for Cartridge Sandbox — signed supply chain + governance enforcement.

Run:  python 02_FORGE/cartridge/test_sandbox.py
      (or)  pytest 02_FORGE/cartridge/test_sandbox.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Deterministic HMAC signing for tests — no keygen / filesystem needed.
os.environ["CAMELOT_CARTRIDGE_HMAC_KEY"] = "unit-test-signing-secret"

from cartridge.sandbox import CartridgeSandbox, TrustMode
from cartridge.cartridge_schemas import CartridgeManifest, GovernancePolicy, ResourceBudget
from cartridge import cartridge_crypto


def _signed_manifest(**overrides) -> CartridgeManifest:
    """Build a manifest, then sign the fully-resolved model (real signature)."""
    data = {
        "cartridge_id": "T",
        "description": "test",
        "governance": {},
        "resource_budget": {},
        "signature": "pending",
    }
    data.update(overrides)
    m = CartridgeManifest(**data)
    m.signature = cartridge_crypto.sign(m)
    return m


def test_signed_manifest_verifies_and_runs():
    print("\n=== Signature: valid signed manifest runs ===")
    sb = CartridgeSandbox(trust_mode=TrustMode.STRICT)
    m = _signed_manifest(cartridge_id="GOOD",
                         governance={"allowed_tools": ["SecurityScan"]})
    res = sb.run_cartridge_tool(m, "SecurityScan", {})
    assert res["status"] == "success", res
    assert res["simulated"] is True  # default executor is an explicit simulation
    print("✅ signed manifest verified and executed")


def test_unsigned_manifest_rejected_in_strict():
    print("\n=== Signature: legacy/unsigned manifest rejected (STRICT) ===")
    sb = CartridgeSandbox(trust_mode=TrustMode.STRICT)
    m = CartridgeManifest(cartridge_id="LEGACY", description="d",
                          signature="sha256:deadbeef",
                          governance=GovernancePolicy(allowed_tools=["*"]))
    res = sb.run_cartridge_tool(m, "SecurityScan", {})
    assert res["status"] == "error" and res["violation"] == "SignatureViolation", res
    print("✅ unsigned/legacy manifest blocked before governance is even consulted")


def test_tampered_manifest_rejected():
    print("\n=== Signature: tampering after signing is detected ===")
    sb = CartridgeSandbox(trust_mode=TrustMode.STRICT)
    m = _signed_manifest(cartridge_id="TAMPER",
                         governance={"allowed_tools": ["CodeGen"]})
    # Attacker widens the whitelist AFTER signing.
    m.governance.allowed_tools.append("NetworkStrike")
    res = sb.run_cartridge_tool(m, "NetworkStrike", {})
    assert res["status"] == "error" and res["violation"] == "SignatureViolation", res
    print("✅ post-signing tamper invalidates the signature → blocked")


def test_deny_list_wins_over_allow():
    print("\n=== Governance: deny-list beats allow-list ===")
    sb = CartridgeSandbox(trust_mode=TrustMode.STRICT)
    m = _signed_manifest(cartridge_id="DENY",
                         governance={"allowed_tools": ["*"],
                                     "denied_operations": ["NetworkStrike"]})
    ok = sb.run_cartridge_tool(m, "CodeGen", {})
    assert ok["status"] == "success", ok
    blocked = sb.run_cartridge_tool(m, "NetworkStrike", {})
    assert blocked["status"] == "error" and blocked["violation"] == "GovernanceViolation", blocked
    print("✅ denied_operations blocks even under wildcard allow")


def test_hitl_required_gate():
    print("\n=== Governance: HITL_required needs approval ===")
    # No approval callback → blocked.
    sb_block = CartridgeSandbox(trust_mode=TrustMode.STRICT)
    m = _signed_manifest(cartridge_id="HITL",
                         governance={"allowed_tools": ["*"], "HITL_required": True})
    res = sb_block.run_cartridge_tool(m, "CodeGen", {})
    assert res["status"] == "error" and res["violation"] == "HITLRequired", res

    # Approval callback returns True → allowed.
    approvals = []

    def approve(cid, tool, params):
        approvals.append((cid, tool))
        return True

    sb_ok = CartridgeSandbox(trust_mode=TrustMode.STRICT, approval_callback=approve)
    res2 = sb_ok.run_cartridge_tool(m, "CodeGen", {})
    assert res2["status"] == "success", res2
    assert approvals == [("HITL", "CodeGen")]
    print("✅ HITL blocks without approval, proceeds with approval")


def test_not_whitelisted_blocked():
    print("\n=== Governance: allow-list still enforced ===")
    sb = CartridgeSandbox(trust_mode=TrustMode.STRICT)
    m = _signed_manifest(cartridge_id="WL",
                         governance={"allowed_tools": ["SecurityScan", "Ruff"]})
    res = sb.run_cartridge_tool(m, "WebCrawler", {})
    assert res["status"] == "error" and res["violation"] == "SecurityViolation", res
    print("✅ non-whitelisted tool blocked")


def test_real_executor_injection():
    print("\n=== Execution: injected executor replaces the simulation ===")
    calls = {}

    def real_exec(tool_id, params):
        calls["tool"] = tool_id
        return {"data": {"ran": tool_id}, "token_cost": 5}

    sb = CartridgeSandbox(trust_mode=TrustMode.STRICT, tool_executor=real_exec)
    m = _signed_manifest(cartridge_id="EXEC",
                         governance={"allowed_tools": ["*"]})
    res = sb.run_cartridge_tool(m, "Build", {})
    assert res["status"] == "success"
    assert res["simulated"] is False
    assert res["result"] == {"ran": "Build"}
    assert calls["tool"] == "Build"
    print("✅ production executor invoked; not a mock")


def test_warn_mode_allows_unsigned():
    print("\n=== Migration: WARN mode allows unsigned but logs ===")
    sb = CartridgeSandbox(trust_mode=TrustMode.WARN)
    m = CartridgeManifest(cartridge_id="MIG", description="d",
                          signature="sha256:legacy",
                          governance=GovernancePolicy(allowed_tools=["*"]))
    res = sb.run_cartridge_tool(m, "CodeGen", {})
    assert res["status"] == "success", res
    print("✅ WARN mode permits legacy cartridges during migration")


ALL_TESTS = [
    test_signed_manifest_verifies_and_runs,
    test_unsigned_manifest_rejected_in_strict,
    test_tampered_manifest_rejected,
    test_deny_list_wins_over_allow,
    test_hitl_required_gate,
    test_not_whitelisted_blocked,
    test_real_executor_injection,
    test_warn_mode_allows_unsigned,
]


if __name__ == "__main__":
    print("🧪 Cartridge Sandbox — signed supply chain + governance")
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
