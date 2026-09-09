# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Verification Tests for Penguin Builder & Tool Scaffolding

import sys
import shutil
import tempfile
from pathlib import Path
import pytest

# Ensure skill path is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / ".agents" / "skills" / "merlin-knight-forge"
FORGE_ASSIM_DIR = REPO_ROOT / "02_FORGE" / "assimilation" / "penguin_harness"

if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))
if str(FORGE_ASSIM_DIR) not in sys.path:
    sys.path.insert(0, str(FORGE_ASSIM_DIR))

from penguin_builder import (
    ToolRegistry,
    build_agent_from_sentence,
    derive_agent_blueprint,
    forge_knight_to_penguin,
    slugify_agent_id,
)


@pytest.fixture
def temp_workspace():
    """Create and tear down a clean temporary workspace."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="camelot_penguin_test_"))
    yield tmp_dir
    shutil.rmtree(tmp_dir, ignore_errors=True)


def test_slugify_agent_id():
    """Verify POSIX-safe agent ID sanitization."""
    assert slugify_agent_id("Commit Helper") == "commit-helper"
    assert slugify_agent_id("Sir_Codex! v5.5 (Hyper-Auditor)") == "sir_codex-v5-5-hyper-auditor"
    assert slugify_agent_id("   multiple---hyphens   ") == "multiple-hyphens"
    assert slugify_agent_id("") == "penguin-agent"


def test_derive_agent_blueprint_commit_helper():
    """Test 1-sentence derivation for commit-helper requirement."""
    req = 'Create an agent called "commit-helper" that writes high-quality conventional git commit messages.'
    bp = derive_agent_blueprint(req)
    
    assert bp["agent_id"] == "commit-helper"
    assert "Commit Helper" in bp["name"]
    assert "git commit" in bp["role"].lower()
    assert bp["thinking_level"] == "low"
    assert len(bp["domain_guidance"]) >= 3
    assert any(s.name == "git-workflow" for s in bp["skills"])


def test_derive_agent_blueprint_security():
    """Test 1-sentence derivation for security audit requirement."""
    req = "A security specialist that audits code for secrets, tokens, and vulnerabilities."
    bp = derive_agent_blueprint(req)
    
    assert bp["thinking_level"] == "high"
    assert "security" in bp["role"].lower()
    assert any(s.name == "security-audit" for s in bp["skills"])


def test_derive_agent_blueprint_generic():
    """Test 1-sentence derivation for arbitrary knowledge domain."""
    req = "An expert that answers technical questions about Kubernetes networking."
    bp = derive_agent_blueprint(req)
    
    assert bp["thinking_level"] == "medium"
    assert "Kubernetes networking" in bp["role"]
    assert len(bp["skills"]) >= 1


def test_build_agent_from_sentence_scaffolding(temp_workspace):
    """Verify complete Agent State layout generation and validation."""
    req = "Create an agent called 'doc-wizard' that generates markdown documentation."
    state = build_agent_from_sentence(req, target_dir=temp_workspace)

    assert state.agent_id == "doc-wizard"
    assert state.agent_dir.exists()
    assert state.state_dir.exists()
    assert state.scratchpad_dir.exists()

    # Check subdirectories
    assert (state.state_dir / "memory").is_dir()
    assert (state.state_dir / "tools").is_dir()
    assert (state.state_dir / "skills").is_dir()

    # Check system_config.yaml
    config_file = state.state_dir / "system_config.yaml"
    assert config_file.exists()
    config_text = config_file.read_text(encoding="utf-8")
    assert "doc-wizard" in config_text or "Doc Wizard" in config_text
    assert "version: 1" in config_text

    # Check AGENTS.md
    agents_md = state.state_dir / "AGENTS.md"
    assert agents_md.exists()
    agents_text = agents_md.read_text(encoding="utf-8")
    assert "## Role" in agents_text
    assert "## Domain Guidance" in agents_text

    # Check skills
    for skill_name, skill in state.skills.items():
        skill_file = state.state_dir / "skills" / skill_name / "SKILL.md"
        assert skill_file.exists()
        content = skill_file.read_text(encoding="utf-8")
        assert f"name: {skill_name}" in content
        assert "version: 1" in content

    # Validation should pass cleanly
    errors = state.validate()
    assert len(errors) == 0


def test_forge_knight_to_penguin_adapter(temp_workspace):
    """Verify conversion from Merlin Knight Character Sheet to Penguin Agent State."""
    sheet = """# Sir Lancelot

## Identity
- Archetype: ForgeKnight
- Mission: Kinetic code generation and zero-trust refactoring.
- Humanistic persona: Focused, precise engineer.

## Mandate
- Primary objective: Build clean software.

## Mental Framework
- Planning model: Vertical Slice + TDD

## Skill Stack
- Primary skills: `tdd`, `ralph-local`, `diagnose`
- Camelot-native tools: //FORGE
"""
    state = forge_knight_to_penguin(sheet, target_dir=temp_workspace)
    assert state.agent_id == "sir-lancelot"
    assert state.system_config.name == "Sir Lancelot"
    assert "tdd" in state.skills
    assert "ralph-local" in state.skills
    assert len(state.validate()) == 0


def test_minimal_tool_calling_file_tools(temp_workspace):
    """Verify BuiltinTool file operations: write, read, and edit."""
    registry = ToolRegistry()

    # 1. Write file
    write_res = registry.execute(
        "write_file",
        {"path": "test_dir/hello.txt", "content": "Line 1: Alpha\nLine 2: Beta\nLine 3: Gamma\n"},
        workspace_dir=str(temp_workspace),
    )
    assert write_res.is_success
    assert (temp_workspace / "test_dir" / "hello.txt").exists()

    # 2. Read file with line bounds
    read_res = registry.execute(
        "read_file",
        {"path": "test_dir/hello.txt", "start_line": 2, "max_lines": 2},
        workspace_dir=str(temp_workspace),
    )
    assert read_res.is_success
    assert "Line 2: Beta" in read_res.output
    assert "Line 3: Gamma" in read_res.output
    assert "Line 1: Alpha" not in read_res.output

    # 3. Edit file (replace substring)
    edit_res = registry.execute(
        "edit_file",
        {"path": "test_dir/hello.txt", "old_str": "Beta", "new_str": "Omega"},
        workspace_dir=str(temp_workspace),
    )
    assert edit_res.is_success

    # Read back edited file
    verify_read = registry.execute(
        "read_file",
        {"path": "test_dir/hello.txt"},
        workspace_dir=str(temp_workspace),
    )
    assert "Line 2: Omega" in verify_read.output


def test_minimal_tool_calling_exec_and_subagent(temp_workspace):
    """Verify exec_command and run_subagent built-in tools."""
    registry = ToolRegistry()

    # Command tool
    cmd_res = registry.execute(
        "exec_command",
        {"command": "python -c \"print('Hello Camelot Penguin')\""},
        workspace_dir=str(temp_workspace),
    )
    assert cmd_res.is_success
    assert "Hello Camelot Penguin" in cmd_res.output
    assert "[exit code: 0]" in cmd_res.note

    # Subagent delegation tool
    sub_res = registry.execute(
        "run_subagent",
        {"agent_id": "auditor", "prompt": "Audit recent commits"},
        workspace_dir=str(temp_workspace),
    )
    assert sub_res.is_success
    assert "auditor" in sub_res.output
    assert "Audit recent commits" in sub_res.output


def test_openai_tool_schema_export():
    """Verify tool definitions export to standard OpenAI schema format."""
    registry = ToolRegistry()
    schemas = registry.to_openai_tools()
    assert len(schemas) >= 5
    
    names = [s["function"]["name"] for s in schemas]
    assert "read_file" in names
    assert "write_file" in names
    assert "edit_file" in names
    assert "exec_command" in names
    assert "run_subagent" in names


def test_02_forge_kinetic_bridge_import():
    """Verify that 02_FORGE assimilation module exposes the builder functions."""
    import penguin_scaffold
    assert hasattr(penguin_scaffold, "build_agent_from_sentence")
    assert hasattr(penguin_scaffold, "ToolRegistry")
    assert hasattr(penguin_scaffold, "forge_knight_to_penguin")
