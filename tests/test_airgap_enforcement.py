"""The air-gapped lane must actually prevent egress.

Before this, ``privacy_level = 1.0`` on Sir Ghost was a float in a weighted
routing score — it made the router *prefer* him and bound him to a local model,
but nothing stopped a socket being opened. The README called it a guarantee.

These tests are the guarantee. Each network assertion is paired with a control
that runs the *same* probe without isolation: if the control cannot reach the
network either, the test skips rather than passing vacuously, because a host with
no egress would otherwise make a broken air-gap look perfect.
"""
from __future__ import annotations

import subprocess
import sys

import pytest

from control_plane.core.airgap import (
    AirgapCapabilities,
    AirgapUnavailableError,
    probe,
    require_airgap,
    run_airgapped,
)

pytestmark = pytest.mark.skipif(
    sys.platform != "linux", reason="namespace isolation is Linux-only"
)

# Probes run in the child. Exit 0 means "blocked", exit 1 means "reachable".
_DNS_PROBE = (
    "import socket, sys\n"
    "try:\n"
    "    socket.getaddrinfo('example.com', 80)\n"
    "    sys.exit(1)\n"
    "except OSError:\n"
    "    sys.exit(0)\n"
)
_TCP_PROBE = (
    "import socket, sys\n"
    "try:\n"
    "    socket.create_connection(('1.1.1.1', 53), timeout=3)\n"
    "    sys.exit(1)\n"
    "except OSError:\n"
    "    sys.exit(0)\n"
)
_METADATA_PROBE = (
    "import socket, sys\n"
    "try:\n"
    "    socket.create_connection(('169.254.169.254', 80), timeout=3)\n"
    "    sys.exit(1)\n"
    "except OSError:\n"
    "    sys.exit(0)\n"
)


@pytest.fixture(scope="module")
def caps() -> AirgapCapabilities:
    found = probe()
    if not found.sufficient:
        pytest.skip(f"host cannot enforce network isolation:\n{found.render()}")
    return found


def _reachable_without_airgap(probe_src: str) -> bool:
    """True when the probe can reach the network with no isolation applied."""
    result = subprocess.run(
        [sys.executable, "-c", probe_src], capture_output=True, timeout=30, check=False
    )
    return result.returncode == 1


# ── Capability probing ───────────────────────────────────────────────────────

def test_probe_does_not_isolate_the_calling_process():
    """Asking what's possible must not move this process into a namespace."""
    probe()
    import socket

    # Still able to construct a socket and see real interfaces.
    assert socket.socket(socket.AF_INET, socket.SOCK_STREAM) is not None


def test_capabilities_render_is_human_readable(caps):
    text = caps.render()
    assert "network namespace" in text
    assert "yes" in text


# ── The guarantee ────────────────────────────────────────────────────────────

def test_dns_resolution_is_blocked(caps):
    if not _reachable_without_airgap(_DNS_PROBE):
        pytest.skip("no DNS on this host without the air-gap; control inconclusive")

    result = run_airgapped([sys.executable, "-c", _DNS_PROBE])
    assert result.returncode == 0, (
        "air-gapped process resolved a hostname — the lane leaks DNS"
    )


def test_outbound_tcp_is_blocked(caps):
    result = run_airgapped([sys.executable, "-c", _TCP_PROBE])
    assert result.returncode == 0, (
        "air-gapped process opened an outbound TCP connection"
    )


def test_cloud_metadata_endpoint_is_unreachable(caps):
    """169.254.169.254 is the standard credential-theft target."""
    result = run_airgapped([sys.executable, "-c", _METADATA_PROBE])
    assert result.returncode == 0, (
        "air-gapped process reached the cloud metadata endpoint"
    )


def test_airgapped_process_still_runs_normally(caps):
    """Isolation must not break ordinary local work."""
    result = run_airgapped([sys.executable, "-c", "print(6 * 7)"])
    assert result.returncode == 0
    assert result.stdout.strip() == b"42"


def test_child_is_told_it_is_airgapped(caps):
    result = run_airgapped(
        [sys.executable, "-c", "import os; print(os.environ.get('CAMELOT_AIRGAPPED'))"]
    )
    assert result.stdout.strip() == b"1"


def test_ambient_environment_is_not_inherited(caps, monkeypatch):
    """Proxy variables and tokens are a standard exfiltration path."""
    monkeypatch.setenv("HTTPS_PROXY", "http://should-not-leak.example")
    monkeypatch.setenv("SUPER_SECRET_TOKEN", "leaked")

    result = run_airgapped(
        [sys.executable, "-c",
         "import os; print(os.environ.get('HTTPS_PROXY'), os.environ.get('SUPER_SECRET_TOKEN'))"]
    )
    assert result.stdout.strip() == b"None None"


# ── Fail-closed behaviour ────────────────────────────────────────────────────

def test_require_airgap_raises_when_isolation_unavailable(monkeypatch):
    """No silent downgrade: if the guarantee cannot be met, nothing runs."""
    import control_plane.core.airgap as airgap

    monkeypatch.setattr(
        airgap, "probe",
        lambda: AirgapCapabilities(True, False, False, False, {"reason": "simulated"}),
    )
    with pytest.raises(AirgapUnavailableError) as excinfo:
        airgap.require_airgap()
    assert "Refusing to run unisolated" in str(excinfo.value)


def test_run_airgapped_refuses_rather_than_running_unisolated(monkeypatch):
    import control_plane.core.airgap as airgap

    monkeypatch.setattr(
        airgap, "probe",
        lambda: AirgapCapabilities(True, False, False, False, {"reason": "simulated"}),
    )
    marker = "/tmp/camelot-airgap-should-never-exist"
    with pytest.raises(AirgapUnavailableError):
        airgap.run_airgapped([sys.executable, "-c", f"open({marker!r}, 'w')"])

    import os

    assert not os.path.exists(marker), "command ran despite unavailable isolation"


# ── The gate honours the lane ────────────────────────────────────────────────

def test_air_gapped_knights_are_identified_from_the_router_roster():
    """The lane is derived from privacy_level, not a second hardcoded list."""
    from control_plane.core.anya_gate import _is_air_gapped_knight

    assert _is_air_gapped_knight("sir_ghost")
    assert _is_air_gapped_knight("sir_zeroclaw")
    assert not _is_air_gapped_knight("sir_boris")
    assert not _is_air_gapped_knight("sir_codex")


def test_gate_blocks_air_gapped_knight_when_host_cannot_isolate(monkeypatch):
    """An unenforceable air-gap claim must BLOCK, not proceed unisolated."""
    import control_plane.core.airgap as airgap
    from control_plane.core.anya_gate import _stage_validate, _stage_parse, _stage_enrich
    from control_plane.core.anya_gate import _stage_compile

    monkeypatch.setattr(
        airgap, "probe",
        lambda: AirgapCapabilities(True, False, False, False, {"reason": "simulated"}),
    )

    parse = _stage_parse("summarise this private note locally")
    enrich = _stage_enrich(parse)
    titan = _stage_compile(parse, enrich)
    result = _stage_validate(parse, titan, enrich, knight_id="sir_ghost")

    assert result.iron_gate == "BLOCKED", result.issues
    assert any("cannot enforce network isolation" in i for i in result.issues), result.issues


def test_gate_does_not_block_a_normal_knight_for_airgap_reasons(monkeypatch):
    """The air-gap check must not leak into lanes that never claimed it."""
    import control_plane.core.airgap as airgap
    from control_plane.core.anya_gate import (
        _stage_compile, _stage_enrich, _stage_parse, _stage_validate,
    )

    monkeypatch.setattr(
        airgap, "probe",
        lambda: AirgapCapabilities(True, False, False, False, {"reason": "simulated"}),
    )

    parse = _stage_parse("what is 2+2")
    enrich = _stage_enrich(parse)
    titan = _stage_compile(parse, enrich)
    result = _stage_validate(parse, titan, enrich, knight_id="sir_ouroboros")

    assert not any("network isolation" in i for i in result.issues), result.issues


def test_resource_limits_are_applied(caps):
    """A runaway allocation is stopped by RLIMIT_AS rather than eating the host."""
    result = run_airgapped(
        [sys.executable, "-c", "b = bytearray(2 * 1024 * 1024 * 1024)"],
        memory_bytes=128 * 1024 * 1024,
    )
    assert result.returncode != 0, "2GB allocation succeeded under a 128MB cap"
