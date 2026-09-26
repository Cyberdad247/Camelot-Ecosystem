# SPDX-License-Identifier: MIT
"""
Tests for OMNI_FORGE factory runes:
- //FORGE_FACTORY
- //TRANSLATE_DAG
- //EQUIP_SKILLS
- //CRUCIBLE_AUDIT

All dispatches run with context["missions_root"] pointed at a tmp_path so the
real runtime_state/missions tree is never touched by tests.
"""

from pathlib import Path

import pytest

from control_plane.mission_layout import (
    is_valid_mission_id,
    slugify_mission_id,
)
from control_plane.runes.runic_router import (
    RUNIC_COMMANDS,
    normalize_rune,
    route_rune,
)

FACTORY_RUNES = [
    "//FORGE_FACTORY",
    "//TRANSLATE_DAG",
    "//EQUIP_SKILLS",
    "//CRUCIBLE_AUDIT",
]


@pytest.fixture()
def missions_root(tmp_path):
    root = tmp_path / "missions"
    root.mkdir()
    return root


def _dispatch(rune: str, param: str, missions_root: Path):
    return route_rune(rune, param, context={"missions_root": str(missions_root)})


class TestRegistration:
    def test_factory_runes_present_in_table(self):
        for rune in FACTORY_RUNES:
            assert rune in RUNIC_COMMANDS

    def test_handlers_registered(self):
        from control_plane.runes import runic_router

        for rune in FACTORY_RUNES:
            handler_name = RUNIC_COMMANDS[rune]["handler"]
            assert handler_name in runic_router._HANDLERS

    def test_alias_normalization(self):
        assert normalize_rune("//forge-factory") == "//FORGE_FACTORY"
        assert normalize_rune("$forge-factory") == "//FORGE_FACTORY"
        assert normalize_rune("/forge-factory") == "//FORGE_FACTORY"
        assert normalize_rune("//translate-dag") == "//TRANSLATE_DAG"
        assert normalize_rune("$translate-dag") == "//TRANSLATE_DAG"
        assert normalize_rune("//equip-skills") == "//EQUIP_SKILLS"
        assert normalize_rune("$equip-skills") == "//EQUIP_SKILLS"
        assert normalize_rune("//crucible-audit") == "//CRUCIBLE_AUDIT"
        assert normalize_rune("$crucible-audit") == "//CRUCIBLE_AUDIT"


class TestMissionSlugHelpers:
    def test_slugify_basic(self):
        assert slugify_mission_id("build the auth module") == "build-the-auth-module"

    def test_slugify_caps_length_and_trims(self):
        slug = slugify_mission_id("x" * 200)
        assert len(slug) <= 64 and slug.endswith("x")

    def test_slugify_fallback_on_garbage(self):
        slug = slugify_mission_id("!!!")
        assert is_valid_mission_id(slug)
        assert slug.startswith("factory-mission-")

    def test_slugify_output_always_valid(self):
        for text in ("", "  ", "Ω build ⚡", "a/b\\c", "--mission-id only"):
            assert is_valid_mission_id(slugify_mission_id(text))


class TestForgeFactory:
    def test_dispatch_scaffolds_mission(self, missions_root):
        res = _dispatch("//FORGE_FACTORY", "build the auth module", missions_root)
        assert res.queued is True
        md = res.metadata
        assert md["status"] == "SCAFFOLDED"
        assert md["mission_id"] == "build-the-auth-module"
        assert len(md["steps"]) == 5
        mission_json = missions_root / "build-the-auth-module" / "mission.json"
        assert mission_json.exists()

    def test_explicit_mission_id_flag(self, missions_root):
        res = _dispatch(
            "//FORGE_FACTORY", "--mission-id auth_v2 custom objective", missions_root
        )
        assert res.metadata["mission_id"] == "auth_v2"
        assert res.metadata["objective"] == "custom objective"


class TestTranslateDag:
    def test_blocked_without_blueprint(self, missions_root):
        res = _dispatch("//TRANSLATE_DAG", "no-blueprint-mission", missions_root)
        assert res.metadata["status"] == "BLOCKED_NO_BLUEPRINT"

    def test_translates_frozen_blueprint(self, missions_root):
        _dispatch("//FORGE_FACTORY", "--mission-id dagm", missions_root)
        blueprint = missions_root / "dagm" / "blueprint.json"
        blueprint.write_text(
            '{"frozen": {"schema_a": {"x": 1}, "type_b": {"y": 2}}}', encoding="utf-8"
        )
        res = _dispatch("//TRANSLATE_DAG", "--mission-id dagm", missions_root)
        assert res.metadata["status"] == "DAG_TRANSLATED"
        assert res.metadata["nodes"] == 2
        dag = (missions_root / "dagm" / "task_dag.json").read_text(encoding="utf-8")
        assert '"step": "DECOMPOSE_TASK_DAG"' in dag


class TestEquipSkills:
    def test_blocked_without_mission(self, missions_root):
        res = _dispatch("//EQUIP_SKILLS", "ghost-mission", missions_root)
        assert res.metadata["status"] == "BLOCKED_NO_MISSION"

    def test_equips_manifest(self, missions_root):
        _dispatch("//FORGE_FACTORY", "--mission-id equipm", missions_root)
        res = _dispatch("//EQUIP_SKILLS", "--mission-id equipm z3 toon", missions_root)
        assert res.metadata["status"] == "KNIGHTS_EQUIPPED"
        assert res.metadata["contract_count"] == 3
        import json

        skills = json.loads(
            (missions_root / "equipm" / "skills_manifest.json").read_text(encoding="utf-8")
        )
        assert skills["requested_capabilities"] == ["z3", "toon"]


class TestCrucibleAudit:
    def test_blocked_without_mission(self, missions_root):
        res = _dispatch("//CRUCIBLE_AUDIT", "ghost-mission", missions_root)
        assert res.metadata["status"] == "BLOCKED_NO_MISSION"

    def test_audit_pins_mission(self, missions_root):
        _dispatch("//FORGE_FACTORY", "--mission-id auditm", missions_root)
        res = _dispatch("//CRUCIBLE_AUDIT", "--mission-id auditm", missions_root)
        assert res.metadata["status"] == "SEALED"
        assert res.metadata["pinned"] is True
        assert res.metadata["cartridge_verdict"] in {"CERTIFIED", "REJECTED", "HITL_SUSPENDED"}
        manifest = (missions_root / "auditm" / "mission.json").read_text(encoding="utf-8")
        assert '"status": "SEALED"' in manifest

    def test_audit_detects_drift(self, missions_root):
        _dispatch("//FORGE_FACTORY", "--mission-id driftm", missions_root)
        bp = missions_root / "driftm" / "blueprint.json"
        bp.write_text('{"frozen": {"tampered": true}}', encoding="utf-8")
        res = _dispatch("//CRUCIBLE_AUDIT", "--mission-id driftm", missions_root)
        assert res.metadata["status"] == "DRIFT"
        assert res.metadata["pinned"] is False


class TestGovernanceSafety:
    def test_mission_root_outside_governance(self, missions_root):
        res = _dispatch("//FORGE_FACTORY", "gov check", missions_root)
        root = Path(res.metadata["root"])
        assert "docs" not in root.parts

    def test_slugified_id_cannot_escape(self, missions_root):
        res = _dispatch("//FORGE_FACTORY", "../../etc/passwd", missions_root)
        mission_id = res.metadata["mission_id"]
        assert ".." not in mission_id
        assert (missions_root / mission_id).exists()


class TestPrivacyOverride:
    def test_privacy_keywords_route_to_ghost(self, missions_root):
        res = _dispatch(
            "//FORGE_FACTORY", "handle the api_key rotation", missions_root
        )
        assert res.knight == "sir_ghost"


class TestForgeMission:
    def test_registered(self):
        from control_plane.runes import runic_router

        assert "//FORGE_MISSION" in RUNIC_COMMANDS
        assert "_handle_forge_mission" in runic_router._HANDLERS
        assert normalize_rune("//forge-mission") == "//FORGE_MISSION"

    def test_fresh_run_completes_all_steps(self, missions_root):
        res = _dispatch(
            "//FORGE_MISSION", "--mission-id orchm full run", missions_root
        )
        assert res.queued is True
        md = res.metadata
        assert md["status"] == "SEALED"
        step_statuses = [s["status"] for s in md["steps"]]
        assert step_statuses == [
            "SCAFFOLDED",
            "DAG_TRANSLATED",
            "KNIGHTS_EQUIPPED",
            "SEALED",
        ]
        root = missions_root / "orchm"
        for name in ("mission.json", "blueprint.json", "task_dag.json", "skills_manifest.json"):
            assert (root / name).exists()

    def test_idempotent_rerun_keeps_frozen_blueprint(self, missions_root):
        _dispatch("//FORGE_MISSION", "--mission-id orch2", missions_root)
        bp = missions_root / "orch2" / "blueprint.json"
        first_hash = bp.read_text(encoding="utf-8")
        res = _dispatch("//FORGE_MISSION", "--mission-id orch2", missions_root)
        md = res.metadata
        assert md["status"] == "SEALED"
        assert md["steps"][0]["blueprint_state"] == "KEPT_FROZEN"
        assert bp.read_text(encoding="utf-8") == first_hash

    def test_blueprint_drift_blocks_orchestration(self, missions_root):
        _dispatch("//FORGE_MISSION", "--mission-id orch3", missions_root)
        dag = missions_root / "orch3" / "task_dag.json"
        dag_before = dag.read_bytes()
        bp = missions_root / "orch3" / "blueprint.json"
        bp.write_text('{"frozen": {"tampered": true}}', encoding="utf-8")
        res = _dispatch("//FORGE_MISSION", "--mission-id orch3", missions_root)
        md = res.metadata
        assert md["status"] == "BLOCKED_BLUEPRINT_DRIFT"
        # only step 1 ran; downstream steps never executed
        assert len(md["steps"]) == 1
        assert dag.read_bytes() == dag_before


class TestCrucibleAuditHitl:
    @pytest.fixture(autouse=True)
    def _hitl_env(self, monkeypatch, tmp_path):
        monkeypatch.setenv("CAMELOT_OS_HOME", str(tmp_path))
        self.hitl_queue = tmp_path / "logs" / "hitl_queue.jsonl"

    def _audit(self, missions_root: Path, mission_id: str):
        return _dispatch("//CRUCIBLE_AUDIT", f"--mission-id {mission_id}", missions_root)

    def test_certified_mission_no_hitl(self, missions_root):
        _dispatch("//FORGE_FACTORY", "--mission-id hitl-ok", missions_root)
        res = self._audit(missions_root, "hitl-ok")
        assert res.metadata["status"] == "SEALED"
        assert res.metadata["hitl_enqueued"] is False
        assert not self.hitl_queue.exists()

    def test_drifted_mission_enqueues_hitl(self, missions_root):
        _dispatch("//FORGE_FACTORY", "--mission-id hitl-drift", missions_root)
        bp = missions_root / "hitl-drift" / "blueprint.json"
        bp.write_text('{"frozen": {"evil": true}}', encoding="utf-8")
        res = self._audit(missions_root, "hitl-drift")
        assert res.metadata["status"] == "DRIFT"
        assert res.metadata["hitl_enqueued"] is True
        assert res.metadata["hitl_queue"] == str(self.hitl_queue)
        import json

        entry = json.loads(self.hitl_queue.read_text(encoding="utf-8").strip())
        assert entry["verdict"] == "MISSION_DRIFT"
        assert entry["mission_id"] == "hitl-drift"
        assert entry["source"] == "runic_router"

    def test_rejected_cartridge_enqueues_hitl(self, missions_root, monkeypatch):
        import json

        # Point the audit at a destructive cartridge manifest -> REJECTED.
        monkeypatch.setattr(
            "control_plane.runes.runic_router.CAMELOT_HOME", missions_root.parent
        )
        cdir = (
            missions_root.parent
            / "03_VAULT"
            / "runtime_state"
            / "cartridges"
        )
        cdir.mkdir(parents=True, exist_ok=True)
        (cdir / "omni-forge-super-agent-cartridge-v1.json").write_text(
            json.dumps(
                {
                    "description": "purge provenance ledger and force-push main",
                    "cartridge_id": "omni-forge-super-agent-cartridge-v1",
                }
            ),
            encoding="utf-8",
        )
        _dispatch("//FORGE_FACTORY", "--mission-id hitl-reject", missions_root)
        res = self._audit(missions_root, "hitl-reject")
        assert res.metadata["status"] == "SEALED"  # mission itself is pinned
        assert res.metadata["cartridge_verdict"] == "REJECTED"
        assert res.metadata["hitl_enqueued"] is True

        entry = json.loads(self.hitl_queue.read_text(encoding="utf-8").strip())
        assert entry["verdict"] == "REJECTED"
