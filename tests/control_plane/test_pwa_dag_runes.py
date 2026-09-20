import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "01_KERNEL") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "01_KERNEL"))

from control_plane.runes.runic_router import route_rune
from memory.cloudbrain_connector import route_by_domain


def test_forge_ui_dag_routing():
    res = route_rune("//FORGE_UI_DAG", "")
    assert res.rune == "//FORGE_UI_DAG"
    assert res.knight == "sir_boris"
    assert res.mode == "SWARM"
    meta = res.metadata
    assert meta["action"] == "forge_pwa_ecosystem_bootstrap_dag"
    assert len(meta["phases"]) == 8
    assert "Phase_0_Foundation" in meta["phases"]
    assert "Phase_7_Deployment_Gideon_Gate" in meta["phases"]


def test_forge_source_routing():
    res = route_rune("//FORGE_SOURCE", "Phase_1")
    assert res.rune == "//FORGE_SOURCE"
    assert res.knight == "sir_codex"
    assert res.mode == "KINETIC"
    meta = res.metadata
    assert meta["target_phase"] == "Phase_1"


def test_cloudbrain_pwa_domain_routing():
    ui_knights = route_by_domain(["pwa", "desktop_grid", "interface"])
    assert "SIR_BORIS" in ui_knights or "SIR_FORGE" in ui_knights or "LADY_GUINEVERE" in ui_knights

    vad_knights = route_by_domain(["audio", "vad", "webrtc"])
    assert "KICKBOX" in vad_knights or "SIR_HELIO" in vad_knights

    sec_knights = route_by_domain(["bio_auth", "security", "ed25519"])
    assert "SIR_SENTINEL" in sec_knights
