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
