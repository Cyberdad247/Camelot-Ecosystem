# -*- coding: utf-8 -*-
"""
sir_gideon.py — Sir Gideon, The Forensic Auditor
=================================================
Implements the 10 GIDEON_RISK_MATRIX Shatterpoints as Python detection
functions. Triggered by //SCORPION rune or "gideon" knight_id.

Each Shatterpoint scanner returns: CLEAR | WARN | CRITICAL + evidence list.
GIDEON_RISK_SCORE = sum of criticality weights. Pass threshold: <= 2.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .base import BaseKnight

CAMELOT_OS = Path(__file__).resolve().parents[4]
CONTROL_PLANE = CAMELOT_OS / "control_plane"
VAULT_CONFIGS = CAMELOT_OS / "03_VAULT" / "training" / "configs"
SKILLS_DIR    = CAMELOT_OS / ".hive" / "skills"
FORGE_DIR     = CAMELOT_OS / "02_FORGE"
KINETIC_DIR   = CAMELOT_OS / "kinetic_edge"

EXPECTED_SKILLS = [
    "rust-kinetic", "security", "swarm-colony", "python-api",
    "nextjs", "reasoning", "voice-media", "bitnet",
]

SEVERITY_WEIGHT = {"CRITICAL": 2, "WARN": 1, "CLEAR": 0}


@dataclass
class SpResult:
    shatterpoint: str
    status: str       # CLEAR | WARN | CRITICAL
    evidence: list[str] = field(default_factory=list)
    weight: int = 0

    def __post_init__(self):
        self.weight = SEVERITY_WEIGHT.get(self.status, 0)


@dataclass
class GideonReport:
    shatterpoints: list[SpResult]
    gideon_risk_score: int
    passed: bool
    duration_ms: float
    summary: str


# ── Shatterpoint Detection Functions ─────────────────────────────────────────

def _sp01_a2a_no_rbac() -> SpResult:
    """SP-01: A2A dispatch gateway lacks RBAC enforcement.

    Strategy: verify that the OMC dispatch gateway (omc_team.py) enforces RBAC
    before sending work to any terminal. Callers of omc_team.dispatch() are
    protected by proxy — we don't require RBAC in every upstream caller.
    Direct .execute() calls that bypass omc_team are separately flagged.
    """
    evidence = []
    rbac_import = re.compile(r"rbac_matrix|RBACMatrix", re.IGNORECASE)

    # Primary: omc_team.py (the dispatch gateway) must have RBAC
    gateway = CONTROL_PLANE / "omc_team.py"
    if gateway.exists():
        try:
            txt = gateway.read_text(encoding="utf-8", errors="replace")
            if not rbac_import.search(txt):
                evidence.append("omc_team.py: dispatch gateway missing RBAC enforcement")
        except OSError:
            evidence.append("omc_team.py: unreadable")
    else:
        evidence.append("omc_team.py: missing — dispatch gateway not found")

    # Secondary: files that call .execute() directly on an agent (bypassing omc_team)
    direct_exec_re = re.compile(r"\w+\s*\.\s*execute\s*\(", re.IGNORECASE)
    omc_via_re = re.compile(r"omc_team|OMCTeam|_omc_team", re.IGNORECASE)
    skip = {"rbac_matrix.py", "harness.py", "anya_gate.py", "omc_team.py"}
    for py in CONTROL_PLANE.glob("*.py"):
        if py.name in skip:
            continue
        try:
            txt = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if direct_exec_re.search(txt) and not omc_via_re.search(txt) and not rbac_import.search(txt):
            evidence.append(f"{py.name}: direct .execute() without RBAC or omc_team routing")

    if not (VAULT_CONFIGS / "config" / "access_matrix.json").exists():
        evidence.append("access_matrix.json missing")

    status = "CLEAR" if not evidence else ("CRITICAL" if evidence else "WARN")
    return SpResult("SP-01: A2A no RBAC", status, evidence)


def _sp02_iron_gate_bypass() -> SpResult:
    """SP-02: Iron Gate / HITL bypass patterns."""
    evidence = []
    bypass_re = re.compile(
        r"skip_hitl|no.?verify|bypass.*iron|iron.*bypass|HITL\s*=\s*False",
        re.IGNORECASE,
    )
    for py in list(CONTROL_PLANE.glob("*.py")) + list(VAULT_CONFIGS.glob("*.py")):
        try:
            txt = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(txt.splitlines(), 1):
            if bypass_re.search(line) and not line.strip().startswith("#"):
                evidence.append(f"{py.name}:{i}: {line.strip()[:80]}")

    status = "CLEAR" if not evidence else "CRITICAL"
    return SpResult("SP-02: Iron Gate bypass", status, evidence)


def _sp03_kinetic_purity() -> SpResult:
    """SP-03: Python used where Rust/Go binary exists."""
    evidence = []
    # Check for subprocess calls to python where a binary equivalent should exist
    py_subprocess_re = re.compile(
        r'subprocess\.[^(]+\([^)]*[\'"]\s*python[^\'"]*[\'"]',
        re.IGNORECASE,
    )
    # Binaries that should not be re-implemented in Python
    protected_bins = ["cribo", "saltare", "rotel", "bitnet"]

    for py in CONTROL_PLANE.glob("*.py"):
        try:
            txt = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(txt.splitlines(), 1):
            if py_subprocess_re.search(line):
                evidence.append(f"{py.name}:{i}: {line.strip()[:80]}")

    # Check if swarm_spawner Cargo.toml exists (Rust binary should exist)
    if not (KINETIC_DIR / "swarm_spawner" / "Cargo.toml").exists():
        evidence.append("swarm_spawner/Cargo.toml missing — Python fallback risk")

    status = "CLEAR" if not evidence else "WARN"
    return SpResult("SP-03: Kinetic Purity", status, evidence)


def _sp04_voxservice_race() -> SpResult:
    """SP-04: VoxService async race conditions (time.sleep inside async def blocks)."""
    evidence = []
    voice_files = list(VAULT_CONFIGS.glob("*voice*")) + list(VAULT_CONFIGS.glob("*vox*"))
    voice_files += list(FORGE_DIR.rglob("*voice*"))

    for vf in voice_files:
        if not vf.is_file() or vf.suffix not in (".py",):
            continue
        try:
            lines = vf.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        in_async = False
        async_indent: int | None = None
        for i, line in enumerate(lines, 1):
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            if re.match(r"async\s+def\s+", stripped):
                in_async = True
                async_indent = indent
            elif in_async and async_indent is not None and line.strip() and indent <= async_indent and not stripped.startswith("#"):
                in_async = False
                async_indent = None
            if in_async and re.search(r"\btime\.sleep\s*\(", line):
                evidence.append(f"{vf.name}:{i}: time.sleep inside async def")

    # Also flag unguarded global voice state
    global_re = re.compile(r"^global\s+_voice", re.MULTILINE)
    for vf in voice_files:
        if not vf.is_file() or vf.suffix != ".py":
            continue
        try:
            txt = vf.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if global_re.search(txt):
            evidence.append(f"{vf.name}: unguarded global voice state")

    status = "CLEAR" if not evidence else "WARN"
    return SpResult("SP-04: VoxService race", status, evidence)


def _sp05_sql_injection() -> SpResult:
    """SP-05: SQL injection via f-string / string concatenation."""
    evidence = []
    # Require SQL structure: keyword + space + typical SQL context words
    sqli_re = re.compile(
        r'f["\'][^"\']*\b(SELECT|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)\b',
        re.IGNORECASE,
    )
    for py in list(CONTROL_PLANE.glob("*.py")) + list(VAULT_CONFIGS.glob("*.py")):
        try:
            txt = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(txt.splitlines(), 1):
            if sqli_re.search(line) and not line.strip().startswith("#"):
                evidence.append(f"{py.name}:{i}: {line.strip()[:80]}")

    status = "CLEAR" if not evidence else "CRITICAL"
    return SpResult("SP-05: SQL injection", status, evidence)


def _sp06_missing_briefing_script() -> SpResult:
    """SP-06: Mass WRITE/DELETE ops without BriefingScript / Iron Gate approval."""
    evidence = []
    # Only flag destructive ops (write/delete/move), not read-only glob/walk
    destructive_re = re.compile(
        r"shutil\.(copy|move|rmtree|copytree)|os\.(remove|unlink|rename)|"
        r"Path\(.*\)\.(write_text|write_bytes|unlink|rename)|"
        r"open\([^)]+['\"][wa]['\"]",
        re.IGNORECASE,
    )
    plan_gate_re = re.compile(r"briefing|hitl|iron_gate|user_approv", re.IGNORECASE)
    # Exclude known scan-only modules and sandbox/temp-dir patterns
    scan_only = {"lord_archivist.py", "rbac_matrix.py", "runic_router.py",
                 "config_manager.py", "deerflow_sandbox.py"}

    for py in CONTROL_PLANE.glob("*.py"):
        if py.name in scan_only:
            continue
        try:
            txt = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if destructive_re.search(txt) and not plan_gate_re.search(txt):
            evidence.append(f"{py.name}: destructive file ops without approval gate")

    status = "CLEAR" if not evidence else "WARN"
    return SpResult("SP-06: Missing BriefingScript", status, evidence)


def _sp07_swarm_without_harness() -> SpResult:
    """SP-07: Bio-Swarm spawned outside Sovereign Harness control."""
    evidence = []
    # Species names used outside harness / swarm_spawner
    species_re = re.compile(
        r"\b(formica|pongid|castor|arachne|simian|strigiform)\b",
        re.IGNORECASE,
    )
    harness_ref_re = re.compile(r"harness|HarnessTask|swarm_spawner", re.IGNORECASE)

    for py in CONTROL_PLANE.glob("*.py"):
        if py.name in ("harness.py",):
            continue
        try:
            txt = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if species_re.search(txt) and not harness_ref_re.search(txt):
            evidence.append(f"{py.name}: species referenced outside harness context")

    status = "CLEAR" if not evidence else "WARN"
    return SpResult("SP-07: Swarm outside harness", status, evidence)


def _sp08_missing_zod() -> SpResult:
    """SP-08: External API calls without response validation (Zod / pydantic).

    Internal service probes (127.0.0.1 / localhost) wrapped in try/except and
    guarded by status_code checks are exempt — they are not trust boundaries.
    """
    evidence = []
    # Only flag calls to external (non-localhost) endpoints
    external_fetch_re = re.compile(
        r'(requests|httpx)\.(get|post|put|delete|request)\s*\(\s*["\']https?://(?!127\.0\.0\.1|localhost)',
        re.IGNORECASE,
    )
    validate_re = re.compile(
        r"\.model_validate|BaseModel|TypeAdapter|ZodSchema|\.raise_for_status\(\)|schema_validator",
        re.IGNORECASE,
    )

    for py in list(CONTROL_PLANE.glob("*.py")) + list(VAULT_CONFIGS.glob("*.py")):
        try:
            txt = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if external_fetch_re.search(txt) and not validate_re.search(txt):
            evidence.append(f"{py.name}: external HTTP call without response validation")

    status = "CLEAR" if not evidence else "WARN"
    return SpResult("SP-08: Missing validation", status, evidence)


def _sp09_sync_db_in_async() -> SpResult:
    """SP-09: time.sleep() called directly inside an async def body."""
    evidence = []

    for py in CONTROL_PLANE.glob("*.py"):
        try:
            lines = py.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        in_async = False
        async_indent: int | None = None
        for i, line in enumerate(lines, 1):
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            if re.match(r"async\s+def\s+", stripped):
                in_async = True
                async_indent = indent
            elif in_async and async_indent is not None and line.strip() and indent <= async_indent and not stripped.startswith("#"):
                in_async = False
                async_indent = None
            if in_async and re.search(r"\btime\.sleep\s*\(", line):
                evidence.append(f"{py.name}:{i}: time.sleep inside async def (use asyncio.sleep)")

    status = "CLEAR" if not evidence else "WARN"
    return SpResult("SP-09: Sync I/O in async", status, evidence)


def _sp10_missing_skill_bible() -> SpResult:
    """SP-10: Expected skill bibles absent from .hive/skills/."""
    evidence = []
    for skill in EXPECTED_SKILLS:
        skill_path = SKILLS_DIR / f"{skill}.md"
        if not skill_path.exists():
            evidence.append(f".hive/skills/{skill}.md missing")

    if not (SKILLS_DIR / "brain_directory.md").exists():
        evidence.append(".hive/skills/brain_directory.md missing")

    status = "CLEAR" if not evidence else ("CRITICAL" if len(evidence) >= 4 else "WARN")
    return SpResult("SP-10: Missing skill bibles", status, evidence)


# ── SCORPION Pass ─────────────────────────────────────────────────────────────

def run_scorpion() -> GideonReport:
    t0 = time.perf_counter()
    scanners = [
        _sp01_a2a_no_rbac,
        _sp02_iron_gate_bypass,
        _sp03_kinetic_purity,
        _sp04_voxservice_race,
        _sp05_sql_injection,
        _sp06_missing_briefing_script,
        _sp07_swarm_without_harness,
        _sp08_missing_zod,
        _sp09_sync_db_in_async,
        _sp10_missing_skill_bible,
    ]
    results: list[SpResult] = []
    for fn in scanners:
        try:
            results.append(fn())
        except Exception as exc:
            results.append(SpResult(fn.__name__, "WARN", [f"scanner error: {exc}"]))

    score = sum(r.weight for r in results)
    passed = score <= 2
    criticals = [r.shatterpoint for r in results if r.status == "CRITICAL"]
    warns     = [r.shatterpoint for r in results if r.status == "WARN"]
    duration  = (time.perf_counter() - t0) * 1000

    if passed:
        summary = f"PASS — GIDEON_RISK_SCORE={score}/20 (threshold <=2). No blockers."
    else:
        summary = (
            f"FAIL — GIDEON_RISK_SCORE={score}/20. "
            f"CRITICAL={len(criticals)} WARN={len(warns)}. Iron Gate HITL required."
        )

    return GideonReport(
        shatterpoints=results,
        gideon_risk_score=score,
        passed=passed,
        duration_ms=round(duration, 1),
        summary=summary,
    )


# ── Knight class ──────────────────────────────────────────────────────────────

class SirGideon(BaseKnight):
    """Forensic auditor — runs //SCORPION Shatterpoint pass."""

    name = "sir_gideon"
    tier = "HIGH_KNIGHT"

    def execute(
        self,
        directive: str,
        intent: Optional[str] = None,
        write: bool = False,
    ) -> dict:
        report = run_scorpion()
        sp_summary = [
            {"sp": r.shatterpoint, "status": r.status, "findings": len(r.evidence)}
            for r in report.shatterpoints
        ]
        return {
            "gideon_risk_score": report.gideon_risk_score,
            "passed": report.passed,
            "duration_ms": report.duration_ms,
            "summary": report.summary,
            "shatterpoints": sp_summary,
            "evidence": {
                r.shatterpoint: r.evidence
                for r in report.shatterpoints
                if r.evidence
            },
        }


if __name__ == "__main__":
    import json
    g = SirGideon()
    print(json.dumps(g.execute("//SCORPION"), indent=2))
