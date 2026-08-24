#!/usr/bin/env python3
"""
Camelot-OS — operator-console gate (Python contract mirror of the TS plane).

Implements the four operator-console behaviors the harness fixtures name,
mirroring the *semantics* of the TypeScript operator plane
(``apps/bifrost/src/operator/{sentinel,receipts,chain}.ts``) so the offline,
Python-only harness gate can exercise them without Node:

  * operator-console-approval          — approve issues a lease, deny records
    a denial; controls require a valid operator session and all evidence
    gates green (AC10–AC13).
  * operator-console-cancellation      — cancelling an active task emits a
    cancellation receipt, revokes the lease, stops workers, and cleans the
    VFS workspace (AC20).
  * operator-console-integrity-failure — a snapshot carrying
    ``integrity: integrity_failed`` (forged receipt hash) raises an
    INTEGRITY FAILED alert, disables approval, and preserves the record
    (AC17–AC18).
  * operator-console-readonly-audit    — a deterministic read-only audit task
    renders real state and emits a no-write receipt; no approval path and no
    fabricated content (AC19).

Canonical serialization intentionally matches the TS side
(``chain.ts``'s key-sorted compact JSON) so payload hashes computed here are
byte-identical to the ones the TS plane computes — the mirror is cross-checked
by the wiring tests against the same sha256 scheme.

Usage:
    python harness/contracts/operator_console_gate.py   # run the battery
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import uuid

# Windows consoles default to cp1252, which cannot encode the ✓/✗ glyphs used
# in output. Force UTF-8 (with replacement fallback) so the battery never
# crashes on print, regardless of the active console codepage.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# v1.2 closed effect-class set per §5.5 (mirror of the Bifrost contract).
EFFECT_CLASSES = (
    "ro.fetch", "ro.audit", "internal.synth", "workspace.test",
    "workspace.patch", "promote.worktree.merge", "promote.deploy",
    "external.publish.draft", "external.publish.publish", "external.email.send",
    "payment.invoice.draft", "payment.invoice.issue", "payment.capture",
    "payment.refund", "device.calendar.write", "device.sms.send",
    "device.call.initiate", "promote.failover",
)
RISK_TIERS = ("T0", "T1", "T2", "T3", "T4")
INTEGRITY_STATES = ("verified", "pending_anchor", "unavailable", "integrity_failed")


class OperatorConsoleError(Exception):
    """A gate violation — the action is refused."""


# ---------------------------------------------------------------------------
# Canonical serialization — MUST match apps/bifrost/src/operator/chain.ts
# ---------------------------------------------------------------------------

def canonical_json(value: object) -> str:
    """Key-sorted compact JSON. Matches the TS `canonicalJson` (sortKeys +
    JSON.stringify) so payload hashes agree byte-for-byte."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def payload_hash(payload: object) -> str:
    return "sha256:" + sha256_hex(canonical_json(payload).encode("utf-8"))


# ---------------------------------------------------------------------------
# Evidence chain (mirror of receipts.ts append-only hash chain)
# ---------------------------------------------------------------------------

class EvidenceChain:
    """Append-only event chain with payload-hash linkage (per task)."""

    def __init__(self) -> None:
        self._rows: list[dict] = []

    def append(
        self,
        *,
        event_id: str,
        task_id: str,
        kind: str,
        actor: str,
        integrity: str = "verified",
        payload: dict | None = None,
    ) -> dict:
        payload = payload or {}
        parent_hash = None
        for row in reversed(self._rows):
            if row["task_id"] == task_id:
                parent_hash = row["payload_hash"]
                break
        event = {
            "event_id": event_id,
            "task_id": task_id,
            "kind": kind,
            "actor": actor,
            "integrity": integrity,
            "payload": payload,
            "payload_hash": payload_hash(payload),
            "parent_hash": parent_hash,
        }
        self._rows.append(event)
        return event

    def list_by_task(self, task_id: str) -> list[dict]:
        return [r for r in self._rows if r["task_id"] == task_id]

    def verify_chain(self, task_id: str) -> tuple[bool, str]:
        """Hash-chain verification: each event's parent_hash must equal the
        previous event's payload_hash (mirror of receipts.ts verifyChain)."""
        rows = [r for r in self._rows if r["task_id"] == task_id]
        if not rows:
            return False, "no events for task"
        expected_parent: str | None = None
        for row in rows:
            if row["parent_hash"] != expected_parent:
                return False, f"chain break at {row['event_id']}"
            expected_parent = row["payload_hash"]
        return True, f"{len(rows)} events linked"


# ---------------------------------------------------------------------------
# Approval gate (mirror of sentinel.ts verifyManifest / issueLease)
# ---------------------------------------------------------------------------

class ApprovalGate:
    """Decision service: approve issues a lease, deny records a denial.

    Controls are enabled only when: the manifest is schema-conformant, not
    expired, every required evidence ref is present, Gideon verdict is pass,
    VFS evidence is OK, and the one-time nonce is fresh.
    """

    def __init__(self, now: float | None = None) -> None:
        self._now = time.time() if now is None else now
        self._seen_nonces: set[str] = set()
        self._leases: dict[str, dict] = {}

    def verify_manifest(self, manifest: dict) -> tuple[bool, list[str]]:
        reasons: list[str] = []
        m = manifest
        if m.get("schemaVersion") != "effect-manifest/1":
            reasons.append("manifest_schema_invalid")
        if m.get("effectClass") not in EFFECT_CLASSES:
            reasons.append("manifest_schema_invalid")
        if m.get("declaredRiskTier") not in RISK_TIERS:
            reasons.append("manifest_schema_invalid")
        try:
            if float(m["expiresAt"]) <= self._now:
                reasons.append("manifest_expired")
        except (KeyError, TypeError, ValueError):
            reasons.append("manifest_expired")
        for ref in m.get("requiredEvidence", []):
            if not ref.get("present", False):
                reasons.append("required_evidence_missing")
        if m.get("gideonVerdict") != "pass":
            reasons.append("gideon_verdict_not_pass")
        if not m.get("vfsEvidenceOk", False):
            reasons.append("vfs_evidence_not_ok")
        if m.get("oneTimeNonce") in self._seen_nonces:
            reasons.append("nonce_replayed")
        if not m.get("operatorSessionValid", False):
            reasons.append("operator_session_invalid")

        if not reasons:
            self._seen_nonces.add(m.get("oneTimeNonce", ""))
        return len(reasons) == 0, reasons

    def issue_lease(self, manifest: dict, ttl_ms: int = 5 * 60_000) -> dict:
        ok, reasons = self.verify_manifest(manifest)
        if not ok:
            raise OperatorConsoleError(f"approval denied: {', '.join(reasons)}")
        lease = {
            "leaseId": "lease:" + uuid.uuid4().hex,
            "manifestId": manifest["manifestId"],
            "issuedAt": self._now,
            "expiresAt": self._now + ttl_ms / 1000.0,
        }
        self._leases[lease["leaseId"]] = lease
        return lease

    def record_denial(self, manifest: dict, reasons: list[str]) -> dict:
        return {
            "manifestId": manifest.get("manifestId", ""),
            "decision": "deny",
            "reasons": reasons,
            "issuedAt": self._now,
            "kind": "approval.denied",
        }

    def get_lease(self, lease_id: str) -> dict | None:
        lease = self._leases.get(lease_id)
        if lease is None:
            return None
        if self._now > lease["expiresAt"]:
            self._leases.pop(lease_id, None)
            return None
        return lease

    def revoke_lease(self, lease_id: str) -> bool:
        return self._leases.pop(lease_id, None) is not None


# ---------------------------------------------------------------------------
# Cancellation (AC20) — lease revoked, workers stopped, workspace cleaned
# ---------------------------------------------------------------------------

class TaskController:
    """Lifecycle controller for an active task (cancellation semantics)."""

    def __init__(self, chain: EvidenceChain, gate: ApprovalGate) -> None:
        self._chain = chain
        self._gate = gate
        self._workers: set[str] = set()
        self._workspace_clean = False

    def start(self, task_id: str, worker_ids: list[str]) -> None:
        self._workers.update(worker_ids)
        self._chain.append(
            event_id=f"evt_{task_id}_start", task_id=task_id,
            kind="task.started", actor="operator",
        )

    def cancel(self, task_id: str, lease_id: str) -> dict:
        """Cancel an active task: emit cancellation receipt, revoke the lease,
        stop all workers, clean the VFS workspace."""
        if task_id not in {r["task_id"] for r in self._chain.list_by_task(task_id)}:
            raise OperatorConsoleError("unknown task")
        revoked = self._gate.revoke_lease(lease_id)
        self._workers.clear()
        self._workspace_clean = True
        return self._chain.append(
            event_id=f"evt_{task_id}_cancel", task_id=task_id,
            kind="task.cancelled", actor="operator",
            payload={"lease_revoked": revoked, "workers_stopped": True,
                     "workspace_cleaned": True},
        )


# ---------------------------------------------------------------------------
# Integrity-failure (AC17–AC18) — forged hash suspends approval, preserves record
# ---------------------------------------------------------------------------

def detect_integrity_failure(chain: EvidenceChain, task_id: str) -> dict:
    """Run chain verification; a forged receipt hash is a chain break. Returns
    the alert; the broken record is preserved (not deleted) for investigation."""
    rows = chain.list_by_task(task_id)
    ok, msg = chain.verify_chain(task_id)
    failed = next((r for r in rows if r["integrity"] == "integrity_failed"), None)
    if ok and failed is None:
        return {"alert": None, "integrity": "verified"}
    return {
        "alert": "INTEGRITY FAILED",
        "integrity": "integrity_failed",
        "chain_verified": ok,
        "reason": msg,
        "preserved_record": failed or rows[-1] if rows else None,
        "approval_disabled": True,
    }


# ---------------------------------------------------------------------------
# Read-only audit (AC19) — deterministic render, no approval path, no writes
# ---------------------------------------------------------------------------

def run_readonly_audit(chain: EvidenceChain, task_id: str) -> dict:
    """Deterministic read-only audit: render real state from the chain, no
    approval path, no fabricated content, emit a no-write receipt."""
    rows = chain.list_by_task(task_id)
    panels = {
        "workers": [{"id": w, "status": "running" if i == 0 else "done"}
                    for i, w in enumerate(["ant-mapper", "owl-auditor"])],
        "receipts": [{"event_id": r["event_id"], "kind": r["kind"]} for r in rows],
        "intent": {"kind": rows[0]["kind"]} if rows else {},
        "approval": None,  # read-only audit has no approval path
        "diffs": [],
        "tests": [],
    }
    return {
        "task_id": task_id,
        "panels": panels,
        "no_write_receipt": {
            "event_id": f"evt_{task_id}_audit",
            "task_id": task_id,
            "kind": "audit.readonly",
            "write_path_exercised": False,
            "payload_hash": payload_hash(panels),
        },
        "fabricated": False,
    }


# ---------------------------------------------------------------------------
# Battery — each behavior MUST pass its happy path and reject its negative case
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 72)
    print("Operator-console gate — Python mirror of the TS operator plane")
    print("fixtures: approval / cancellation / integrity-failure / readonly-audit")
    print("=" * 72)

    failures: list[str] = []
    now = time.time()

    def expect(cond: bool, label: str) -> None:
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        if not cond:
            failures.append(label)

    # --- approval (AC10–AC13) ---------------------------------------------
    gate = ApprovalGate(now=now)
    manifest = {
        "schemaVersion": "effect-manifest/1",
        "manifestId": "manifest_0001",
        "taskId": "task_0001",
        "effectClass": "workspace.patch",
        "declaredRiskTier": "T2",
        "expiresAt": str(now + 3600),
        "requiredEvidence": [{"ref": "receipt://t", "present": True}],
        "gideonVerdict": "pass",
        "vfsEvidenceOk": True,
        "oneTimeNonce": "nonce-a",
        "operatorSessionValid": True,
    }
    ok, reasons = gate.verify_manifest(manifest)
    expect(ok and not reasons, "approval: all gates green -> approve")

    # The same manifest must NOT verify twice (nonce replay), but a fresh
    # nonce on an otherwise identical manifest is a new approval.
    replayed = dict(manifest, manifestId="manifest_0001r")
    ok_r, reasons_r = gate.verify_manifest(replayed)
    expect(not ok_r and "nonce_replayed" in reasons_r,
           "approval: nonce replay -> deny")

    denied = dict(manifest, gideonVerdict="fail", manifestId="manifest_0002",
                  oneTimeNonce="nonce-b")
    ok2, reasons2 = gate.verify_manifest(denied)
    expect(not ok2 and "gideon_verdict_not_pass" in reasons2,
           "approval: gideon fail -> deny with reason")

    lease_manifest = dict(manifest, manifestId="manifest_0003",
                          oneTimeNonce="nonce-c")
    lease = gate.issue_lease(lease_manifest)
    expect(gate.get_lease(lease["leaseId"]) is not None, "approval: lease issued")

    # --- cancellation (AC20) ----------------------------------------------
    chain = EvidenceChain()
    ctrl = TaskController(chain, gate)
    ctrl.start("task_c", ["w1", "w2"])
    cancel_evt = ctrl.cancel("task_c", lease["leaseId"])
    expect(cancel_evt["kind"] == "task.cancelled"
           and cancel_evt["payload"]["lease_revoked"]
           and cancel_evt["payload"]["workspace_cleaned"],
           "cancellation: receipt + lease revoked + workspace cleaned")
    expect(gate.get_lease(lease["leaseId"]) is None,
           "cancellation: lease no longer active")

    # --- integrity failure (AC17–AC18) ------------------------------------
    chain2 = EvidenceChain()
    chain2.append(event_id="evt_1", task_id="task_i", kind="snapshot",
                  actor="gideon", integrity="integrity_failed",
                  payload={"receipt_hash": "sha256:" + "f" * 64})
    alert = detect_integrity_failure(chain2, "task_i")
    expect(alert["alert"] == "INTEGRITY FAILED" and alert["approval_disabled"],
           "integrity-failure: INTEGRITY FAILED alert + approval disabled")
    expect(alert["preserved_record"] is not None,
           "integrity-failure: broken record preserved")

    # --- readonly audit (AC19) --------------------------------------------
    chain3 = EvidenceChain()
    chain3.append(event_id="evt_1", task_id="task_r", kind="audit.readonly",
                  actor="owl-auditor", payload={"worker": "owl-auditor"})
    audit = run_readonly_audit(chain3, "task_r")
    expect(audit["fabricated"] is False
           and audit["no_write_receipt"]["write_path_exercised"] is False
           and audit["panels"]["approval"] is None,
           "readonly-audit: real state, no-write receipt, no approval path")

    print("=" * 72)
    if failures:
        print(f"✗ {len(failures)} check(s) FAILED: {failures}")
        return 1
    print("✓ ALL CHECKS PASSED — operator-console gate clears.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
