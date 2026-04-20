"""Bifrost — Camelot-OS Sovereign Identity & Network Gate.

Three-layer access control for any Camelot entry point:

    1. LOCAL IDENTITY   — caller is the owner (getpass.getuser())
    2. TAILNET PEER     — if remote, source IP is in tailnet (100.64/10)
                          AND tailscale whois returns a trusted owner
    3. BIFROST TOKEN    — caller presents the shared secret from
                          ~/.camelot/bifrost.token (owner-only read)

Any caller must satisfy AT LEAST ONE of:
    A) layer 1 alone (local user on the owning host)
    B) layers 2 + 3 (tailnet peer presenting the token)

Third-party local processes running as another user are rejected.
Public-internet probes are rejected.
Tailnet peers without the token are rejected.
"""
from __future__ import annotations

import getpass
import hashlib
import hmac
import ipaddress
import os
import socket
import subprocess
import sys
from pathlib import Path

CAMELOT_OWNER = os.environ.get("CAMELOT_OWNER", "vizio")
TOKEN_PATH = Path.home() / ".camelot" / "bifrost.token"
TAILNET_CGNAT = ipaddress.ip_network("100.64.0.0/10")
TRUSTED_TAILNET_OWNERS = {"Cyberdad247@github", "Cyberdad247@"}


class AccessDenied(Exception):
    pass


def _read_token() -> str | None:
    try:
        return TOKEN_PATH.read_text(encoding="ascii").strip()
    except (FileNotFoundError, PermissionError):
        return None


def token_fingerprint() -> str:
    tok = _read_token()
    if not tok:
        return "no-token"
    return "sha256:" + hashlib.sha256(tok.encode()).hexdigest()[:16]


def verify_token(presented: str) -> bool:
    """Constant-time token comparison. False if no local token exists."""
    local = _read_token()
    if not local or not presented:
        return False
    return hmac.compare_digest(local.encode(), presented.encode())


def _is_loopback(ip: str | None) -> bool:
    if not ip:
        return True
    try:
        return ipaddress.ip_address(ip).is_loopback
    except ValueError:
        return False


def _is_tailnet(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip) in TAILNET_CGNAT
    except ValueError:
        return False


def _tailscale_whois(ip: str) -> str | None:
    try:
        out = subprocess.run(
            ["tailscale", "whois", ip],
            capture_output=True, text=True, timeout=2.5,
        )
        if out.returncode != 0:
            return None
        for line in out.stdout.splitlines():
            s = line.strip()
            if s.startswith("Name:") and "@" in s:
                return s.split("Name:", 1)[1].strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return None


def verify_caller(remote_addr: str | None = None,
                  presented_token: str | None = None,
                  strict: bool = True) -> tuple[bool, str]:
    """
    Decide whether the caller may awaken Camelot-OS.

    Args:
        remote_addr: source IP if this is a network invocation (None for local)
        presented_token: bifrost token header from remote caller
        strict: if False, warnings are returned but not raised

    Returns:
        (allowed, reason)
    """
    local_user = getpass.getuser()

    # Rule A: Local-host owner
    if _is_loopback(remote_addr):
        if local_user == CAMELOT_OWNER:
            return True, f"local-owner:{local_user}"
        return False, f"local-user-mismatch: {local_user!r} != {CAMELOT_OWNER!r}"

    # Rule B: Tailnet peer with valid bifrost token
    if not _is_tailnet(remote_addr):
        return False, f"non-tailnet-source: {remote_addr}"

    if not verify_token(presented_token or ""):
        return False, f"tailnet-peer-no-token: {remote_addr}"

    owner = _tailscale_whois(remote_addr)
    if owner is None:
        return False, f"tailnet-whois-failed: {remote_addr}"
    if owner not in TRUSTED_TAILNET_OWNERS:
        return False, f"tailnet-untrusted-owner: {owner}"

    return True, f"tailnet-peer:{remote_addr}:{owner}"


def enforce(remote_addr: str | None = None, presented_token: str | None = None):
    """Raise AccessDenied if the caller is not authorized."""
    ok, reason = verify_caller(remote_addr, presented_token)
    if not ok:
        raise AccessDenied(f"Bifrost gate: {reason}")
    return reason


def status_report() -> dict:
    """Machine-readable gate status for --json mode."""
    return {
        "owner": CAMELOT_OWNER,
        "current_user": getpass.getuser(),
        "hostname": socket.gethostname(),
        "token_present": _read_token() is not None,
        "token_fingerprint": token_fingerprint(),
        "token_path": str(TOKEN_PATH),
        "trusted_owners": sorted(TRUSTED_TAILNET_OWNERS),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(status_report(), indent=2))
    ok, reason = verify_caller()
    print(f"local-check: ok={ok} reason={reason}")
    sys.exit(0 if ok else 1)
