# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Bifrost → Sandbox Bridge — the governed dispatch seam
=====================================================
This is the keystone that connects the bifrost dispatch world (control_plane) to
the signed-cartridge governance world (this package). Without it, traffic sent via
bifrost bypasses every control we built; with it, a bifrost command that names a
cartridge + tool is turned into a fully **governed, authorized, audited** execution:

    inbound bytes
        │  1. HMAC verify (same WEBHOOK_SECRET / scheme as control_plane/bifrost_gateway
        │     and apps/bifrost/src/security.ts) — no new ingress surface
        ▼
    GovernedDispatch {cartridge_id, tool_id, params, principal}
        │  2. load the SIGNED manifest for cartridge_id
        ▼
    CartridgeSandbox.run_cartridge_tool
        │  3. TrustManager: signature → key-id/rotation/revocation
        │  4. governance: deny-list → HITL (RBAC cartridge:approve) → allow-list → budget
        │  5. ToolRegistry: REAL execution (not simulation)
        ▼
    result  (every decision already written to the tamper-evident audit log)

Transport-light by design (mirrors bifrost_gateway): the caller hands us the raw
signed body it already received on the gateway's HMAC webhook; we add no daemon.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from . import cartridge_rbac
from .cartridge_schemas import CartridgeManifest
from .sandbox import CartridgeSandbox, TrustMode
from .tool_registry import ToolRegistry


# ── Request schema ────────────────────────────────────────────────────────────
@dataclass
class GovernedDispatch:
    cartridge_id: str
    tool_id: str
    params: Dict[str, Any] = field(default_factory=dict)
    principal: Optional[str] = None      # who is dispatching (threads into RBAC + audit)
    nonce: str = ""                       # optional replay id

    @staticmethod
    def from_json(raw: str) -> "GovernedDispatch":
        d = json.loads(raw)
        return GovernedDispatch(
            cartridge_id=d["cartridge_id"],
            tool_id=d["tool_id"],
            params=d.get("params", {}),
            principal=d.get("principal"),
            nonce=d.get("nonce", ""),
        )


# ── HMAC bridge auth (identical scheme to control_plane/bifrost_gateway._sign) ─
def sign_body(raw: str, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), raw.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_body(raw: str, signature: str, secret: str) -> bool:
    if not secret or not signature:
        return False
    return hmac.compare_digest(sign_body(raw, secret), signature)


# ── Manifest loading ──────────────────────────────────────────────────────────
def packages_manifest_loader(packages_dir: str | Path) -> Callable[[str], Optional[CartridgeManifest]]:
    """Load a fabricated, signed manifest from packages/<cartridge_id>/manifest.json."""
    base = Path(packages_dir)

    def _load(cartridge_id: str) -> Optional[CartridgeManifest]:
        # Guard against path traversal in cartridge_id.
        safe = os.path.basename(cartridge_id)
        p = base / safe / "manifest.json"
        if not p.exists():
            return None
        try:
            return CartridgeManifest(**json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            return None
    return _load


ManifestLoader = Callable[[str], Optional[CartridgeManifest]]


# ── The bridge ────────────────────────────────────────────────────────────────
class BifrostCartridgeBridge:
    """Turns a signed bifrost command into a governed cartridge tool execution."""

    def __init__(
        self,
        *,
        manifest_loader: ManifestLoader,
        registry: Optional[ToolRegistry] = None,
        trust_manager: Optional[Any] = None,
        rbac: Optional[cartridge_rbac.RBACPolicy] = None,
        webhook_secret: Optional[str] = None,
        trust_mode: TrustMode = TrustMode.STRICT,
    ):
        self._load_manifest = manifest_loader
        self._registry = registry or ToolRegistry(with_builtins=True)
        self._rbac = rbac
        self._secret = webhook_secret if webhook_secret is not None else os.getenv("WEBHOOK_SECRET", "")

        # HITL gate is satisfied only by a principal holding cartridge:approve.
        approval = None
        if rbac is not None:
            approval = cartridge_rbac.make_rbac_approval(
                rbac, lambda cid, tool, params: self._current_principal)
        self._current_principal: Optional[str] = None

        self._sandbox = CartridgeSandbox(
            trust_mode=trust_mode,
            trust_manager=trust_manager,
            tool_executor=self._registry.executor,
            approval_callback=approval,
        )

    # ---- entry points ---------------------------------------------------------
    def handle_signed(self, raw_body: str, signature: str) -> Dict[str, Any]:
        """Verify the bridge HMAC, then dispatch. Use this on the gateway webhook path."""
        if not verify_body(raw_body, signature, self._secret):
            return {"status": "error", "violation": "BridgeAuthFailure",
                    "error": "invalid or missing HMAC signature"}
        try:
            dispatch = GovernedDispatch.from_json(raw_body)
        except (json.JSONDecodeError, KeyError) as e:
            return {"status": "error", "violation": "BadRequest",
                    "error": f"malformed dispatch: {e}"}
        return self.dispatch(dispatch)

    def dispatch(self, req: GovernedDispatch) -> Dict[str, Any]:
        """Dispatch an already-parsed request through the full governed stack."""
        manifest = self._load_manifest(req.cartridge_id)
        if manifest is None:
            return {"status": "error", "violation": "UnknownCartridge",
                    "error": f"no signed manifest for cartridge '{req.cartridge_id}'"}

        # Thread the dispatcher identity into the RBAC-backed HITL approval + audit.
        self._current_principal = req.principal
        try:
            result = self._sandbox.run_cartridge_tool(manifest, req.tool_id, req.params)
        finally:
            self._current_principal = None

        result.setdefault("cartridge_id", req.cartridge_id)
        result.setdefault("tool_id", req.tool_id)
        result.setdefault("principal", req.principal)
        return result


if __name__ == "__main__":
    # Minimal self-demo: sign → verify → dispatch through the real executor.
    from . import cartridge_crypto as cc

    os.environ.setdefault("CAMELOT_CARTRIDGE_HMAC_KEY", "bridge-demo-cartridge-key")
    secret = "bridge-demo-webhook"

    # A signed manifest allowing the built-in echo tool.
    m = CartridgeManifest(cartridge_id="DEMO", description="d", signature="pending",
                          governance={"allowed_tools": ["echo"]})
    m.signature = cc.sign(m)

    bridge = BifrostCartridgeBridge(
        manifest_loader=lambda cid: m if cid == "DEMO" else None,
        webhook_secret=secret,
    )
    body = json.dumps({"cartridge_id": "DEMO", "tool_id": "echo",
                       "params": {"value": "hello via bifrost"}, "principal": "demo"})
    good = bridge.handle_signed(body, sign_body(body, secret))
    print("valid signed dispatch :", good["status"], "->", good.get("result"))
    bad = bridge.handle_signed(body, "deadbeef")
    print("bad signature         :", bad["violation"])
