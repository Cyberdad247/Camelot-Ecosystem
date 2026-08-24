#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

# test_lockbox_ci.py -- pytest suite for scripts/cybertronia_lockbox_ci.py.
#
# Tests exercise the script as a CLI subprocess (mimics how CI invokes it)
# AND as importable module functions (parser-only paths).
#
# Branch coverage:
#
# 1.  Pass case -- real CAMELOT_OS files align -> exit 0, all invariants PASS
# 2.  Fail case (vector names) -- divergent 25-string array -> exit 1, FAIL message
# 3.  Fail case (length mismatch) -- 26 strings vs EXPECTED_VECTOR_LEN=25 ->
#     implicit-length FAIL fires before cross-source compare
# 4.  Soft-skip case -- invariant declared in only 1 source (Python-only) ->
#     without migration mode -> SOFT-SKIP, exit 0
# 5.  Migration mode case -- same soft-skip scenario with --mode=migration-week-1
#     -> exit 1 because consumer-only invariant soft-skipped in BOTH md sources
# 6.  Env error case -- missing producer file -> exit 2
#
# The "real files align" test depends on the current state of CAMELOT_OS;
# if those files diverge (which they should NOT in a green repo), this test
# will catch it.
#
# Section number references are written as ASCII (e.g. "(section 6.3)") to
# stay parser-safe across Python 3.13 (which rejects non-ASCII identifiers
# though strings tolerate U+00A7); using ASCII avoids any locale-encoding
# flake when the file is rewritten or linted.
"""Module docstring."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "cybertronia_lockbox_ci.py"

# Importable target -- load the script's source as a module without executing
# main(). Same pattern as tests/conftest.py boot.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import cybertronia_lockbox_ci as lbx  # type: ignore  # noqa: E402

# -----------------------------------------------------------------------------
#  helper builders for fixture sources
# -----------------------------------------------------------------------------

PY_BASE = '''\
"""fixture"""
SHARED_TYPES = tuple[str, ...]
VECTOR25_FIELD_NAMES: tuple[str, ...] = ({names})
EXPECTED_VECTOR_LEN: int = {declared_len}
LAYERS: tuple[str, ...] = {layers}
KIND_TO_INDEX: dict[str, int] = {kinds_dict}
SCHEMA_VERSION_SNAPSHOT: str = "cybertronia.snapshot/v1"
'''

SPEC_BASE = '''\
# spec.md fixture (Draft 0.3.1)
```typescript
const EXPECTED_LAYERS = [
  {layers_md}
] as const;
const EXPECTED_KINDS = [
  {kinds_md}
] as const;
const EXPECTED_VECTOR_FIELD_NAMES = [
  {vector_names_md}
] as const;
const EXPECTED_VECTOR_LEN = {declared_len} as const;
const EXPECTED_NODE_STRIDE_FLOATS = 10 as const;
const EXPECTED_EDGE_STRIDE_FLOATS = 8 as const;
const EXPECTED_RELATIONS = [
  {relations}
] as const;
const EXPECTED_PERF_PROFILES = [
  {perf}
] as const;
SCHEMA_VERSION_SNAPSHOT: spec literal = "cybertronia.snapshot/v1";
```
'''

PKG_BASE = '''\
# package-spec.md fixture (Draft 0.1.1) -- single-line TS literal style
```typescript
const EXPECTED_LAYERS = [{layers_md}] as const;
const EXPECTED_KINDS = [{kinds_md}] as const;
const EXPECTED_VECTOR_FIELD_NAMES = [{vector_names_md}] as const;
const EXPECTED_VECTOR_LEN = {declared_len} as const;
const EXPECTED_NODE_STRIDE_FLOATS = 10 as const;
const EXPECTED_EDGE_STRIDE_FLOATS = 8 as const;
const EXPECTED_RELATIONS = [{relations}] as const;
const EXPECTED_PERF_PROFILES = [{perf}] as const;
```
'''


def _make_py_text(vector_names: list[str], declared_len: int = 25) -> str:
    names_py = ", ".join(f'"{n}"' for n in vector_names)
    layers_py = '("bin", "control_plane", "02_FORGE", "03_VAULT", "runtime")'
    kinds_dict_py = '{"file": 0, "dir": 1, "runtime_service": 2}'
    return PY_BASE.format(
        names=names_py, declared_len=declared_len,
        layers=layers_py, kinds_dict=kinds_dict_py,
    )


def _make_spec_text(vector_names: list[str], declared_len: int = 25) -> str:
    return SPEC_BASE.format(
        layers_md='\n  '.join(f'"{x}"' for x in ["bin", "control_plane", "02_FORGE", "03_VAULT", "runtime"]),
        kinds_md=', '.join(f'"{x}"' for x in ["file", "dir", "runtime_service"]),
        vector_names_md="\n  ".join(f'"{n}"' for n in vector_names),
        declared_len=declared_len,
        relations=', '.join(f'"{x}"' for x in ["imports", "wires"]),
        perf=', '.join(f'"{x}"' for x in ["high", "mid"]),
    )


def _make_pkg_text(vector_names: list[str], declared_len: int = 25) -> str:
    return PKG_BASE.format(
        layers_md=", ".join(f'"{x}"' for x in ["bin", "control_plane", "02_FORGE", "03_VAULT", "runtime"]),
        kinds_md=", ".join(f'"{x}"' for x in ["file", "dir", "runtime_service"]),
        vector_names_md=", ".join(f'"{n}"' for n in vector_names),
        declared_len=declared_len,
        relations=", ".join(f'"{x}"' for x in ["imports", "wires"]),
        perf=", ".join(f'"{x}"' for x in ["high", "mid"]),
    )


def _run_cli(tmp_path: Path, py_text: str, spec_text: str, pkg_text: str,
             mode: str = "default") -> subprocess.CompletedProcess:
    py_p = tmp_path / "producer.py"
    spec_p = tmp_path / "spec.md"
    pkg_p = tmp_path / "pkg.md"
    py_p.write_text(py_text, encoding="utf-8")
    spec_p.write_text(spec_text, encoding="utf-8")
    pkg_p.write_text(pkg_text, encoding="utf-8")

    cmd = [
        sys.executable, str(SCRIPT_PATH),
        "--producer-path", str(py_p),
        "--spec-md", str(spec_p),
        "--package-spec-md", str(pkg_p),
        "--mode", mode,
    ]
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=30,
    )


# -----------------------------------------------------------------------------
#  Tests
# -----------------------------------------------------------------------------

CORRECT_25 = [
    "layer", "type", "path depth", "size", "file count",
    "recency", "churn", "cpu cost", "memory cost", "storage cost",
    "runtime state", "health", "exposure", "in_degree", "out_degree",
    "centrality", "betweenness", "pagerank", "community", "criticality",
    "sensitivity", "mutability", "provenance", "sync state", "resource pressure",
]


def test_pass_case_all_sources_aligned(tmp_path: Path):
    """Real-style fixture: all 3 sources agree -> exit 0, all invariants PASS."""
    proc = _run_cli(tmp_path, _make_py_text(CORRECT_25), _make_spec_text(CORRECT_25), _make_pkg_text(CORRECT_25))
    assert proc.returncode == 0, f"unexpected fail: stdout={proc.stdout}\nstderr={proc.stderr}"
    assert "[LOCKBOX-PASS]" in proc.stdout
    assert "[LOCKBOX-FAIL]" not in proc.stdout


def test_fail_case_vector_names_diverge(tmp_path: Path):
    """Producer has storage cost; spec has storage_costs (typo) -> FAIL."""
    divergent = list(CORRECT_25)
    divergent[9] = "storage_costs"  # one-element typo
    proc = _run_cli(
        tmp_path,
        _make_py_text(CORRECT_25),       # correct
        _make_spec_text(divergent),      # divergent
        _make_pkg_text(CORRECT_25),
    )
    assert proc.returncode == 1, f"expected exit-1 FAIL but got {proc.returncode}\nstderr={proc.stderr}"
    assert "[LOCKBOX-FAIL]" in proc.stderr
    assert "expected_vector_field_names" in proc.stderr
    assert "element[9]" in proc.stderr
    assert "storage_costs" in proc.stderr


def test_fail_case_length_mismatch(tmp_path: Path):
    """Producer declares len=25 but ships only 24 strings -> implicit-length FAIL."""
    proc = _run_cli(
        tmp_path,
        _make_py_text(CORRECT_25[:24]),   # 24 elements (one short)
        _make_spec_text(CORRECT_25),
        _make_pkg_text(CORRECT_25),
    )
    assert proc.returncode == 1
    assert "implicit_length" in proc.stderr
    assert "len(VECTOR25_FIELD_NAMES)=24" in proc.stderr
    assert "EXPECTED_VECTOR_LEN=25" in proc.stderr


def test_soft_skip_case_python_only_invariant(tmp_path: Path):
    """Producer emits only its data-side invariants; the spec lacks the snapshot marker."""
    proc = _run_cli(
        tmp_path,
        _make_py_text(CORRECT_25),
        _make_spec_text(CORRECT_25).replace(
            'SCHEMA_VERSION_SNAPSHOT: spec literal = "cybertronia.snapshot/v1";',
            ""
        ),
        _make_pkg_text(CORRECT_25),
    )
    # Without migration mode, missing producer-only invariant = SOFT-SKIP = exit 0
    assert proc.returncode == 0
    assert "[LOCKBOX-PASS]" in proc.stdout
    assert "soft-skipped=" in proc.stdout


def test_migration_mode_consumer_only_present(tmp_path: Path):
    """--mode=migration-week-1: consumer-only invariants present in BOTH md
    sources -> exit 0 (the migration-week-1 contract holds)."""
    proc = _run_cli(
        tmp_path, _make_py_text(CORRECT_25), _make_spec_text(CORRECT_25),
        _make_pkg_text(CORRECT_25), mode="migration-week-1",
    )
    assert proc.returncode == 0


def test_migration_mode_consumer_only_missing(tmp_path: Path):
    """--mode=migration-week-1 with a consumer-only invariant absent from ONE
    md source -> FAIL exit 1 (Draft 0.3.1 section6.3 binary-window rule).

    The binary-window rule fires when at least one md source declares the
    invariant but the other does not (partial declaration). Removing it from
    BOTH sources is a SOFT-SKIP ("no source declares this invariant") and is
    covered by test_soft_skip_case_python_only_invariant."""
    py_text = _make_py_text(CORRECT_25)
    spec_text = _make_spec_text(CORRECT_25)
    pkg_text = _make_pkg_text(CORRECT_25).replace(
        'const EXPECTED_RELATIONS = ["imports", "wires"] as const;\n', ""
    )
    proc = _run_cli(tmp_path, py_text, spec_text, pkg_text, mode="migration-week-1")
    assert proc.returncode == 1
    assert "expected_relations" in proc.stderr
    assert "migration-week-1" in proc.stderr


def test_env_error_missing_file(tmp_path: Path):
    """Missing producer file -> exit 2 (env error)."""
    cmd = [
        sys.executable, str(SCRIPT_PATH),
        "--producer-path", str(tmp_path / "does_not_exist.py"),
        "--spec-md", str(tmp_path / "spec.md"),
        "--package-spec-md", str(tmp_path / "pkg.md"),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    assert proc.returncode == 2
    assert "file_missing" in proc.stderr


def test_python_producer_parser_handles_kinds_dict_keys(tmp_path: Path):
    """Verify PythonProducer.get_dict_keys_sorted returns a sorted tuple of keys."""
    py = lbx.PythonProducer(_make_py_text(CORRECT_25))
    keys = py.expected_kinds_or_kind_index()
    assert keys is not None
    assert keys == ("dir", "file", "runtime_service")  # alphabetical, no 'runtime_service' typo


def test_markdown_parser_handles_multiline_array(tmp_path: Path):
    """spec.md uses multiline arrays; spec extractor must handle them."""
    md = lbx.MarkdownSpec(_make_spec_text(CORRECT_25))
    assert md.expected_vector_field_names() == tuple(CORRECT_25)
    assert md.expected_vector_len() == 25


def test_markdown_parser_handles_singleline_array(tmp_path: Path):
    """package-spec.md uses single-line arrays; the same parser handles both."""
    md = lbx.MarkdownSpec(_make_pkg_text(CORRECT_25))
    assert md.expected_vector_field_names() == tuple(CORRECT_25)
    assert md.expected_vector_len() == 25


# -----------------------------------------------------------------------------
#  Real-files integration test (CI-anchor mode)
# -----------------------------------------------------------------------------

@pytest.mark.skipif(
    not (REPO_ROOT / "control_plane" / "cybertronia_compile.py").exists(),
    reason="CAMELOT_OS root not found; skipping real-files integration test",
)
def test_kinds_set_compare_passes_with_positional_divergence(tmp_path: Path):
    """KINDS is unordered (frozenset compare). spec.md lists
    ['runtime_service','file','dir'] (declaration order); pkg.md lists
    ['file','dir','runtime_service'] (alphabetical). Positional mismatch
    would fail; set-compare passes.

    The Python producer fixture has {'file', 'dir', 'runtime_service'}
    so all three sources align on the SET of kinds."""
    py_text = PY_BASE.format(
        names=', '.join(f'"{n}"' for n in CORRECT_25),
        declared_len=25,
        layers='("bin", "control_plane", "02_FORGE", "03_VAULT", "runtime")',
        kinds_dict='{"file": 0, "dir": 1, "runtime_service": 2}',
    )
    spec_text = SPEC_BASE.format(
        layers_md='\n  '.join(f'"{x}"' for x in ["bin", "control_plane", "02_FORGE", "03_VAULT", "runtime"]),
        kinds_md='"runtime_service", "file", "dir"',  # positional divergence!
        vector_names_md="\n  ".join(f'"{n}"' for n in CORRECT_25),
        declared_len=25,
        relations=', '.join(f'"{x}"' for x in ["imports", "wires"]),
        perf=', '.join(f'"{x}"' for x in ["high", "mid"]),
    )
    pkg_text = _make_pkg_text(CORRECT_25)  # has correct kinds order
    proc = _run_cli(tmp_path, py_text, spec_text, pkg_text)
    assert proc.returncode == 0, (
        f"set-compare should pass despite positional divergence; "
        f"got exit={proc.returncode} stderr={proc.stderr}"
    )
    # Make sure it specifically checked kinds invariant
    assert 'expected_kinds_or_kind_index' in proc.stdout


def test_fail_case_kinds_set_divergence(tmp_path: Path):
    """spec.md has foo as a kind; pkg.md has runtime_service; set-compare
    detects foo present in spec (equal lengths so the UNORDERED path fires,
    not the length-mismatch path)."""
    py_text = PY_BASE.format(
        names=', '.join(f'"{n}"' for n in CORRECT_25),
        declared_len=25,
        layers='("bin", "control_plane", "02_FORGE", "03_VAULT", "runtime")',
        kinds_dict='{"file": 0, "dir": 1, "runtime_service": 2}',
    )
    spec_text = SPEC_BASE.format(
        layers_md='\n  '.join(f'"{x}"' for x in ["bin", "control_plane", "02_FORGE", "03_VAULT", "runtime"]),
        kinds_md='"file", "dir", "foo"',  # same length as producer/pkg; 'foo' diverges
        vector_names_md="\n  ".join(f'"{n}"' for n in CORRECT_25),
        declared_len=25,
        relations=', '.join(f'"{x}"' for x in ["imports", "wires"]),
        perf=', '.join(f'"{x}"' for x in ["high", "mid"]),
    )
    pkg_text = _make_pkg_text(CORRECT_25)
    proc = _run_cli(tmp_path, py_text, spec_text, pkg_text)
    assert proc.returncode == 1
    assert 'expected_kinds_or_kind_index' in proc.stderr
    # Set-compare path -> "only=" message
    assert "only=" in proc.stderr or "unordered" in proc.stderr


def test_fail_case_schema_version_divergence(tmp_path: Path):
    """Producer pins 'cybertronia.snapshot/v1'; spec.md echoes 'cybertronia.snapshot/v2'.
    Failure fires with file path."""
    py_text = PY_BASE.format(
        names=', '.join(f'"{n}"' for n in CORRECT_25),
        declared_len=25,
        layers='("bin", "control_plane", "02_FORGE", "03_VAULT", "runtime")',
        kinds_dict='{"file": 0, "dir": 1}',
    )
    spec_text = SPEC_BASE.format(
        layers_md='\n  '.join(f'"{x}"' for x in ["bin", "control_plane", "02_FORGE", "03_VAULT", "runtime"]),
        kinds_md='"file", "dir"',
        vector_names_md="\n  ".join(f'"{n}"' for n in CORRECT_25),
        declared_len=25,
        relations=', '.join(f'"{x}"' for x in ["imports", "wires"]),
        perf=', '.join(f'"{x}"' for x in ["high", "mid"]),
    ).replace(
        'SCHEMA_VERSION_SNAPSHOT: spec literal = "cybertronia.snapshot/v1";',
        'schema_version: "cybertronia.snapshot/v2";',
    )
    pkg_text = _make_pkg_text(CORRECT_25)
    proc = _run_cli(tmp_path, py_text, spec_text, pkg_text)
    assert proc.returncode == 1
    assert 'schema_version_snapshot' in proc.stderr
    # Diff message should include the FILE PATH (drift-risk F fix):
    assert 'path=' in proc.stderr


def test_drift_test_ts_missing_is_warn_only(tmp_path: Path):
    """--drift-test-ts absent (or arg unused) is WARN, not FAIL,
    pre-Draft 0.3.1 section6.3 1.0.0 gate."""
    py_text = _make_py_text(CORRECT_25)
    spec_text = _make_spec_text(CORRECT_25)
    pkg_text = _make_pkg_text(CORRECT_25)
    py_p = tmp_path / "producer.py"; py_p.write_text(py_text)
    spec_p = tmp_path / "spec.md"; spec_p.write_text(spec_text)
    pkg_p = tmp_path / "pkg.md"; pkg_p.write_text(pkg_text)
    # Pass --drift-test-ts pointing at a non-existent file
    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH),
         "--producer-path", str(py_p),
         "--spec-md", str(spec_p),
         "--package-spec-md", str(pkg_p),
         "--drift-test-ts", str(tmp_path / "does_not_exist.ts")],
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, (
        f"missing drift-test-ts should be WARN not FAIL; "
        f"got exit={proc.returncode} stderr={proc.stderr}"
    )
    assert 'drift-test-ts missing' in proc.stderr
    assert 'acceptable pre-hoist' in proc.stderr


def test_exit2_on_zero_invariants_parsed(tmp_path: Path):
    """Producer file exists but has zero EXPECTED_* constants (e.g. someone
    accidentally deleted the lockbox by emptying the file but not deleting it)."""
    py_text = '"""empty stub with no invariants declared"""\n'
    spec_text = _make_spec_text(CORRECT_25)
    pkg_text = _make_pkg_text(CORRECT_25)
    py_p = tmp_path / "producer.py"; py_p.write_text(py_text)
    spec_p = tmp_path / "spec.md"; spec_p.write_text(spec_text)
    pkg_p = tmp_path / "pkg.md"; pkg_p.write_text(pkg_text)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH),
         "--producer-path", str(py_p),
         "--spec-md", str(spec_p),
         "--package-spec-md", str(pkg_p)],
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 2, (
        f"empty producer should exit 2 (parse sanity); "
        f"got exit={proc.returncode} stderr={proc.stderr}"
    )
    assert 'zero_invariants_parsed' in proc.stderr


@pytest.mark.skipif(
    not (REPO_ROOT / "control_plane" / "cybertronia_compile.py").exists(),
    reason="CAMELOT_OS root not found; skipping real-files integration test",
)
def test_real_files_integration(tmp_path: Path):
    proc = subprocess.run(
        [
            sys.executable, str(SCRIPT_PATH),
            "--producer-path",       str(REPO_ROOT / "control_plane" / "cybertronia_compile.py"),
            "--spec-md",              str(REPO_ROOT / "docs" / "cybertronia-graph-ui-spec.md"),
            "--package-spec-md",     str(REPO_ROOT / "docs" / "cybertronia-graph-ui-package-spec.md"),
        ],
        capture_output=True, text=True, timeout=30,
    )
    if proc.returncode != 0:
        pytest.fail(
            f"Real-files integration test FAILED -- migration-window lockbox drifted.\n"
            f"exit={proc.returncode}\n"
            f"stdout={proc.stdout[:2000]}\n"
            f"stderr={proc.stderr[:2000]}"
        )
