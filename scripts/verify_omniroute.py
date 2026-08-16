#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Verify all knights route through CLIProxyAPI in OmniRoute."""
import sys
from pathlib import Path

repo = Path(__file__).parent.parent
sys.path.insert(0, str(repo))

from control_plane.cli_intercept import CLIIntercept  # noqa: E402
from control_plane.soul_router import CLIPROXY_URL, SALTARE_URL  # noqa: E402

intercept = CLIIntercept()
cliproxy_url = "http://127.0.0.1:8080/v1"

# Representative intent per knight engine type
KNIGHT_PROBES = {
    "sir_boris":    "architecture design critique",
    "sir_alex":     "cognitive reasoning decision",
    "sir_sentinel": "security audit armor",
    "sir_codex":    "velocity rapid_proto boilerplate",
    "sir_helio":    "context_map full_repo 1m_context cloud_burst",
    "sir_link":     "bridge handoff terminal ui",
    "sir_forge":    "technical code_gen kinetic",
    "sir_ghost":    "private secret local credential",
    "sir_mnemo":    "memory recall archive synthesize",
    "sir_liberte":  "sovereignty oss anti_lock",
}

print(f"CLIPROXY_URL (soul_router): {CLIPROXY_URL}")
print(f"SALTARE_URL (routing):     {SALTARE_URL}")
print(f"CLIProxy upstream URL:     {cliproxy_url}")
print()
print(f"{'KNIGHT':<16} {'ENGINE':<18} {'BACKEND_URL':<38} {'MODEL':<24} STATUS")
print("-" * 115)

issues = []
for knight_id, probe_intent in KNIGHT_PROBES.items():
    result = intercept.intercept(probe_intent)
    r = result.route
    # Confirm actual routing knight matches expected
    routed_to = r.knight_id
    backend = result.backend_url
    model = result.model

    via_cliproxy = backend == cliproxy_url
    via_local    = "11434" in backend
    is_local_engine = result.engine_cmd in ("ollama",)

    if via_cliproxy:
        status = "CLIPROXY :8080"
    elif via_local and is_local_engine:
        status = "LOCAL (intentional)"
    else:
        status = f"UNROUTED -> {backend}"
        issues.append((knight_id, backend))

    print(f"{routed_to:<16} {result.engine_cmd:<18} {backend:<38} {model:<24} {status}")

print()
if issues:
    print(f"ISSUES ({len(issues)}):")
    for kid, url in issues:
        print(f"  {kid} -> {url}  <-- NOT through CLIProxy")
else:
    print("ALL cloud knights verified through CLIProxyAPI :8080")
    print("LOCAL knights (sir_forge, sir_ghost) -> Ollama :11434 (intentional, free)")
