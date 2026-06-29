"""JUDGE squire — synthesizes SCAN/GHOST/SWEEP/INDEX results into a risk verdict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ghost import GhostReport
    from .index import ColonyIndex
    from .sweep import SweepReport


@dataclass
class Verdict:
    risk_score: float           # 0.0 – 100.0
    risk_label: str             # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    requires_hitl: bool = False  # True → SENTINEL gate fires

    def to_dict(self) -> dict:
        return {
            "risk_score": self.risk_score,
            "risk_label": self.risk_label,
            "requires_hitl": self.requires_hitl,
            "findings": self.findings,
            "recommendations": self.recommendations,
        }


def _label(score: float) -> str:
    if score >= 75:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "MEDIUM"
    return "LOW"


def judge(
    ghost: "GhostReport",
    sweep: "SweepReport",
    index: "ColonyIndex",
) -> Verdict:
    score = 0.0
    findings: list[str] = []
    recs: list[str] = []

    # GHOST critical = secrets → heavy weight
    n_secrets = sum(1 for f in ghost.flags if f.kind == "secret")
    if n_secrets:
        score += n_secrets * 20.0
        findings.append(f"{n_secrets} potential secret(s) detected — CRITICAL")
        recs.append("Remove secrets from source, rotate credentials, use `camelot keys set`")

    # Large files
    n_large = sum(1 for f in ghost.flags if f.kind == "large_file")
    if n_large:
        score += n_large * 3.0
        findings.append(f"{n_large} large file(s) (>500 KB) found")
        recs.append("Consider moving large files to .gitignore or media storage")

    # TODOs
    n_todos = sum(1 for f in ghost.flags if f.kind == "todo")
    if n_todos > 20:
        score += 5.0
        findings.append(f"{n_todos} TODO/FIXME markers — technical debt accumulation")
        recs.append("Triage TODOs: assign to squires or create PROVENANCE_LEDGER entries")
    elif n_todos:
        findings.append(f"{n_todos} TODO/FIXME markers")

    # Sweep: duplicates
    n_dupes = sum(1 for f in sweep.flags if f.kind == "duplicate_content")
    if n_dupes:
        score += n_dupes * 2.0
        findings.append(f"{n_dupes} duplicate file(s) detected")
        recs.append("Run MASON to generate dedup report")

    # Sweep: unused imports
    n_unused = sum(1 for f in sweep.flags if f.kind == "unused_import")
    if n_unused > 5:
        score += 4.0
        findings.append(f"{n_unused} unused imports (dead code)")
        recs.append("Run `ruff check --select F401` or equivalent linter")

    # Index: codebase health signals
    total_files = index.stats.get("total_files", 0)
    total_lines = index.stats.get("total_lines", 0)
    if total_lines > 100_000:
        score += 5.0
        findings.append(f"Large codebase: {total_lines:,} lines — context management critical")
        recs.append("Enable //ELEPHAS mode for memory-first execution")

    if not findings:
        findings.append("No significant issues detected")

    label = _label(score)
    hitl = score >= 50 or n_secrets > 0

    return Verdict(
        risk_score=min(score, 100.0),
        risk_label=label,
        findings=findings,
        recommendations=recs,
        requires_hitl=hitl,
    )
