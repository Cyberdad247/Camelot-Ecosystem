# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Cartridge RBAC — Lifecycle Authorization (who may do what)
==========================================================
The trust lifecycle (cartridge_trust) answers "is this cartridge genuine?". RBAC
answers the orthogonal enterprise question: "is THIS PRINCIPAL allowed to perform
this LIFECYCLE OPERATION?" — fabricate, sign, approve (HITL), rotate/revoke keys,
recall cartridges, read the audit log.

This deliberately reuses the existing knight/tier principal model in
``03_VAULT/training/configs/config/access_matrix.json`` (see control_plane/rbac_matrix.py,
which governs a different axis — execution modes/domains). Here, an OMEGA-tier
knight bridges to the ``admin`` role, and a cartridge-specific overlay file grants
finer lifecycle roles to service accounts and humans.

Capabilities
------------
    cartridge:fabricate   build a new cartridge
    cartridge:sign        produce a trusted signature
    cartridge:approve     satisfy a HITL_required gate
    key:rotate            rotate a signing key
    key:revoke            revoke a compromised key
    cartridge:revoke      recall a cartridge / signature
    audit:read            read the audit trail
    *                     all of the above (admin)

Default roles → capabilities
----------------------------
    admin              *
    security-officer   key:rotate, key:revoke, cartridge:revoke, audit:read
    release-engineer   cartridge:fabricate, cartridge:sign
    approver           cartridge:approve
    auditor            audit:read

Principal overlay (env CAMELOT_CARTRIDGE_RBAC, default ~/.camelot/cartridge_rbac.json)
-------------------------------------------------------------------------------------
    {
      "principals": {
        "release_bot":   {"roles": ["release-engineer"]},
        "dame_sparkle":  {"roles": ["approver"]},
        "alice":         {"roles": ["release-engineer"], "grants": ["cartridge:approve"]},
        "contractor":    {"roles": ["release-engineer"], "deny": ["cartridge:sign"]}
      },
      "role_capabilities": { "custom-role": ["cartridge:fabricate"] }
    }

Least privilege: an unknown principal has NO capabilities. ``deny`` always wins.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Callable, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KEY_DIR = Path(os.path.expanduser("~")) / ".camelot"

# ── Capabilities ──────────────────────────────────────────────────────────────
CAP_FABRICATE = "cartridge:fabricate"
CAP_SIGN = "cartridge:sign"
CAP_APPROVE = "cartridge:approve"
CAP_KEY_ROTATE = "key:rotate"
CAP_KEY_REVOKE = "key:revoke"
CAP_CARTRIDGE_REVOKE = "cartridge:revoke"
CAP_AUDIT_READ = "audit:read"
WILDCARD = "*"

ALL_CAPS = frozenset({
    CAP_FABRICATE, CAP_SIGN, CAP_APPROVE, CAP_KEY_ROTATE,
    CAP_KEY_REVOKE, CAP_CARTRIDGE_REVOKE, CAP_AUDIT_READ,
})

DEFAULT_ROLE_CAPS: dict[str, set[str]] = {
    "admin": {WILDCARD},
    "security-officer": {CAP_KEY_ROTATE, CAP_KEY_REVOKE, CAP_CARTRIDGE_REVOKE, CAP_AUDIT_READ},
    "release-engineer": {CAP_FABRICATE, CAP_SIGN},
    "approver": {CAP_APPROVE},
    "auditor": {CAP_AUDIT_READ},
}

# Path to the existing knight/tier matrix (env-overridable).
_ACCESS_MATRIX_PATH = Path(os.getenv("CAMELOT_ACCESS_MATRIX") or (
    Path(__file__).resolve().parent.parent.parent
    / "03_VAULT" / "training" / "configs" / "config" / "access_matrix.json"
))


class AuthorizationError(PermissionError):
    """Raised when a principal is not permitted to perform a lifecycle operation."""


class RBACPolicy:
    def __init__(self, path: Optional[str | Path] = None, *, bridge_omega: bool = True):
        self.path = Path(path or os.getenv("CAMELOT_CARTRIDGE_RBAC")
                         or (KEY_DIR / "cartridge_rbac.json"))
        self.bridge_omega = bridge_omega
        self.principals: dict[str, dict[str, Any]] = {}
        self.role_caps: dict[str, set[str]] = {k: set(v) for k, v in DEFAULT_ROLE_CAPS.items()}
        self._omega_knights: set[str] = set()
        self._load()

    # ---- loading --------------------------------------------------------------
    def _load(self) -> None:
        if self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                self.principals = raw.get("principals", {})
                for role, caps in (raw.get("role_capabilities") or {}).items():
                    self.role_caps[role] = set(caps)
            except (json.JSONDecodeError, OSError):
                pass
        if self.bridge_omega:
            self._omega_knights = self._load_omega_knights()

    @staticmethod
    def _load_omega_knights() -> set[str]:
        try:
            m = json.loads(_ACCESS_MATRIX_PATH.read_text(encoding="utf-8"))
            return {k for k, v in m.get("knights", {}).items()
                    if str(v.get("tier", "")).upper() == "OMEGA"}
        except (json.JSONDecodeError, OSError):
            return set()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Persist only the overlay-owned data (never the bridged defaults).
        custom_roles = {r: sorted(c) for r, c in self.role_caps.items()
                        if r not in DEFAULT_ROLE_CAPS}
        self.path.write_text(json.dumps(
            {"principals": self.principals, "role_capabilities": custom_roles}, indent=2),
            encoding="utf-8")

    # ---- admin --------------------------------------------------------------
    @staticmethod
    def _norm(principal: str) -> str:
        return principal.lower().replace("-", "_").replace(" ", "_")

    def assign(self, principal: str, roles: list[str], *,
               grants: Optional[list[str]] = None, deny: Optional[list[str]] = None) -> None:
        self.principals[principal] = {
            "roles": roles,
            "grants": grants or [],
            "deny": deny or [],
        }
        self.save()

    # ---- resolution -----------------------------------------------------------
    def _record(self, principal: str) -> Optional[dict[str, Any]]:
        if principal in self.principals:
            return self.principals[principal]
        # exact-miss → try normalized match against overlay keys
        n = self._norm(principal)
        for k, v in self.principals.items():
            if self._norm(k) == n:
                return v
        return None

    def _is_omega(self, principal: str) -> bool:
        n = self._norm(principal)
        return any(self._norm(k) == n for k in self._omega_knights)

    def capabilities_of(self, principal: str) -> set[str]:
        """Effective granted capabilities (before deny is applied)."""
        caps: set[str] = set()
        rec = self._record(principal)
        if rec:
            for role in rec.get("roles", []):
                caps |= self.role_caps.get(role, set())
            caps |= set(rec.get("grants", []))
        if self.bridge_omega and self._is_omega(principal):
            caps.add(WILDCARD)
        return caps

    def _deny_set(self, principal: str) -> set[str]:
        rec = self._record(principal)
        return set(rec.get("deny", [])) if rec else set()

    def authorize(self, principal: Optional[str], capability: str) -> tuple[bool, str]:
        """Return (allowed, reason). Unknown principal → denied (least privilege)."""
        if not principal:
            return False, "no principal supplied"
        if capability in self._deny_set(principal):
            return False, f"'{principal}' is explicitly denied '{capability}'"
        caps = self.capabilities_of(principal)
        if not caps:
            return False, f"'{principal}' has no capabilities (unknown or unassigned principal)"
        if WILDCARD in caps or capability in caps:
            return True, f"'{principal}' granted '{capability}'"
        return False, f"'{principal}' lacks '{capability}' (has: {sorted(caps)})"

    def require(self, principal: Optional[str], capability: str) -> None:
        ok, reason = self.authorize(principal, capability)
        if not ok:
            raise AuthorizationError(reason)


def make_rbac_approval(policy: RBACPolicy, approver_resolver: Callable[[str, str, dict], Optional[str]]):
    """
    Build a sandbox ApprovalCallback that only approves a HITL gate when the resolved
    approver holds ``cartridge:approve``. ``approver_resolver(cartridge_id, tool_id, params)``
    returns the principal who is approving (e.g. from a UI/session), or None.
    """
    def _approve(cartridge_id: str, tool_id: str, params: dict) -> bool:
        principal = approver_resolver(cartridge_id, tool_id, params)
        ok, _ = policy.authorize(principal, CAP_APPROVE)
        return ok
    return _approve


# ── CLI ───────────────────────────────────────────────────────────────────────
def _main(argv: Optional[list[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="cartridge_rbac", description="Cartridge lifecycle RBAC")
    sub = ap.add_subparsers(dest="cmd")

    asg = sub.add_parser("assign", help="assign roles to a principal")
    asg.add_argument("principal")
    asg.add_argument("--roles", nargs="+", required=True)
    asg.add_argument("--grants", nargs="*", default=[])
    asg.add_argument("--deny", nargs="*", default=[])

    ck = sub.add_parser("check", help="check a capability for a principal")
    ck.add_argument("principal"); ck.add_argument("capability")

    who = sub.add_parser("whoami", help="show a principal's effective capabilities")
    who.add_argument("principal")

    sub.add_parser("roles", help="list default roles and their capabilities")

    args = ap.parse_args(argv)
    pol = RBACPolicy()

    if args.cmd == "assign":
        pol.assign(args.principal, args.roles, grants=args.grants, deny=args.deny)
        print(f"Assigned {args.principal}: roles={args.roles} grants={args.grants} deny={args.deny}")
    elif args.cmd == "check":
        ok, reason = pol.authorize(args.principal, args.capability)
        print(("✅ ALLOW " if ok else "❌ DENY  ") + reason)
        return 0 if ok else 1
    elif args.cmd == "whoami":
        caps = pol.capabilities_of(args.principal)
        omega = pol.bridge_omega and pol._is_omega(args.principal)
        print(f"{args.principal}: {sorted(caps) or '(none)'}" + (" [OMEGA-bridged]" if omega else ""))
    elif args.cmd == "roles":
        for r, c in DEFAULT_ROLE_CAPS.items():
            print(f"  {r:18s} {sorted(c)}")
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
