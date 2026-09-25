# SPDX-License-Identifier: MIT
"""Unit tests for control_plane.mission_layout — per-mission artifact isolation."""

import json

import pytest

from control_plane.mission_layout import (
    MISSION_ARTIFACTS,
    MISSIONS_ROOT,
    MissionLayoutError,
    MissionSession,
    is_governance_path,
)


@pytest.fixture()
def mission(tmp_path):
    return MissionSession("pytest_mission", objective="unit test", root=tmp_path / "missions" / "pytest_mission")


class TestGovernanceGuard:
    def test_docs_governance_docs_protected(self, tmp_path):
        for name in ("blueprint.md", "task.md", "verification.md"):
            assert is_governance_path(tmp_path / "docs" / name)

    def test_nested_docs_protected(self, tmp_path):
        assert is_governance_path(tmp_path / "a" / "docs" / "blueprint.md")

    def test_ledger_basename_protected_anywhere(self, tmp_path):
        assert is_governance_path(tmp_path / "PROVENANCE_LEDGER.md")
        assert is_governance_path(tmp_path / "x" / "y" / "PROVENANCE_LEDGER.md")

    def test_mission_artifacts_not_protected(self, tmp_path):
        assert not is_governance_path(tmp_path / "missions" / "m" / "blueprint.json")
        assert not is_governance_path(MISSIONS_ROOT / "m" / "task_dag.json")


class TestMissionSession:
    def test_invalid_mission_id_rejected(self):
        with pytest.raises(MissionLayoutError):
            MissionSession("Bad ID!")

    def test_create_scaffolds_manifest(self, mission):
        manifest = mission.create()
        assert mission.manifest_path.exists()
        assert manifest["mission_id"] == "pytest_mission"
        assert manifest["schema"] == "camelot.mission/1"
        assert len(manifest["steps"]) == 5

    def test_create_is_idempotent(self, mission):
        first = mission.create()
        second = mission.create()
        assert first["mission_id"] == second["mission_id"]

    def test_write_artifact_pins_sha256(self, mission):
        mission.create()
        receipt = mission.write_artifact("blueprint.json", {"frozen": True})
        assert receipt["sha256"]
        manifest = mission.load_manifest()
        assert manifest["artifacts"]["blueprint.json"] == receipt["sha256"]

    def test_unknown_artifact_refused(self, mission):
        mission.create()
        with pytest.raises(MissionLayoutError, match="unknown artifact"):
            mission.write_artifact("task.md", {"x": 1})

    def test_path_escape_blocked(self, mission):
        mission.create()
        with pytest.raises(MissionLayoutError, match="escapes mission root"):
            mission._safe_child("../outside.json")

    def test_governance_write_refused_even_via_safe_child(self, tmp_path):
        session = MissionSession("gov_test", root=tmp_path / "missions" / "gov_test")
        session.create()
        # Refused either as an escape or as a governance path — both are safe.
        with pytest.raises(MissionLayoutError):
            session._safe_child("../../../docs/task.md")

    def test_governance_refused_without_escape_prefix(self, tmp_path):
        # A root that itself sits under docs/ must also be unwritable.
        session = MissionSession("gov_docs", root=tmp_path / "docs" / "missions" / "gov_docs")
        with pytest.raises(MissionLayoutError, match="governance"):
            session.create()

    def test_receipts_are_append_only(self, mission):
        mission.create()
        mission.write_artifact("blueprint.json", {"n": 1})
        mission.write_artifact("blueprint.json", {"n": 2})
        receipts = sorted((mission.root / "receipts").glob("*.json"))
        assert [p.name for p in receipts] == ["001_step.json", "002_step.json"]

    def test_verify_detects_mutation(self, mission):
        mission.create()
        mission.write_artifact("task_dag.json", {"dag": []})
        assert mission.verify_mission()["ok"] is True

        target = mission.root / "task_dag.json"
        target.write_text('{"dag": ["tampered"]}', encoding="utf-8")
        verdict = mission.verify_mission()
        assert verdict["ok"] is False
        assert verdict["artifacts"][0]["status"] == "MUTATED"

    def test_verify_detects_missing(self, mission):
        mission.create()
        mission.write_artifact("verification.json", {"ok": True})
        (mission.root / "verification.json").unlink()
        verdict = mission.verify_mission()
        assert verdict["ok"] is False
        assert verdict["artifacts"][0]["status"] == "MISSING"

    def test_set_status_round_trip(self, mission):
        mission.create()
        mission.set_status("SEALED")
        assert mission.load_manifest()["status"] == "SEALED"


def test_canonical_artifact_set_stable():
    assert set(MISSION_ARTIFACTS) == {
        "blueprint.json",
        "task_dag.json",
        "skills_manifest.json",
        "verification.json",
        "receipts",
    }


def test_manifest_payload_is_valid_json_on_disk(mission):
    mission.create()
    mission.write_artifact("skills_manifest.json", {"tools": ["z3"]})
    data = json.loads((mission.root / "skills_manifest.json").read_text(encoding="utf-8"))
    assert data == {"tools": ["z3"]}
