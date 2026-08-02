# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Test Suite — Bifrost → Sandbox Bridge (the governed dispatch seam).

Covers: HMAC bridge auth, real (non-simulated) execution, signature/governance
enforcement through the seam, full trust+revocation, RBAC-gated HITL, and the
packages manifest loader (fabricate → load → dispatch).

Run:  python 02_FORGE/cartridge/test_bifrost_bridge.py
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["CAMELOT_CARTRIDGE_HMAC_KEY"] = "bridge-test-cartridge-secret"

from cartridge import cartridge_crypto as cc
from cartridge.cartridge_schemas import CartridgeManifest
from cartridge.tool_registry import ToolRegistry
from cartridge.bifrost_bridge import (
    BifrostCartridgeBridge, sign_body, packages_manifest_loader,
)
from cartridge.cartridge_trust import TrustStore, RevocationList, AuditLog, TrustManager
from cartridge.cartridge_rbac import RBACPolicy
from cartridge.fabrication_engine import CartridgeFabricator

SECRET = "test-webhook-secret"


def _tmp(name):
    return os.path.join(tempfile.mkdtemp(prefix="camelot_bridge_"), name)


def _signed(cid, allowed, **gov):
    g = {"allowed_tools": allowed}; g.update(gov)
    m = CartridgeManifest(cartridge_id=cid, description="d", signature="pending", governance=g)
    m.signature = cc.sign(m)
    return m


def _loader(*manifests):
    idx = {m.cartridge_id: m for m in manifests}
    return lambda cid: idx.get(cid)


def _body(cid, tool, params=None, principal=None):
    return json.dumps({"cartridge_id": cid, "tool_id": tool,
                       "params": params or {}, "principal": principal})


def test_valid_signed_dispatch_runs_real_tool():
    print("\n=== Bridge: valid signed dispatch → REAL execution ===")
    reg = ToolRegistry(with_builtins=True)
    marker = {"ran": "for-real"}
    reg.register("do_work", lambda p: marker)
    m = _signed("C1", ["do_work"])
    bridge = BifrostCartridgeBridge(manifest_loader=_loader(m), registry=reg, webhook_secret=SECRET)

    body = _body("C1", "do_work", {"x": 1})
    res = bridge.handle_signed(body, sign_body(body, SECRET))
    assert res["status"] == "success", res
    assert res["result"] == marker
    assert res["simulated"] is False, "must be real execution, not simulation"
    print("✅ dispatched through the seam and ran the real tool:", res["result"])


def test_bad_hmac_rejected():
    print("\n=== Bridge: bad/missing HMAC rejected before anything runs ===")
    m = _signed("C1", ["echo"])
    bridge = BifrostCartridgeBridge(manifest_loader=_loader(m), webhook_secret=SECRET)
    body = _body("C1", "echo", {"value": "hi"})
    assert bridge.handle_signed(body, "deadbeef")["violation"] == "BridgeAuthFailure"
    assert bridge.handle_signed(body, "")["violation"] == "BridgeAuthFailure"
    print("✅ forged bridge signature blocked at the door")


def test_unknown_cartridge():
    print("\n=== Bridge: unknown cartridge id ===")
    bridge = BifrostCartridgeBridge(manifest_loader=_loader(), webhook_secret=SECRET)
    body = _body("NOPE", "echo")
    res = bridge.handle_signed(body, sign_body(body, SECRET))
    assert res["violation"] == "UnknownCartridge", res
    print("✅ unknown cartridge rejected:", res["error"])


def test_tampered_manifest_blocked_through_seam():
    print("\n=== Bridge: tampered manifest → SignatureViolation ===")
    reg = ToolRegistry(); reg.register("do_work", lambda p: "x")
    m = _signed("C1", ["do_work"])
    m.governance.allowed_tools.append("exfil")  # tamper AFTER signing
    bridge = BifrostCartridgeBridge(manifest_loader=_loader(m), registry=reg, webhook_secret=SECRET)
    body = _body("C1", "exfil")
    res = bridge.handle_signed(body, sign_body(body, SECRET))
    assert res["violation"] == "SignatureViolation", res
    print("✅ tampering detected at the seam, before execution")


def test_governance_blocks_unlisted_tool():
    print("\n=== Bridge: tool not in allowed_tools → SecurityViolation ===")
    reg = ToolRegistry(with_builtins=True)
    m = _signed("C1", ["echo"])  # only echo allowed
    bridge = BifrostCartridgeBridge(manifest_loader=_loader(m), registry=reg, webhook_secret=SECRET)
    body = _body("C1", "http_get", {"url": "http://example.com"})
    res = bridge.handle_signed(body, sign_body(body, SECRET))
    assert res["violation"] == "SecurityViolation", res
    print("✅ registry has the tool, but governance forbids it → blocked")


def test_allowed_but_unimplemented_tool_errors_cleanly():
    print("\n=== Bridge: allowed but unimplemented tool → clean error, no crash ===")
    reg = ToolRegistry()  # empty
    m = _signed("C1", ["ghost"])
    bridge = BifrostCartridgeBridge(manifest_loader=_loader(m), registry=reg, webhook_secret=SECRET)
    body = _body("C1", "ghost")
    res = bridge.handle_signed(body, sign_body(body, SECRET))
    assert res["status"] == "error" and "not implemented" in res["error"], res
    print("✅ missing implementation surfaces as a structured error")


def test_full_trust_with_revocation():
    print("\n=== Bridge: enterprise trust + cartridge revocation ===")
    reg = ToolRegistry(with_builtins=True)
    store = TrustStore(_tmp("ts.json"))
    store.add_key("default", cc.SCHEME_HMAC)  # kid used by cc.sign default
    rev = RevocationList(_tmp("r.json"))
    tm = TrustManager(store, rev, AuditLog(_tmp("a.log")))
    m = _signed("PROD", ["echo"])
    bridge = BifrostCartridgeBridge(manifest_loader=_loader(m), registry=reg,
                                    trust_manager=tm, webhook_secret=SECRET)

    body = _body("PROD", "echo", {"value": "ok"})
    assert bridge.handle_signed(body, sign_body(body, SECRET))["status"] == "success"

    rev.revoke_cartridge("PROD", reason="recall")
    res = bridge.handle_signed(body, sign_body(body, SECRET))
    assert res["violation"] == "SignatureViolation", res
    print("✅ recalled cartridge blocked at the seam even with a valid signature")


def test_rbac_gated_hitl_via_bridge():
    print("\n=== Bridge: HITL cartridge honors dispatcher's cartridge:approve ===")
    reg = ToolRegistry(with_builtins=True)
    pol = RBACPolicy(_tmp("rbac.json"))
    pol.assign("manager", ["approver"])
    pol.assign("intern", ["auditor"])
    m = _signed("HITL_C", ["echo"], HITL_required=True)
    bridge = BifrostCartridgeBridge(manifest_loader=_loader(m), registry=reg,
                                    rbac=pol, webhook_secret=SECRET)

    ok_body = _body("HITL_C", "echo", {"value": "go"}, principal="manager")
    assert bridge.handle_signed(ok_body, sign_body(ok_body, SECRET))["status"] == "success"

    no_body = _body("HITL_C", "echo", {"value": "go"}, principal="intern")
    res = bridge.handle_signed(no_body, sign_body(no_body, SECRET))
    assert res["violation"] == "HITLRequired", res
    print("✅ approver's dispatch runs; non-approver's HITL dispatch is blocked")


def test_packages_loader_end_to_end():
    print("\n=== Bridge: fabricate → packages loader → dispatch ===")
    reg = ToolRegistry(with_builtins=True)
    pkg = tempfile.mkdtemp(prefix="camelot_pkgs_")
    fab = CartridgeFabricator(output_dir=pkg)  # abs output honored? uses join(dirname, out)
    # Fabricator joins output_dir onto its own dir; write via a direct loader instead
    # to test the loader against a real on-disk signed manifest.
    m = _signed("DISK_C", ["utc_now"])
    d = os.path.join(pkg, "DISK_C"); os.makedirs(d, exist_ok=True)
    dump = m.model_dump_json(indent=2) if hasattr(m, "model_dump_json") else m.json(indent=2)
    open(os.path.join(d, "manifest.json"), "w", encoding="utf-8").write(dump)

    bridge = BifrostCartridgeBridge(manifest_loader=packages_manifest_loader(pkg),
                                    registry=reg, webhook_secret=SECRET)
    body = _body("DISK_C", "utc_now")
    res = bridge.handle_signed(body, sign_body(body, SECRET))
    assert res["status"] == "success" and "T" in res["result"], res
    # path traversal guard
    trav = _body("../../etc/passwd", "utc_now")
    assert bridge.handle_signed(trav, sign_body(trav, SECRET))["violation"] == "UnknownCartridge"
    print("✅ on-disk signed manifest loaded + dispatched; traversal guarded")


ALL_TESTS = [
    test_valid_signed_dispatch_runs_real_tool,
    test_bad_hmac_rejected,
    test_unknown_cartridge,
    test_tampered_manifest_blocked_through_seam,
    test_governance_blocks_unlisted_tool,
    test_allowed_but_unimplemented_tool_errors_cleanly,
    test_full_trust_with_revocation,
    test_rbac_gated_hitl_via_bridge,
    test_packages_loader_end_to_end,
]

if __name__ == "__main__":
    print("🧪 Bifrost → Sandbox Bridge")
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
