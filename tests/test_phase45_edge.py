"""Phase 4 MESH + Phase 5 EDGE acceptance tests (feasible tasks).

Covers the platform-agnostic mesh/edge modules: drone discovery (P4-T03),
swarm pinning (P5-T03), 4GB scarcity budget (P5-T04), voice ingress (P5-T05),
and preview drones (P5-T06). Environment-gated tasks (tsnet mesh P4-T01,
ml-kem migration P4-T04, memfd P4-T05, MicroVM P5-T02) are tracked separately.
"""
from __future__ import annotations

from control_plane.infra.empire_drone import DroneAnnounce, EmpireMesh
from control_plane.infra.preview_drone import PreviewDrone
from control_plane.infra.scarcity_protocol import GiB, ScarcityBreach, ScarcityManager
from control_plane.infra.swarm_pin import SwarmPinner
from control_plane.infra.voice_ingress import VoiceIngress, parse_transcript

# ── P4-T03 Empire Drone discovery/registration ───────────────────────────────

def test_drone_auto_registers_and_reaps():
    mesh = EmpireMesh(ttl_sec=10.0)
    mesh.register(DroneAnnounce("d1", "wasm", "100.64.0.2", ["wasm32-wasi"]), now=1000.0)
    mesh.register(DroneAnnounce("d2", "voice", "100.64.0.3", ["voice"]), now=1001.0)
    assert len(mesh) == 2
    # re-announce is idempotent
    mesh.register(DroneAnnounce("d1", "wasm", "100.64.0.2", ["wasm32-wasi"]), now=1002.0)
    assert len(mesh) == 2
    evicted = mesh.reap(now=1020.0)
    assert set(evicted) == {"d1", "d2"} and len(mesh) == 0


# ── P5-T03 Swarm pinning ──────────────────────────────────────────────────────

def test_swarm_pin_round_trips(tmp_path):
    pinner = SwarmPinner(root=tmp_path)
    addr = pinner.pin(b"edge pill")
    assert len(addr) == 64
    assert pinner.fetch(addr) == b"edge pill"
    assert pinner.pin(b"edge pill") == addr  # idempotent


# ── P5-T04 Scarcity protocol ──────────────────────────────────────────────────

def test_scarcity_envelope_and_reclaim():
    mgr = ScarcityManager()
    mgr.lease("a", 2 * GiB)
    b = mgr.lease("b", int(1.5 * GiB))
    assert b.bytes_zram_logical > 0  # overflowed to ZRAM
    try:
        mgr.lease("c", 4 * GiB)
        assert False, "expected ScarcityBreach"
    except ScarcityBreach:
        pass
    assert mgr.reclaim("a")
    assert mgr.lease("c", int(2.5 * GiB)).lease_id == "c"  # fits after reclaim


# ── P5-T05 Voice ingress ──────────────────────────────────────────────────────

def test_voice_transcript_to_intent():
    vi = parse_transcript("Hey Jarvis, please build a status dashboard.")
    assert vi.wake_word == "jarvis"
    assert vi.intent == "build a status dashboard"
    assert vi.is_command


def test_voice_dispatches_command():
    res = VoiceIngress().ingest_transcript("Camelot, build a small dashboard", auto_approve=True)
    assert res["dispatched"] and res["result"].complete


def test_voice_chatter_not_dispatched():
    res = VoiceIngress().ingest_transcript("Hermes, what a lovely day")
    assert not res["dispatched"]


# ── P5-T06 Preview drones ─────────────────────────────────────────────────────

def test_preview_pins_only_when_healthy(tmp_path):
    drone = PreviewDrone(swarm_root=tmp_path)
    ok = drone.deploy_and_pin("print('PREVIEW_OK')\n")
    assert ok.healthy and ok.pinned and ok.bzz_addr

    bad = drone.deploy_and_pin("raise SystemExit(1)\n")
    assert not bad.healthy and not bad.pinned and bad.blocked_reason
