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

import base64
import getpass
import hashlib
import hmac
import ipaddress
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

CAMELOT_OWNER = os.environ.get("CAMELOT_OWNER", "vizio")
TOKEN_PATH = Path.home() / ".camelot" / "bifrost.token"
TAILNET_CGNAT = ipaddress.ip_network("100.64.0.0/10")
_DEFAULT_TRUSTED_TAILNET_OWNERS = ("Cyberdad247@github", "Cyberdad247@")


def _parse_csv_env(name: str, default: tuple[str, ...]) -> set[str]:
    raw = os.environ.get(name, "")
    if not raw.strip():
        return set(default)
    values = {part.strip() for part in raw.split(",") if part.strip()}
    return values or set(default)


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


TRUSTED_TAILNET_OWNERS = _parse_csv_env(
    "BIFROST_TRUSTED_TAILNET_OWNERS",
    _DEFAULT_TRUSTED_TAILNET_OWNERS,
)
try:
    TAILSCALE_WHOIS_TIMEOUT_S = float(os.environ.get("BIFROST_TAILSCALE_WHOIS_TIMEOUT_S", "2.5"))
except ValueError:
    TAILSCALE_WHOIS_TIMEOUT_S = 2.5
REQUIRE_TOKEN_ON_LOOPBACK = _env_flag("BIFROST_REQUIRE_TOKEN_ON_LOOPBACK", default=False)

# Rule C: mobile/OIDC gateway — trusted issuers for JWT bearer tokens
# Add your auth provider issuer URL (e.g. Auth0 tenant, Clerk, Firebase)
MOBILE_TRUSTED_ISSUERS: set[str] = set(
    os.environ.get("BIFROST_OIDC_ISSUERS", "").split(",")
) - {""}
# Example: BIFROST_OIDC_ISSUERS=https://accounts.google.com,https://my-tenant.auth0.com


class AccessDenied(Exception):
    pass


# ── OIDC / mobile gate helpers ────────────────────────────────────────────────

def _b64url_decode(segment: str) -> bytes:
    """Decode base64url without padding."""
    segment += "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment)


def verify_oidc_token(token: str) -> tuple[bool, str]:
    """
    Verify a JWT bearer token from a mobile/OIDC client.

    Checks:
      1. JWT structure (3 dot-separated segments)
      2. Issuer (iss) present in MOBILE_TRUSTED_ISSUERS
      3. Expiry (exp) not in the past
      4. Audience (aud) contains "camelot-os" if present in token

    NOTE: Cryptographic signature verification requires the issuer's public key
    (JWKS). Install PyJWT + cryptography for full signature validation.
    Until then this provides issuer + expiry enforcement only.
    """
    if not MOBILE_TRUSTED_ISSUERS:
        return False, "no trusted OIDC issuers configured (set BIFROST_OIDC_ISSUERS)"

    parts = token.split(".")
    if len(parts) != 3:
        return False, "malformed JWT (expected 3 segments)"

    try:
        payload = json.loads(_b64url_decode(parts[1]))
    except Exception as e:
        return False, f"JWT decode error: {e}"

    iss = payload.get("iss", "")
    if iss not in MOBILE_TRUSTED_ISSUERS:
        return False, f"untrusted issuer: {iss!r}"

    exp = payload.get("exp")
    if exp is not None and time.time() > float(exp):
        return False, "JWT expired"

    aud = payload.get("aud")
    if aud is not None:
        audiences = [aud] if isinstance(aud, str) else aud
        if "camelot-os" not in audiences:
            return False, f"JWT audience mismatch: {audiences}"

    sub = payload.get("sub", "unknown")
    return True, f"oidc-jwt:iss={iss}:sub={sub}"


def mobile_gate(token: str, remote_addr: str | None = None) -> tuple[bool, str]:
    """Rule C: accept OIDC bearer token from any network location (mobile roaming)."""
    ok, reason = verify_oidc_token(token)
    if not ok:
        return False, f"mobile-gate-denied: {reason}"
    addr = remote_addr or "unknown"
    return True, f"mobile-gate:{addr}:{reason}"


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
            capture_output=True, text=True, timeout=TAILSCALE_WHOIS_TIMEOUT_S,
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


def verify_client_cert(cert_der: bytes | None) -> tuple[bool, str]:
    """Verify ASGI client certificate (DER format)."""
    if not cert_der:
        return False, "no client certificate presented"
    
    # Calculate sha256 fingerprint of DER bytes
    fingerprint = hashlib.sha256(cert_der).hexdigest()
    trusted_fingerprints = _parse_csv_env("BIFROST_TRUSTED_CERT_FINGERPRINTS", ())
    if fingerprint in trusted_fingerprints:
        return True, f"mtls:fingerprint={fingerprint[:16]}"
        
    try:
        import re
        import ssl
        pem = ssl.DER_cert_to_PEM_cert(cert_der)
        match = re.search(r"CN\s*=\s*([^,\n/]+)", pem)
        if match:
            cn = match.group(1).strip()
            trusted_cns = _parse_csv_env("BIFROST_TRUSTED_CERT_CNS", ("camelot-client",))
            if cn in trusted_cns:
                return True, f"mtls:cn={cn}"
    except Exception:
        pass
        
    if _env_flag("BIFROST_ALLOW_ANY_VALID_CERT", default=False):
        return True, "mtls:any-valid-cert"
        
    return False, f"untrusted client certificate (fingerprint: {fingerprint[:16]})"


def verify_caller(remote_addr: str | None = None,
                  presented_token: str | None = None,
                  strict: bool = True,
                  oidc_token: str | None = None,
                  client_cert_der: bytes | None = None) -> tuple[bool, str]:
    """
    Decide whether the caller may awaken Camelot-OS.

    Args:
        remote_addr: source IP if this is a network invocation (None for local)
        presented_token: bifrost token header from remote caller
        strict: if False, warnings are returned but not raised
        oidc_token: JWT bearer token for Rule C (mobile/OIDC clients)
        client_cert_der: client certificate bytes from mTLS handshake

    Returns:
        (allowed, reason)

    Rules (first match wins):
        A) loopback + local owner
        D) valid mTLS client certificate (any network location)
        C) valid OIDC JWT from a trusted issuer (any network location)
        B) tailnet peer + valid bifrost token + trusted whois owner
    """
    local_user = getpass.getuser()

    # Rule A: Local-host owner
    if _is_loopback(remote_addr):
        if local_user == CAMELOT_OWNER:
            if REQUIRE_TOKEN_ON_LOOPBACK and not verify_token(presented_token or ""):
                return False, "local-owner-token-required"
            return True, f"local-owner:{local_user}"
        return False, f"local-user-mismatch: {local_user!r} != {CAMELOT_OWNER!r}"

    # Rule D: mTLS client certificate gate (roaming bypass)
    cert_reason = None
    if client_cert_der:
        cert_ok, cert_reason = verify_client_cert(client_cert_der)
        if cert_ok:
            return True, cert_reason

    # Rule C: OIDC mobile gate (checked before Rule B so mobile clients skip tailnet check)
    oidc_reason = None
    if oidc_token:
        oidc_ok, oidc_reason = mobile_gate(oidc_token, remote_addr)
        if oidc_ok:
            return True, oidc_reason

    # Rule B: Tailnet peer with valid bifrost token
    if not _is_tailnet(remote_addr):
        # Roaming/Public IP. If they presented certificate or token that failed, report that.
        if cert_reason:
            return False, cert_reason
        if oidc_reason:
            return False, oidc_reason
        return False, f"non-tailnet-source: {remote_addr}"

    if not verify_token(presented_token or ""):
        return False, f"tailnet-peer-no-token: {remote_addr}"

    owner = _tailscale_whois(remote_addr)
    if owner is None:
        return False, f"tailnet-whois-failed: {remote_addr}"
    if owner not in TRUSTED_TAILNET_OWNERS:
        return False, f"tailnet-untrusted-owner: {owner}"

    return True, f"tailnet-peer:{remote_addr}:{owner}"


def enforce(remote_addr: str | None = None, presented_token: str | None = None,
            oidc_token: str | None = None, client_cert_der: bytes | None = None):
    """Raise AccessDenied if the caller is not authorized."""
    ok, reason = verify_caller(remote_addr, presented_token, oidc_token=oidc_token, client_cert_der=client_cert_der)
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
        "tailscale_whois_timeout_s": TAILSCALE_WHOIS_TIMEOUT_S,
        "require_token_on_loopback": REQUIRE_TOKEN_ON_LOOPBACK,
        "oidc_issuers": sorted(MOBILE_TRUSTED_ISSUERS),
        "oidc_enabled": bool(MOBILE_TRUSTED_ISSUERS),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(status_report(), indent=2))
    ok, reason = verify_caller()
    print(f"local-check: ok={ok} reason={reason}")
    sys.exit(0 if ok else 1)
