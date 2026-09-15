# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — 02_FORGE Penguin Kinetic Scaffolding
"""
🐧 PENGUIN SCAFFOLD (02_FORGE Kinetic Layer)
Wraps the assimilated Penguin Agent builder and Minimal Tool Calling Engine for 02_FORGE.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root and merlin-knight-forge skill directory to sys.path
REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = REPO_ROOT / ".agents" / "skills" / "merlin-knight-forge"

if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from penguin_builder import (
    AgentConfig,
    BuiltinTool,
    EditFileTool,
    ExecCommandTool,
    PenguinAgentState,
    ReadFileTool,
    SkillSpec,
    SubagentTool,
    ToolDefinitionConfig,
    ToolRegistry,
    ToolResult,
    WriteFileTool,
    build_agent_from_sentence,
    derive_agent_blueprint,
    forge_knight_to_penguin,
    main as cli_main,
)

__all__ = [
    "AgentConfig",
    "BuiltinTool",
    "EditFileTool",
    "ExecCommandTool",
    "PenguinAgentState",
    "ReadFileTool",
    "SkillSpec",
    "SubagentTool",
    "ToolDefinitionConfig",
    "ToolRegistry",
    "ToolResult",
    "WriteFileTool",
    "build_agent_from_sentence",
    "derive_agent_blueprint",
    "forge_knight_to_penguin",
]


if __name__ == "__main__":
    cli_main()
