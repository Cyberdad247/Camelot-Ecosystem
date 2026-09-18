import json
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "vfs"))
sys.path.insert(0, str(REPO_ROOT / "01_KERNEL"))


def test_sir_helios_session_keepalive_cron():
    """Verify Sir Helios responsibility to keep session alive as a cron job."""
    from control_plane.dispatch.session_keepalive_cron import helios_keepalive_daemon, SessionKeepAliveReport
    from control_plane.infra.knight_registry import ArchLibrarianRegistry

    # 1. Verify keepalive tick execution
    report = helios_keepalive_daemon.execute_keepalive_tick()
    assert report["guardian"] == "SIR_HELIOS"
    assert report["status"] in ("HEALTHY_ALIVE", "NO_LOCAL_STORAGE_FOUND", "EXPIRATION_IMMINENT", "REMOTE_UNSYNC", "PARSE_ERROR")
    assert report["cron_interval_minutes"] > 0
    assert report["last_ping_status"] in ("PULSE_ACKNOWLEDGED", "UNKNOWN")

    # 1b. Verify Google-side prime-brain visibility (file-fresh != Google-valid)
    assert report["remote_sync"] in ("SYNCED", "REMOTE_UNSYNC_LOCAL_FALLBACK", "REMOTE_UNREACHABLE", "PROBE_TIMEOUT", "UNKNOWN")
    if report["remote_sync"] == "REMOTE_UNSYNC_LOCAL_FALLBACK":
        assert report["status"] == "REMOTE_UNSYNC"
        assert any("notebooklm login" in a for a in report["alerts"])

    # 2. Verify state persistence
    state_file = REPO_ROOT / "03_VAULT" / "runtime_state" / "helios_session_keepalive.json"
    assert state_file.exists()

    # 3. Verify character sheet assigns session keepalive cron responsibility
    reg = ArchLibrarianRegistry()
    helios = reg.summon_knight("SIR_HELIOS")
    assert helios is not None
    assert any("Session Alive Cron Job" in r for r in helios.responsibilities)
    assert helios.cron_schedule is not None
    assert "cron_guardian" in helios.domain_tags


def test_sir_sonus_multivoice_router_engineer_responsibilities():
    """Verify Sir Sonus engineering responsibilities for Multivoice persona router and all aspects."""
    from control_plane.infra.knight_registry import ArchLibrarianRegistry
    from control_plane.runes.runic_router import route_rune

    reg = ArchLibrarianRegistry()
    sonus = reg.summon_knight("SIR_SONUS")
    assert sonus is not None
    assert sonus.knight_id == "SIR_SONUS"
    assert "Lead Engineer of Multivoice Persona Router" in sonus.title or "Lead Engineer" in sonus.role
    assert any("Multivoice Persona Router" in r for r in sonus.responsibilities)
    assert any("Go Kinetic Switchboard" in r for r in sonus.responsibilities)
    assert any("Fonoster PBX" in r for r in sonus.responsibilities)
    assert "multivoice_router" in sonus.domain_tags

    # Verify runic routing binds voice to sir_sonus
    res = route_rune("//MULTIVOICE_ROUTE", "Synthesize dialogue for Lady Mnemosyne")
    assert res.metadata.get("operator") == "sir_sonus"
    assert res.metadata.get("action") == "multivoice_route"


def test_lady_mnemosyne_active_triggered_sync_loop():
    """Verify Lady Mnemosyne active sync triggered loop per 5 changes to Cloudbrain system."""
    from vfs.worldtree_vkg_sync import LadyMnemosyneTriggerLoop, TRIGGER_STATE_PATH
    from control_plane.infra.knight_registry import ArchLibrarianRegistry

    # 1. Verify character sheet
    reg = ArchLibrarianRegistry()
    mnemo = reg.summon_knight("LADY_MNEMOSYNE_Ω")
    assert mnemo is not None
    assert any("Active Triggered Sync Loop" in r for r in mnemo.responsibilities)
    assert "5_change_sync_loop" in mnemo.domain_tags

    # 2. Test 5-change trigger mechanism with dedicated test loop
    test_state_file = REPO_ROOT / "03_VAULT" / "runtime_state" / "test_mnemosyne_trigger.json"
    loop = LadyMnemosyneTriggerLoop(threshold=5)
    loop.state_path = test_state_file
    loop.state["change_counter"] = 0
    loop.state["syncs_triggered"] = 0

    # Record mutations 1 through 4: should not trigger sync
    for i in range(1, 5):
        res = loop.record_change(f"Test mutation {i}")
        assert res["triggered"] is False
        assert res["change_counter"] == i
        assert res["remaining_until_next_sync"] == 5 - i

    # Record mutation 5: must trigger active sync pass and reset counter to 0
    res5 = loop.record_change("Test mutation 5 (Threshold Trigger)")
    assert res5["triggered"] is True
    assert res5["change_counter"] == 0
    assert res5["remaining_until_next_sync"] == 0
    assert res5["sync_result"] is not None
    assert res5["sync_result"]["status"] == "SYNCHRONIZED"

    # Cleanup test state file
    if test_state_file.exists():
        test_state_file.unlink()
