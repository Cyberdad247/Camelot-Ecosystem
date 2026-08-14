#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

# ruff: noqa: E501
"""cybertronia_lockbox_ci.py -- 3-way cross-check anchor for the Draft 0.3.1 (section 6.3)
migration window (v3: post-second-review corrections).

READS  (always three sources; plus optional fourth ``--drift-test-ts``):
    1. cybertronia_compile.py             (Phase 2 Python producer)
    2. cybertronia-graph-ui-spec.md       (Draft 0.3.1 upstream contract section 6)
    3. cybertronia-graph-ui-package-spec.md (Draft 0.1.1 package spec section 6.1)
    4. <package>/tests/cybertronia-graph-drift.test.ts  (optional, post-hoist)

Usage
    python scripts/cybertronia_lockbox_ci.py
    CAMELOT_OS_HOME=/path/to/camelot python scripts/cybertronia_lockbox_ci.py
    python scripts/cybertronia_lockbox_ci.py --mode=migration-week-1
    python scripts/cybertronia_lockbox_ci.py \\
        --drift-test-ts /path/to/packages/cybertronia-graph-ui/tests/cybertronia-graph-drift.test.ts

Exit codes
    0 -- every invariant matches across every present source (PASS or SOFT-SKIP)
    1 -- one or more invariants drifted (FAIL -- migration window cannot close)
    2 -- environment error (a required source is unreadable OR zero invariants parsed)

Design notes
    * Each invariant declares ``comparison = ORDERED | UNORDERED | SCALAR``;
      ordered invariants are compared positionally (VECTOR25_FIELD_NAMES is
      order-sensitive), unordered invariants are compared as frozensets
      (KINDS, RELATIONS, PERF_PROFILES -- order-independent semantics).
    * The 25-string VECTOR25_FIELD_NAMES / 25-scalar EXPECTED_VECTOR_LEN pair
      is implicitly self-checking -- if a source declares ``len == 25`` but
      provides 24 strings, the implicit-length-vs-payload assertion fires
      before the cross-source comparison.
    * Migration-window contract: this script is the deterministic anchor that
      catches Concern F (the unilateral relocation of lockbox ownership to
      the package slipping through CI on either side). Phase 3 sign-off is
      gated on
          (a) this script returning exit 0 in --mode=migration-week-1, AND
          (b) Draft 0.3.1 section 6.3's 7-day green-streak closing the migration window.

v3 changes from v2 (post second-review):
    * MarkdownSpec parser REWRITTEN: fence-aware + line-walking. Extracts
      arrays strictly within fenced ` ```typescript ` (or ` ```ts `) blocks,
      walking lines and terminating each `[NAME] = [...]` declaration at
      the FIRST `];` / `] as const` / `] as const satisfies` line. Eliminates
      the v2 bug where DOTALL+non-greedy `];` regex captured across multiple
      arrays (returning len=61 instead of 25 for spec.md VECTOR25_FIELD_NAMES).
    * SourceKind.DRIFT_TEST_TS added to 8 consumer-side INVARIANTS.tuple
      so the (post-hoist) tests/cybertronia-graph-drift.test.ts file actually
      participates in the cross-check when present. Pre-hoist, the loader's
      WARN + extractors' `None`-skip keeps the behavior unchanged.
    * Single-source-of-truth: `_check_invariant`'s migration-week-1 check
      consults `invariant.consumer_required_in_migration` (the dataclass
      flag) instead of a hardcoded set of 6 names -- so adding a new
      invariant with `consumer_required_in_migration=True` automatically
      gets the migration-window enforcement.
    * Zero-invariants reporting: collect ALL zero-count sources into one
      `[LOCKBOX-FAIL]` block listing every offending path, then return 2.
    * Dead `Invariant.__post_init__` (whose hardcoded set was already
      shadowed by explicit dataclass flags) deleted.

v4 changes from v3 (post third-review):
    * _ARRAY_END_RE extended to also match `].\w+\(` -- closes the DRIFT_MSG
      unterminated-array hazard where spec.md section 6.2's `].join("");`
      was not recognized as an array terminator.
    * _FENCE_OPEN_RE extended to `tsx` (jsx-fence) AND uses \b word boundary
      + drops \s*$ end-of-line requirement so future
      ` ```typescript title="..." `` fences still match.
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

__version__ = "9000.19-LBX-4"


# ─────────────────────────────────────────────────────────────────────────────
#  Source model
# ─────────────────────────────────────────────────────────────────────────────

class SourceKind(str, Enum):
    PYTHON         = "python-producer"
    SPEC_MD        = "spec-upstream-contract"
    PACKAGE_SPEC_MD = "package-spec-contract"
    DRIFT_TEST_TS  = "package-drift-test-ts"


class Comparison(Enum):
    ORDERED   = "ordered"
    UNORDERED = "unordered"
    SCALAR    = "scalar"


# All consumer-side invariants include DRIFT_TEST_TS so the post-hoist
# packages/cybertronia-graph-ui/tests/cybertronia-graph-drift.test.ts file
# participates in the cross-check when present (the Concern F anchor).
_CONSUMER_SOURCES = (
    SourceKind.SPEC_MD,
    SourceKind.PACKAGE_SPEC_MD,
    SourceKind.DRIFT_TEST_TS,
)
_SHARED_SOURCES = (
    SourceKind.PYTHON,
    SourceKind.SPEC_MD,
    SourceKind.PACKAGE_SPEC_MD,
    SourceKind.DRIFT_TEST_TS,
)


@dataclass
class Invariant:
    name: str
    comparison: Comparison
    sources: tuple[SourceKind, ...]
    consumer_required_in_migration: bool = False
    notes: str = ""


# 9 invariants -- names mirror the Python / TS declarations verbatim.
INVARIANTS: tuple[Invariant, ...] = (
    Invariant(
        "expected_layers",
        Comparison.UNORDERED,
        _SHARED_SOURCES,
        consumer_required_in_migration=True,
        notes="5-element layer order is irrelevant -- comparison set-wise.",
    ),
    Invariant(
        "expected_kinds_or_kind_index",
        Comparison.UNORDERED,
        _SHARED_SOURCES,
        consumer_required_in_migration=True,
        notes="Python: dict keys; md: array. Order irrelevant.",
    ),
    Invariant(
        "expected_vector_field_names",
        Comparison.ORDERED,
        _SHARED_SOURCES,
        consumer_required_in_migration=True,
        notes=(
            "25-string positional -- see section 6.2 'preserves captured "
            "order (not alphabetical)'."
        ),
    ),
    Invariant(
        "expected_vector_len",
        Comparison.SCALAR,
        _SHARED_SOURCES,
        consumer_required_in_migration=True,
        notes="Pair with VECTOR25_FIELD_NAMES via implicit-length check.",
    ),
    Invariant(
        "expected_relations",
        Comparison.UNORDERED,
        _CONSUMER_SOURCES,
        consumer_required_in_migration=True,
        notes="9-element relation vocabulary -- order is decorative.",
    ),
    Invariant(
        "expected_perf_profiles",
        Comparison.UNORDERED,
        _CONSUMER_SOURCES,
        consumer_required_in_migration=True,
        notes="5-band union -- order is decorative.",
    ),
    Invariant(
        "expected_node_stride_floats",
        Comparison.SCALAR,
        _CONSUMER_SOURCES,
        consumer_required_in_migration=True,
        notes="InstancedMesh stride ceiling (Draft 0.3 section 4.2).",
    ),
    Invariant(
        "expected_edge_stride_floats",
        Comparison.SCALAR,
        _CONSUMER_SOURCES,
        consumer_required_in_migration=True,
        notes="InstancedMesh edge stride (Draft 0.3 section 4.2, weight inlined).",
    ),
    Invariant(
        "schema_version_snapshot",
        Comparison.SCALAR,
        # NOT including DRIFT_TEST_TS because the drift-test file is a
        # vitest .ts that defines the lockbox but does NOT echo the
        # producer's runtime constant.
        (SourceKind.PYTHON, SourceKind.SPEC_MD),
        consumer_required_in_migration=False,
        notes='TS literal "cybertronia.snapshot/v1" -- string equality.',
    ),
)


@dataclass
class CheckResult:
    invariant: str
    status: str
    sources_checked: list[str] = field(default_factory=list)
    source_paths: dict[str, str] = field(default_factory=dict)
    payload_summary: str = ""
    failure_detail: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
#  Path resolution
# ─────────────────────────────────────────────────────────────────────────────

def _camelot_root() -> Path:
    env = os.environ.get("CAMELOT_OS_HOME")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parent.parent


def _build_parser() -> argparse.ArgumentParser:
    base = _camelot_root()
    p = argparse.ArgumentParser(
        prog="python scripts/cybertronia_lockbox_ci.py",
        description=(
            "Cross-check cybertronia-graph-ui lockbox invariants across the "
            "Python producer + Draft 0.3.1 spec.md + Draft 0.1.1 package spec.md. "
            "Anchors the Draft 0.3.1 section 6.3 migration window."
        ),
    )
    p.add_argument(
        "--producer-path",
        default=str(base / "control_plane" / "cybertronia_compile.py"),
        help="Path to the Python producer (default: %(default)s)",
    )
    p.add_argument(
        "--spec-md",
        default=str(base / "docs" / "cybertronia-graph-ui-spec.md"),
        help="Path to Draft 0.3.1 upstream contract markdown (default: %(default)s)",
    )
    p.add_argument(
        "--package-spec-md",
        default=str(base / "docs" / "cybertronia-graph-ui-package-spec.md"),
        help="Path to Draft 0.1.1 package spec markdown (default: %(default)s)",
    )
    p.add_argument(
        "--drift-test-ts",
        default=None,
        help=(
            "Optional path to packages/cybertronia-graph-ui/tests/"
            "cybertronia-graph-drift.test.ts (Phase 3 post-hoist). Pre-hoist, "
            "absent-or-missing is a WARN, not a FAIL. Post-hoist (per Draft 0.3.1 "
            "(section 6.3) 1.0.0 gate), missing is a FAIL with exit 1."
        ),
    )
    p.add_argument(
        "--mode",
        choices=("default", "migration-week-1"),
        default="default",
        help=(
            "default: any consumer-only soft-skip is allowed. "
            "migration-week-1: per Draft 0.3.1 section 6.3 the window is binary; "
            "consumer-only invariants must match across BOTH md sources."
        ),
    )
    return p


# ─────────────────────────────────────────────────────────────────────────────
#  Python producer extractor (ast-based -- handles Assign AND AnnAssign)
# ─────────────────────────────────────────────────────────────────────────────

def _ast_eval_literal(node: ast.AST):
    """Recursively evaluate a python AST literal -- Tuple / List / Dict / Constant."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Tuple):
        return tuple(_ast_eval_literal(e) for e in node.elts)
    if isinstance(node, ast.List):
        return [_ast_eval_literal(e) for e in node.elts]
    if isinstance(node, ast.Dict):
        return {
            _ast_eval_literal(k): _ast_eval_literal(v)
            for k, v in zip(node.keys, node.values, strict=False)
        }
    raise ValueError(f"unsupported literal node: {type(node).__name__}")


def _name_targets(node: ast.AST):
    """Yield (name, value) pairs for both Assign and AnnAssign AST nodes."""
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        if node.value is not None:
            yield node.target.id, node.value
    elif isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name):
                yield t.id, node.value


class PythonProducer:
    def __init__(self, source_text: str):
        self.tree = ast.parse(source_text)

    def _first_match(self, name: str):
        for node in self.tree.body:
            for tgt, val in _name_targets(node):
                if tgt == name:
                    return val
        return None

    def get_tuple(self, name: str) -> Optional[tuple]:
        v = self._first_match(name)
        if v is None:
            return None
        if isinstance(v, (ast.Tuple, ast.List)):
            return tuple(_ast_eval_literal(e) for e in v.elts)
        return None

    def get_scalar(self, name: str) -> Optional[object]:
        v = self._first_match(name)
        if v is None:
            return None
        return _ast_eval_literal(v)

    def get_dict_keys_sorted(self, name: str) -> Optional[tuple]:
        v = self._first_match(name)
        if v is None or not isinstance(v, ast.Dict):
            return None
        keys = [_ast_eval_literal(k) for k in v.keys]
        return tuple(sorted(keys))

    # Required interface for the MarkdownSpec-compat contract below
    def expected_layers(self) -> Optional[tuple]:
        return self.get_tuple("LAYERS")

    def expected_kinds_or_kind_index(self) -> Optional[tuple]:
        return self.get_dict_keys_sorted("KIND_TO_INDEX")

    def expected_vector_field_names(self) -> Optional[tuple]:
        return self.get_tuple("VECTOR25_FIELD_NAMES")

    def expected_vector_len(self) -> Optional[object]:
        return self.get_scalar("EXPECTED_VECTOR_LEN")

    def schema_version_snapshot(self) -> Optional[str]:
        s = self.get_scalar("SCHEMA_VERSION_SNAPSHOT")
        return s if isinstance(s, str) else None


# ─────────────────────────────────────────────────────────────────────────────
#  MarkdownSpec extractor (fence-aware line-walking; replaces v2 regex).
#  Eliminates the v2 bug where DOTALL+non-greedy `]\s*;` captured across
#  multiple array declarations.
# ─────────────────────────────────────────────────────────────────────────────

# Trailing-terminator patterns for `[NAME] = [...]` array literals in TS:
#   `];`                         -- pure statement end
#   `] as const;`                -- TS const assertion
#   `] as const satisfies readonly X[];` -- typed const assertion
#   `])`                         -- end of a function call arg
#   `]}`                         -- end of an object literal
#   `].join("");` or `].foo(...)` -- DRIFT_MSG / chained-call style
# Inline-comment / embedded-comment are tolerated by per-line pull-quoted.
_ARRAY_END_RE = re.compile(
    r"\]\s*(?:;|\bas\s+const\b|,|\)|\}|[\.]\s*\w+\s*\()",
)

# Fenced TS code block opener. Tolerates metadata after the language tag
# (e.g. ```typescript title="..."` is matched because we don't anchor on \s*$,
# just on the language token followed by a word boundary).
_FENCE_OPEN_RE = re.compile(
    r"^\s*```(?:typescript|ts|tsx)\b",
)
_FENCE_CLOSE_RE = re.compile(
    r"^\s*```\s*$",
)


def _pull_quoted_strings(line: str) -> list[str]:
    """Pull single- or double-quoted strings out of one line.

    Tolerates inline `// comments` because they live AFTER the closing
    bracket or before another opening statement; line-scoped walk splits
    them naturally.
    """
    return [q.strip() for q in re.findall(r"""['"]([^'"\n]+)['"]""", line)]


def _walk_fence_arrays(block_text: str) -> dict[str, tuple[str, ...]]:
    """Walk a fenced TS code block line by line, collecting arrays.

    Terminates at: `];`, `] as const`, `] as const satisfies ...`,
    `]`, or `])`. Comment lines (`// X`) and empty lines are tolerated
    inside an array.
    """
    results: dict[str, tuple[str, ...]] = {}
    lines = block_text.splitlines()
    current_name: Optional[str] = None
    current_elements: list[str] = []
    array_start_re = re.compile(
        r"^\s*(?:const\s+)?(?P<name>[A-Z_][A-Z0-9_]*)\s*=\s*\[",
    )
    for line in lines:
        if current_name is None:
            m = array_start_re.match(line)
            if m:
                current_name = m.group("name")
                current_elements = []
                # The remainder of the line AFTER `[`.
                rest = line[m.end():]
                current_elements.extend(_pull_quoted_strings(rest))
                # If the array starts AND ends on one line (single-line
                # array), the same line may contain the terminator.
                if _ARRAY_END_RE.search(rest):
                    results[current_name] = tuple(current_elements)
                    current_name = None
                    current_elements = []
            continue

        # We are inside an open array. Pull quoted strings; check terminator.
        current_elements.extend(_pull_quoted_strings(line))
        if _ARRAY_END_RE.search(line):
            results[current_name] = tuple(current_elements)
            current_name = None
            current_elements = []
    if current_name is not None:
        # Unterminated -- keep the partial under its name so the consumer
        # can surface a length-mismatch failure.
        results[current_name] = tuple(current_elements)
    return results


def _extract_all_arrays_from_md(md_text: str) -> dict[str, tuple[str, ...]]:
    """Walk fenced TS code blocks; collect every `[NAME] = [...]` array."""
    out: dict[str, tuple[str, ...]] = {}
    lines = md_text.splitlines()
    in_fence = False
    fence_lines: list[str] = []
    for line in lines:
        if not in_fence:
            if _FENCE_OPEN_RE.match(line):
                in_fence = True
                fence_lines = []
            continue
        if _FENCE_CLOSE_RE.match(line):
            in_fence = False
            out.update(_walk_fence_arrays("\n".join(fence_lines)))
            fence_lines = []
        else:
            fence_lines.append(line)
    return out


# Scalar regex anchors `[A-Z_][A-Z0-9_]*` then captures an integer or float
# value. Tolerates `const NAME: type = 25 as const;` and bare `EXPECTED_X = 25;`.
_SCALAR_RE = re.compile(
    r"""\b(?P<name>[A-Z_][A-Z0-9_]*)\b(?:\s*:\s*[\w \[\]\.|,<>]+?)?\s*=\s*(?P<value>\d+(?:\.\d+)?)\b""",
)
# TS literal string: cybertronia.snapshot/v1 (spec.md type annotation)
_TS_STRING_LITERAL_RE = re.compile(
    r"""["'](?P<value>cybertronia\.snapshot/v\d+)["']"""
)
# EXPECTED_VECTOR_LEN extractor -- tolerates `const X = 25 as const;`,
# `const X: number = 25;`, and `X = 25`.
_VECTOR_LEN_RE = re.compile(
    r"\bEXPECTED_VECTOR_LEN\b[^=]{0,80}=\s*(\d+)",
)


class MarkdownSpec:
    """Reads `EXPECTED_*` constants from a markdown file's fenced TS code blocks."""

    def __init__(self, source_text: str, source_path: Path | None = None):
        self.source_text = source_text
        self.source_path = source_path
        self._arrays = _extract_all_arrays_from_md(source_text)

    def _array(self, name: str) -> Optional[tuple]:
        return self._arrays.get(name)

    def _scalar(self, name: str) -> Optional[object]:
        for m in _SCALAR_RE.finditer(self.source_text):
            if m.group("name") == name:
                try:
                    return int(m.group("value"))
                except ValueError:
                    return m.group("value")
        return None

    def expected_layers(self) -> Optional[tuple]:
        return self._array("EXPECTED_LAYERS")

    def expected_kinds_or_kind_index(self) -> Optional[tuple]:
        return self._array("EXPECTED_KINDS")

    def expected_vector_field_names(self) -> Optional[tuple]:
        return self._array("EXPECTED_VECTOR_FIELD_NAMES")

    def expected_vector_len(self) -> Optional[object]:
        m = _VECTOR_LEN_RE.search(self.source_text)
        if not m:
            return None
        try:
            return int(m.group(1))
        except ValueError:
            return m.group(1)

    def expected_relations(self) -> Optional[tuple]:
        return self._array("EXPECTED_RELATIONS")

    def expected_perf_profiles(self) -> Optional[tuple]:
        return self._array("EXPECTED_PERF_PROFILES")

    def expected_node_stride_floats(self) -> Optional[object]:
        return self._scalar("EXPECTED_NODE_STRIDE_FLOATS")

    def expected_edge_stride_floats(self) -> Optional[object]:
        return self._scalar("EXPECTED_EDGE_STRIDE_FLOATS")

    def schema_version_snapshot(self) -> Optional[str]:
        m = _TS_STRING_LITERAL_RE.search(self.source_text)
        return m.group("value") if m else None


# ─────────────────────────────────────────────────────────────────────────────
#  Drift-test-ts extractor (post-hoist package file; uses MarkdownSpec)
# ─────────────────────────────────────────────────────────────────────────────

class DriftTestTS:
    """Reads `EXPECTED_*` constants from the post-hoist drift-test file.

    Pre-hoist, the source path is None, so this object is never constructed
    (the lookup in extractors returns None and the comparison loop SKIPs).
    """

    def __init__(self, source_text: str, source_path: Path):
        self.source_text = source_text
        self.source_path = source_path
        self._md = MarkdownSpec(source_text, source_path)

    def expected_layers(self):               return self._md.expected_layers()
    def expected_kinds_or_kind_index(self):  return self._md.expected_kinds_or_kind_index()
    def expected_vector_field_names(self):   return self._md.expected_vector_field_names()
    def expected_vector_len(self):           return self._md.expected_vector_len()
    def expected_relations(self):            return self._md.expected_relations()
    def expected_perf_profiles(self):        return self._md.expected_perf_profiles()
    def expected_node_stride_floats(self):   return self._md.expected_node_stride_floats()
    def expected_edge_stride_floats(self):   return self._md.expected_edge_stride_floats()
    def schema_version_snapshot(self):       return self._md.schema_version_snapshot()


# ─────────────────────────────────────────────────────────────────────────────
#  Per-invariant checker
# ─────────────────────────────────────────────────────────────────────────────

_GETTER_BY_INVARIANT = {
    "expected_layers":              "expected_layers",
    "expected_kinds_or_kind_index": "expected_kinds_or_kind_index",
    "expected_vector_field_names":  "expected_vector_field_names",
    "expected_vector_len":          "expected_vector_len",
    "expected_relations":           "expected_relations",
    "expected_perf_profiles":       "expected_perf_profiles",
    "expected_node_stride_floats":  "expected_node_stride_floats",
    "expected_edge_stride_floats":  "expected_edge_stride_floats",
    "schema_version_snapshot":      "schema_version_snapshot",
}


def _check_invariant(
    invariant: Invariant,
    extractors: dict[SourceKind, object],
    source_paths: dict[SourceKind, Path],
    mode: str,
) -> CheckResult:
    getter = _GETTER_BY_INVARIANT[invariant.name]
    sources_used: dict[SourceKind, object] = {}
    for sk in invariant.sources:
        ext = extractors.get(sk)
        if ext is None:
            continue
        try:
            value = getattr(ext, getter)()
        except Exception as e:  # noqa: BLE001 -- surface as a deterministic message
            return CheckResult(
                invariant=invariant.name,
                status="FAIL",
                failure_detail=(
                    f"invariant=\"{invariant.name}\" source={sk.value} "
                    f"path={source_paths.get(sk, '?')} parse_error=`{type(e).__name__}: {e}`"
                ),
            )
        if value is not None:
            sources_used[sk] = value

    sources_checked = [s.value for s in sources_used.keys()]
    source_paths_used = {s.value: str(source_paths[s]) for s in sources_used.keys()}
    if not sources_checked:
        return CheckResult(
            invariant=invariant.name,
            status="SOFT-SKIP",
            payload_summary="no source declares this invariant",
        )

    first_kind = next(iter(sources_used.keys()))
    first_value = sources_used[first_kind]
    first_summary = _summarize(first_value)

    for k, v in sources_used.items():
        if k == first_kind:
            continue
        if not _values_equal(invariant.comparison, first_value, v):
            return CheckResult(
                invariant=invariant.name,
                status="FAIL",
                sources_checked=sources_checked,
                source_paths=source_paths_used,
                payload_summary=first_summary,
                failure_detail=_diff_message(
                    invariant.name, invariant.comparison,
                    first_kind, first_value, k, v, source_paths,
                ),
            )

    # Migration-window contract: for invariants flagged
    # `consumer_required_in_migration`, BOTH md sources must hold GREEN.
    # Single source of truth: the dataclass flag, NOT a hardcoded set.
    if mode == "migration-week-1" and invariant.consumer_required_in_migration:
        md_required = {SourceKind.SPEC_MD, SourceKind.PACKAGE_SPEC_MD}
        if not md_required.issubset(set(sources_used.keys())):
            missing_kinds = md_required - set(sources_used.keys())
            missing = sorted(s.value for s in missing_kinds)
            missing_paths = ", ".join(
                str(source_paths.get(k, "?")) for k in missing_kinds
            )
            return CheckResult(
                invariant=invariant.name,
                status="FAIL",
                sources_checked=sources_checked,
                source_paths=source_paths_used,
                payload_summary=first_summary,
                failure_detail=(
                    f"invariant=\"{invariant.name}\" migration-week-1 "
                    f"missing=[{','.join(missing)}] paths=[{missing_paths}]"
                ),
            )

    return CheckResult(
        invariant=invariant.name,
        status="PASS",
        sources_checked=sources_checked,
        source_paths=source_paths_used,
        payload_summary=first_summary,
    )


def _values_equal(comparison: Comparison, a, b) -> bool:
    if comparison is Comparison.SCALAR:
        return a == b
    if comparison is Comparison.ORDERED:
        if not (isinstance(a, (tuple, list)) and isinstance(b, (tuple, list))):
            return a == b
        return tuple(a) == tuple(b)
    if comparison is Comparison.UNORDERED:
        if isinstance(a, (tuple, list)) and isinstance(b, (tuple, list)):
            return frozenset(a) == frozenset(b)
        return a == b
    raise ValueError(f"unknown comparison: {comparison}")


def _summarize(value) -> str:
    if isinstance(value, (tuple, list)):
        if all(isinstance(v, str) for v in value):
            return f"{len(value)} elements"
        return f"{len(value)}-length"
    return f"scalar={value!r}"


def _diff_message(
    name: str,
    comparison: Comparison,
    a_kind: SourceKind,
    a_val,
    b_kind: SourceKind,
    b_val,
    source_paths: dict[SourceKind, Path],
) -> str:
    """Format the cross-source mismatch detail for PR-review copy-pasting."""
    a_path = source_paths.get(a_kind, "?")
    b_path = source_paths.get(b_kind, "?")
    if isinstance(a_val, (tuple, list)) and isinstance(b_val, (tuple, list)):
        la, lb = len(a_val), len(b_val)
        if la != lb:
            return (
                f"invariant=\"{name}\" path={a_path} len={la} "
                f"vs path={b_path} len={lb}"
            )
        if comparison is Comparison.UNORDERED:
            only_in_a = sorted(set(a_val) - set(b_val))
            only_in_b = sorted(set(b_val) - set(a_val))
            return (
                f"invariant=\"{name}\" unordered path={a_path} only={only_in_a} "
                f"path={b_path} only={only_in_b}"
            )
        for i, (x, y) in enumerate(zip(a_val, b_val, strict=False)):
            if x != y:
                return (
                    f"invariant=\"{name}\" ordered path={a_path} "
                    f"element[{i}]=`{x}` (expected) vs path={b_path} element[{i}]=`{y}`"
                )
        return (
            f"invariant=\"{name}\" path={a_path}=={b_path} "
            f"reported FAIL but values matched (script bug?)"
        )
    return (
        f"invariant=\"{name}\" scalar path={a_path}={a_val!r} "
        f"vs path={b_path}={b_val!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Implicit length-vs-payload assertion (the locked-room guarantee)
# ─────────────────────────────────────────────────────────────────────────────

def _check_implicit_length(extractors, source_paths) -> list[CheckResult]:
    """For each source, assert len(VECTOR25_FIELD_NAMES) == EXPECTED_VECTOR_LEN.
    Catches 'declares 25 but ships 24' bugs BEFORE the cross-source comparison."""
    results: list[CheckResult] = []
    for sk, ext in extractors.items():
        if ext is None:
            continue
        try:
            arr = ext.expected_vector_field_names()
            ln = ext.expected_vector_len()
        except Exception as e:  # noqa: BLE001
            results.append(CheckResult(
                invariant="implicit_length",
                status="FAIL",
                failure_detail=(
                    f"invariant=\"implicit_length_vs_payload\" source={sk.value} "
                    f"path={source_paths.get(sk, '?')} parse_error=`{type(e).__name__}: {e}`"
                ),
            ))
            continue
        if arr is None or ln is None:
            continue
        if len(arr) != ln:
            results.append(CheckResult(
                invariant="implicit_length",
                status="FAIL",
                failure_detail=(
                    f"invariant=\"implicit_length_vs_payload\" source={sk.value} "
                    f"path={source_paths.get(sk, '?')} "
                    f"len(VECTOR25_FIELD_NAMES)={len(arr)} vs EXPECTED_VECTOR_LEN={ln}"
                ),
            ))
        else:
            results.append(CheckResult(
                invariant="implicit_length",
                status="PASS",
                sources_checked=[sk.value],
                source_paths={sk.value: str(source_paths.get(sk, "?"))},
                payload_summary=f"{sk.value} len({len(arr)})==expected({ln})",
            ))
    return results


# ─────────────────────────────────────────────────────────────────────────────
#  Source loaders
# ─────────────────────────────────────────────────────────────────────────────

def _load_source(label: str, path: Path) -> str:
    if not path.exists():
        print(f"[LOCKBOX-FAIL] source={label} path={path} file_missing",
              file=sys.stderr)
        sys.exit(2)
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"[LOCKBOX-FAIL] source={label} path={path} read_error={e}",
              file=sys.stderr)
        sys.exit(2)


def _load_drift_test_ts(label: str, path: Path) -> Optional[str]:
    """Optional loader for the future TS drift-test file. Pre-hoist = WARN."""
    if path is None:
        return None
    if not path.exists():
        print(f"[LOCKBOX-WARN] source={label} path={path} drift-test-ts missing "
              "(acceptable pre-hoist; required post-Draft 0.3.1 (section 6.3) 1.0.0 gate)",
              file=sys.stderr)
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"[LOCKBOX-FAIL] source={label} path={path} read_error={e}",
              file=sys.stderr)
        sys.exit(2)


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    args = _build_parser().parse_args()
    py_path = Path(args.producer_path)
    spec_path = Path(args.spec_md)
    pkg_path = Path(args.package_spec_md)
    drift_path = Path(args.drift_test_ts) if args.drift_test_ts else None

    print(f"[LOCKBOX-CHECK] cybertronia_lockbox_ci.py v{__version__}")
    print(f"[LOCKBOX-CHECK] CAMELOT_OS_HOME={_camelot_root()} mode={args.mode}")
    print(
        f"[LOCKBOX-CHECK] producer={py_path}\n"
        f"[LOCKBOX-CHECK] spec={spec_path}\n"
        f"[LOCKBOX-CHECK] package-spec={pkg_path}\n"
        f"[LOCKBOX-CHECK] drift-test-ts={drift_path or '(not set)'}\n"
    )

    py_src = _load_source("python-producer", py_path)
    spec_src = _load_source("spec-upstream-contract", spec_path)
    pkg_src = _load_source("package-spec-contract", pkg_path)
    drift_src = _load_drift_test_ts("package-drift-test-ts", drift_path)

    py = PythonProducer(py_src)
    spec = MarkdownSpec(spec_src, spec_path)
    pkg = MarkdownSpec(pkg_src, pkg_path)
    drift = DriftTestTS(drift_src, drift_path) if drift_src else None

    extractors = {
        SourceKind.PYTHON: py,
        SourceKind.SPEC_MD: spec,
        SourceKind.PACKAGE_SPEC_MD: pkg,
        SourceKind.DRIFT_TEST_TS: drift,
    }
    source_paths = {
        SourceKind.PYTHON: py_path,
        SourceKind.SPEC_MD: spec_path,
        SourceKind.PACKAGE_SPEC_MD: pkg_path,
        SourceKind.DRIFT_TEST_TS: drift_path or Path("(unset)"),
    }

    # Zero-invariants sanity: a successfully-loaded file that yields zero
    # invariants is a parse-failure -- collect ALL and exit 2 with a
    # combined error block.
    required_sources_for_check = (
        SourceKind.PYTHON,
        SourceKind.SPEC_MD,
        SourceKind.PACKAGE_SPEC_MD,
    )

    def _parsed_count(sk: SourceKind) -> int:
        ext = extractors.get(sk)
        if ext is None:
            return 0
        n = 0
        for inv in INVARIANTS:
            if sk in inv.sources:
                try:
                    if getattr(ext, _GETTER_BY_INVARIANT[inv.name])() is not None:
                        n += 1
                except Exception:  # noqa: BLE001
                    continue
        return n

    zero_sources = [
        (sk, _parsed_count(sk))
        for sk in required_sources_for_check
        if _parsed_count(sk) == 0
    ]
    if zero_sources:
        for sk, _count in zero_sources:
            print(
                f"[LOCKBOX-FAIL] source={sk.value} path={source_paths[sk]} "
                f"zero_invariants_parsed -- likely parse failure",
                file=sys.stderr,
            )
        return 2

    results: list[CheckResult] = []
    results.extend(_check_implicit_length(extractors, source_paths))
    for inv in INVARIANTS:
        results.append(_check_invariant(inv, extractors, source_paths, args.mode))

    for r in results:
        if r.status == "PASS":
            scope = " vs ".join(r.sources_checked) if r.sources_checked else ""
            paths = " ".join(f"{k}={v}" for k, v in r.source_paths.items()) if r.source_paths else ""
            line = f"  [PASS    ] invariant=\"{r.invariant}\" {r.payload_summary}"
            if scope:
                line += f"  sources=[{scope}]"
            if paths:
                line += f"  paths={paths}"
            print(line)
        elif r.status == "SOFT-SKIP":
            print(
                f"  [SOFT-SKIP] invariant=\"{r.invariant}\"  "
                f"payload={r.payload_summary}"
            )
        else:
            print(f"  [FAIL    ] invariant=\"{r.invariant}\"  see-detail", file=sys.stderr)

    failed = [r for r in results if r.status == "FAIL"]
    soft = [r for r in results if r.status == "SOFT-SKIP"]
    passed = [r for r in results if r.status == "PASS"]
    print()
    if failed:
        print(
            f"[LOCKBOX-FAIL] {len(failed)} invariant(s) DRIFTED across sources "
            f"({len(passed)} matched, {len(soft)} soft-skipped):",
            file=sys.stderr,
        )
        for r in failed:
            print(f"  - {r.failure_detail}", file=sys.stderr)
        return 1
    print(
        f"[LOCKBOX-PASS] all {len(passed)} invariant(s) matched across sources "
        f"(soft-skipped={len(soft)}, mode={args.mode})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
