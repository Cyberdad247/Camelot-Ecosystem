"""VFS Preflight runner: load catalog, execute checks, emit evidence.

Slice #1 Task 3 lands `load_catalog` for real. Task 6 will replace the
NotImplementedError stubs for `execute_check` and `execute_catalog`
once per-check probes land (Task 4) and probe-runners (Task 6).
"""
from __future__ import annotations
from pathlib import Path
from typing import List

from .schemas import CheckSpec, CheckResult, RunManifest
from .state import GraduationFlag  # noqa: F401  (used by run() in Task 6)


class CatalogError(ValueError):
    """Catalog load failed. The message bundles per-file error info."""


def load_catalog(checks_dir: Path) -> List[CheckSpec]:
    """Read `*.yaml` from checks_dir, parse via CheckSpec, sort by sequence.

    Behavior:
    - Files are read via `glob('*.yaml')` (lexicographic by filename).
    - Each file is parsed via `CheckSpec.from_yaml_text` which raises
      `schemas.CatalogParseError` on validation failures.
    - Per-file failures are bundled into one `CatalogError` so the
      operator sees all catalog problems in one report.
    - Duplicate `sequence` values raise `CatalogError` (no silent shadowing).
    - Missing checks_dir raises `CatalogError`.
    - Empty directory returns `[]` (caller decides whether to halt).
    """
    if not checks_dir.exists():
        raise CatalogError(f"checks directory missing: {checks_dir}")
    if not checks_dir.is_dir():
        raise CatalogError(
            f"checks path is not a directory: {checks_dir}"
        )

    specs: List[CheckSpec] = []
    per_file_errors: List[str] = []
    yaml_files = sorted(checks_dir.glob("*.yaml"))
    for f in yaml_files:
        try:
            specs.append(CheckSpec.from_yaml_text(f.read_text()))
        except Exception as e:  # schemas.CatalogParseError or yaml error
            per_file_errors.append(f"{f.name}: {e}")

    if per_file_errors:
        raise CatalogError("; ".join(per_file_errors))

    seen_seqs: set = set()
    duplicates: List[str] = []
    for s in specs:
        if s.sequence in seen_seqs:
            duplicates.append(
                f"sequence {s.sequence} duplicated (ids: "
                f"{[sp.id for sp in specs if sp.sequence == s.sequence]})"
            )
        seen_seqs.add(s.sequence)

    if duplicates:
        raise CatalogError("; ".join(duplicates))

    specs.sort(key=lambda s: s.sequence)
    return specs


# ============================================================================
# Stub entry points — Task 6 will replace with real implementations.
# ============================================================================

def execute_check(
    spec: CheckSpec, *, strict_mode: bool, anya_triage_fn
) -> CheckResult:  # pragma: no cover
    """Run a single check. Task 6 fills this in.

    `anya_triage_fn` is the **advisory** triage function signature:
        anya_triage_fn(raw_intent: str) -> dict | TriageScore
    Preflight **owns** evidence_class via direct observation; this
    function is invoked for **advisory metadata only** (per
    VFS_PREFLIGHT_DESIGN.md §3.3 substrate-patched-on-2026-08-13).
    """
    raise NotImplementedError(
        "Task 6 will implement execute_check "
        "(see docs/superpowers/plans/2026-08-13-vfs-preflight.md)."
    )


def execute_catalog(
    *,
    specs: List[CheckSpec],
    run_root: Path,
    scene_text: str,
    strict_mode: bool,
    anya_triage_fn,
) -> RunManifest:  # pragma: no cover
    """Run the catalog end-to-end. Task 6 fills this in."""
    raise NotImplementedError(
        "Task 6 will implement execute_catalog "
        "(see docs/superpowers/plans/2026-08-13-vfs-preflight.md)."
    )
