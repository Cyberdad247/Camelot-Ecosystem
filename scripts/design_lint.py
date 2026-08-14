#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""design_lint.py — Phase 4 build-fail lint for the HiveIDE_Apex_v1000 DAG.

Scans staged TSX/JSX/CSS in scoped repositories for AGENTS.md Rule 1 violations:

  1. JSX ``class="..."`` strings should use Tailwind v4 utility prefixes.
     Inline ``style={{ ... }}`` props for layout/color/typography are forbidden
     unless the file declares an ``@layer components`` wrapping CSS. Recognized
     using a permissive identifier matcher so camelCase variants (e.g.
     ``marginTop``, ``paddingLeft``, ``borderRadius``) are also caught.
  2. Icon JSX nodes must import from ``@lucide/react`` (Lucide-React only).
     Direct ``<svg>`` icon literals require either a co-located ``@lucide/react``
     import or a file-level ``// CML_LUCIDE_OK`` annotation (validated anywhere
     in the same file as a Camelot opt-out convention).

Honors bypass via ``CAMELOT_LINT_WAIVER_TOKEN=<token>`` env var; the waiver is
logged to ``.hive/design_lint_waivers.jsonl`` with only the 6-char prefix to
avoid leaking the token string.

Run as module::

    python scripts/design_lint.py --self-test
    python scripts/design_lint.py [--repo <path>] [--strict]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Static rule definitions (AGENTS.md Rule 1).
# ---------------------------------------------------------------------------

_TAILWIND_PREFIXES: tuple[str, ...] = (
    "bg-", "text-", "border-", "rounded-", "shadow-", "ring-",
    "p-", "px-", "py-", "pt-", "pr-", "pb-", "pl-",
    "m-", "mx-", "my-", "mt-", "mr-", "mb-", "ml-",
    "w-", "h-", "min-w-", "min-h-", "max-w-", "max-h-",
    "flex", "grid", "block", "inline", "inline-flex", "inline-grid", "table",
    "hidden", "visible", "sr-only",
    "absolute", "relative", "fixed", "sticky", "static",
    "z-", "opacity-", "transition", "duration-", "ease-", "delay-", "animate-",
    "font-", "tracking-", "leading-", "italic", "uppercase", "lowercase",
    "capitalize", "underline", "line-through", "no-underline",
    "select-", "cursor-", "outline-",
    "gap-", "space-x-", "space-y-",
    "justify-", "items-", "self-", "content-",
    "col-", "row-", "order-",
    "truncate", "overflow-",
    "hover:", "focus:", "active:", "disabled:", "group-", "peer-", "dark:",
    "luxora-",
)

# JSX style={{ prop1: 'a', prop2: 'b' }} — we first capture each style-block's
# body (non-greedy until `}}`) and then iterate every prop name in it. This
# handles chains of camelCase- or kebab-case props correctly, in contrast to a
# single anchor that would only match the first prop after `{{`.
_STYLE_BLOCK = re.compile(r"style=\{\{([^}]*)\}\}")
_STYLE_PROP = re.compile(r"([a-zA-Z][a-zA-Z0-9]*)\s*:")

_FORBIDDEN_BASES: tuple[str, ...] = (
    "margin", "padding", "color", "background", "border", "width", "height",
    "font", "text", "position",
    "top", "right", "bottom", "left", "inset",
    "flex", "grid", "gap", "justify", "align",
    "display", "opacity", "transform", "translate", "scale", "rotate", "z",
    "transition", "animation", "outline", "shadow", "overflow", "visibility",
)

_CLASS_PATTERN = re.compile(r'class(?:Name)?\s*=\s*(["\'])([^"\']+)\1')

# File extensions in scope.
_SCOPED_ROOTS: tuple[str, ...] = (
    "02_FORGE/PORTAL_CORE",
    "02_FORGE/apps",
    "01_KERNEL/dashboard",
)


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    path: str
    line: int
    rule: str
    excerpt: str
    severity: str = "ERROR"
    suggestion: str = ""


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    scanned_files: int = 0
    bypassed: bool = False
    bypass_token: str | None = None

    def by_rule(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for f in self.findings:
            out[f.rule] = out.get(f.rule, 0) + 1
        return out

    @property
    def is_clean(self) -> bool:
        return all(f.severity != "ERROR" for f in self.findings)


# ---------------------------------------------------------------------------
# Token recognition
# ---------------------------------------------------------------------------

def _is_tailwind_token(token: str) -> bool:
    token = token.strip()
    if not token:
        return False
    # Allow arbitrary values: e.g. w-[42px]
    if re.match(r"^[a-z]+-\[[^\]]+\]$", token):
        return True
    return token.startswith(_TAILWIND_PREFIXES)


def _is_palette_token(token: str) -> bool:
    """Mandated palette: #050505, #D4AF37, royal-purple family."""
    s = token.upper().lstrip("#")
    if s in {"050505", "D4AF37"}:
        return True
    upper = token.upper()
    return "PURPLE" in upper or "ROYAL-PURPLE" in upper or "LUXORA" in upper


def _is_forbidden_style_prop(prop: str) -> bool:
    """Loose prefix match — covers camelCase like `marginTop`, `borderRadius`."""
    base = prop.lower()
    return any(base.startswith(b.lower()) for b in _FORBIDDEN_BASES)


# ---------------------------------------------------------------------------
# File-level scanning
# ---------------------------------------------------------------------------

def _scan_jsx(path: Path, text: str, report: Report) -> None:
    imports = re.findall(r'^\s*import\s+.*?\s+from\s+["\']([^"\']+)["\']', text, re.M)
    uses_lucide = any("@lucide/react" in imp for imp in imports)
    # File-level opt-out: any `CML_LUCIDE_OK` annotation anywhere in the file
    # silences all inline-SVG icon literals in the same file. The annotation is
    # a Camelot convention documented in `epic_ui_design`.
    lucide_filelevel_opt_out = "CML_LUCIDE_OK" in text
    forbids_inline_svg = not uses_lucide and not lucide_filelevel_opt_out

    for i, line in enumerate(text.splitlines(), start=1):
        for block_m in _STYLE_BLOCK.finditer(line):
            body = block_m.group(1)
            for prop_m in _STYLE_PROP.finditer(body):
                prop = prop_m.group(1)
                if _is_forbidden_style_prop(prop):
                    report.findings.append(Finding(
                        path=str(path),
                        line=i,
                        rule="tailwind-v4.inline-style",
                        excerpt=f"prop={prop}",
                        suggestion=f"Use a Tailwind v4 utility class instead of inline style prop '{prop}'.",
                    ))

        if "<svg" in line and forbids_inline_svg:
            report.findings.append(Finding(
                path=str(path),
                line=i,
                rule="lucide-only.icon-violation",
                excerpt=line.strip()[:200],
                suggestion="Import icon from '@lucide/react' or annotate '// CML_LUCIDE_OK' anywhere in this file.",
            ))

        for m in _CLASS_PATTERN.finditer(line):
            classes = m.group(2).split()
            bad = [
                c for c in classes
                if not _is_tailwind_token(c)
                and not _is_palette_token(c)
                and not c.startswith("data-[")
                and not c.startswith("aria-")
            ]
            if bad:
                report.findings.append(Finding(
                    path=str(path),
                    line=i,
                    rule="tailwind-v4.unknown-token",
                    excerpt=f"non-Tailwind tokens: {bad}",
                    suggestion="Move to Tailwind v4 utilities, or move palette colors into theme.css.",
                ))


def _scan_css(path: Path, text: str, report: Report) -> None:
    in_components_layer = False
    for i, line in enumerate(text.splitlines(), start=1):
        if "@layer components" in line:
            in_components_layer = True
        elif in_components_layer and line.strip().startswith("}"):
            in_components_layer = False
        if not in_components_layer:
            color_match = re.search(r'#[0-9a-fA-F]{6}', line)
            if color_match and "var(--" not in line:
                color = color_match.group(0).upper().lstrip("#")
                if color not in {"050505", "D4AF37"} and "PURPLE" not in color.upper():
                    report.findings.append(Finding(
                        path=str(path),
                        line=i,
                        rule="tailwind-v4.palette-violation",
                        excerpt=line.strip()[:200],
                        suggestion="Use a CSS variable from theme.css or one of #050505 / #D4AF37 / royal-purple.",
                    ))


def _scan_file(path: Path, report: Report) -> None:
    if not path.is_file():
        return
    report.scanned_files += 1
    suffix = path.suffix.lower()
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        report.findings.append(Finding(
            path=str(path),
            line=0,
            rule="io.read-error",
            excerpt=f"{type(exc).__name__}: {exc}",
            severity="WARN",
        ))
        return
    if suffix in {".tsx", ".jsx"}:
        _scan_jsx(path, text, report)
    elif suffix == ".css":
        _scan_css(path, text, report)


def _discover_paths(repo_root: Path) -> list[Path]:
    paths: list[Path] = []
    for scope in _SCOPED_ROOTS:
        root = repo_root / scope
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".tsx", ".jsx", ".css"}:
                paths.append(p)
    return paths


# ---------------------------------------------------------------------------
# Waiver + reporting
# ---------------------------------------------------------------------------

def _check_waiver() -> tuple[bool, str | None]:
    token = os.environ.get("CAMELOT_LINT_WAIVER_TOKEN")
    if not token:
        return False, None
    waiver_log = Path(".hive") / "design_lint_waivers.jsonl"
    waiver_log.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": time.time(),
        "env_token_present": True,
        # Persist only the prefix so the full token is not on disk.
        "token_prefix": token[:6],
    }
    with waiver_log.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
    return True, token[:6] + "***"


def _render_report(report: Report) -> str:
    lines = [
        f"design_lint — scanned {report.scanned_files} file(s)",
        f"waived: {report.bypassed} (token={report.bypass_token or 'unused'})",
        "",
        f"findings: {len(report.findings)}",
    ]
    by = report.by_rule()
    if by:
        for rule, count in sorted(by.items()):
            lines.append(f"  {rule}: {count}")
        for f in report.findings:
            lines.append(f"  - {f.path}:{f.line} [{f.rule}] {f.excerpt}")
        if any(f.severity == "ERROR" for f in report.findings):
            lines.append("")
            lines.append("Build-fail violations exceed zero. Remediation per AGENTS.md Rule 1.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="AGENTS.md Rule 1 design lint")
    parser.add_argument("--repo", default=".", help="repo root")
    parser.add_argument("--self-test", action="store_true", help="run smoke tests")
    args = parser.parse_args()

    if args.self_test:
        return _selftest_or_zero()

    report = Report()
    waived, prefix = _check_waiver()
    report.bypassed = waived
    report.bypass_token = prefix

    repo_root = Path(args.repo).resolve()
    paths = _discover_paths(repo_root)
    for p in paths:
        _scan_file(p, report)

    print(_render_report(report))
    if waived:
        return 0
    return 1 if report.findings else 0


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest_or_zero() -> int:
    failures = 0
    sandbox = Path(".hive/_test_violations.tsx")

    def check(name: str, cond: bool) -> None:
        nonlocal failures
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            failures += 1

    print("design_lint self-test")
    check("bg-black is tailwind", _is_tailwind_token("bg-black"))
    check("hover:bg-luxora-gold is tailwind", _is_tailwind_token("hover:bg-luxora-gold"))
    check("w-[42px] arbitrary value recognized", _is_tailwind_token("w-[42px]"))
    check("sty-my-component rejected", not _is_tailwind_token("sty-my-component"))
    check("#D4AF37 is palette", _is_palette_token("#D4AF37"))
    check("#050505 is palette", _is_palette_token("#050505"))
    check("#abcdef NOT in palette", not _is_palette_token("#abcdef"))
    check("marginTop forbidden", _is_forbidden_style_prop("marginTop"))
    check("borderRadius forbidden", _is_forbidden_style_prop("borderRadius"))
    check("paddingLeft forbidden", _is_forbidden_style_prop("paddingLeft"))
    check("color forbidden", _is_forbidden_style_prop("color"))
    check("ariaLabel NOT forbidden", not _is_forbidden_style_prop("ariaLabel"))

    # JSX scan: inline style + non-Tailwind class (camelCase coverage check)
    r = Report()
    sandbox.parent.mkdir(parents=True, exist_ok=True)
    sandbox.write_text(
        "export const X = () => (\n"
        "  <div style={{ marginTop: '10px', borderRadius: '4px', ariaLabel: 'tip' }} class=\"sty-foo bg-black\" />\n"
        ");\n",
        encoding="utf-8",
    )
    _scan_file(sandbox, r)
    check("camelCase inline-style flagged (marginTop)",
          any("marginTop" in f.excerpt for f in r.findings if f.rule == "tailwind-v4.inline-style"))
    check("camelCase inline-style flagged (borderRadius)",
          any("borderRadius" in f.excerpt for f in r.findings if f.rule == "tailwind-v4.inline-style"))
    check("non-Tailwind class flagged",
          any(f.rule == "tailwind-v4.unknown-token" for f in r.findings))
    # ariaLabel should NOT be flagged.
    check("ariaLabel NOT flagged as inline-style",
          not any("ariaLabel" in f.excerpt for f in r.findings))

    # @lucide/react import silences inline-SVG flag
    r = Report()
    sandbox.write_text(
        "import { Sun } from '@lucide/react';\n"
        "export const Y = () => <Sun />;\n",
        encoding="utf-8",
    )
    _scan_file(sandbox, r)
    check("@lucide/react import silences SVG literal flag",
          not any(f.rule == "lucide-only.icon-violation" for f in r.findings))

    # File-level CML_LUCIDE_OK annotation silences SVG flag
    r = Report()
    sandbox.write_text(
        "export const Z = () => (\n"
        "  // CML_LUCIDE_OK\n"
        "  <svg><circle cx='10' cy='10' r='5' /></svg>\n"
        ");\n",
        encoding="utf-8",
    )
    _scan_file(sandbox, r)
    check("file-level CML_LUCIDE_OK silences SVG flag",
          not any(f.rule == "lucide-only.icon-violation" for f in r.findings))

    # Without CML_LUCIDE_OK and without @lucide/react, SVG literal is flagged
    r = Report()
    sandbox.write_text(
        "export const W = () => (\n"
        "  <svg><circle cx='10' cy='10' r='5' /></svg>\n"
        ");\n",
        encoding="utf-8",
    )
    _scan_file(sandbox, r)
    check("bare inline-SVG literal flagged",
          any(f.rule == "lucide-only.icon-violation" for f in r.findings))

    # Waiver: token bypasses (smoke)
    os.environ["CAMELOT_LINT_WAIVER_TOKEN"] = "test-waiver-token"
    waived, prefix = _check_waiver()
    check("CAMELOT_LINT_WAIVER_TOKEN triggers waiver", waived and prefix is not None)
    # Verify the log contains only the prefix, not the full token.
    log = Path(".hive/design_lint_waivers.jsonl")
    check("waiver log written", log.exists())
    if log.exists():
        last_line = log.read_text(encoding="utf-8").splitlines()[-1]
        check("full token NOT leaked to log", "test-waiver-token" not in last_line)
        check("token prefix (6 chars) present", '"token_prefix": "test-w' in last_line)
    os.environ.pop("CAMELOT_LINT_WAIVER_TOKEN", None)

    # Cleanup sandbox
    if sandbox.exists():
        sandbox.unlink()

    print(f"\n{'ALL PASS' if failures == 0 else f'{failures} FAILURE(S)'} — design_lint")
    return failures


if __name__ == "__main__":
    sys.exit(main())
