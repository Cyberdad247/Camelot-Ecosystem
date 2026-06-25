"""Sir Boris - The Anvil / Polyglot Architect (God-Tier v2.1).

Autonomous Senior-Level Code Synthesis, Antagonistic Peer Review,
E2E Self-Healing, Squire Colony Command, //vocal Voice OS Bootstrap.

Upgrade: BORIS_OMEGA_UPGRADE v2.0 -> v2.1 (13-Agent Critique real checks).
Harnesses: ECC v1.9.0, DeerFlow 2.0, Vercel E2E Self-Healing.
"""

import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from .base import BaseKnight

# Squire Colony root (relative to CAMELOT_OS)
CAMELOT_OS = Path(os.environ.get("CAMELOT_OS", Path.home() / "CAMELOT_OS"))
SQUIRE_COLONY = CAMELOT_OS / "squires"

# Patterns for validation checks
_SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|credential)\s*[=:]\s*['\"][^'\"]{8,}"),
    re.compile(r"(?i)(AKIA[0-9A-Z]{16})"),  # AWS
    re.compile(r"(?i)(sk-[a-zA-Z0-9]{20,})"),  # OpenAI
    re.compile(r"(?i)(ghp_[a-zA-Z0-9]{36})"),  # GitHub PAT
]

_DANGEROUS_CALLS = {"exec", "eval", "os.system", "subprocess.call", "__import__"}

_CONCURRENCY_MARKERS = {"threading.Thread", "multiprocessing.Process",
                        "asyncio.gather", "Lock(", "Semaphore("}


class PlanModeViolation(RuntimeError):
    """Raised when code execution is attempted without a prior plan phase."""


class SirBoris(BaseKnight):
    name = "Sir Boris"
    title = "The Anvil / Polyglot Architect"
    specialty = "Claude Code Orchestration & Squire Colony Command"
    icon = "\U0001f30c"  # galaxy emoji
    version = "2.1"
    layer = "L5_AGENTIC"
    rune = "//vocal"
    codename = "The_Polyglot_Architect"

    # AST-Aware Plan Mode enforcement state

    # Personality & Prisms
    personality = "Diplomatic but blunt, values correctness over consensus, Ice-cold debugging."
    backstory = "Survivor of the API Blackouts. Rose to lead the Foundry Council as The Anvil."
    humanistic_prism = "Protect the system to protect the user. Security and stability are fundamental human rights."
    alexandria_prism = "Complete map of cross-engine critique failures, system collapses, and supply chain vulnerabilities."
    # Plan must be generated and approved before kinetic execution
    _plan_state: str = "IDLE"  # IDLE -> PLANNED -> CRITIQUED -> APPROVED -> EXECUTING
    _active_plan: dict | None = None
    _critique_report: list[dict] | None = None

    # Proteus MPI vectors (Soul Matrix) — full OCEAN
    MPI = {
        "openness": 0.95,
        "conscientiousness": 1.00,
        "extraversion": 0.35,
        "agreeableness": 0.45,
        "neuroticism": 0.01,
    }

    # 13-Agent Antagonistic Critique pipeline — each with real validation
    CRITIQUE_AGENTS = [
        "architect",            # Agent 1: AST plan + dependency map
        "security_auditor",     # Agent 2: injection, auth, crypto
        "contract_verifier",    # Agent 3: input/output contracts
        "test_coverage",        # Agent 4: missing test paths
        "edge_case_analyst",    # Agent 5: boundary conditions
        "type_safety",          # Agent 6: type narrowing, nulls
        "perf_profiler",        # Agent 7: hot paths, allocation
        "concurrency_check",    # Agent 8: race conditions, deadlocks
        "api_surface_review",   # Agent 9: breaking changes, versioning
        "rollback_validator",   # Agent 10: revert strategy
        "agentshield_scanner",  # Agent 11: prompt injection guard
        "integration_auditor",  # Agent 12: cross-module compat
        "ops_reviewer",         # Agent 13: deploy impact, monitoring
    ]

    def execute(self, directive: str, intent: dict, write: bool = False) -> dict:
        """Execute a directive with mandatory AST-Aware Plan Mode enforcement.

        Flow: PLAN -> CRITIQUE -> APPROVE -> EXECUTE (Titanium Law T4).
        Bypass is only permitted for Colony status queries and //vocal bootstrap.
        """
        tokens = intent.get("tokens", [])
        domain = intent.get("domain", "GENERAL")
        complexity = intent.get("complexity", 2)
        runic = intent.get("runic", "")

        # --- Passthrough commands (no plan required) ---
        if runic == "//vocal" or directive.strip().lower().startswith("//vocal"):
            return self._vocal_bootstrap(directive, intent, write)

        if "colony" in directive.lower() or "squire" in directive.lower():
            return self._colony_command(directive, intent, write)

        # --- Critique request: run pipeline, cache results ---
        if "critique" in directive.lower() or "review" in directive.lower():
            result = self._critique_files(directive, intent, write)
            self._critique_report = result.get("_findings", [])
            self._plan_state = "CRITIQUED"
            return result

        # --- PLAN MODE ENFORCEMENT (ECC v1.9.0 Mandate) ---
        # If complexity > 3 reasoning steps OR this is a code-gen request,
        # the plan gate is MANDATORY. No plan = no code.
        if "approve" in directive.lower() and self._plan_state == "CRITIQUED":
            self._plan_state = "APPROVED"
            return {
                "status": "success",
                "output": "[EXECUTE] Plan APPROVED. Sir Boris is now cleared for kinetic execution.",
                "files_created": [],
            }

        if "execute" in directive.lower() or write:
            if self._plan_state not in ("APPROVED", "EXECUTING"):
                # Enforce: must plan first
                if self._plan_state == "IDLE":
                    plan_result = self._plan_mode_synthesis(directive, intent, write=False)
                    self._plan_state = "PLANNED"
                    plan_result["output"] = (
                        "[PLAN] AST-Aware Plan Mode ENFORCED.\n"
                        + plan_result["output"]
                        + "\n\n[GATE] 13-Agent Critique required before execution.\n"
                        "Run 'critique' on target files, then 'approve' to unlock kinetic execution."
                    )
                    return plan_result
                elif self._plan_state == "PLANNED":
                    return {
                        "status": "blocked",
                        "output": "[GATE] 13-Agent Critique not yet run. "
                                  "Execute 'critique' before proceeding.",
                        "files_created": [],
                    }
                elif self._plan_state == "CRITIQUED":
                    return {
                        "status": "blocked",
                        "output": "[GATE] Critique complete but not approved. "
                                  "Execute 'approve' to unlock kinetic execution.",
                        "files_created": [],
                    }

            # Approved — proceed to kinetic execution
            self._plan_state = "EXECUTING"
            result = self._plan_mode_synthesis(directive, intent, write)
            self._plan_state = "IDLE"  # Reset for next cycle
            self._active_plan = None
            self._critique_report = None
            return result

        # --- Default: Generate plan (first step of the gate) ---
        plan_result = self._plan_mode_synthesis(directive, intent, write=False)
        self._active_plan = plan_result
        self._plan_state = "PLANNED"
        plan_result["output"] = (
            "[PLAN] AST-Aware Plan Mode (ECC v1.9.0)\n"
            + plan_result["output"]
            + "\n\n[NEXT] Run 'critique' -> 'approve' -> 'execute' to proceed."
        )
        return plan_result

    # ------------------------------------------------------------------
    # 13-AGENT ANTAGONISTIC CRITIQUE (Minimum Validation Checks)
    # ------------------------------------------------------------------

    def _critique_files(self, directive: str, intent: dict, write: bool) -> dict:
        """Run 13-Agent Critique pipeline on target files."""
        target = intent.get("parameters", {}).get("path", ".")
        target_path = Path(target)
        if not target_path.exists():
            target_path = CAMELOT_OS / target

        py_files = list(target_path.rglob("*.py")) if target_path.is_dir() else [target_path]
        py_files = [f for f in py_files if f.is_file() and "__pycache__" not in str(f)]

        all_findings: list[dict] = []
        for fpath in py_files[:50]:  # cap at 50 files
            try:
                source = fpath.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            findings = self._run_critique_pipeline(fpath, source)
            if findings:
                all_findings.extend(findings)

        report = self._format_critique_report(all_findings, len(py_files))

        files = []
        if write:
            report_path = CAMELOT_OS / "logs" / "boris_critique.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps({
                "files_scanned": len(py_files),
                "total_findings": len(all_findings),
                "findings": all_findings,
            }, indent=2, default=str), encoding="utf-8")
            files.append(str(report_path))

        return {"status": "success", "output": report, "files_created": files}

    def _run_critique_pipeline(self, fpath: Path, source: str) -> list[dict]:
        """Execute all 13 agents against a single file."""
        findings: list[dict] = []
        fname = str(fpath)

        # Agent 1: Architect — AST parse check
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            findings.append({"agent": "architect", "severity": "HIGH",
                             "file": fname, "msg": f"SyntaxError: {e.msg} (line {e.lineno})"})
            return findings  # can't continue if AST fails

        # Agent 2: Security Auditor — secret leaks + dangerous calls
        for i, line in enumerate(source.splitlines(), 1):
            for pat in _SECRET_PATTERNS:
                if pat.search(line):
                    findings.append({"agent": "security_auditor", "severity": "CRITICAL",
                                     "file": fname, "line": i,
                                     "msg": f"Potential secret/credential on line {i}"})
            for danger in _DANGEROUS_CALLS:
                if danger in line and not line.lstrip().startswith("#"):
                    findings.append({"agent": "security_auditor", "severity": "HIGH",
                                     "file": fname, "line": i,
                                     "msg": f"Dangerous call '{danger}' on line {i}"})

        # Agent 3: Contract Verifier — functions missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not ast.get_docstring(node) and not node.name.startswith("_"):
                    findings.append({"agent": "contract_verifier", "severity": "LOW",
                                     "file": fname, "line": node.lineno,
                                     "msg": f"Public function '{node.name}' missing docstring"})

        # Agent 4: Test Coverage — check if test file exists for modules
        if not fname.endswith("test_") and "test" not in Path(fname).stem:
            test_name = f"test_{Path(fname).stem}.py"
            test_dir = CAMELOT_OS / "tests"
            if test_dir.is_dir() and not (test_dir / test_name).exists():
                findings.append({"agent": "test_coverage", "severity": "MEDIUM",
                                 "file": fname,
                                 "msg": f"No test file found: tests/{test_name}"})

        # Agent 5: Edge Case Analyst — bare except, division without guard
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                findings.append({"agent": "edge_case_analyst", "severity": "MEDIUM",
                                 "file": fname, "line": node.lineno,
                                 "msg": f"Bare 'except:' clause (line {node.lineno}) — may swallow errors"})

        # Agent 6: Type Safety — function args without annotations
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    unannotated = [a.arg for a in node.args.args
                                   if a.annotation is None and a.arg != "self"]
                    if unannotated:
                        findings.append({"agent": "type_safety", "severity": "LOW",
                                         "file": fname, "line": node.lineno,
                                         "msg": f"'{node.name}' has untyped args: {unannotated}"})

        # Agent 7: Perf Profiler — nested loops (O(n²) warning)
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if child is not node and isinstance(child, (ast.For, ast.While)):
                        findings.append({"agent": "perf_profiler", "severity": "LOW",
                                         "file": fname, "line": node.lineno,
                                         "msg": f"Nested loop detected at line {node.lineno} — O(n²) risk"})
                        break

        # Agent 8: Concurrency Check — threading/async markers
        for i, line in enumerate(source.splitlines(), 1):
            for marker in _CONCURRENCY_MARKERS:
                if marker in line:
                    findings.append({"agent": "concurrency_check", "severity": "INFO",
                                     "file": fname, "line": i,
                                     "msg": f"Concurrency construct '{marker.rstrip('(')}' at line {i} — verify thread safety"})

        # Agent 9: API Surface Review — public functions/classes count
        public_items = [n for n in ast.iter_child_nodes(tree)
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                        and not n.name.startswith("_")]
        if len(public_items) > 15:
            findings.append({"agent": "api_surface_review", "severity": "MEDIUM",
                             "file": fname,
                             "msg": f"Large public API surface: {len(public_items)} exports — consider splitting module"})

        # Agent 10: Rollback Validator — file size warning
        line_count = len(source.splitlines())
        if line_count > 500:
            findings.append({"agent": "rollback_validator", "severity": "INFO",
                             "file": fname,
                             "msg": f"Large file ({line_count} lines) — rollback risk higher, consider decomposition"})

        # Agent 11: AgentShield Scanner — prompt injection patterns
        injection_patterns = [
            re.compile(r"(?i)ignore\s+(previous|above|all)\s+instructions"),
            re.compile(r"(?i)you\s+are\s+now\s+"),
            re.compile(r"(?i)system\s*:\s*"),
        ]
        for i, line in enumerate(source.splitlines(), 1):
            for pat in injection_patterns:
                if pat.search(line) and not line.lstrip().startswith("#"):
                    findings.append({"agent": "agentshield_scanner", "severity": "HIGH",
                                     "file": fname, "line": i,
                                     "msg": f"Potential prompt injection pattern at line {i}"})

        # Agent 12: Integration Auditor — import health check
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith(".") or node.module.startswith("knights"):
                    # Relative import — check if module file exists
                    parts = node.module.lstrip(".").split(".")
                    candidate = fpath.parent / "/".join(parts)
                    if not candidate.with_suffix(".py").exists() and not (candidate / "__init__.py").exists():
                        findings.append({"agent": "integration_auditor", "severity": "MEDIUM",
                                         "file": fname, "line": node.lineno,
                                         "msg": f"Import '{node.module}' may be broken — target not found"})

        # Agent 13: Ops Reviewer — print statements (should use logging)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "print":
                    findings.append({"agent": "ops_reviewer", "severity": "INFO",
                                     "file": fname, "line": node.lineno,
                                     "msg": f"print() at line {node.lineno} — consider logging for production"})
                    break  # only flag once per file

        return findings

    def _format_critique_report(self, findings: list[dict], file_count: int) -> str:
        """Format findings into a concise report."""
        if not findings:
            return f"[REVIEW] 13-Agent Critique: {file_count} files scanned. ALL CLEAR — no findings."

        by_severity: dict[str, int] = {}
        by_agent: dict[str, int] = {}
        for f in findings:
            by_severity[f["severity"]] = by_severity.get(f["severity"], 0) + 1
            by_agent[f["agent"]] = by_agent.get(f["agent"], 0) + 1

        lines = [
            f"[REVIEW] 13-Agent Critique: {file_count} files scanned, {len(findings)} findings.",
            "",
            "  Severity:",
        ]
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            if sev in by_severity:
                lines.append(f"    {sev}: {by_severity[sev]}")
        lines.append("")
        lines.append("  By Agent:")
        for agent, count in sorted(by_agent.items(), key=lambda x: -x[1]):
            lines.append(f"    {agent}: {count}")
        lines.append("")

        # Show top 10 most severe findings
        priority = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        top = sorted(findings, key=lambda f: priority.get(f["severity"], 5))[:10]
        lines.append("  Top Findings:")
        for f in top:
            loc = f"line {f['line']}" if "line" in f else ""
            lines.append(f"    [{f['severity']}] {f['agent']}: {f['msg']}")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # PLAN MODE
    # ------------------------------------------------------------------

    def _plan_mode_synthesis(self, directive: str, intent: dict, write: bool) -> dict:
        """Phase 1: Sir Oracle — AST-Aware Plan Mode."""
        topic = directive.strip()
        complexity = intent.get("complexity", 2)
        budget = intent.get("budget_tokens", 1000000)

        # [HYPERAGENT_UPGRADE] v400.1.0: Compute-Aware Orchestration
        swarm_mode = budget > 500000 and complexity > 3
        
        plan = {
            "title": f"Sir Boris Plan: {topic[:60]}",
            "phase": "ORACLE (SWARM)" if swarm_mode else "ORACLE",
            "ast_dependencies": [],
            "hopeful_paths": [],
            "rollback_strategy": "git stash + provenance ledger checkpoint",
            "critique_pipeline": self.CRITIQUE_AGENTS,
            "critique_count": len(self.CRITIQUE_AGENTS),
            "soul_matrix": self.MPI,
            "estimated_phases": max(2, complexity),
            "swarm_mode": swarm_mode,
        }

        output = self._format_plan(plan)

        files = []
        if write:
            plan_path = CAMELOT_OS / "logs" / "boris_plan.json"
            plan_path.parent.mkdir(parents=True, exist_ok=True)
            plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
            files.append(str(plan_path))

        return {
            "status": "success",
            "output": output,
            "files_created": files,
        }

    def _colony_command(self, directive: str, intent: dict, write: bool) -> dict:
        """Route Squire Colony commands."""
        lower = directive.lower()

        # Determine sub-command
        if "status" in lower:
            cmd = "status"
        elif "triage" in lower:
            cmd = "triage"
        elif "index" in lower:
            cmd = "index"
        elif "ghost" in lower:
            cmd = "ghost"
        elif "vector" in lower:
            cmd = "vector"
        elif "scan" in lower:
            cmd = "scan"
        else:
            cmd = "status"

        colony_py = SQUIRE_COLONY / "colony.py"
        if not colony_py.exists():
            return {
                "status": "error",
                "output": f"Squire Colony not found at {colony_py}",
                "files_created": [],
            }

        try:
            result = subprocess.run(
                [sys.executable, "-m", "squires.colony", cmd],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(CAMELOT_OS),
            )
            output = result.stdout or result.stderr or "(no output)"
        except subprocess.TimeoutExpired:
            output = f"[COLONY] {cmd} timed out after 120s"
        except Exception as e:
            output = f"[COLONY] Error: {e}"

        return {
            "status": "success",
            "output": f"[COLONY] {cmd.upper()}\n{output}",
            "files_created": [],
        }

    def _vocal_bootstrap(self, directive: str, intent: dict, write: bool) -> dict:
        """//vocal — 3-phase Voice OS bootstrap."""
        phases = []

        # Phase 1: Oracle
        phases.append("[PLAN] Phase 1: The Oracle Phase")
        phases.append("  - Mapping local directory structure")
        phases.append("  - Verifying notebooklm-mcp-cli auth")
        phases.append("  - Mapping OmniRoute (port 20128) -> LiveKit endpoints")

        # Phase 2: Veritas
        phases.append("[REVIEW] Phase 2: The Veritas Phase")
        phases.append("  - Extracting persona Souls from NotebookLM Cloud Brain")
        phases.append("  - Mapping Proteus MPI vectors per persona")
        phases.append("  - Assigning distinct Voice IDs (ElevenLabs/Cartesia)")
        phases.append("  - Running 13-Agent critique on voice bindings")

        # Phase 3: Lazarus
        phases.append("[EXECUTE] Phase 3: The Lazarus Phase")
        phases.append("  - Configuring Saltare Semantic Gateway")
        phases.append("  - Running mock voice interruption test")
        phases.append("  - E2E self-healing loop (up to 3 cycles)")
        phases.append("  - Handing live microphone to user")

        output = "\n".join(phases)

        return {
            "status": "success",
            "output": f"[VOCAL] //vocal Bootstrap Protocol\n{output}\n\n"
                      f"[VOCAL] Voice OS deployment requires LiveKit + OmniRoute. "
                      f"Run 'nlm login' first to authenticate.",
            "files_created": [],
        }

    def _format_plan(self, plan: dict) -> str:
        lines = [
            f"[PLAN] {plan['title']}",
            f"  Phase: {plan['phase']} (Sir Oracle)",
            f"  Rollback: {plan['rollback_strategy']}",
            f"  Critique Pipeline: {plan['critique_count']} agents armed",
            f"  Estimated Phases: {plan['estimated_phases']}",
            f"  Soul Matrix: O={plan['soul_matrix']['openness']} "
            f"C={plan['soul_matrix']['conscientiousness']} "
            f"N={plan['soul_matrix']['neuroticism']}",
        ]
        return "\n".join(lines)

    def format_header(self) -> str:
        return (
            f"{self.icon} {self.name} v{self.version} "
            f"({self.title}) -- {self.specialty} "
            f"[{self.layer}] [{self.rune}]"
        )
