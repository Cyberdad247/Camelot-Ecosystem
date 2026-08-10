# Made by Invisioned Marketing Inc. (c) 2024-2026 | ALL RIGHTS RESERVED
"""Sir Alchemist - The Optimization Smith.

Specializes in code-to-efficiency transmutation: performance profiling,
bundle analysis, query optimization, and algorithmic improvement.
"""

import ast
import re
from pathlib import Path

from .base import BaseKnight


class SirAlchemist(BaseKnight):
    name = "Sir Alchemist"
    title = "Optimization Smith"
    specialty = "Performance Profiling & Code Optimization"
    icon = "[ALCHEMIST]"

    # Optimization smell patterns (Python-focused, extendable)
    PERF_SMELLS = {
        "n_plus_one": {
            "pattern": r"for\s+\w+\s+in\s+.*:\s*\n\s+.*\.(query|execute|fetch|find|get)\(",
            "label": "N+1 Query",
            "fix": "Batch query outside loop or use eager loading / prefetch_related",
        },
        "sync_in_async": {
            "pattern": r"async\s+def\s+.*\n(?:.*\n)*?.*(?:time\.sleep|open\(|os\.read)",
            "label": "Blocking call in async function",
            "fix": "Use asyncio.sleep / aiofiles / async I/O equivalents",
        },
        "string_concat_loop": {
            "pattern": r"for\s+.*:\s*\n\s+\w+\s*\+?=\s*.*\+\s*(?:str|f['\"])",
            "label": "String concatenation in loop",
            "fix": "Use list append + ''.join() or io.StringIO",
        },
        "global_import_in_func": {
            "pattern": r"def\s+\w+.*:\s*\n(?:\s+.*\n)*?\s+import\s+",
            "label": "Import inside function",
            "fix": "Move to module level unless conditional/optional",
        },
        "bare_except": {
            "pattern": r"except\s*:",
            "label": "Bare except clause",
            "fix": "Catch specific exceptions (Exception at minimum)",
        },
    }

    def execute(self, directive: str, intent: dict, write: bool = False) -> dict:
        text = directive.lower()
        params = intent.get("parameters", {})
        target_path = params.get("path", "")

        # Profile a specific file
        if target_path and ("profile" in text or "optimize" in text or "audit" in text):
            return self._profile_file(target_path)

        # Bundle analysis guidance
        if "bundle" in text or "webpack" in text or "turbopack" in text:
            return self._bundle_analysis()

        # Query optimization guidance
        if "query" in text or "sql" in text or "database" in text:
            return self._query_optimization()

        # Default capabilities
        lines = [
            "# Sir Alchemist — Optimization Smith",
            "",
            "## Transmutation Domains",
            "- **Code Profiling**: AST-based smell detection (N+1, sync-in-async, concat loops)",
            "- **Bundle Analysis**: Tree-shaking audit, code-split recommendations",
            "- **Query Optimization**: Index suggestions, N+1 detection, batch strategies",
            "- **Algorithmic**: Complexity reduction, data structure selection",
            "",
            "## Available Actions",
            "- `profile <path>` — Scan Python file for performance smells",
            "- `optimize bundle` — Frontend bundle optimization checklist",
            "- `optimize query` — Database query optimization guide",
        ]
        return {"status": "success", "output": "\n".join(lines), "files_created": []}

    def _profile_file(self, target_path: str) -> dict:
        lines = [f"[ALCHEMIST] Performance Profile: `{target_path}`", ""]
        findings = []

        try:
            abs_path = Path(target_path).expanduser().resolve()
            if abs_path.exists() and abs_path.suffix == ".py":
                source = abs_path.read_text(encoding="utf-8", errors="replace")

                # AST complexity check
                try:
                    tree = ast.parse(source)
                    func_count = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
                    class_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
                    loc = len(source.splitlines())
                    lines.append("### Metrics")
                    lines.append(f"- Lines: {loc}")
                    lines.append(f"- Functions: {func_count}")
                    lines.append(f"- Classes: {class_count}")
                    lines.append(f"- Density: {func_count / max(loc, 1) * 100:.1f} functions/100 LOC")
                    lines.append("")
                except SyntaxError as e:
                    lines.append(f"[WARN] AST parse failed: {e}")
                    lines.append("")

                # Pattern-based smell detection
                for key, smell in self.PERF_SMELLS.items():
                    matches = list(re.finditer(smell["pattern"], source, re.MULTILINE))
                    if matches:
                        findings.append((smell["label"], len(matches), smell["fix"]))

                if findings:
                    lines.append("### Performance Smells Detected")
                    for label, count, fix in findings:
                        lines.append(f"- **{label}** ({count}x) — {fix}")
                else:
                    lines.append("### No performance smells detected.")
            else:
                lines.append(f"[SKIP] File not found or not Python: `{target_path}`")
                lines.append("Provide a valid .py file path for profiling.")

        except Exception as e:
            lines.append(f"[ERROR] Could not profile: {e}")

        return {"status": "success", "output": "\n".join(lines), "files_created": []}

    def _bundle_analysis(self) -> dict:
        lines = [
            "[ALCHEMIST] Frontend Bundle Optimization",
            "",
            "### Tree-Shaking Audit",
            "- [ ] No barrel files re-exporting entire modules",
            "- [ ] Named exports only (no default export of objects)",
            "- [ ] `sideEffects: false` in package.json where safe",
            "",
            "### Code Splitting",
            "- [ ] Dynamic imports for route-level splits: `const X = dynamic(() => import(...))`",
            "- [ ] Heavy libraries loaded lazily (chart libs, editors, maps)",
            "- [ ] Suspense boundaries around lazy-loaded components",
            "",
            "### Asset Optimization",
            "- [ ] Images via next/image (automatic WebP/AVIF)",
            "- [ ] Fonts via next/font (no layout shift)",
            "- [ ] SVGs as React components or inline (not <img>)",
            "",
            "### Analysis Commands",
            "- `ANALYZE=true next build` — Webpack bundle analyzer",
            "- `npx @next/bundle-analyzer` — Next.js specific",
        ]
        return {"status": "success", "output": "\n".join(lines), "files_created": []}

    def _query_optimization(self) -> dict:
        lines = [
            "[ALCHEMIST] Database Query Optimization",
            "",
            "### N+1 Detection",
            "- Symptom: Loop issuing one query per iteration",
            "- Fix: `select_related()` / `prefetch_related()` (Django)",
            "- Fix: `.include()` / eager loading (Prisma/SQLAlchemy)",
            "",
            "### Index Strategy",
            "- Index columns in WHERE, JOIN, ORDER BY clauses",
            "- Composite index for multi-column filters (leftmost prefix rule)",
            "- Partial indexes for filtered subsets",
            "- EXPLAIN ANALYZE before and after",
            "",
            "### Batch Operations",
            "- `INSERT ... VALUES (row1), (row2), ...` instead of loop",
            "- `executemany()` for parameterized batch inserts",
            "- Bulk upsert: `ON CONFLICT DO UPDATE`",
            "",
            "### Connection Pooling",
            "- Use pgBouncer or built-in pool (SQLAlchemy `pool_size`)",
            "- Close connections promptly in serverless (Vercel/Modal)",
        ]
        return {"status": "success", "output": "\n".join(lines), "files_created": []}
