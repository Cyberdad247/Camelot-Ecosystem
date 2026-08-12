# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Test Suite — Enterprise Cartridge Trust Lifecycle
(key rotation, multi-signer, revocation, expiry, tamper-evident audit).

Run:  python 02_FORGE/cartridge/test_trust.py
"""
import os
import sys
import tempfile
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cartridge import cartridge_crypto as cc
from cartridge.cartridge_trust import (
    TrustStore, RevocationList, AuditLog, TrustManager,
    STATUS_ROTATED, STATUS_REVOKED,
)
from cartridge.cartridge_schemas import CartridgeManifest
from cartridge.sandbox import CartridgeSandbox, TrustMode


def _tmp(name):
    return os.path.join(tempfile.mkdtemp(prefix="camelot_trust_"), name)


def _manifest(cid, allowed):
    return CartridgeManifest(cartridge_id=cid, description="d",
                             signature="pending",
                             governance={"allowed_tools": allowed})


def _tm(store=None, rev=None, audit=None):
    return TrustManager(store=store, revocations=rev, audit=audit)


def test_known_key_verifies_unknown_rejected():
    print("\n=== Trust: known kid verifies, unknown kid rejected ===")
    priv, pub = cc.generate_keypair(save=False)
    store = TrustStore(path=_tmp("ts.json"))
    store.add_key("ed-2026-q3", cc.SCHEME_ED25519, public_key_b64=pub)
    tm = _tm(store, RevocationList(_tmp("r.json")), AuditLog(_tmp("a.log")))

    m = _manifest("C1", ["CodeGen"])
    m.signature = cc.sign(m, kid="ed-2026-q3", private_key_b64=priv)
    ok, reason = tm.verify(m, m.signature)
    assert ok, reason
    print("✅ registered key verifies")

    # Same signature but the store doesn't know the kid.
    empty = _tm(TrustStore(_tmp("ts2.json")), RevocationList(_tmp("r2.json")), AuditLog(_tmp("a2.log")))
    ok2, reason2 = empty.verify(m, m.signature)
    assert not ok2 and "unknown key id" in reason2, reason2
    print("✅ unknown key id rejected:", reason2)


def test_key_rotation():
    print("\n=== Trust: rotated key still verifies existing cartridges ===")
    priv, pub = cc.generate_keypair(save=False)
    store = TrustStore(path=_tmp("ts.json"))
    store.add_key("old-key", cc.SCHEME_ED25519, public_key_b64=pub)
    tm = _tm(store, RevocationList(_tmp("r.json")), AuditLog(_tmp("a.log")))

    m = _manifest("LEGACY_C", ["*"])
    m.signature = cc.sign(m, kid="old-key", private_key_b64=priv)
    assert tm.verify(m, m.signature)[0]

    store.rotate("old-key")
    assert store.keys["old-key"].status == STATUS_ROTATED
    ok, reason = tm.verify(m, m.signature)
    assert ok, f"rotated key must still verify old cartridges: {reason}"
    assert not store.keys["old-key"].usable_for_signing()
    print("✅ rotated key verifies old artifacts but is no longer valid for signing")


def test_revoked_key_never_trusted():
    print("\n=== Trust: revoked key is never trusted ===")
    priv, pub = cc.generate_keypair(save=False)
    store = TrustStore(path=_tmp("ts.json"))
    store.add_key("compromised", cc.SCHEME_ED25519, public_key_b64=pub)
    tm = _tm(store, RevocationList(_tmp("r.json")), AuditLog(_tmp("a.log")))

    m = _manifest("C_REV", ["*"])
    m.signature = cc.sign(m, kid="compromised", private_key_b64=priv)
    assert tm.verify(m, m.signature)[0]

    store.revoke_key("compromised", note="leaked in incident-4471")
    ok, reason = tm.verify(m, m.signature)
    assert not ok and "REVOKED" in reason, reason
    print("✅ post-incident key revocation blocks even valid signatures:", reason)


def test_expired_key():
    print("\n=== Trust: expired key rejected ===")
    priv, pub = cc.generate_keypair(save=False)
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    store = TrustStore(path=_tmp("ts.json"))
    store.add_key("short-lived", cc.SCHEME_ED25519, public_key_b64=pub, not_after=past)
    tm = _tm(store, RevocationList(_tmp("r.json")), AuditLog(_tmp("a.log")))

    m = _manifest("C_EXP", ["*"])
    m.signature = cc.sign(m, kid="short-lived", private_key_b64=priv)
    ok, reason = tm.verify(m, m.signature)
    assert not ok and "expired" in reason, reason
    print("✅ expired key rejected:", reason)


def test_cartridge_and_signature_revocation():
    print("\n=== Trust: cartridge recall + signature revocation ===")
    priv, pub = cc.generate_keypair(save=False)
    store = TrustStore(path=_tmp("ts.json"))
    store.add_key("k", cc.SCHEME_ED25519, public_key_b64=pub)
    rev = RevocationList(_tmp("r.json"))
    tm = _tm(store, rev, AuditLog(_tmp("a.log")))

    bad = _manifest("MALICIOUS_C", ["*"])
    bad.signature = cc.sign(bad, kid="k", private_key_b64=priv)
    assert tm.verify(bad, bad.signature)[0]

    rev.revoke_cartridge("MALICIOUS_C", reason="exfil behavior found")
    ok, reason = tm.verify(bad, bad.signature)
    assert not ok and "cartridge revoked" in reason, reason
    print("✅ cartridge recall by id:", reason)

    other = _manifest("OTHER_C", ["*"])
    other.signature = cc.sign(other, kid="k", private_key_b64=priv)
    rev.revoke_signature(other.signature, reason="specific build pulled")
    ok2, reason2 = tm.verify(other, other.signature)
    assert not ok2 and "signature revoked" in reason2, reason2
    print("✅ revocation by signature fingerprint:", reason2)


def test_multi_signer():
    print("\n=== Trust: multiple active signers ===")
    p1, pub1 = cc.generate_keypair(save=False)
    p2, pub2 = cc.generate_keypair(save=False)
    store = TrustStore(path=_tmp("ts.json"))
    store.add_key("ci-signer", cc.SCHEME_ED25519, public_key_b64=pub1)
    store.add_key("release-signer", cc.SCHEME_ED25519, public_key_b64=pub2)
    tm = _tm(store, RevocationList(_tmp("r.json")), AuditLog(_tmp("a.log")))

    a = _manifest("A", ["*"]); a.signature = cc.sign(a, kid="ci-signer", private_key_b64=p1)
    b = _manifest("B", ["*"]); b.signature = cc.sign(b, kid="release-signer", private_key_b64=p2)
    assert tm.verify(a, a.signature)[0]
    assert tm.verify(b, b.signature)[0]
    # cross-key must fail: sign as ci-signer but a's kid says ci-signer — try wrong pub
    forged = _manifest("A", ["*"]); forged.signature = cc.sign(forged, kid="release-signer", private_key_b64=p1)
    assert not tm.verify(forged, forged.signature)[0]
    print("✅ two active signers both trusted; kid/key mismatch rejected")


def test_audit_chain_tamper_evident():
    print("\n=== Audit: hash chain detects tampering ===")
    path = _tmp("audit.log")
    log = AuditLog(path)
    for i in range(4):
        log.append("tool_exec", cartridge_id=f"C{i}", tool_id="X",
                   decision="allow", reason="ok")
    ok, msg = log.verify_chain()
    assert ok, msg
    print("✅ intact chain verifies:", msg)

    # Tamper: flip a decision in the middle without fixing the hash chain.
    lines = open(path, encoding="utf-8").read().splitlines()
    lines[1] = lines[1].replace('"decision": "allow"', '"decision": "deny"') \
                       .replace('"decision":"allow"', '"decision":"deny"')
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    ok2, msg2 = log.verify_chain()
    assert not ok2, "tamper should be detected"
    print("✅ tampered chain rejected:", msg2)


def test_sandbox_enterprise_integration():
    print("\n=== Integration: sandbox + TrustManager audits every decision ===")
    priv, pub = cc.generate_keypair(save=False)
    store = TrustStore(path=_tmp("ts.json"))
    store.add_key("prod", cc.SCHEME_ED25519, public_key_b64=pub)
    rev = RevocationList(_tmp("r.json"))
    audit = AuditLog(_tmp("a.log"))
    tm = _tm(store, rev, audit)
    sb = CartridgeSandbox(trust_mode=TrustMode.STRICT, trust_manager=tm)

    m = _manifest("PROD_C", ["CodeGen"])
    m.signature = cc.sign(m, kid="prod", private_key_b64=priv)

    assert sb.run_cartridge_tool(m, "CodeGen", {})["status"] == "success"
    assert sb.run_cartridge_tool(m, "NotAllowed", {})["violation"] == "SecurityViolation"

    # Recall the cartridge → even a valid signature is now blocked at the gate.
    rev.revoke_cartridge("PROD_C", reason="recall")
    blocked = sb.run_cartridge_tool(m, "CodeGen", {})
    assert blocked["violation"] == "SignatureViolation", blocked

    ok, msg = audit.verify_chain()
    assert ok, msg
    records = [l for l in open(audit.path, encoding="utf-8").read().splitlines() if l]
    assert len(records) == 3, f"expected 3 audit records, got {len(records)}"
    print(f"✅ 3 decisions audited, chain intact ({msg})")


ALL_TESTS = [
    test_known_key_verifies_unknown_rejected,
    test_key_rotation,
    test_revoked_key_never_trusted,
    test_expired_key,
    test_cartridge_and_signature_revocation,
    test_multi_signer,
    test_audit_chain_tamper_evident,
    test_sandbox_enterprise_integration,
]

if __name__ == "__main__":
    print("🧪 Enterprise Cartridge Trust Lifecycle")
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
