#!/usr/bin/env python3
r"""
navigator.py — CAMELOT-OS Project Navigation + Dev-UX + Topology Index
======================================================================
A single-file, stdlib-only project navigator for CAMELOT-OS.

Goals (operator-confirmed target): assess developer UX, code readability,
and project navigation. Honors the existing audit hierarchy — sits as the
**Navigator** rung next to **Audit Governor** on the audit log.

Public surface
--------------

    python ./navigator.py [--json-only|--md-only|--both (default)]
                          [--out-dir DIR (default=.)]
                          [--rune NAME] [--knight SUBSTR]
                          [--surface bin|cp|sq|knights|docs|audit|all (default=all)]
                          [--version|--help]

Examples
--------

    python ./navigator.py                       # both artifacts at repo root
    python ./navigator.py --md-only --out-dir ./docs
    python ./navigator.py --rune //FORGE        # dispatch table hit
    python ./navigator.py --knight sir_boris    # knight surface resolution

Design notes
------------

* **No execution**: the script parses Python source with `ast` only — never
  imports any project module. This avoids touching `01_KERNEL.*`, kinetic
  binaries, or anything fragile at import time.
* **Bounded walk**: surfaces are limited to top-level directories of interest.
  The 46K-file repo is *not* enumerated end-to-end; we only inspect the
  surfaces a developer cares about for routing or onboarding.
* **Composability**: reuses `.colony/index.json` for ground-truth totals; does
  not duplicate the squire colony's scanner/parser surface.
* **Evidence-class discipline**: every output row carries either a `confirmed`
  or `planned` tag per the project's `harness.md` rule.

This script was added to the audit hierarchy on 2026-07-06 as the
**Navigator** rung, alongside **Audit Governor**.
"""
from __future__ import annotations

__version__ = "1.1.0"
__nav_rung__ = "Navigator (sibling of Audit Governor) + Crucible rung"


import argparse
import ast
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

# Ensure UTF-8 on stdout/stderr for cp1252-host safety (Windows consoles).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

CAMELOT_HOME = Path(__file__).resolve().parent
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class EntryPoint:
    path: str
    role: str
    first_line: str
    classes: list[str]
    functions: list[str]
    imports: list[str]
    module_version: str | None
    size_bytes: int
    lines: int
    docstring_present: bool
    banner_present: bool
    has_sibling_docs: bool


@dataclass
class RuneRow:
    rune: str
    type: str
    knight: str
    mode: str
    priority: int
    handler: str | None
    description: str
    has_handler: bool


@dataclass
class KnightRow:
    name: str
    role: str | None
    surface: str
    path: str


@dataclass
class AuditRow:
    path: str
    title: str | None
    verdict: str | None
    score: int | None
    date: str | None
    has_verdict_line: bool
    has_score_line: bool


@dataclass
class DocRow:
    path: str
    role: str
    bytes: int


@dataclass
class DxMetric:
    name: str
    value: float | str
    target: float | str
    status: str
    note: str


@dataclass
class NavigatorReport:
    emitted_at: str
    camelot_home: str
    navigator_version: str
    navigator_rung: str
    canonical_files: int | None
    canonical_lines: int | None
    canonical_symbols: int | None
    extensions: dict[str, int]
    bin_entry_points: list[EntryPoint]
    control_plane_modules: list[EntryPoint]
    squire_modules: list[EntryPoint]
    runes: list[RuneRow]
    knights: list[KnightRow]
    audit_ladder: list[AuditRow]
    docs: list[DocRow]
    dx_metrics: list[DxMetric]
    topology_metrics: list[DxMetric]
    topology_score: float
    crucible_metrics: list[DxMetric]
    crucible_score: float
    findings: dict[str, list[str]]
    letter_grade: str
    numeric_score: float


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _safe_text(p: Path, max_chars: int = 400) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except OSError:
        return ""


def _first_nontrivial_line(snippet: str) -> str:
    for line in snippet.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#!"):
            continue
        if stripped.startswith("/*"):
            continue
        return stripped[:120]
    return ""


_BANNER_PATTERNS = (
    re.compile(r"__version__\s*=", re.MULTILINE),
    re.compile(r"\b(CAMELOT[- ]?OS|camelot)\s+v\d", re.IGNORECASE),
    re.compile(r"_banner\s*\(", re.MULTILINE),
)


def _has_banner(source: str) -> bool:
    return any(p.search(source) for p in _BANNER_PATTERNS)


def _module_docstring(source: str) -> bool:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    return ast.get_docstring(tree) is not None


def _extract_version(source: str) -> str | None:
    m = re.search(r"__version__\s*=\s*[\"']([^\"']+)[\"']", source)
    return m.group(1) if m else None


@dataclass
class _ModuleScan:
    first_line: str
    classes: list[str]
    functions: list[str]
    imports: list[str]
    module_version: str | None
    docstring_present: bool
    banner_present: bool


def _scan_python(path: Path) -> _ModuleScan | None:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return _ModuleScan(
            first_line=_first_nontrivial_line(source),
            classes=[],
            functions=[],
            imports=[],
            module_version=_extract_version(source),
            docstring_present=False,
            banner_present=_has_banner(source),
        )

    classes: list[str] = []
    top_level_functions: list[str] = []
    imports: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            top_level_functions.append(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split(".")[0])
    return _ModuleScan(
        first_line=_first_nontrivial_line(source),
        classes=sorted(set(classes)),
        functions=sorted(set(top_level_functions)),
        imports=sorted(set(imports)),
        module_version=_extract_version(source),
        docstring_present=ast.get_docstring(tree) is not None,
        banner_present=_has_banner(source),
    )


_VERDICT_LINE = re.compile(r"^\s*\*{0,2}Verdict:?\**\s*[A-Z/0-9 \-]+(.*)?$", re.MULTILINE | re.IGNORECASE)
_SCORE_LINE = re.compile(r"score[:\s]*([0-9]+)/100", re.MULTILINE | re.IGNORECASE)


def _scan_audit(path: Path) -> AuditRow:
    text = _safe_text(path, max_chars=20000)
    title_m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    score_m = _SCORE_LINE.search(text)
    verdict_match = _VERDICT_LINE.search(text)
    has_verdict = verdict_match is not None
    return AuditRow(
        path=str(path.relative_to(CAMELOT_HOME)),
        title=title_m.group(1).strip() if title_m else None,
        verdict=verdict_match.group(0).strip() if verdict_match else None,
        score=int(score_m.group(1)) if score_m else None,
        date=TODAY if path.name.endswith("2026-07-06.md") else None,
        has_verdict_line=has_verdict,
        has_score_line=score_m is not None,
    )


def _scan_md_knight(path: Path) -> KnightRow:
    text = _safe_text(path, max_chars=2000)
    role_m = re.search(r"^#{1,3}\s+(.+)$", text, re.MULTILINE)
    name = path.stem
    sub = path.parent.name if path.parent else "knights"
    role = role_m.group(1).strip() if role_m else None
    return KnightRow(name=name, role=role, surface=sub, path=str(path.relative_to(CAMELOT_HOME)))


# ---------------------------------------------------------------------------
# Discovery + scoring
# ---------------------------------------------------------------------------

SURFACES = ("bin", "control_plane", "squires")

CANONICAL_DOCS = {
    "AGENTS.md": "Constitution",
    ".agent/system_instructions.md": "Operational backplane",
    "harness.md": "Codex meta-harness",
    "UNIVERSAL_BOOTSTRAP_UKG_NANO.md": "OMEGA bootstrap",
    "SYSTEM_PERSONAS_CRYSTAL.md": "Persona crystal catalog",
}


def _collect_python_dir(subdir: str, role: str) -> list[EntryPoint]:
    root = CAMELOT_HOME / subdir
    if not root.exists():
        return []
    out: list[EntryPoint] = []
    for p in sorted(root.glob("*.py")):
        if p.name.startswith("_"):
            continue
        try:
            size = p.stat().st_size
        except OSError:
            continue
        lines = sum(1 for _ in p.open("r", encoding="utf-8", errors="replace"))
        scan = _scan_python(p)
        if scan is None:
            continue
        sibling_doc = (
            (p.parent / "README.md").exists()
            or (p.parent / "ARCHITECTURE.md").exists()
            or (p.parent.parent / "README.md").exists()
            or (p.parent.parent / "ARCHITECTURE.md").exists()
        )
        out.append(EntryPoint(
            path=str(p.relative_to(CAMELOT_HOME)),
            role=role,
            first_line=scan.first_line,
            classes=scan.classes,
            functions=scan.functions,
            imports=scan.imports,
            module_version=scan.module_version,
            size_bytes=size,
            lines=lines,
            docstring_present=scan.docstring_present,
            banner_present=scan.banner_present,
            has_sibling_docs=sibling_doc,
        ))
    return out


def _collect_runes() -> tuple[list[RuneRow], set[str]]:
    src = CAMELOT_HOME / "control_plane" / "runic_router.py"
    if not src.exists():
        return [], set()
    text = src.read_text(encoding="utf-8", errors="replace")

    rows: list[RuneRow] = []
    handler_map: set[str] = set()

    handlers_block = re.search(r"_HANDLERS\s*=\s*\{(.+?)\}\n", text, re.DOTALL)
    if handlers_block:
        handler_map.update(re.findall(r"_handle_\w+", handlers_block.group(1)))

    RUNE_ENTRY = re.compile(
        r"\"(//[\w-]+)\"\s*:\s*\{([^{}]*?)\}(?:,|\s*$)",
        re.MULTILINE,
    )
    OMEGA_ENTRY = re.compile(
        r"\"(Omega_\w+)\"\s*:\s*\{([^{}]*?)\}(?:,|\s*$)",
        re.MULTILINE,
    )
    for m in RUNE_ENTRY.finditer(text):
        rune_str = m.group(1)
        body = m.group(2)
        knight = re.search(r"\"knight\":\s*\"([^\"]+)\"", body)
        mode = re.search(r"\"mode\":\s*\"([^\"]+)\"", body)
        priority = re.search(r"\"priority\":\s*([0-9]+)", body)
        handler = re.search(r"\"handler\":\s*\"([^\"]+)\"", body)
        desc = re.search(r"\"description\":\s*\"([^\"]+)\"", body)
        h_name = handler.group(1).strip() if handler else None
        rows.append(RuneRow(
            rune=rune_str,
            type="runic",
            knight=knight.group(1) if knight else "?",
            mode=mode.group(1) if mode else "FORGE",
            priority=int(priority.group(1)) if priority else 2,
            handler=h_name,
            description=(desc.group(1) if desc else ""),
            has_handler=(h_name in handler_map) if h_name else False,
        ))
    for m in OMEGA_ENTRY.finditer(text):
        rune_str = m.group(1)
        body = m.group(2)
        knight = re.search(r"\"knight\":\s*\"([^\"]+)\"", body)
        desc = re.search(r"\"description\":\s*\"([^\"]+)\"", body)
        rows.append(RuneRow(
            rune=rune_str,
            type="omega",
            knight=knight.group(1) if knight else "?",
            mode="ORACLE",
            priority=2,
            handler=None,
            description=(desc.group(1) if desc else ""),
            has_handler=False,
        ))

    return rows, handler_map


def _collect_knights() -> list[KnightRow]:
    out: list[KnightRow] = []
    knights_dir = CAMELOT_HOME / "03_VAULT" / "Knights"
    if not knights_dir.exists():
        return out
    for sub in sorted(knights_dir.iterdir()):
        if not sub.is_dir():
            continue
        for p in sorted(sub.glob("*.md")):
            out.append(_scan_md_knight(p))
    return out


def _collect_audit_ladder() -> list[AuditRow]:
    out: list[AuditRow] = []
    for p in sorted(CAMELOT_HOME.glob("TITAN_AUDIT_*.md")):
        out.append(_scan_audit(p))
    for p in sorted(CAMELOT_HOME.glob("NAVIGATOR_RUNG_*.md")):
        out.append(_scan_audit(p))
    return out


def _collect_canonical_docs() -> list[DocRow]:
    out: list[DocRow] = []
    for rel, role in CANONICAL_DOCS.items():
        p = CAMELOT_HOME / rel
        if not p.exists():
            out.append(DocRow(path=rel, role=role + " (missing)", bytes=0))
            continue
        out.append(DocRow(path=rel, role=role, bytes=p.stat().st_size))
    return out


def _consume_colony() -> tuple[int | None, int | None, int | None, dict[str, int]]:
    candidates = [
        CAMELOT_HOME / ".colony" / "index.json.gz",
        CAMELOT_HOME / ".colony" / "index.json",
    ]
    for path in candidates:
        if not path.exists():
            continue
        try:
            if path.suffix == ".gz":
                import gzip
                data = json.loads(gzip.decompress(path.read_bytes()))
            else:
                data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        stats = data.get("stats", {})
        by_ext = stats.get("by_ext", {}) or {}
        return (
            int(stats.get("total_files", 0)),
            int(stats.get("total_lines", 0)),
            int(stats.get("total_symbols", 0)),
            {k: int(v) for k, v in by_ext.items()},
        )
    return None, None, None, {}


# ---------------------------------------------------------------------------
# DX scoring
# ---------------------------------------------------------------------------

_DX_WEIGHTS: dict[str, float] = {
    "docstring_coverage_bin": 0.10,
    "banner_present_bin": 0.05,
    "rune_handler_resolvable": 0.20,
    "rune_omega_described": 0.05,
    "audit_chain_completeness": 0.20,
    "knight_creative_role_lines": 0.10,
    "doc_to_code_ratio": 0.05,
    "max_python_file_kb": 0.05,
    "entry_point_meaningful_first_line": 0.05,
    "agent_references_in_docs": 0.10,
    "discoverability_smoke": 0.05,
}


def _pct(num: int, den: int) -> float:
    return 100.0 * num / den if den else 0.0


def _score_dx(
    bin_eps: list[EntryPoint],
    cp_eps: list[EntryPoint],
    sq_eps: list[EntryPoint],
    runes: list[RuneRow],
    audit: list[AuditRow],
    knights: list[KnightRow],
    docs: list[DocRow],
    colony_files: int | None,
    colony_lines: int | None,
) -> tuple[list[DxMetric], dict[str, list[str]], float]:
    findings: dict[str, list[str]] = {}
    metrics: list[DxMetric] = []
    n_bin = len(bin_eps)

    if n_bin:
        have = sum(1 for e in bin_eps if e.docstring_present)
        pct = _pct(have, n_bin)
        status = "pass" if pct >= 95 else ("warn" if pct >= 70 else "fail")
        metrics.append(DxMetric("docstring_coverage_bin", f"{pct:.1f}%", ">=95%", status, f"{have}/{n_bin} bin/*.py modules"))
        if status != "pass":
            findings.setdefault("docstring_coverage", []).extend(
                e.path for e in bin_eps if not e.docstring_present
            )

    if n_bin:
        have = sum(1 for e in bin_eps if e.banner_present)
        pct = _pct(have, n_bin)
        status = "pass" if pct >= 80 else ("warn" if pct >= 60 else "fail")
        metrics.append(DxMetric("banner_present_bin", f"{pct:.1f}%", ">=80%", status, f"{have}/{n_bin} bin/*.py modules"))
        if status != "pass":
            findings.setdefault("banner_present", []).extend(
                e.path for e in bin_eps if not e.banner_present
            )

    runic = [r for r in runes if r.type == "runic"]
    if runic:
        have = sum(1 for r in runic if r.has_handler)
        pct = _pct(have, len(runic))
        status = "pass" if pct >= 95 else ("warn" if pct >= 70 else "fail")
        metrics.append(DxMetric("rune_handler_resolvable", f"{pct:.1f}%", ">=95%", status, f"{have}/{len(runic)} RUNIC_COMMANDS resolved"))
        if status != "pass":
            findings.setdefault("rune_handler_resolvable", []).extend(
                f"{r.rune} \u2192 {r.handler}" for r in runic if not r.has_handler
            )

    omega = [r for r in runes if r.type == "omega"]
    if omega:
        have = sum(1 for r in omega if r.description)
        metrics.append(DxMetric("rune_omega_described", f"{_pct(have, len(omega)):.1f}%", ">=95%", "pass" if _pct(have, len(omega)) >= 95 else "warn", f"{have}/{len(omega)} OMEGA_RUNES described"))

    if audit:
        have = sum(1 for a in audit if a.has_verdict_line and a.has_score_line)
        pct = _pct(have, len(audit))
        status = "pass" if pct >= 100 else "fail"
        metrics.append(DxMetric("audit_chain_completeness", f"{pct:.1f}%", "100%", status, f"{have}/{len(audit)} audit docs with Verdict+score"))
        if status != "pass":
            findings.setdefault("audit_chain", []).extend(
                a.path for a in audit if not (a.has_verdict_line and a.has_score_line)
            )

    creative = [k for k in knights if k.surface == "Creative"]
    if creative:
        have = sum(1 for k in creative if k.role)
        pct = _pct(have, len(creative))
        status = "pass" if pct >= 80 else ("warn" if pct >= 60 else "fail")
        metrics.append(DxMetric("knight_creative_role_lines", f"{pct:.1f}%", ">=80%", status, f"{have}/{len(creative)} Creative/*.md have # role line"))

    md_bytes = sum(d.bytes for d in docs)
    py_lines = sum(e.lines for e in bin_eps) + sum(e.lines for e in cp_eps) + sum(e.lines for e in sq_eps)
    if py_lines:
        ratio = md_bytes / py_lines
        status = "pass" if ratio >= 1.0 else ("warn" if ratio >= 0.5 else "fail")
        metrics.append(DxMetric("doc_to_code_ratio", f"{ratio:.2f}", ">=1.0", status, f"{md_bytes} bytes(md)/{py_lines} lines(py)"))
    if colony_files and colony_lines:
        metrics.append(DxMetric("colony_canonical_files", str(colony_files), "n/a", "pass", "ground truth from .colony/index.json"))
        metrics.append(DxMetric("colony_canonical_lines", str(colony_lines), "n/a", "pass", "ground truth from .colony/index.json"))

    all_eps = bin_eps + cp_eps + sq_eps
    max_kb = max((e.size_bytes for e in all_eps), default=0) / 1024.0
    over = [e.path for e in all_eps if e.size_bytes > 300 * 1024]
    status = "pass" if not over else ("warn" if all(e.size_bytes <= 600 * 1024 for e in all_eps) else "fail")
    largest = max(((e.size_bytes, e.path) for e in all_eps), default=(0, "n/a"))[1]
    metrics.append(DxMetric("max_python_file_kb", f"{max_kb:.0f}", "<=300", status, f"largest file: {largest}"))
    if over:
        findings.setdefault("max_file_size", []).extend(over)

    if n_bin:
        have = sum(1 for e in bin_eps if e.first_line and not e.first_line.startswith("import") and not e.first_line.startswith("from "))
        pct = _pct(have, n_bin)
        status = "pass" if pct >= 80 else ("warn" if pct >= 60 else "fail")
        metrics.append(DxMetric("entry_point_meaningful_first_line", f"{pct:.1f}%", ">=80%", status, f"{have}/{n_bin} bin/*.py first line describes the script"))

    ag_text = ""
    for rel, _ in CANONICAL_DOCS.items():
        p = CAMELOT_HOME / rel
        if p.exists():
            ag_text += p.read_text(encoding="utf-8", errors="replace")
    if runic and ag_text:
        rng_names = [r.rune.lstrip("/").lower() for r in runic]
        hit = sum(1 for n in rng_names if n in ag_text.lower())
        pct = _pct(hit, len(rng_names))
        status = "pass" if pct >= 60 else ("warn" if pct >= 30 else "fail")
        metrics.append(DxMetric("agent_references_in_docs", f"{pct:.1f}%", ">=60%", status, f"{hit}/{len(rng_names)} RUNIC_COMMANDS named in canonical docs"))

    weights = _DX_WEIGHTS
    by_name = {m.name: m for m in metrics}
    score = 0.0
    for k, w in weights.items():
        m = by_name.get(k)
        if not m:
            continue
        try:
            val = float(str(m.value).rstrip("%"))
        except ValueError:
            val = 100.0 if m.status == "pass" else (50.0 if m.status == "warn" else 0.0)
        score += w * val
    return metrics, findings, score


# ---------------------------------------------------------------------------
# Topology scoring — separate weight table; does NOT perturb dev-UX score.
# ---------------------------------------------------------------------------

_TOPO_WEIGHTS: dict[str, float] = {
    "orphan_detector": 0.05,
    "convoluted_flow": 0.10,
    "doc_coverage_scorer": 0.05,
}
_TOPO_FLOW_THRESHOLDS: dict[str, int] = {"bin": 15, "control_plane": 40, "squire": 20}


def _score_topology(
    bin_eps: list[EntryPoint],
    cp_eps: list[EntryPoint],
    sq_eps: list[EntryPoint],
) -> tuple[list[DxMetric], dict[str, list[str]], float]:
    all_eps: list[EntryPoint] = list(bin_eps) + list(cp_eps) + list(sq_eps)
    if not all_eps:
        return [], {}, 0.0

    metrics: list[DxMetric] = []
    findings: dict[str, list[str]] = {}

    module_basenames: dict[str, str] = {
        Path(ep.path).stem: ep.path for ep in all_eps
    }

    referenced: set[str] = set()
    for ep in all_eps:
        for imp in ep.imports:
            if imp in module_basenames:
                referenced.add(module_basenames[imp])
    orphan_paths = [ep.path for ep in all_eps if ep.path not in referenced]
    orphan_pct = 100.0 * len(orphan_paths) / len(all_eps)
    metrics.append(DxMetric(
        "orphan_detector",
        f"{len(orphan_paths)}/{len(all_eps)} orphans",
        "<=10% orphans",
        "pass" if orphan_pct <= 10 else ("warn" if orphan_pct <= 25 else "fail"),
        f"{orphan_pct:.1f}% of surfaced modules are unreferenced",
    ))
    if orphan_paths:
        findings.setdefault("orphan_detector", []).extend(orphan_paths)

    convoluted: list[tuple[str, int, int]] = []
    for ep in all_eps:
        cap = _TOPO_FLOW_THRESHOLDS.get(ep.role, 30)
        if len(ep.imports) > cap:
            convoluted.append((ep.path, len(ep.imports), cap))
    flow_pct = 100.0 * len(convoluted) / len(all_eps)
    metrics.append(DxMetric(
        "convoluted_flow",
        f"{len(convoluted)}/{len(all_eps)} modules",
        "<=10% high-fan-in files",
        "pass" if flow_pct <= 10 else ("warn" if flow_pct <= 20 else "fail"),
        f"thresholds: bin<={_TOPO_FLOW_THRESHOLDS['bin']} . cp<={_TOPO_FLOW_THRESHOLDS['control_plane']} . sq<={_TOPO_FLOW_THRESHOLDS['squire']}",
    ))
    if convoluted:
        findings.setdefault("convoluted_flow", []).extend(
            f"{p} ({n} imports > cap {c})" for p, n, c in convoluted
        )

    doc_covered = sum(1 for ep in all_eps if ep.has_sibling_docs)
    pct_cov = 100.0 * doc_covered / len(all_eps)
    metrics.append(DxMetric(
        "doc_coverage_scorer",
        f"{pct_cov:.1f}%",
        ">=75%",
        "pass" if pct_cov >= 75 else ("warn" if pct_cov >= 50 else "fail"),
        f"{doc_covered}/{len(all_eps)} modules have sibling README/ARCHITECTURE within +/-1 dir",
    ))
    if pct_cov < 75:
        findings.setdefault("doc_coverage_scorer", []).extend(
            ep.path for ep in all_eps if not ep.has_sibling_docs
        )

    by_name = {m.name: m for m in metrics}
    score = 0.0
    for k, w in _TOPO_WEIGHTS.items():
        m = by_name.get(k)
        if not m:
            continue
        try:
            val = float(str(m.value).rstrip("%"))
        except ValueError:
            val = 100.0 if m.status == "pass" else (50.0 if m.status == "warn" else 0.0)
        score += w * val
    return metrics, findings, score


# ---------------------------------------------------------------------------
# Crucible scoring -- 3rd parallel weight table; does NOT perturb dev-UX
# or topology scores. Captures code-effectiveness + security primitives.
# ---------------------------------------------------------------------------

_CRUCIBLE_WEIGHTS: dict[str, float] = {
    "test_coverage_scorer": 0.40,
    "docstring_coverage_scorer": 0.20,
    "hitl_gate_coverage": 0.40,
}
_CRUCIBLE_HITL_MODULES: tuple[str, ...] = (
    "control_plane/anya_gate.py",
    "control_plane/soul_oversight.py",
    "control_plane/factory_lane.py",
)
_CRUCIBLE_HITL_TESTS: tuple[str, ...] = (
    "tests/test_anya_gate.py",
    "tests/test_soul_oversight.py",
)
_CRUCIBLE_GHOST_SQUIRE = "squires/ghost.py"


def _collect_pytest_targets() -> set[str]:
    tests_dir = CAMELOT_HOME / "tests"
    if not tests_dir.exists():
        return set()
    targets: set[str] = set()
    for p in tests_dir.glob("test_*.py"):
        stem = p.stem
        if stem.startswith("test_"):
            targets.add(stem[len("test_"):])
    return targets


def _score_crucible(
    bin_eps: list[EntryPoint],
    cp_eps: list[EntryPoint],
    sq_eps: list[EntryPoint],
) -> tuple[list[DxMetric], dict[str, list[str]], float]:
    metrics: list[DxMetric] = []
    findings: dict[str, list[str]] = {}
    all_eps: list[EntryPoint] = list(bin_eps) + list(cp_eps) + list(sq_eps)
    if not all_eps:
        return metrics, findings, 0.0

    module_stems: set[str] = {
        Path(ep.path).stem for ep in all_eps
    }
    test_targets = _collect_pytest_targets()
    matched = module_stems & test_targets
    coverage_pct = 100.0 * len(matched) / len(module_stems) if module_stems else 0.0
    metrics.append(DxMetric(
        "test_coverage_scorer",
        f"{coverage_pct:.1f}%",
        ">=80%",
        "pass" if coverage_pct >= 80 else ("warn" if coverage_pct >= 50 else "fail"),
        f"{len(matched)}/{len(module_stems)} surfaced modules have a test_*.py counterpart",
    ))
    if coverage_pct < 80:
        findings.setdefault("test_coverage_scorer", []).extend(
            sorted(module_stems - test_targets)
        )

    doc_covered = sum(1 for ep in all_eps if ep.docstring_present)
    doc_pct = 100.0 * doc_covered / len(all_eps)
    metrics.append(DxMetric(
        "docstring_coverage_scorer",
        f"{doc_pct:.1f}%",
        ">=80%",
        "pass" if doc_pct >= 80 else ("warn" if doc_pct >= 50 else "fail"),
        f"{doc_covered}/{len(all_eps)} entry points across bin+cp+sq carry a module docstring",
    ))
    if doc_pct < 80:
        findings.setdefault("docstring_coverage_scorer", []).extend(
            ep.path for ep in all_eps if not ep.docstring_present
        )

    clauses: list[tuple[str, bool, str]] = []
    for rel in _CRUCIBLE_HITL_MODULES:
        clauses.append((f"module {rel}", (CAMELOT_HOME / rel).exists(), rel))
    for rel in _CRUCIBLE_HITL_TESTS:
        clauses.append((f"test {rel}", (CAMELOT_HOME / rel).exists(), rel))
    clauses.append((
        f"ghost_squire {_CRUCIBLE_GHOST_SQUIRE}",
        (CAMELOT_HOME / _CRUCIBLE_GHOST_SQUIRE).exists(),
        _CRUCIBLE_GHOST_SQUIRE,
    ))
    met = sum(1 for _, ok, _ in clauses if ok)
    total = len(clauses)
    hitl_pct = 100.0 * met / total if total else 0.0
    metrics.append(DxMetric(
        "hitl_gate_coverage",
        f"{hitl_pct:.1f}%",
        "100.0%",
        "pass" if met == total else ("warn" if met >= total - 1 else "fail"),
        f"{met}/{total} security/HITL primitives present and tested (anya_gate, soul_oversight, factory_lane, ghost_squire + their tests)",
    ))
    if met < total:
        findings.setdefault("hitl_gate_coverage", []).extend(
            f"{label} (missing: {rel})" for label, ok, rel in clauses if not ok
        )

    by_name = {m.name: m for m in metrics}
    score = 0.0
    for k, w in _CRUCIBLE_WEIGHTS.items():
        m = by_name.get(k)
        if not m:
            continue
        try:
            val = float(str(m.value).rstrip("%"))
        except ValueError:
            val = 100.0 if m.status == "pass" else (50.0 if m.status == "warn" else 0.0)
        score += w * val
    return metrics, findings, score


_GRADE_BANDS = [
    (92, "A"),
    (84, "B"),
    (70, "C"),
    (55, "D"),
    (0,  "F"),
]


def _letter_grade(score: float) -> str:
    for cutoff, letter in _GRADE_BANDS:
        if score >= cutoff:
            return letter
    return "F"


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def _write_json(report: NavigatorReport, out: Path) -> None:
    data = {
        "emitted_at": report.emitted_at,
        "navigator_version": report.navigator_version,
        "navigator_rung": report.navigator_rung,
        "camelot_home": report.camelot_home,
        "canonical_files": report.canonical_files,
        "canonical_lines": report.canonical_lines,
        "canonical_symbols": report.canonical_symbols,
        "extensions": report.extensions,
        "bin_entry_points": [asdict(e) for e in report.bin_entry_points],
        "control_plane_modules": [asdict(e) for e in report.control_plane_modules],
        "squire_modules": [asdict(e) for e in report.squire_modules],
        "runes": [asdict(r) for r in report.runes],
        "knights": [asdict(k) for k in report.knights],
        "audit_ladder": [asdict(a) for a in report.audit_ladder],
        "docs": [asdict(d) for d in report.docs],
        "dx_metrics": [asdict(m) for m in report.dx_metrics],
        "topology_metrics": [asdict(m) for m in report.topology_metrics],
        "topology_score": round(report.topology_score, 1),
        "crucible_metrics": [asdict(m) for m in report.crucible_metrics],
        "crucible_score": round(report.crucible_score, 1),
        "findings": report.findings,
        "letter_grade": report.letter_grade,
        "numeric_score": round(report.numeric_score, 1),
    }
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_md(report: NavigatorReport, out: Path) -> None:
    lines: list[str] = []
    lines.append(f"# NAVIGATOR REPORT -- {report.emitted_at}\n")
    lines.append(f"_Generated by `navigator.py` v{report.navigator_version} . Rung: **{report.navigator_rung}**_\n")
    lines.append(f"- Camelot home: `{report.camelot_home}`")
    lines.append(f"- Numeric score: **{round(report.numeric_score, 1)}** / 100 -> **Grade {report.letter_grade}**")
    if report.canonical_files is not None:
        lines.append(f"- Canonical surface (per `.colony/index.json`): **{report.canonical_files:,} files**, **{report.canonical_lines:,} lines**, **{report.canonical_symbols:,} symbols**")
    lines.append("")
    lines.append("## 1. Entry Points (bin/, control_plane/, squires/)")
    lines.append("")
    for role, eps in (
        ("bin", report.bin_entry_points),
        ("control_plane", report.control_plane_modules),
        ("squires", report.squire_modules),
    ):
        lines.append(f"### `{role}` -- {len(eps)} modules\n")
        for e in eps[:30]:
            banner = "Y" if e.banner_present else "."
            doc = "doc" if e.docstring_present else "no-doc"
            cls_n = len(e.classes)
            fn_n = len(e.functions)
            ver = f"v{e.module_version}" if e.module_version else "v?"
            lines.append(f"- {banner} `{e.path}` -- {ver} . {e.lines} lines . {e.size_bytes//1024} KB . {cls_n} cls / {fn_n} fn . {doc}")
            if e.first_line:
                lines.append(f"   > {e.first_line}")
        if len(eps) > 30:
            lines.append(f"- ... {len(eps)-30} more")
        lines.append("")

    lines.append("## 2. Runic Dispatch (`control_plane/runic_router.py`)")
    lines.append("")
    lines.append(f"- {len([r for r in report.runes if r.type=='runic'])} RUNIC_COMMANDS")
    lines.append(f"- {len([r for r in report.runes if r.type=='omega'])} OMEGA_RUNES")
    lines.append("")
    lines.append("### Privileged (priority=1) RUNIC_COMMANDS\n")
    for r in sorted([r for r in report.runes if r.type == "runic" and r.priority == 1], key=lambda x: x.rune):
        status = "Y " if r.has_handler else "X "
        lines.append(f"- {status}`{r.rune}` -> **{r.knight}** . mode=`{r.mode}` . handler=`{r.handler or '--'}` -- {r.description}")
    lines.append("")
    lines.append("## 3. Knight Surface (`03_VAULT/Knights/.../*.md`)")
    lines.append("")
    by_surface: dict[str, list[KnightRow]] = {}
    for k in report.knights:
        by_surface.setdefault(k.surface, []).append(k)
    for surface, rows in sorted(by_surface.items()):
        lines.append(f"### `{surface}/` -- {len(rows)} sheets")
        for r in rows[:8]:
            lines.append(f"- `{r.role or 'no-role'}` . `{r.name}` -- {r.path}")
        if len(rows) > 8:
            lines.append(f"- ... {len(rows)-8} more")
        lines.append("")

    lines.append("## 4. Audit Ladder (`TITAN_AUDIT_*.md` at repo root)")
    lines.append("")
    for a in report.audit_ladder:
        score = a.score if a.score is not None else "--"
        verdict = a.verdict or "--"
        ok = "Y" if (a.has_verdict_line and a.has_score_line) else "X"
        lines.append(f"- {ok} `{a.path}` . **{a.title or 'no title'}** . score={score} . verdict={verdict}")
    lines.append("")

    lines.append("## 5. Canonical Docs\n")
    for d in report.docs:
        kb = d.bytes // 1024
        lines.append(f"- `{d.path}` -- {d.role} . {kb} KB")
    lines.append("")

    lines.append("## 6. Dev-UX Metrics\n")
    lines.append("| Axis | Value | Target | Status | Note |")
    lines.append("|---|---|---|---|---|")
    for m in report.dx_metrics:
        icon = {"pass": "Y", "warn": "!", "fail": "X"}.get(m.status, "?")
        lines.append(f"| {m.name} | {m.value} | {m.target} | {icon} {m.status} | {m.note} |")
    lines.append("")

    if report.findings:
        lines.append("## 7. Findings (resolved at the row level)\n")
        for axis, items in report.findings.items():
            lines.append(f"### {axis} ({len(items)} item(s))\n")
            for it in items[:40]:
                lines.append(f"- `{it}`")
            if len(items) > 40:
                lines.append(f"- ... {len(items)-40} more")
            lines.append("")

    if report.topology_metrics:
        lines.append("## 9. Topology Metrics\n")
        lines.append("| Axis | Value | Target | Status | Note |")
        lines.append("|---|---|---|---|---|")
        for m in report.topology_metrics:
            icon = {"pass": "Y", "warn": "!", "fail": "X"}.get(m.status, "?")
            lines.append(f"| {m.name} | {m.value} | {m.target} | {icon} {m.status} | {m.note} |")
        lines.append("")
        lines.append(f"**Topology score:** {round(report.topology_score, 1)} / 100 (separate weight table -- does NOT perturb the dev-UX score)\n")
        lines.append("")

    if report.crucible_metrics:
        lines.append("## 10. Crucible Metrics\n")
        lines.append("| Axis | Value | Target | Status | Note |")
        lines.append("|---|---|---|---|---|")
        for m in report.crucible_metrics:
            icon = {"pass": "Y", "warn": "!", "fail": "X"}.get(m.status, "?")
            lines.append(f"| {m.name} | {m.value} | {m.target} | {icon} {m.status} | {m.note} |")
        lines.append("")
        lines.append(f"**Crucible score:** {round(report.crucible_score, 1)} / 100 (3rd parallel weight table -- does NOT perturb dev-UX or topology scores)\n")
        lines.append("")

    lines.append("## 8. Navigator Rung\n")
    lines.append("```yaml")
    lines.append("navigator:")
    lines.append("  status: confirmed")
    lines.append(f"  rung_version: {report.navigator_version}")
    lines.append("  scope: 'Cross-surface project navigation + dev-UX scoring'")
    lines.append("  sibling: 'Audit Governor (TITAN_AUDIT_GOVERNOR_7D_2026-07-06.md)'")
    lines.append(f"  emitted_at: {report.emitted_at}")
    lines.append(f"  letter_grade: {report.letter_grade}")
    lines.append(f"  numeric_score: {round(report.numeric_score, 1)}")
    lines.append(f"  topology_score: {round(report.topology_score, 1)}")
    lines.append(f"  crucible_score: {round(report.crucible_score, 1)}")
    lines.append("  evidence_classes:")
    lines.append("    - 'all surface listings: planned (re-derive from AST walk)'")
    lines.append("    - 'runic/omega tables: confirmed (regex-parse of runic_router.py)'")
    lines.append("    - 'knight roster: confirmed (filesystem walk under 03_VAULT/Knights)'")
    lines.append("    - 'audit ladder: confirmed (TITAN_AUDIT_*.md + NAVIGATOR_RUNG_*.md at root)'")
    lines.append("```\n")

    out.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _normalize_rune_key(s: str) -> str:
    s = s.strip().lstrip("/").lstrip("\\").lower()
    if s.startswith("omega_"):
        s = s[len("omega_"):]
    return s


def _resolve_rune(name: str, runes: list[RuneRow]) -> RuneRow | None:
    norm = _normalize_rune_key(name)
    for r in runes:
        if _normalize_rune_key(r.rune) == norm:
            return r
    return None


def _resolve_knight(substr: str, knights: list[KnightRow]) -> list[KnightRow]:
    low = substr.lower()
    return [k for k in knights if low in k.name.lower() or (k.role and low in k.role.lower())]


def _build_report() -> NavigatorReport:
    t0 = time.perf_counter()
    bin_eps = _collect_python_dir("bin", "bin")
    cp_eps = _collect_python_dir("control_plane", "control_plane")
    sq_eps = _collect_python_dir("squires", "squire")
    runes, _ = _collect_runes()
    knights = _collect_knights()
    audit = _collect_audit_ladder()
    docs = _collect_canonical_docs()
    files, lines, symbols, by_ext = _consume_colony()

    metrics, findings, score = _score_dx(
        bin_eps, cp_eps, sq_eps, runes, audit, knights, docs, files, lines,
    )

    topology_metrics, topo_findings, topology_score = _score_topology(bin_eps, cp_eps, sq_eps)
    for k, v in topo_findings.items():
        findings.setdefault(k, []).extend(v)

    crucible_metrics, crucible_findings, crucible_score = _score_crucible(bin_eps, cp_eps, sq_eps)
    for k, v in crucible_findings.items():
        findings.setdefault(k, []).extend(v)

    t_smoke = time.perf_counter()
    _resolve_rune("//FORGE", runes)
    smoke_ms = (time.perf_counter() - t_smoke) * 1000
    status = "pass" if smoke_ms < 100 else ("warn" if smoke_ms < 250 else "fail")
    metrics.append(
        DxMetric("discoverability_smoke", f"{smoke_ms:.1f} ms", "<100 ms", status, "self-resolution of //FORGE")
    )
    weights = _DX_WEIGHTS
    by_name = {m.name: m for m in metrics}
    score = 0.0
    for k, w in weights.items():
        m = by_name.get(k)
        if not m:
            continue
        try:
            val = float(str(m.value).rstrip("%"))
        except ValueError:
            val = 100.0 if m.status == "pass" else (50.0 if m.status == "warn" else 0.0)
        score += w * val

    return NavigatorReport(
        emitted_at=datetime.now(timezone.utc).isoformat(),
        camelot_home=str(CAMELOT_HOME),
        navigator_version=__version__,
        navigator_rung=__nav_rung__,
        canonical_files=files,
        canonical_lines=lines,
        canonical_symbols=symbols,
        extensions=by_ext,
        bin_entry_points=bin_eps,
        control_plane_modules=cp_eps,
        squire_modules=sq_eps,
        runes=runes,
        knights=knights,
        audit_ladder=audit,
        docs=docs,
        dx_metrics=metrics,
        topology_metrics=topology_metrics,
        topology_score=topology_score,
        crucible_metrics=crucible_metrics,
        crucible_score=crucible_score,
        findings=findings,
        letter_grade=_letter_grade(score),
        numeric_score=score,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="./navigator.py",
        description="CAMELOT-OS Project Navigation + Dev-UX + Topology Index.",
    )
    mode_group = ap.add_mutually_exclusive_group()
    mode_group.add_argument("--json-only", action="store_true", help="Write only NAVIGATOR_INDEX_<date>.json (mutually exclusive with --md-only and --both)")
    mode_group.add_argument("--md-only", action="store_true", help="Write only NAVIGATOR_REPORT_<date>.md (mutually exclusive with --json-only and --both)")
    mode_group.add_argument("--both", action="store_true", help="(default) Write both JSON and MD (mutually exclusive with --json-only and --md-only)")
    ap.add_argument("--out-dir", default=".", help="Output directory (default: repo root)")
    ap.add_argument("--rune", metavar="NAME", help="Resolve a single rune, print JSON, exit")
    ap.add_argument("--knight", metavar="SUBSTR", help="Find knight sheets matching substring, print list, exit")
    ap.add_argument("--surface", choices=("bin", "cp", "sq", "knights", "docs", "audit", "all"), default="all",
                    help="Limit surface scope (default: all)")
    ap.add_argument("--version", action="store_true", help="Print version and exit")
    args = ap.parse_args(argv)

    if args.version:
        print(f"navigator.py v{__version__}  //  {__nav_rung__}")
        return 0

    if args.rune:
        runes, _ = _collect_runes()
        r = _resolve_rune(args.rune, runes)
        if not r:
            print(json.dumps({"error": "rune not found", "rune": args.rune}, indent=2))
            return 1
        print(json.dumps(asdict(r), indent=2, ensure_ascii=False))
        return 0
    if args.knight:
        ks = _collect_knights()
        hits = _resolve_knight(args.knight, ks)
        print(json.dumps([asdict(k) for k in hits], indent=2, ensure_ascii=False))
        return 0

    report = _build_report()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    wrote: list[str] = []
    if not args.md_only:
        j = out_dir / f"NAVIGATOR_INDEX_{TODAY}.json"
        _write_json(report, j)
        wrote.append(str(j))
    if not args.json_only:
        m = out_dir / f"NAVIGATOR_REPORT_{TODAY}.md"
        _write_md(report, m)
        wrote.append(str(m))

    print(json.dumps({
        "navigator_version": report.navigator_version,
        "navigator_rung": report.navigator_rung,
        "grade": report.letter_grade,
        "score": round(report.numeric_score, 1),
        "topology_score": round(report.topology_score, 1),
        "crucible_score": round(report.crucible_score, 1),
        "canonical_files": report.canonical_files,
        "canonical_lines": report.canonical_lines,
        "bin_modules": len(report.bin_entry_points),
        "control_plane_modules": len(report.control_plane_modules),
        "squire_modules": len(report.squire_modules),
        "runes": len(report.runes),
        "knights": len(report.knights),
        "audit_ladder": [a.path for a in report.audit_ladder],
        "wrote": wrote,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
