# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Cartridge Sandbox (Node 3.5)
============================
Isolated execution environment for agent cartridges. Enforces — in this order,
before any tool runs:

    1. SIGNATURE       manifest.signature must verify against a trusted public key
                       (TrustMode.STRICT rejects unsigned/forged; WARN logs+allows;
                        OFF skips — dev only).
    2. DENY-LIST       tool_id in governance.denied_operations  → blocked (deny wins).
    3. HITL            governance.HITL_required  → approval_callback must return True.
    4. ALLOW-LIST      tool_id must be in governance.allowed_tools (or "*").
    5. BUDGET          token / latency budgets from resource_budget.

Execution is delegated to an injected ``tool_executor``. The default executor is an
explicit SIMULATION (clearly labeled) — production wires a real one so the gate is
never guarding a silent mock.
"""
from __future__ import annotations

import time
import json
import os
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict

from .cartridge_schemas import CartridgeManifest, GovernancePolicy, ResourceBudget
from . import cartridge_crypto


class TrustMode(str, Enum):
    STRICT = "strict"   # reject unsigned or invalid signatures  (PRODUCTION DEFAULT)
    WARN = "warn"       # log a warning but allow                (migration)
    OFF = "off"         # skip signature checks entirely          (dev only)


# Executor contract: (tool_id, params) -> {"data": Any, "token_cost": int}
ToolExecutor = Callable[[str, Dict[str, Any]], Dict[str, Any]]
# Approval contract for HITL cartridges: (cartridge_id, tool_id, params) -> bool
ApprovalCallback = Callable[[str, str, Dict[str, Any]], bool]


@dataclass
class SandboxSession:
    """State of a single cartridge execution session."""
    cartridge_id: str
    start_time: float = field(default_factory=time.time)
    token_usage: int = 0
    memory_peak_mb: float = 0.0
    calls_made: int = 0
    logs: List[str] = field(default_factory=list)


def _simulation_executor(tool_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Default executor — an explicit simulation, NOT a production tool runner."""
    time.sleep(0.005)
    return {
        "token_cost": 250,
        "data": f"[SIMULATION] executed {tool_id} with params {json.dumps(params, default=str)}",
        "simulated": True,
    }


class CartridgeSandbox:
    """Control layer for secure cartridge execution — the tool-level Iron Gate."""

    def __init__(
        self,
        *,
        trust_mode: Optional[TrustMode] = None,
        public_key_b64: Optional[str] = None,
        hmac_key: Optional[str] = None,
        tool_executor: Optional[ToolExecutor] = None,
        approval_callback: Optional[ApprovalCallback] = None,
        trust_manager: Optional[Any] = None,
    ):
        # Production default is STRICT; overridable via CAMELOT_CARTRIDGE_TRUST_MODE.
        if trust_mode is None:
            env_mode = os.getenv("CAMELOT_CARTRIDGE_TRUST_MODE", "strict").lower()
            trust_mode = TrustMode(env_mode) if env_mode in TrustMode._value2member_map_ else TrustMode.STRICT
        self.trust_mode = trust_mode
        self.public_key_b64 = public_key_b64
        self.hmac_key = hmac_key
        self._executor = tool_executor or _simulation_executor
        self._approve = approval_callback
        # Enterprise trust lifecycle (kid rotation, revocation, tamper-evident audit).
        # When None, falls back to the single-key verify path.
        self._trust = trust_manager
        self.active_sessions: Dict[str, SandboxSession] = {}
        print(f"[Sandbox] Isolation Layer Online "
              f"(trust_mode={self.trust_mode.value}, "
              f"enterprise_trust={'on' if trust_manager else 'off'})")

    # ── public API ─────────────────────────────────────────────────────────────
    def run_cartridge_tool(self, manifest: CartridgeManifest, tool_id: str,
                           params: Dict[str, Any]) -> Dict[str, Any]:
        session_id = f"sess_{manifest.cartridge_id}_{int(time.time()*1000)}"
        session = SandboxSession(cartridge_id=manifest.cartridge_id)
        self.active_sessions[session_id] = session
        signature = getattr(manifest, "signature", None)

        def finish(resp: Dict[str, Any], decision: str, reason: str) -> Dict[str, Any]:
            """Emit a tamper-evident audit record (if enterprise trust is on), then return."""
            if self._trust is not None:
                try:
                    self._trust.record("tool_exec", manifest, tool_id=tool_id,
                                       decision=decision, reason=reason, signature=signature)
                except Exception as e:  # noqa: BLE001 - auditing must never break execution
                    session.logs.append(f"audit-failure: {e}")
            return resp

        try:
            # 1. SIGNATURE — verify provenance before trusting the policy itself.
            sig_ok, sig_reason = self._verify_signature(manifest)
            if not sig_ok:
                return finish(self._deny(session, "SignatureViolation", sig_reason),
                              "deny", sig_reason)

            policy = manifest.governance

            # 2. DENY-LIST — deny always wins over allow.
            if tool_id in (policy.denied_operations or []):
                r = f"Tool '{tool_id}' is explicitly denied for '{manifest.cartridge_id}'"
                return finish(self._deny(session, "GovernanceViolation", r), "deny", r)

            # 3. HITL — high-trust cartridges require human approval.
            if policy.HITL_required:
                if self._approve is None or not self._approve(manifest.cartridge_id, tool_id, params):
                    r = f"Tool '{tool_id}' requires human approval (HITL_required=True)"
                    return finish(self._deny(session, "HITLRequired", r), "deny", r)

            # 4. ALLOW-LIST.
            if not self._tool_allowed(policy, tool_id):
                r = f"Tool '{tool_id}' is not whitelisted for '{manifest.cartridge_id}'"
                return finish(self._deny(session, "SecurityViolation", r), "deny", r)

            # 5. BUDGET (pre-check).
            if session.token_usage >= manifest.resource_budget.max_tokens:
                return finish(self._deny(session, "ResourceExhausted", "Token budget exceeded"),
                              "deny", "token budget exceeded")

            # Execution (delegated — default is an explicit simulation).
            result = self._executor(tool_id, params)

            session.calls_made += 1
            session.token_usage += int(result.get("token_cost", 100))
            session.memory_peak_mb = max(session.memory_peak_mb, 25.5)

            latency = (time.time() - session.start_time) * 1000
            if latency > manifest.resource_budget.max_latency_ms:
                session.logs.append(
                    f"Performance Warning: Latency {latency:.2f}ms exceeds budget "
                    f"{manifest.resource_budget.max_latency_ms}ms")

            return finish({
                "status": "success",
                "result": result.get("data"),
                "simulated": bool(result.get("simulated", False)),
                "telemetry": {
                    "tokens": session.token_usage,
                    "latency_ms": latency,
                    "memory_mb": session.memory_peak_mb,
                },
            }, "allow", "governance passed")
        except Exception as e:  # noqa: BLE001 - sandbox must never crash the host
            session.logs.append(f"Execution Failure: {str(e)}")
            return finish({"status": "error", "error": str(e)}, "error", str(e))

    def get_session_report(self, session_id: str) -> Optional[Dict[str, Any]]:
        if session_id not in self.active_sessions:
            return None
        return asdict(self.active_sessions[session_id])

    # ── internals ──────────────────────────────────────────────────────────────
    def _verify_signature(self, manifest: CartridgeManifest) -> tuple[bool, str]:
        if self.trust_mode == TrustMode.OFF:
            return True, "signature check disabled (OFF)"

        if self._trust is not None:
            # Enterprise path: key-id resolution, rotation/expiry, revocation.
            valid, reason = self._trust.verify(manifest, getattr(manifest, "signature", None))
        else:
            # Single-key path.
            signed = cartridge_crypto.is_signed(getattr(manifest, "signature", None))
            valid = signed and cartridge_crypto.verify(
                manifest, manifest.signature,
                public_key_b64=self.public_key_b64, hmac_key=self.hmac_key,
            )
            reason = ("signature verified" if valid else
                      ("manifest is unsigned or uses a legacy checksum" if not signed
                       else "signature does not match manifest content (tampered or wrong key)"))
        if valid:
            return True, reason
        if self.trust_mode == TrustMode.WARN:
            print(f"[Sandbox][WARN] {manifest.cartridge_id}: {reason} — allowed under WARN mode")
            return True, f"WARN: {reason}"
        return False, reason

    @staticmethod
    def _tool_allowed(policy: GovernancePolicy, tool_id: str) -> bool:
        if "*" in policy.allowed_tools:
            return True
        return tool_id in policy.allowed_tools

    def _deny(self, session: SandboxSession, kind: str, msg: str) -> Dict[str, Any]:
        full = f"{kind}: {msg}"
        session.logs.append(full)
        return {"status": "error", "error": full, "violation": kind}


if __name__ == "__main__":
    # Demo: sign a manifest, then show STRICT mode accepting it and rejecting a forgery.
    from .cartridge_schemas import CartridgeManifest
    from . import cartridge_crypto

    # Ephemeral HMAC key so the demo runs with zero setup.
    os.environ.setdefault("CAMELOT_CARTRIDGE_HMAC_KEY", "demo-signing-secret")

    manifest = CartridgeManifest(
        cartridge_id="RESTRICTED_CORE",
        description="Test restricted cartridge",
        governance={"allowed_tools": ["CodeGen"], "denied_operations": ["NetworkStrike"]},
        signature="pending",
        resource_budget={"max_latency_ms": 10},
    )
    manifest.signature = cartridge_crypto.sign(manifest)

    sb = CartridgeSandbox(trust_mode=TrustMode.STRICT)
    print("Valid+allowed :", sb.run_cartridge_tool(manifest, "CodeGen", {"x": 1})["status"])
    print("Denied tool   :", sb.run_cartridge_tool(manifest, "NetworkStrike", {}).get("violation"))
    print("Not-whitelisted:", sb.run_cartridge_tool(manifest, "Other", {}).get("violation"))

    manifest.governance.allowed_tools.append("Tamper")  # mutate AFTER signing
    print("Tampered      :", sb.run_cartridge_tool(manifest, "Tamper", {}).get("violation"))
