# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Omarchy Multi-Agent Matrix Harmonizer
=====================================
Harmonizes Omarchy's mise-managed agent CLI launchers with Camelot's Sovereign
Knight Pantheon:
- `claude`   -> SIR_BORIS (Claude Code / Lead Architect)
- `codex`    -> SIR_CODEX (OpenAI Codex / Kinetic Implementer)
- `agy`      -> ANTIGRAVITY (Google Antigravity CLI / FastMCP)
- `hermes`   -> HERMES_PRIME (NousResearch Hermes Agent VPS Layer)
- `opencode` -> SIR_FORGE (Kinetic Code Generation)
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class AgentMapping:
    omarchy_cmd: str
    knight_id: str
    engine: str
    rune_alias: str
    role: str
    proxy_target: str


OMARCHY_KNIGHT_MATRIX: Dict[str, AgentMapping] = {
    "hermes": AgentMapping(
        omarchy_cmd="hermes",
        knight_id="HERMES_PRIME",
        engine="Hermes Agent v0.20.5 (VPS Docker :8642/:9119)",
        rune_alias="//HERMES",
        role="Autonomous Recursive Execution & Dialectic Synthesis",
        proxy_target="vps://162.35.107.134:8642",
    ),
    "codex": AgentMapping(
        omarchy_cmd="codex",
        knight_id="SIR_CODEX",
        engine="GPT-5.5 Codex (Kinetic DGM-H)",
        rune_alias="//CODEX",
        role="Kinetic Implementer & Formal AST Logic Architect",
        proxy_target="local://camelot/control_plane",
    ),
    "claude": AgentMapping(
        omarchy_cmd="claude",
        knight_id="SIR_BORIS",
        engine="Claude 3.7 Sonnet / Opus (Crucible)",
        rune_alias="//FORGE",
        role="Lead System Architect & 13-Agent Crucible Conductor",
        proxy_target="local://camelot/agora",
    ),
    "agy": AgentMapping(
        omarchy_cmd="agy",
        knight_id="ANTIGRAVITY",
        engine="Antigravity CLI (FastMCP / Gemini)",
        rune_alias="//FLEET",
        role="NotebookLM CloudBrain Synergy & Dual-Brain Bridge",
        proxy_target="local://camelot/antigravity",
    ),
}


def get_agent_matrix() -> Dict[str, Any]:
    """Return serialized mapping of Omarchy agent commands to Camelot Knights."""
    return {
        "status": "HARMONIZED",
        "total_agents": len(OMARCHY_KNIGHT_MATRIX),
        "agents": {k: asdict(v) for k, v in OMARCHY_KNIGHT_MATRIX.items()},
    }


def generate_omarchy_mise_stub(agent_name: str) -> str:
    """Generate shell launcher script for an Omarchy mise stub."""
    mapping = OMARCHY_KNIGHT_MATRIX.get(agent_name.lower())
    if not mapping:
        raise ValueError(f"Unknown agent: {agent_name}")

    if mapping.omarchy_cmd == "hermes":
        return (
            "#!/bin/bash\n"
            "# Omarchy ↔ Camelot Hermes Proxy Stub\n"
            'ssh -o BatchMode=yes root@162.35.107.134 "docker exec -i hermes hermes \"$@\""\n'
        )

    return (
        f"#!/bin/bash\n"
        f"# Omarchy ↔ Camelot {mapping.knight_id} Launcher Stub\n"
        f'python3 -m control_plane.runes.runic_router "{mapping.rune_alias} $*"\n'
    )


if __name__ == "__main__":
    print(json.dumps(get_agent_matrix(), indent=2))
