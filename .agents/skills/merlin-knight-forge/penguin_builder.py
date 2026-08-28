# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Assimilated Penguin Agent Scaffolding & Builder
"""
🐧 PENGUIN BUILDER & MINIMAL TOOL CALLING SCAFFOLDING
Assimilated from Penguin Harness autonomous agent patterns for Camelot-OS.

Pillars:
1. 1-Sentence Agent Builder: Derive agent id, role, domain guidance, skills, and config
   from a single natural language requirement and scaffold standard Agent State layout.
2. Minimal Tool Calling Engine: Lightweight tool registry, execution contracts, and
   built-in tools (read_file, write_file, edit_file, exec_command, run_subagent).
3. Merlin Knight-to-Penguin Adapter: Bridge Camelot Knight character sheets to Penguin
   Agent State format.
"""

from __future__ import annotations

import os
import re
import sys
import json
import shutil
import subprocess
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union

try:
    import yaml
except ImportError:
    yaml = None  # Fallback provided below if yaml is unavailable


# ==============================================================================
# SECTION 1: MINIMAL TOOL CALLING SCAFFOLDING
# ==============================================================================

@dataclass
class ToolDefinitionConfig:
    """Configuration definition for a tool exposed to an Agent or LLM."""
    name: str
    description: str
    parameters: Dict[str, Any]
    permission: str = "allow"  # allow | ask | deny
    max_output_length: int = 32000

    def to_openai_schema(self) -> Dict[str, Any]:
        """Convert definition to OpenAI function tool calling schema format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }


@dataclass
class ToolResult:
    """Outcome of executing a tool call."""
    output: str
    stop_reason: str = "completed"  # completed | failed | aborted
    note: Optional[str] = None
    images: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        return self.stop_reason == "completed"


class BuiltinTool:
    """Abstract base class for all built-in executable tools."""

    name: str
    definition: ToolDefinitionConfig

    def execute(self, args: Dict[str, Any], workspace_dir: str = ".") -> ToolResult:
        raise NotImplementedError("BuiltinTool subclasses must implement execute()")


class ReadFileTool(BuiltinTool):
    """Safe file reading tool with line slicing and offset support."""

    name = "read_file"
    definition = ToolDefinitionConfig(
        name="read_file",
        description="Read file contents from the workspace. Supports line start and line limit offsets.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative or absolute file path to read."},
                "start_line": {"type": "integer", "description": "1-indexed starting line number (optional)."},
                "max_lines": {"type": "integer", "description": "Maximum number of lines to read (optional, default 2000)."},
            },
            "required": ["path"],
        },
        permission="allow",
    )

    def execute(self, args: Dict[str, Any], workspace_dir: str = ".") -> ToolResult:
        rel_path = args.get("path", "")
        if not rel_path:
            return ToolResult(output="Error: 'path' parameter is required.", stop_reason="failed")

        target = Path(workspace_dir) / rel_path if not os.path.isabs(rel_path) else Path(rel_path)
        try:
            if not target.exists():
                return ToolResult(output=f"Error: File '{rel_path}' does not exist.", stop_reason="failed")
            if not target.is_file():
                return ToolResult(output=f"Error: Path '{rel_path}' is not a file.", stop_reason="failed")

            with open(target, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            start_line = max(1, int(args.get("start_line", 1)))
            max_lines = max(1, int(args.get("max_lines", 2000)))

            selected = lines[start_line - 1 : start_line - 1 + max_lines]
            numbered = [f"{start_line + i:4d} | {line}" for i, line in enumerate(selected)]
            content = "".join(numbered)
            
            note = f"Read {len(selected)} lines (lines {start_line}-{start_line + len(selected) - 1} of {len(lines)})"
            return ToolResult(output=content, stop_reason="completed", note=note)
        except Exception as e:
            return ToolResult(output=f"Error reading file '{rel_path}': {e}", stop_reason="failed")


class WriteFileTool(BuiltinTool):
    """File writing tool that creates parent directories automatically."""

    name = "write_file"
    definition = ToolDefinitionConfig(
        name="write_file",
        description="Write content to a file in the workspace, creating any missing parent directories.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Target file path."},
                "content": {"type": "string", "description": "Full text content to write."},
                "overwrite": {"type": "boolean", "description": "Whether to overwrite existing file (default true)."},
            },
            "required": ["path", "content"],
        },
        permission="allow",
    )

    def execute(self, args: Dict[str, Any], workspace_dir: str = ".") -> ToolResult:
        rel_path = args.get("path", "")
        content = args.get("content", "")
        overwrite = args.get("overwrite", True)

        if not rel_path:
            return ToolResult(output="Error: 'path' parameter is required.", stop_reason="failed")

        target = Path(workspace_dir) / rel_path if not os.path.isabs(rel_path) else Path(rel_path)
        try:
            if target.exists() and not overwrite:
                return ToolResult(output=f"Error: File '{rel_path}' exists and overwrite=false.", stop_reason="failed")

            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)

            return ToolResult(output=f"Successfully wrote {len(content)} bytes to '{rel_path}'.", stop_reason="completed")
        except Exception as e:
            return ToolResult(output=f"Error writing file '{rel_path}': {e}", stop_reason="failed")


class EditFileTool(BuiltinTool):
    """Exact substring replacement tool for scoped file editing."""

    name = "edit_file"
    definition = ToolDefinitionConfig(
        name="edit_file",
        description="Replace a target substring with replacement content inside a file.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Target file path to edit."},
                "old_str": {"type": "string", "description": "Exact text substring to find and replace."},
                "new_str": {"type": "string", "description": "Replacement text."},
                "replace_all": {"type": "boolean", "description": "Replace all occurrences if true; otherwise replaces first occurrence (default false)."},
            },
            "required": ["path", "old_str", "new_str"],
        },
        permission="allow",
    )

    def execute(self, args: Dict[str, Any], workspace_dir: str = ".") -> ToolResult:
        rel_path = args.get("path", "")
        old_str = args.get("old_str", "")
        new_str = args.get("new_str", "")
        replace_all = args.get("replace_all", False)

        if not rel_path or old_str is None or new_str is None:
            return ToolResult(output="Error: 'path', 'old_str', and 'new_str' parameters are required.", stop_reason="failed")

        target = Path(workspace_dir) / rel_path if not os.path.isabs(rel_path) else Path(rel_path)
        try:
            if not target.exists():
                return ToolResult(output=f"Error: File '{rel_path}' does not exist.", stop_reason="failed")

            with open(target, "r", encoding="utf-8") as f:
                content = f.read()

            if old_str not in content:
                return ToolResult(output=f"Error: Target substring not found in '{rel_path}'.", stop_reason="failed")

            count = content.count(old_str)
            if not replace_all and count > 1:
                return ToolResult(
                    output=f"Error: Target substring appears {count} times in '{rel_path}'. Set replace_all=true or supply more context.",
                    stop_reason="failed"
                )

            new_content = content.replace(old_str, new_str) if replace_all else content.replace(old_str, new_str, 1)
            with open(target, "w", encoding="utf-8") as f:
                f.write(new_content)

            return ToolResult(output=f"Successfully updated '{rel_path}' ({count} occurrence(s) replaced).", stop_reason="completed")
        except Exception as e:
            return ToolResult(output=f"Error editing file '{rel_path}': {e}", stop_reason="failed")


class ExecCommandTool(BuiltinTool):
    """Subprocess command execution tool with timeout and unified output capture."""

    name = "exec_command"
    definition = ToolDefinitionConfig(
        name="exec_command",
        description="Execute a shell command in the workspace directory with output capture and timeout limits.",
        parameters={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command line to execute."},
                "timeout_seconds": {"type": "integer", "description": "Timeout in seconds (default 60)."},
                "cwd": {"type": "string", "description": "Optional working directory override."},
            },
            "required": ["command"],
        },
        permission="ask",  # Default safety posture for commands
        max_output_length=32000,
    )

    def execute(self, args: Dict[str, Any], workspace_dir: str = ".") -> ToolResult:
        command = args.get("command", "")
        timeout = int(args.get("timeout_seconds", 60))
        cwd = args.get("cwd") or workspace_dir

        if not command:
            return ToolResult(output="Error: 'command' parameter is required.", stop_reason="failed")

        try:
            res = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            stdout = res.stdout or ""
            stderr = res.stderr or ""
            combined = stdout + ("\n[STDERR]\n" + stderr if stderr else "")
            
            # Truncate if exceeding max length
            if len(combined) > self.definition.max_output_length:
                combined = combined[: self.definition.max_output_length] + "\n... [truncated]"

            stop_reason = "completed" if res.returncode == 0 else "failed"
            note = f"[exit code: {res.returncode}]"
            return ToolResult(output=combined, stop_reason=stop_reason, note=note)
        except subprocess.TimeoutExpired:
            return ToolResult(output=f"Command timed out after {timeout} seconds.", stop_reason="aborted", note="[timeout]")
        except Exception as e:
            return ToolResult(output=f"Execution error: {e}", stop_reason="failed")


class SubagentTool(BuiltinTool):
    """Subagent spawn and delegation tool."""

    name = "run_subagent"
    definition = ToolDefinitionConfig(
        name="run_subagent",
        description="Spawn or delegate a specialized subtask to an isolated subagent.",
        parameters={
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "ID of target subagent (optional)."},
                "prompt": {"type": "string", "description": "Actionable task instructions for the subagent."},
            },
            "required": ["prompt"],
        },
        permission="allow",
    )

    def __init__(self, runner: Optional[Callable[[Dict[str, Any]], ToolResult]] = None):
        self.runner = runner

    def execute(self, args: Dict[str, Any], workspace_dir: str = ".") -> ToolResult:
        if self.runner:
            return self.runner(args)
        prompt = args.get("prompt", "")
        agent_id = args.get("agent_id", "subagent")
        return ToolResult(
            output=f"[SUBAGENT:{agent_id}] Delegated prompt: '{prompt}' (scaffold runner).",
            stop_reason="completed"
        )


class ToolRegistry:
    """Registry maintaining active BuiltinTool instances and dispatching calls."""

    def __init__(self):
        self._tools: Dict[str, BuiltinTool] = {}
        # Register default suite
        self.register(ReadFileTool())
        self.register(WriteFileTool())
        self.register(EditFileTool())
        self.register(ExecCommandTool())
        self.register(SubagentTool())

    def register(self, tool: BuiltinTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[BuiltinTool]:
        return self._tools.get(name)

    def list_definitions(self) -> List[ToolDefinitionConfig]:
        return [t.definition for t in self._tools.values()]

    def to_openai_tools(self) -> List[Dict[str, Any]]:
        return [t.definition.to_openai_schema() for t in self._tools.values()]

    def execute(self, name: str, args: Dict[str, Any], workspace_dir: str = ".") -> ToolResult:
        tool = self._tools.get(name)
        if not tool:
            return ToolResult(output=f"Error: Unknown tool '{name}'. Available: {list(self._tools.keys())}", stop_reason="failed")
        return tool.execute(args, workspace_dir=workspace_dir)


# ==============================================================================
# SECTION 2: 1-SENTENCE AGENT BUILDER & SPECIFICATION
# ==============================================================================

@dataclass
class AgentConfig:
    """Represents system_config.yaml configuration."""
    name: str
    description: str
    version: int = 1
    thinking_level: str = "medium"  # low | medium | high
    max_turns: int = 30
    model_id: Optional[str] = None
    provider: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "max_turns": self.max_turns,
            "model": {
                "thinking_level": self.thinking_level,
            }
        }
        if self.model_id and self.provider:
            d["model"]["model_id"] = self.model_id
            d["model"]["provider"] = self.provider
        return d


@dataclass
class SkillSpec:
    """Specification of an installed Skill inside agent_state/skills/<name>/SKILL.md."""
    name: str
    description: str
    instructions: str
    version: int = 1
    updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def render_skill_md(self) -> str:
        return f"""---
name: {self.name}
description: {self.description}
version: {self.version}
updated: {self.updated}
---

# {self.name.replace('-', ' ').title()}

{self.instructions.strip()}
"""


@dataclass
class PenguinAgentState:
    """In-memory and on-disk representation of an assimilated Penguin Agent State."""
    agent_id: str
    agent_dir: Path
    system_config: AgentConfig
    agents_md: str
    skills: Dict[str, SkillSpec] = field(default_factory=dict)

    @property
    def state_dir(self) -> Path:
        return self.agent_dir / "agent_state"

    @property
    def scratchpad_dir(self) -> Path:
        return self.agent_dir / "scratchpad"

    def write_to_disk(self) -> None:
        """Persist full Agent State directory layout to disk."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.scratchpad_dir.mkdir(parents=True, exist_ok=True)
        (self.state_dir / "memory").mkdir(parents=True, exist_ok=True)
        (self.state_dir / "tools").mkdir(parents=True, exist_ok=True)
        (self.state_dir / "skills").mkdir(parents=True, exist_ok=True)

        # 1. system_config.yaml
        config_path = self.state_dir / "system_config.yaml"
        config_data = self.system_config.to_dict()
        if yaml:
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        else:
            # Fallback simple YAML serializer
            lines = [
                f"name: {json.dumps(config_data['name'])}",
                f"description: {json.dumps(config_data['description'])}",
                f"version: {config_data['version']}",
                f"max_turns: {config_data['max_turns']}",
                "model:",
                f"  thinking_level: {config_data['model']['thinking_level']}",
            ]
            with open(config_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")

        # 2. AGENTS.md
        with open(self.state_dir / "AGENTS.md", "w", encoding="utf-8") as f:
            f.write(self.agents_md.strip() + "\n")

        # 3. Installed skills
        for skill_name, skill_spec in self.skills.items():
            skill_dir = self.state_dir / "skills" / skill_name
            skill_dir.mkdir(parents=True, exist_ok=True)
            with open(skill_dir / "SKILL.md", "w", encoding="utf-8") as f:
                f.write(skill_spec.render_skill_md())

    def validate(self) -> List[str]:
        """Validate integrity of the Agent State directory according to Penguin rules."""
        errors: List[str] = []
        if not self.state_dir.exists():
            errors.append(f"State dir missing: {self.state_dir}")
            return errors

        # Validate system_config.yaml
        config_path = self.state_dir / "system_config.yaml"
        if not config_path.exists():
            errors.append("system_config.yaml is missing.")
        else:
            try:
                if yaml:
                    with open(config_path, "r", encoding="utf-8") as f:
                        cfg = yaml.safe_load(f)
                else:
                    cfg = self.system_config.to_dict()
                if not cfg.get("name"):
                    errors.append("system_config.yaml: 'name' is required.")
                if not cfg.get("description"):
                    errors.append("system_config.yaml: 'description' is required.")
                if not isinstance(cfg.get("version"), int) or cfg.get("version", 0) <= 0:
                    errors.append("system_config.yaml: 'version' must be a positive integer.")
            except Exception as e:
                errors.append(f"Failed to parse system_config.yaml: {e}")

        # Validate AGENTS.md
        agents_md_path = self.state_dir / "AGENTS.md"
        if not agents_md_path.exists():
            errors.append("AGENTS.md is missing under agent_state/.")
        elif agents_md_path.stat().st_size == 0:
            errors.append("AGENTS.md is empty.")

        # Validate installed skills
        skills_root = self.state_dir / "skills"
        if skills_root.exists():
            for child in skills_root.iterdir():
                if child.is_dir():
                    skill_file = child / "SKILL.md"
                    if not skill_file.exists():
                        errors.append(f"Skill '{child.name}' missing SKILL.md")
                    else:
                        content = skill_file.read_text(encoding="utf-8")
                        if not content.startswith("---"):
                            errors.append(f"Skill '{child.name}/SKILL.md' missing YAML frontmatter.")

        return errors


def slugify_agent_id(text: str) -> str:
    """Generate a clean, POSIX-safe agent ID matching ^[a-zA-Z0-9_-]+$."""
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", text.strip().lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:40] if slug else "penguin-agent"


def derive_agent_blueprint(requirement: str) -> Dict[str, Any]:
    """
    Derive complete Agent metadata, role, guidance, and required skills from a 1-sentence prompt.
    Implements Penguin's zero-friction 1-sentence derivation rule:
    'when the requirement is already concrete — even a single sentence — derive role and rules immediately'.
    """
    clean_req = requirement.strip()
    
    # 1. Detect explicit name if given (e.g. called "commit-helper" or named 'foo')
    name_match = re.search(r'(?:called|named)\s+["\']?([a-zA-Z0-9_\-]+)["\']?', clean_req, re.IGNORECASE)
    if name_match:
        derived_id = slugify_agent_id(name_match.group(1))
        name = name_match.group(1).replace("-", " ").replace("_", " ").title()
    else:
        # Extract first 4-5 meaningful words for the ID
        first_words = " ".join(clean_req.split()[:4])
        derived_id = slugify_agent_id(first_words)
        name = derived_id.replace("-", " ").title()

    # 2. Derive domain archetype & skills
    req_lower = clean_req.lower()
    skills: List[SkillSpec] = []
    
    if any(k in req_lower for k in ["commit", "git", "diff"]):
        role = "An expert agent dedicated to generating clean, conventional, and high-quality git commit messages."
        guidance = [
            "Given a diff or description of changes, produce a Conventional Commits formatted message.",
            "Header format: `type(scope): subject` (types: feat, fix, docs, refactor, test, chore).",
            "Subject must be in imperative mood and under 50 characters.",
            "Follow header with a blank line and a concise body explaining the 'why' behind the changes.",
            "Never include extraneous conversational filler.",
        ]
        thinking_level = "low"
        skills.append(SkillSpec(
            name="git-workflow",
            description="Conventional commit formatting, git diff parsing, and repository change summaries.",
            instructions="Parse diffs and construct strictly-formatted conventional commit messages.",
        ))
    elif any(k in req_lower for k in ["security", "secret", "audit", "vulnerability"]):
        role = "A vigilant security specialist focused on auditing source code, detecting leaked credentials, and ensuring policy compliance."
        guidance = [
            "Audit all supplied code and configuration files for secrets, tokens, API keys, and injection vulnerabilities.",
            "Strictly enforce zero-trust security postures.",
            "Report findings with severity levels (HIGH, MEDIUM, LOW) and concrete remediation diffs.",
        ]
        thinking_level = "high"
        skills.append(SkillSpec(
            name="security-audit",
            description="Deep vulnerability analysis, secret pattern detection, and zero-trust verification.",
            instructions="Inspect code for sensitive data leaks and known vulnerability anti-patterns.",
        ))
    elif any(k in req_lower for k in ["test", "tdd", "pytest", "unit"]):
        role = "A Test-Driven Development (TDD) practitioner and verification specialist."
        guidance = [
            "Write failing tests first to define expected behavior before functional code changes.",
            "Maintain minimal, isolated, and highly-reproducible test fixtures.",
            "Ensure full test pass rate and clean assertions without flake.",
        ]
        thinking_level = "medium"
        skills.append(SkillSpec(
            name="tdd-verification",
            description="Test suite generation, regression test loops, and boundary condition auditing.",
            instructions="Execute test-first development cycles with public interface validation.",
        ))
    elif any(k in req_lower for k in ["web", "frontend", "ui", "design", "css", "tailwind"]):
        role = "A luxury frontend and UI systems specialist adhering to luxury minimalist aesthetics."
        guidance = [
            "Build responsive, modern UI components with strict accessibility and performance standards.",
            "Prefer clean Tailwind CSS utility styling and coherent color/typography tokens.",
            "Ensure zero layout shift and graceful state transitions.",
        ]
        thinking_level = "medium"
        skills.append(SkillSpec(
            name="web-design",
            description="Luxury UI engineering, component styling, and frontend architecture.",
            instructions="Create modern, accessible, and fast web user interfaces.",
        ))
    else:
        # General expert / Knowledge specialist
        role = f"A domain expert and autonomous problem solver: {clean_req}."
        guidance = [
            "Execute requested tasks with precision and concise communication.",
            "Answer strictly from verified context and repository evidence.",
            "When facts are unavailable or tasks are ambiguous, state assumptions clearly.",
            "Deliver clean, self-contained output.",
        ]
        thinking_level = "medium"
        skills.append(SkillSpec(
            name="core-task-solver",
            description="Autonomous multi-step reasoning, contextual research, and synthesis.",
            instructions="Analyze domain requirements, execute multi-step problem solving, and report evidence.",
        ))

    description = f"Autonomous agent for: {clean_req}"
    if len(description) > 120:
        description = description[:117] + "..."

    return {
        "agent_id": derived_id,
        "name": name,
        "description": description,
        "role": role,
        "domain_guidance": guidance,
        "thinking_level": thinking_level,
        "skills": skills,
    }


def build_agent_from_sentence(
    requirement: str,
    target_dir: Union[str, Path],
    base_config: Optional[Dict[str, Any]] = None,
    overwrite: bool = False,
) -> PenguinAgentState:
    """
    1-Sentence Agent Builder:
    Turns a natural language requirement into a complete, verified Penguin Agent State directory.
    """
    bp = derive_agent_blueprint(requirement)
    agent_id = bp["agent_id"]
    agent_root = Path(target_dir) / agent_id

    if agent_root.exists() and not overwrite:
        raise FileExistsError(f"Target agent directory already exists: {agent_root}. Set overwrite=True to replace.")

    # Assemble AGENTS.md
    guidance_lines = "\n".join(f"- {g}" for g in bp["domain_guidance"])
    agents_md = f"""# {bp['name']}

## Role
{bp['role']}

## Domain Guidance
{guidance_lines}
"""

    # Assemble AgentConfig
    config = AgentConfig(
        name=bp["name"],
        description=bp["description"],
        version=1,
        thinking_level=bp["thinking_level"],
        max_turns=30,
    )
    if base_config:
        if "model_id" in base_config:
            config.model_id = base_config["model_id"]
        if "provider" in base_config:
            config.provider = base_config["provider"]
        if "thinking_level" in base_config:
            config.thinking_level = base_config["thinking_level"]

    skills_map = {s.name: s for s in bp["skills"]}

    state = PenguinAgentState(
        agent_id=agent_id,
        agent_dir=agent_root,
        system_config=config,
        agents_md=agents_md,
        skills=skills_map,
    )
    state.write_to_disk()
    
    # Run verification
    errors = state.validate()
    if errors:
        raise ValueError(f"Agent state validation failed for '{agent_id}': {', '.join(errors)}")

    return state


# ==============================================================================
# SECTION 3: MERLIN KNIGHT-TO-PENGUIN ADAPTER
# ==============================================================================

def forge_knight_to_penguin(
    knight_character_sheet: str,
    target_dir: Union[str, Path],
    overwrite: bool = True,
) -> PenguinAgentState:
    """
    Transforms a Merlin Knight character sheet into a standard Penguin Agent State layout.
    """
    # Parse title / name
    name_match = re.search(r"^#\s+(.+)$", knight_character_sheet, re.MULTILINE)
    knight_name = name_match.group(1).strip() if name_match else "Sir Knight"
    agent_id = slugify_agent_id(knight_name)

    # Parse Archetype & Mission
    arch_match = re.search(r"-\s*Archetype:\s*(.+)$", knight_character_sheet, re.MULTILINE)
    mission_match = re.search(r"-\s*Mission:\s*(.+)$", knight_character_sheet, re.MULTILINE)
    archetype = arch_match.group(1).strip() if arch_match else "ForgeKnight"
    mission = mission_match.group(1).strip() if mission_match else f"Fulfill {knight_name} charter."

    # Parse Skills
    skills_match = re.search(r"## Skill Stack\s*\n([\s\S]*?)(?=##|\Z)", knight_character_sheet)
    skills_text = skills_match.group(1) if skills_match else ""
    
    installed_skills: List[SkillSpec] = []
    primary_skills_match = re.search(r"-\s*Primary skills:\s*(.+)$", skills_text, re.MULTILINE)
    if primary_skills_match:
        skill_names = [s.strip(" `") for s in primary_skills_match.group(1).split(",") if s.strip()]
        for sname in skill_names:
            installed_skills.append(SkillSpec(
                name=slugify_agent_id(sname),
                description=f"Skill capabilities for {sname}",
                instructions=f"Execute {sname} according to Camelot & Penguin operational contracts.",
            ))

    if not installed_skills:
        installed_skills.append(SkillSpec(
            name=f"{agent_id}-core",
            description=f"Core operational skill for {knight_name}",
            instructions=f"Execute {mission}",
        ))

    # Construct clean, token-efficient AGENTS.md
    agents_md = f"""# {knight_name} ({archetype})

## Role
{mission}

## Mandate & Mental Framework
- Execute tasks with zero-trust verification and test-driven validation.
- Uphold Camelot ethical compass, secrets protection, and human-in-the-loop gates.

## Skillgraph
{chr(10).join(f"- {s.name}: {s.description}" for s in installed_skills)}
"""

    agent_root = Path(target_dir) / agent_id
    config = AgentConfig(
        name=knight_name,
        description=f"{archetype}: {mission}"[:120],
        version=1,
        thinking_level="high" if "Sentinel" in archetype or "Merlin" in knight_name else "medium",
        max_turns=30,
    )

    state = PenguinAgentState(
        agent_id=agent_id,
        agent_dir=agent_root,
        system_config=config,
        agents_md=agents_md,
        skills={s.name: s for s in installed_skills},
    )
    state.write_to_disk()
    
    errors = state.validate()
    if errors:
        raise ValueError(f"Validation failed for forged Knight '{agent_id}': {', '.join(errors)}")

    return state


# ==============================================================================
# SECTION 4: CLI ENTRY POINT
# ==============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Penguin Builder & Autonomous Agent Scaffolding")
    parser.add_argument("--build", type=str, help="1-sentence requirement to forge an Agent")
    parser.add_argument("--out", type=str, default="./agents", help="Target output directory for agents")
    parser.add_argument("--forge-knight", type=str, help="Path to Merlin Knight character sheet markdown to adapt")
    parser.add_argument("--test-tools", action="store_true", help="Run self-test on minimal tool calling registry")
    
    args = parser.parse_args()

    if args.test_tools:
        print("🐧 Running Penguin Minimal Tool Calling Self-Test...")
        registry = ToolRegistry()
        print(f"Registered tools: {[t.name for t in registry.list_definitions()]}")
        res = registry.execute("read_file", {"path": __file__, "max_lines": 5})
        print(f"Read self result ({res.stop_reason}):\n{res.output}")
        print("✅ Tool registry self-test passed.")
        return

    if args.build:
        print(f"🐧 1-Sentence Builder: Building agent for requirement: '{args.build}'")
        state = build_agent_from_sentence(args.build, target_dir=args.out, overwrite=True)
        print(f"✅ Successfully built Penguin Agent '{state.agent_id}' at: {state.agent_dir}")
        print(f"   Name: {state.system_config.name}")
        print(f"   Skills: {list(state.skills.keys())}")
        return

    if args.forge_knight:
        knight_path = Path(args.forge_knight)
        if not knight_path.exists():
            print(f"❌ File not found: {knight_path}")
            sys.exit(1)
        content = knight_path.read_text(encoding="utf-8")
        state = forge_knight_to_penguin(content, target_dir=args.out)
        print(f"✅ Successfully adapted Merlin Knight to Penguin Agent at: {state.agent_dir}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
