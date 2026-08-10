"""OMEGA Defense Nexus Phase 6 acceptance tests — SWARM + Hermes Fusion."""
import importlib.util as _ilu
import sys
from pathlib import Path

CAMELOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMELOT))

spec = _ilu.spec_from_file_location(
    "nano_swarm_runtime",
    CAMELOT / "control_plane" / "infra" / "nano_swarm_runtime.py",
)
_mod = _ilu.module_from_spec(spec)
sys.modules["nano_swarm_runtime"] = _mod
spec.loader.exec_module(_mod)

OmegaSwarm = _mod.OmegaSwarm
OmegaSwarmNode = _mod.OmegaSwarmNode
OMEGA_CHANNEL_MAP = _mod.OMEGA_CHANNEL_MAP
get_omega_swarm = _mod.get_omega_swarm


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_omega_swarm_has_five_nodes():
    swarm = OmegaSwarm()
    assert len(swarm.nodes) == 5


def test_omega_swarm_node_ids():
    swarm = OmegaSwarm()
    expected = {"swarm.colony", "swarm.compress", "swarm.organize",
                "swarm.shadow", "swarm.dependency"}
    assert set(swarm.nodes.keys()) == expected


def test_omega_channel_mapping():
    assert OMEGA_CHANNEL_MAP["swarm.colony"] == "colony.risk"
    assert OMEGA_CHANNEL_MAP["swarm.shadow"] == "shadow.threats"
    assert OMEGA_CHANNEL_MAP["swarm.dependency"] == "dependency.updates"


def test_dispatch_increments_event_count():
    swarm = OmegaSwarm()
    swarm.dispatch("colony.risk", {"risk_score": 100.0, "delta": 20.0})
    node = swarm.nodes["swarm.colony"]
    assert node.state.events_processed == 1
    assert node.state.status == "ACTIVE"


def test_dispatch_unknown_channel_is_silent():
    swarm = OmegaSwarm()
    # No exception should be raised
    swarm.dispatch("unknown.channel", {"data": "test"})
    for n in swarm.nodes.values():
        assert n.state.events_processed == 0


def test_status_returns_all_five():
    swarm = OmegaSwarm()
    rows = swarm.status()
    assert len(rows) == 5
    for row in rows:
        assert "node_id" in row
        assert "channel" in row
        assert "status" in row
        assert "events" in row


def test_shadow_node_processes_threat():
    swarm = OmegaSwarm()
    swarm.dispatch("shadow.threats", {"critical_count": 3, "vectors": []})
    node = swarm.nodes["swarm.shadow"]
    assert node.state.events_processed == 1
    assert node.state.status == "ACTIVE"


def test_singleton_swarm_is_same_instance():
    # Reset singleton for test isolation
    _mod._SINGLETON_SWARM = None
    s1 = get_omega_swarm()
    s2 = get_omega_swarm()
    assert s1 is s2
