# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Bifrost Gateway Bridge — control-plane link to the TS Bifrost gateway (:3001).

The TS gateway (apps/bifrost) is the voice/webhook ingress + Microcubic swarm
runtime. This module is the Python control plane's curl-able handle on it:

  health()             — GET /health
  send_command(text)   — HMAC-signed POST /webhook/sms (inbound command inject)
  tail_swarm_events()  — read recent gateway/swarm events off the Hermes bus

The link is deliberately transport-light: outbound goes over the gateway's
existing HMAC-signed webhook (no new ingress surface), inbound observability
rides the file-based Hermes bus (control_plane/hermes_bridge.py), so there is
no new network daemon and the [[no-docker-microcubic-vm]] law is honored.

CLI:
    python -m control_plane.bifrost_gateway health
    python -m control_plane.bifrost_gateway send "add transaction 5000"
    python -m control_plane.bifrost_gateway events --last 20
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import urllib.error
import urllib.request
from typing import Any

from control_plane.hermes_bridge import HermesBus

GATEWAY_URL = os.environ.get("BIFROST_GATEWAY_URL", "http://127.0.0.1:3001")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

# Channel the gateway emits to (must match apps/bifrost/src/hermes.ts SWARM_EVENTS).
SWARM_EVENTS_CHANNEL = "swarm.events"

DEFAULT_TIMEOUT = 5.0


# ── Outbound: health + command injection ───────────────────────────────────

def health(timeout: float = DEFAULT_TIMEOUT) -> dict[str, Any]:
    """GET /health. Returns the parsed body plus an `ok` flag (never raises)."""
    url = f"{GATEWAY_URL}/health"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            parsed = json.loads(body) if body else {}
            return {"ok": resp.status == 200, "status_code": resp.status, **parsed}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status_code": exc.code, "error": exc.reason}
    except Exception as exc:  # connection refused, timeout, bad JSON, etc.
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def _sign(raw: str, secret: str) -> str:
    """HMAC-SHA256 hex digest, matching apps/bifrost/src/security.ts."""
    return hmac.new(secret.encode("utf-8"), raw.encode("utf-8"), hashlib.sha256).hexdigest()


def send_command(message: str, timeout: float = DEFAULT_TIMEOUT) -> dict[str, Any]:
    """Inject a command into the gateway via its HMAC-signed /webhook/sms route."""
    if not WEBHOOK_SECRET:
        return {"ok": False, "error": "WEBHOOK_SECRET not set in environment"}

    # The signature must cover the exact bytes the server reads as rawBody.
    raw = json.dumps({"message": message})
    signature = _sign(raw, WEBHOOK_SECRET)

    req = urllib.request.Request(
        f"{GATEWAY_URL}/webhook/sms",
        data=raw.encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-webhook-signature": signature,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            parsed = json.loads(body) if body else {}
            return {"ok": resp.status == 200, "status_code": resp.status, "body": parsed}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status_code": exc.code, "error": exc.reason}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


# ── Inbound: observe gateway/swarm events off the Hermes bus ────────────────

def tail_swarm_events(last_n: int = 20) -> list[dict]:
    """Read the most recent gateway/swarm events from the Hermes bus."""
    return HermesBus().read_channel(SWARM_EVENTS_CHANNEL, last_n=last_n)


# ── CLI ─────────────────────────────────────────────────────────────────────

def _main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Bifrost gateway control-plane bridge")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("health", help="GET /health")

    send_p = sub.add_parser("send", help="Inject an HMAC-signed command")
    send_p.add_argument("message", help="Command text, e.g. 'add transaction 5000'")

    events_p = sub.add_parser("events", help="Tail swarm/gateway events from Hermes")
    events_p.add_argument("--last", type=int, default=20)

    args = parser.parse_args(argv)

    if args.cmd == "health":
        print(json.dumps(health(), indent=2))
    elif args.cmd == "send":
        print(json.dumps(send_command(args.message), indent=2))
    elif args.cmd == "events":
        for ev in tail_swarm_events(args.last):
            print(json.dumps(ev))
    else:
        parser.print_help()


if __name__ == "__main__":
    _main()
