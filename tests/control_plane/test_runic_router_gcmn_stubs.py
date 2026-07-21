"""Tests for the GCMN vMAX stub dispatch table in `runic_router`.

The GCMN vMAX nano-seed is treated as UNTRUSTED external input. These tests
pin two invariants:

1. **Default-inert**: with ``CAMELOT_GCMN_STUBS_ENABLED`` unset (or set to
   anything other than ``"1"``), the four stub runes (``//SYNC_KBA_DATABASES_SQLCIPHER``,
   ``//LOCK_BIFROST_mTLS_KYBER768``, ``//ENGAGE_RUST_IRON_DAEMON``,
   ``//CRYSTALLIZE_GCMN_vMAX``) MUST NOT reach the stub dispatcher.

2. **Opt-in sealed TODO**: with the flag set to ``"1"``, every stub rune
   returns a structured ``RuneResult`` with status ``STUB_INERT``, a
   fingerprint consistent with the seeded governance record, and a
   synthetic (non-queueing) task id. Stubs MUST NOT pollute the harness
   queue and MUST NOT call into Bifrost / pqcrypto / cartridge code paths.

The tests use ``monkeypatch`` for env-var control and ``capsys`` to capture
the single stderr log line emitted per invocation.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Importing `runic_router` directly works because pyproject.toml lists the
# project package roots under setuptools `include = ["control_plane*", "bin*"]`
# and pytest runs from `CAMELOT_OS/` (the pyproject root) — so
# `control_plane.runic_router` is importable in the active interpreter.
from control_plane import runic_router as rr
from control_plane.taxonomy import PRIVACY_KEYWORDS

# Canonical seed keys mirrored from the pasted spec block.
GCMN_RUNE_KEYS = (
    "//SYNC_KBA_DATABASES_SQLCIPHER",
    "//LOCK_BIFROST_mTLS_KYBER768",
    "//ENGAGE_RUST_IRON_DAEMON",
    "//CRYSTALLIZE_GCMN_vMAX",
)


def _set_gcmn_flag(monkeypatch: pytest.MonkeyPatch, value: str | None) -> None:
    """Helper: set/unset the feature flag the same way the runtime reads it."""
    if value is None:
        monkeypatch.delenv("CAMELOT_GCMN_STUBS_ENABLED", raising=False)
    else:
        monkeypatch.setenv("CAMELOT_GCMN_STUBS_ENABLED", value)


# ---------------------------------------------------------------------------
# 1) Governance & dispatch-table shape
# ---------------------------------------------------------------------------


def test_gcmn_governance_carries_sealed_status() -> None:
    """GCMN_GOVERNANCE must mark itself STUB_INERT and demand HITL."""
    g = rr.GCMN_GOVERNANCE
    assert g["status"] == "STUB_INERT"
    assert g["hitl_required_for_activation"] is True
    assert g["hitl_risk_score"] >= 50
    assert g["audit_ledger_pointer"] is None
    # Fingerprint from the seed — must be preserved verbatim so audits can match.
    assert g["fingerprint"] == "νKG_CRYSTAL_OMEGA_STANDARDIZED"


def test_gcmn_stub_table_has_exactly_four_entries_with_canonical_casing() -> None:
    assert set(rr.GCMN_STUB_RUNES.keys()) == set(GCMN_RUNE_KEYS)
    for cfg in rr.GCMN_STUB_RUNES.values():
        # Every stub carries a knight hint, a step, a todo list, and a domain
        # tag — these are the audit invariants callers rely on.
        assert isinstance(cfg["knight_hint"], str) and cfg["knight_hint"]
        assert isinstance(cfg["spec_step"], int) and 1 <= cfg["spec_step"] <= 4
        assert isinstance(cfg["todo"], list) and cfg["todo"]
        for item in cfg["todo"]:
            assert isinstance(item, str) and item
        assert cfg.get("domain") == "KBA_SERVICES"


# ---------------------------------------------------------------------------
# 2) Inert-by-default behaviour
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rune", GCMN_RUNE_KEYS)
def test_gcmn_stub_is_inert_when_flag_unset(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    tmp_path: Path,
    rune: str,
) -> None:
    """Without the flag, the stub rune must NOT route to the stub dispatch.

    It must fall through to the standard unknown/escalation path (knight=
    sir_boris) and MUST NOT emit the [GCMN-STUB] stderr log line. The harness
    queue MUST NOT receive the marker (we redirect it to tmp_path and verify
    no marker lines were written).
    """
    _set_gcmn_flag(monkeypatch, value=None)
    queue_redirect = tmp_path / "harness_queue.jsonl"
    monkeypatch.setattr(rr, "QUEUE_FILE", queue_redirect)

    result = rr.route_rune(rune, param="probe")

    # Falls through to unknown escalation. The metadata.warning is the
    # canonical signal; queued=False means either queue write failed or
    # the stub path was avoided (queue file remains empty / non-existent).
    assert "warning" in result.metadata
    assert "not in dispatch table" in result.metadata["warning"]
    # The (sir_boris) knight is the standard escalation target for clean text.
    assert result.knight == "sir_boris"
    # No [GCMN-STUB] stderr line.
    captured = capsys.readouterr()
    assert "[GCMN-STUB]" not in captured.err
    # The unknown-escalation path WILL write a queue entry, but that entry
    # must NOT carry a STUB:: marker — the stub path is strictly opt-in.
    if queue_redirect.exists():
        queue_text = queue_redirect.read_text(encoding="utf-8")
        assert "STUB::" not in queue_text
        # Sanity: the standard escalation directive carries the same rune we
        # routed, so the queue write we see IS the normal escalation path —
        # not the stub handler leaking through.
        assert rune in queue_text


@pytest.mark.parametrize("flag_value", ["0", "true", "yes", "on", "off", ""])
def test_gcmn_stub_flag_only_accepts_exact_string_one(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    flag_value: str,
) -> None:
    """The gate must reject every value except the literal string ``"1"``.

    This matches the dedup-guard pattern (``CAMELOT_ROUTER_DEDUP_DISABLE=1``)
    so operator scripts that pipe booleans through shell do not silently
    enable stubs via truthy strings.
    """
    _set_gcmn_flag(monkeypatch, value=flag_value)
    assert not rr._gcmn_stubs_enabled()

    rr.route_rune("//SYNC_KBA_DATABASES_SQLCIPHER", param="probe")
    captured = capsys.readouterr()
    assert "[GCMN-STUB]" not in captured.err


# ---------------------------------------------------------------------------
# 3) Opt-in sealed TODO behaviour
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rune", GCMN_RUNE_KEYS)
def test_gcmn_stub_emits_sealed_todo_when_flag_on(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    tmp_path: Path,
    rune: str,
) -> None:
    """With the flag ON, the stub returns the sealed TODO envelope."""
    _set_gcmn_flag(monkeypatch, value="1")
    # Redirect queue file so we can prove the stub does NOT write to it.
    queue_redirect = tmp_path / "harness_queue.jsonl"
    monkeypatch.setattr(rr, "QUEUE_FILE", queue_redirect)

    result = rr.route_rune(rune, param="tenant=alpha")

    # 1) The result is a real RuneResult with the seeded directives.
    assert result.rune == rune
    assert result.knight == rr.GCMN_STUB_RUNES[rune]["knight_hint"]
    assert result.directive.startswith(f"STUB::{rune}")
    assert "tenant=alpha" in result.directive

    # 2) The metadata envelope is sealed and audit-friendly.
    md = result.metadata
    assert md["action"] == "gcmn_stub_exec"
    assert md["status"] == "STUB_INERT"
    assert md["gate"] == "CAMELOT_GCMN_STUBS_ENABLED=1"
    assert md["governance"]["fingerprint"] == rr.GCMN_GOVERNANCE["fingerprint"]
    assert md["governance"]["hitl_required_for_activation"] is True
    assert md["param_echoed"] == "tenant=alpha"
    assert md["next_action"] == "HUMAN_REVIEW_REQUIRED"

    # 3) The synthetic task id is non-queueing, so the harness queue dir
    #    is never touched.
    assert result.task_id.startswith("gcmn-stub-")
    assert result.queued is False
    assert result.queue_error is None
    assert not queue_redirect.exists()

    # 4) The single stderr audit line is well-formed.
    captured = capsys.readouterr()
    assert "[GCMN-STUB]" in captured.err
    assert f"rune={rune}" in captured.err
    assert "status=STUB_INERT" in captured.err


def test_gcmn_stub_metadata_collisions_called_for_already_deployed_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The Bifrost+Kyber stub must surface its collision warning.

    Without this, an operator could enable the flag and then unknowingly
    deploy a second mTLS/Kyber stack on top of the existing P1-implemented
    `bin/bifrost.py` + `control_plane/pqcrypto_bridge.py` chain.
    """
    _set_gcmn_flag(monkeypatch, value="1")
    result = rr.route_rune("//LOCK_BIFROST_mTLS_KYBER768", param="")
    assert result.metadata["collision_warning"] is not None
    assert "bifrost" in result.metadata["collision_warning"].lower()
    assert (
        "pqcrypto" in result.metadata["collision_warning"].lower()
        or "kyber" in result.metadata["collision_warning"].lower()
    )


# ---------------------------------------------------------------------------
# 4) list_runes() visibility
# ---------------------------------------------------------------------------


def test_list_runes_hides_gcmn_stubs_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_gcmn_flag(monkeypatch, value=None)
    listing = rr.list_runes()
    assert "gcmn_stub_runes" not in listing
    # Sanity: real categories remain present so callers don't see an empty map.
    assert "runic_commands" in listing and "//FORGE" in listing["runic_commands"]
    assert "omega_runes" in listing and "Omega_SYNC" in listing["omega_runes"]


def test_list_runes_exposes_gcmn_stubs_when_flag_on(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_gcmn_flag(monkeypatch, value="1")
    listing = rr.list_runes()
    assert "gcmn_stub_runes" in listing
    assert set(listing["gcmn_stub_runes"]) == set(GCMN_RUNE_KEYS)
    # Increased surface — auditors can confirm the flag's effect on visibility.
    assert "runic_commands" in listing and "omega_runes" in listing


# ---------------------------------------------------------------------------
# 5) Privacy override wins over stubs (regression guard)
# ---------------------------------------------------------------------------


def test_privacy_keyword_routes_to_sir_ghost_not_stub(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    """Even with the flag on, a stub carrying a PRIVACY_KEYWORDS token must
    route to ``sir_ghost`` (air-gapped) — the stub dispatchers MUST NOT
    leak through privacy gating.
    """
    assert PRIVACY_KEYWORDS, "taxonomy.PRIVACY_KEYWORDS must be non-empty"
    # Pick the first privacy keyword deterministically so the test does not
    # silently depend on a hardcoded substring that may be renamed upstream.
    privacy_keyword = next(iter(PRIVACY_KEYWORDS))
    _set_gcmn_flag(monkeypatch, value="1")

    result = rr.route_rune(
        "//SYNC_KBA_DATABASES_SQLCIPHER",
        param=f"file containing a {privacy_keyword} token",
    )
    assert result.knight == "sir_ghost"
    assert result.metadata.get("privacy_override") is True
    captured = capsys.readouterr()
    assert "[GCMN-STUB]" not in captured.err  # privacy short-circuits stubs
