# SPDX-License-Identifier: MIT
"""Father's Camelot as the roster-wide behavioral contract."""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SHEETS_PATH = REPO_ROOT / "03_VAULT" / "training" / "configs" / "knight_character_sheets.json"


def _sheets():
    return json.loads(SHEETS_PATH.read_text(encoding="utf-8"))["knights"]


def test_every_knight_bound_to_fathers_camelot():
    knights = _sheets()
    assert len(knights) >= 54
    unbound = [k for k, v in knights.items() if v.get("behavioral_contract") != "FATHER_CAMELOT"]
    assert not unbound, f"knights outside the contract: {unbound}"


def test_father_camelot_carries_contract_clauses():
    father = _sheets()["FATHER_CAMELOT"]
    clauses = father.get("responsibilities", [])
    assert len(clauses) >= 5
    assert any("King Arthur" in c for c in clauses)
    assert any("SIR_GHOST" in c for c in clauses)
    assert father["summoning_rune"] == "Omega_FatherCamelot"


def test_omega_fathercamelot_dispatches():
    from control_plane.runes.runic_router import OMEGA_RUNES, route_rune
    assert OMEGA_RUNES["Omega_FatherCamelot"]["knight"] == "father_camelot"
    res = route_rune("Omega_FatherCamelot", "contract probe")
    assert res.knight == "father_camelot"
    assert res.queued is True
