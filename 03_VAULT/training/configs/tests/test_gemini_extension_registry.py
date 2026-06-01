from __future__ import annotations

import json
from pathlib import Path

from control_plane.gemini_extension_registry import (
    inspect_gemini_extension,
    list_gemini_extensions,
    summarize_gemini_extensions,
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roots(tmp_path: Path) -> tuple[Path, Path]:
    gemini_root = tmp_path / ".gemini" / "extensions"
    skills_root = tmp_path / ".agents" / "skills"

    _write(
        gemini_root / "extension-enablement.json",
        json.dumps({"maestro": {"overrides": ["/C:/Users/vizio/*"]}}),
    )
    _write(
        tmp_path / ".gemini" / "extension_integrity.json",
        json.dumps({"store": {"maestro": {"digest": "abc"}}}),
    )
    _write(
        gemini_root / "maestro" / "gemini-extension.json",
        json.dumps(
            {
                "name": "maestro",
                "version": "1.6.4",
                "description": "Multi-agent orchestration",
                "mcpServers": {"maestro": {"command": "node"}},
            }
        ),
    )
    _write(gemini_root / "maestro" / "commands" / "maestro" / "review.toml", "prompt = 'review'")
    _write(
        skills_root / "gemini-maestro" / "SKILL.md",
        "# Gemini Extension Adapter: maestro\n\n- Gemini status: enabled in Gemini\n",
    )
    _write(
        gemini_root / "system-agents" / "gemini-extension.json",
        json.dumps({"name": "system-agents", "version": "0.1.1"}),
    )
    _write(
        skills_root / "gemini-system-agents" / "SKILL.md",
        "# Gemini Extension Adapter: system-agents\n\n- Gemini status: installed but not globally enabled in Gemini\n",
    )
    return gemini_root, skills_root


def test_summarize_gemini_extensions_counts_enabled_disabled_and_risks(tmp_path: Path):
    gemini_root, skills_root = _sample_roots(tmp_path)

    summary = summarize_gemini_extensions(gemini_root=gemini_root, skills_root=skills_root)

    assert summary["status"] == "OK"
    assert summary["counts"]["total"] == 2
    assert summary["counts"]["enabled"] == 1
    assert summary["counts"]["disabled"] == 1
    assert summary["counts"]["with_mcp_servers"] == 1
    assert "PROFILE_WIDE_OVERRIDES" in summary["risks"]
    assert "DISABLED_EXTENSION_INTEGRITY_GAP" in summary["risks"]


def test_list_gemini_extensions_returns_command_and_mcp_metadata(tmp_path: Path):
    gemini_root, skills_root = _sample_roots(tmp_path)

    listing = list_gemini_extensions(gemini_root=gemini_root, skills_root=skills_root)

    maestro = next(item for item in listing["extensions"] if item["name"] == "maestro")
    assert maestro["enabled"] is True
    assert maestro["command_count"] == 1
    assert maestro["mcp_server_count"] == 1
    assert maestro["adapter"] == "gemini-maestro"


def test_inspect_gemini_extension_reports_missing_extension(tmp_path: Path):
    gemini_root, skills_root = _sample_roots(tmp_path)

    output = inspect_gemini_extension("missing", gemini_root=gemini_root, skills_root=skills_root)

    assert output["status"] == "NOT_FOUND"
    assert output["name"] == "missing"


def test_inspect_gemini_extension_prefers_exact_gemini_prefixed_name(tmp_path: Path):
    gemini_root, skills_root = _sample_roots(tmp_path)
    _write(
        gemini_root / "gemini-kit" / "gemini-extension.json",
        json.dumps({"name": "gemini-kit", "version": "2.3.0"}),
    )
    _write(
        skills_root / "gemini-gemini-kit" / "SKILL.md",
        "# Gemini Extension Adapter: gemini-kit\n\n- Gemini status: enabled in Gemini\n",
    )

    output = inspect_gemini_extension("gemini-kit", gemini_root=gemini_root, skills_root=skills_root)

    assert output["status"] == "OK"
    assert output["name"] == "gemini-kit"
