# VFS Preflight Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the VFS scaffold under `vfs/*.md` from prose to an executable gate that runs at boot (`bin/awaken.py` stage 0) and emits per-check JSON evidence artifacts.

**Architecture:** Augmentation layer above `v1000-EXCALIBUR-A`. A new `control_plane.preflight` package loads a YAML check catalog from `vfs/checks/*.yaml`, executes each check in `sequence` order, asserts evidence class via the existing `anya_gate.triage()`, and writes per-check + run-manifest JSON to `03_VAULT/runtime_state/preflight/<UTC>/`. First-ever run is advisor-mode (proceeds with REJECTED findings surfaced); subsequently strict (REJECTED halts the boot). No sovereign escape hatch — strict halts are hard halts.

**Tech Stack:** Python 3.11+ stdlib (`subprocess`, `hashlib`, `dataclasses`, `pathlib`, `argparse`), `PyYAML` (already in repo), `pytest` (already used in repo), existing `control_plane.anya_gate` for evidence class assertion, existing `bin/awaken.py` shell script for boot wiring.

**Companion docs:**
- Spec: `docs/architecture/VFS_PREFLIGHT_DESIGN.md`
- ADR: `docs/adr/0006-vfs-preflight-strict-mode.md`

## Global Constraints

(Copied verbatim from spec §2 + §6 + AGENTS.md; every task's requirements implicitly include this section.)

- **Scope:** Slice #1 only. Do NOT modify `runic_router.py`, `cartridges/`, `01_KERNEL/`, `04_KINETIC/`, `squires/`, or any of `anya_gate.py` / `soul_oversight.py` / `factory_lane.py` / `firnflow.py` — reuse them.
- **First-run advisor → strict mode.** Default behavior on a fresh system; graduation triggered by `_graduated.flag` after the first all-CONFIRMED run.
- **No sovereign escape hatch.** `runner.py` must explicitly raise on `CAMELOT_SKIP_PREFLIGHT=1`, `--skip-sovereign`, or any `--force` flag.
- **Evidence class is CONFIRMED only.** Anything else is REJECTED. Reuse `anya_gate.triage()`; do not write a new classifier.
- **Catalog schema:** `sequence (int, unique), id, display_name, command_type, command (list[str]), timeout_s, retry (0-2), expected_evidence_class, hitl_on_fail, remediation_hint`. Sequence stride 10 (010, 020, …, 080).
- **8 checks, in this order:** 010 `env_dependency_match`, 020 `foss_validation_constraints`, 030 `northstar_brief_currency`, 040 `port_readiness_scan`, 050 `provenance_ledger_writable`, 060 `tool_registry_presence`, 070 `vfs_scaffold_integrity`, 080 `lattice_yaml_consistency`.
- **Run-target:** total runtime ≤ 2s p95; each check ≤ 30s default timeout.
- **Idempotency:** no overwrites; each run gets its own UTC-stamped dir; no PROVENANCE_LEDGER.md writes from preflight itself.
- **No destructive shell actions** without explicit sovereign approval (per AGENTS.md).
- **Frequent commits.** One commit per task minimum. Commit message style: `feat(preflight): …`, `test(preflight): …`, `docs(preflight): …` matching the recent commit style in `git log --oneline | head -20`.

---

## File Structure (final state)

```
vfs/
  checks/
    _README.md                  # YAML field reference, authoring rules
    010_env_dependency_match.yaml
    020_foss_validation_constraints.yaml
    030_northstar_brief_currency.yaml
    040_port_readiness_scan.yaml
    050_provenance_ledger_writable.yaml
    060_tool_registry_presence.yaml
    070_vfs_scaffold_integrity.yaml
    080_lattice_yaml_consistency.yaml
control_plane/
  preflight/
    __init__.py
    __main__.py                 # CLI: --run, --test, --list, --graduate
    runner.py                   # load YAML → execute → emit JSON
    state.py                    # graduation flag (advisor→strict)
    schemas.py                  # dataclass + YAML parser
    probes/
      __init__.py
      ports.py                  # TCP port probe (used by check 040)
      exec.py                   # subprocess timeout wrapper (used by all)
      file_age.py               # used by check 030
      file_present.py           # used by check 050 / 070
      license_header.py         # used by check 020
      import_smoke.py           # used by check 060
      yaml_parses.py            # used by check 080
        # (NOT 4GL: one probe per check that needs reusable logic; checks
        # 010 and 090+ can inline their logic)
tests/
  preflight/
    __init__.py
    conftest.py                 # tmp_vfs_catalog fixture, tmp_run_dir fixture
    test_state.py               # Task 1
    test_schemas.py             # Task 1
    test_runner_foundation.py   # Task 2
    test_checks_simple.py       # Task 3 (4 simple checks)
    test_checks_hitl.py         # Task 4 (3 hitl checks)
    test_check_lattice.py       # Task 5
    test_runner_integration.py  # Task 6
    test_cli.py                 # Task 7
    test_awaken_stage0.py       # Task 8 (folded E2E per spec §7 refinement)
bin/
  awaken.py                     # MODIFY: insert stage 0 before stage 1
docs/
  architecture/VFS_PREFLIGHT_DESIGN.md      # already written
  adr/0006-vfs-preflight-strict-mode.md     # already written
  superpowers/plans/2026-08-13-vfs-preflight.md  # this file
```

Each file has one responsibility. Cross-file communication is via the
dataclasses in `schemas.py`. Tests live next to the code they cover.

---

## Task 1: Foundations — state.py + schemas.py + test scaffolding

**Files:**
- Create: `control_plane/preflight/__init__.py`
- Create: `control_plane/preflight/__main__.py` (stub raises RuntimeError — Task 7 wires it)
- Create: `control_plane/preflight/state.py`
- Create: `control_plane/preflight/schemas.py`
- Create: `tests/preflight/__init__.py`
- Create: `tests/preflight/conftest.py`
- Create: `tests/preflight/test_state.py`
- Create: `tests/preflight/test_schemas.py`

**Interfaces (consumed by later tasks):**

- `schemas.CheckSpec` — `@dataclass` with fields:
  `sequence: int, id: str, display_name: str, command_type: Literal["python_module","shell"], command: list[str], timeout_s: int = 30, retry: int = 0, expected_evidence_class: Literal["CONFIRMED"] = "CONFIRMED", hitl_on_fail: bool = False, remediation_hint: str | None = None`
- `schemas.RunManifest` — `@dataclass` with JSON-serializable fields per spec §5.4
- `schemas.CheckResult` — `@dataclass` with fields per spec §5.3, including `evidence_class`, `halt_decision`, `advisor_finding`, `rejection_reasons`
- `state.GraduationFlag` — class with `path() → Path`, `is_strict() → bool`, `graduate() → None`, `revoke() → None`

- [ ] **Step 1: Write failing test for `state.GraduationFlag` first-time behavior**

Create `tests/preflight/test_state.py`:

```python
import pytest
from pathlib import Path
from control_plane.preflight import state


def test_graduation_flag_strict_by_default_when_present(tmp_path: Path):
    flag = state.GraduationFlag(tmp_path / "preflight_root")
    (tmp_path / "preflight_root").mkdir()
    flag_path = flag.path()
    flag_path.parent.mkdir(parents=True, exist_ok=True)
    flag_path.touch()  # simulate post-first-run flag present
    assert flag.is_strict() is True


def test_graduation_flag_advisor_when_missing(tmp_path: Path):
    flag = state.GraduationFlag(tmp_path / "preflight_root")
    assert flag.is_strict() is False


def test_graduation_flag_graduate_writes_atomic(tmp_path: Path):
    flag = state.GraduationFlag(tmp_path / "preflight_root")
    flag.graduate()
    assert flag.is_strict() is True
    assert flag.path().read_text() == "vfs-preflight-strict-mode\n"


def test_graduation_flag_revoke_returns_to_advisor(tmp_path: Path):
    flag = state.GraduationFlag(tmp_path / "preflight_root")
    flag.graduate()
    flag.revoke()
    assert flag.is_strict() is False
```

Add `tests/preflight/__init__.py` (empty) and `tests/preflight/conftest.py`:

```python
# conftest.py
import pytest
from pathlib import Path
from textwrap import dedent


@pytest.fixture
def tmp_vfs_root(tmp_path: Path) -> Path:
    """Create a tmp dir layout mirroring vfs/ with one synthetic check YAML."""
    root = tmp_path / "vfs"
    (root / "checks").mkdir(parents=True)
    (root / "preflight.md").write_text("---\nid: preflight\ntitle: Swarm Init Manifest\n---\n# placeholder\n")
    (root / "systeminstructions.md").write_text("---\nid: systeminstructions\n---\n# placeholder\n")
    (root / "skills.md").write_text("---\nid: skills\n---\n# placeholder\n")
    (root / "rosters.md").write_text("---\nid: rosters\n---\n# placeholder\n")
    (root / "protocols.md").write_text("---\nid: protocols\n---\n# placeholder\n")
    (root / "checks" / "_README.md").write_text("# catalog authoring guide\n")
    (root / "checks" / "010_synthetic_pass.yaml").write_text(dedent('''
        sequence: 10
        id: synthetic_pass
        display_name: Synthetic Always Passing
        command_type: shell
        command: ["python", "-c", "print('ok')"]
        timeout_s: 5
        retry: 0
        expected_evidence_class: CONFIRMED
        hitl_on_fail: false
        remediation_hint: null
    ''').lstrip())
    return root


@pytest.fixture
def tmp_preflight_root(tmp_path: Path) -> Path:
    root = tmp_path / "preflight_root"
    root.mkdir()
    return root
```

- [ ] **Step 2: Run test_state.py and confirm 4 FAIL with ImportError**

Run: `pytest tests/preflight/test_state.py -v`
Expected: 4 errors of the form `ImportError: No module named 'control_plane.preflight'`.

- [ ] **Step 3: Implement `state.py`**

Create `control_plane/preflight/__init__.py`:

```python
"""VFS Preflight vertical slice (slice #1 of 5, see docs/architecture/VFS_PREFLIGHT_DESIGN.md §9)."""
from . import state, schemas  # noqa: F401
__version__ = "0.1.0"
```

Create `control_plane/preflight/__main__.py` (Task 7 fills this; for now it must fail loudly with runtime guidance):

```python
"""CLI entry point — implemented in Task 7."""
if __name__ == "__main__":  # pragma: no cover
    raise RuntimeError(
        "control_plane.preflight CLI is not implemented yet. "
        "See docs/superpowers/plans/2026-08-13-vfs-preflight.md Task 7."
    )
```

Create `control_plane/preflight/state.py`:

```python
"""Graduation flag: first-run advisor → strict-mode state."""
from __future__ import annotations
from pathlib import Path

FLAG_FILENAME = "_graduated.flag"
FLAG_CONTENTS = "vfs-preflight-strict-mode\n"


class GraduationFlag:
    """Tracks whether preflight has graduated from advisor to strict mode.

    Path is <root>/_graduated.flag per spec §6.2.
    """

    def __init__(self, root: Path | str):
        self.root = Path(root)

    def path(self) -> Path:
        return self.root / "preflight" / FLAG_FILENAME

    def is_strict(self) -> bool:
        return self.path().exists()

    def graduate(self) -> None:
        """Promote advisor → strict on first successful run. Atomic write."""
        target = self.path()
        target.parent.mkdir(parents=True, exist_ok=True)
        # Use exclusive create via temp + replace to be atomic on POSIX & nt.
        tmp = target.with_suffix(".flag.tmp")
        tmp.write_text(FLAG_CONTENTS)
        try:
            tmp.replace(target)
        except OSError:
            tmp.unlink(missing_ok=True)
            raise

    def revoke(self) -> None:
        """Manual rollback to advisor (operator decision, document in _manifest.json)."""
        try:
            self.path().unlink()
        except FileNotFoundError:
            pass
```

- [ ] **Step 4: Run test_state.py → expect PASS**

Run: `pytest tests/preflight/test_state.py -v`
Expected: 4 passed.

- [ ] **Step 5: Write failing test for `schemas.py`**

Create `tests/preflight/test_schemas.py`:

```python
import pytest
from pathlib import Path
from textwrap import dedent
from control_plane.preflight import schemas


GOOD_YAML = dedent('''
    sequence: 10
    id: synthetic
    display_name: Synthetic
    command_type: python_module
    command: ["control_plane.preflight.probes.exec", "--echo", "ok"]
    timeout_s: 5
    retry: 0
    expected_evidence_class: CONFIRMED
    hitl_on_fail: false
    remediation_hint: "do a thing"
''').lstrip()


def test_checkspec_parses_clean_yaml():
    spec = schemas.CheckSpec.from_yaml_text(GOOD_YAML)
    assert spec.sequence == 10
    assert spec.id == "synthetic"
    assert spec.command_type == "python_module"
    assert spec.command == ["control_plane.preflight.probes.exec", "--echo", "ok"]
    assert spec.timeout_s == 5
    assert spec.expected_evidence_class == "CONFIRMED"


@pytest.mark.parametrize("bad_field,value", [
    ("sequence", "ten"),                # not int
    ("command_type", "ruby"),            # not in Literal
    ("expected_evidence_class", "ASPIRATIONAL"),  # outside CONFIRMED only
    ("retry", 5),                        # out of 0..2
    ("timeout_s", -1),                   # negative
])
def test_checkspec_rejects_invalid_yaml(bad_field, value):
    bad = GOOD_YAML.replace(f"{bad_field}:", f"{bad_field}: {value}", 1)
    # Note: the bad_field's default quoting might break YAML; we use : for shape-change.
    with pytest.raises(schemas.CatalogParseError):
        schemas.CheckSpec.from_yaml_text(bad)


def test_checkspec_command_must_be_list_of_str_for_shell():
    bad = GOOD_YAML.replace('command_type: python_module', 'command_type: shell').replace(
        'command: ["control_plane.preflight.probes.exec", "--echo", "ok"]',
        'command: "echo ok"',
    )
    with pytest.raises(schemas.CatalogParseError):
        schemas.CheckSpec.from_yaml_text(bad)
```

- [ ] **Step 6: Run test_schemas.py → expect FAIL with ImportError on schemas**

Run: `pytest tests/preflight/test_schemas.py -v`
Expected: ImportError on `control_plane.preflight.schemas`.

- [ ] **Step 7: Implement `schemas.py`**

Create `control_plane/preflight/schemas.py`:

```python
"""Dataclasses + YAML parser for the preflight catalog and run artifacts."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal, Optional
from datetime import datetime, timezone
import yaml


EvidenceClass = Literal["CONFIRMED", "REJECTED"]
CommandType = Literal["python_module", "shell"]
HaltDecision = Literal["continue", "block_boot", "await_hitl"]
HitlTier = Literal["AUTO", "PROMPT", "HUMAN_GATE"]


class CatalogParseError(ValueError):
    """Catalog YAML did not validate against the schema."""


@dataclass(frozen=True)
class CheckSpec:
    sequence: int
    id: str
    display_name: str
    command_type: CommandType
    command: list[str]
    timeout_s: int = 30
    retry: int = 0
    expected_evidence_class: EvidenceClass = "CONFIRMED"
    hitl_on_fail: bool = False
    remediation_hint: Optional[str] = None

    @classmethod
    def from_yaml_text(cls, text: str) -> "CheckSpec":
        try:
            raw = yaml.safe_load(text)
        except yaml.YAMLError as e:
            raise CatalogParseError(f"yaml parse error: {e}") from e
        if not isinstance(raw, dict):
            raise CatalogParseError("check yaml must be a mapping")
        # Required fields first
        for f in ("sequence", "id", "display_name", "command_type", "command"):
            if f not in raw:
                raise CatalogParseError(f"missing required field '{f}'")
        # Sequence must be a positive int
        seq = raw["sequence"]
        if not isinstance(seq, int) or isinstance(seq, bool) or seq <= 0:
            raise CatalogParseError(f"sequence must be a positive int, got {seq!r}")
        # command_type must be in literal
        if raw["command_type"] not in ("python_module", "shell"):
            raise CatalogParseError(
                f"command_type must be 'python_module' or 'shell', got {raw['command_type']!r}"
            )
        # command must be list[str]
        cmd = raw["command"]
        if not isinstance(cmd, list) or not all(isinstance(c, str) for c in cmd):
            raise CatalogParseError("command must be a list of strings")
        # evidence class — only CONFIRMED accepted
        ec = raw.get("expected_evidence_class", "CONFIRMED")
        if ec != "CONFIRMED":
            raise CatalogParseError(
                f"expected_evidence_class must be 'CONFIRMED' (CONFIRMED-only gate), got {ec!r}"
            )
        # retry bounds
        retry = int(raw.get("retry", 0))
        if retry < 0 or retry > 2:
            raise CatalogParseError(f"retry must be 0..2, got {retry}")
        # timeout_s bounds
        timeout_s = int(raw.get("timeout_s", 30))
        if timeout_s <= 0:
            raise CatalogParseError(f"timeout_s must be positive, got {timeout_s}")
        return cls(
            sequence=seq,
            id=str(raw["id"]),
            display_name=str(raw["display_name"]),
            command_type=raw["command_type"],
            command=cmd,
            timeout_s=timeout_s,
            retry=retry,
            expected_evidence_class=ec,
            hitl_on_fail=bool(raw.get("hitl_on_fail", False)),
            remediation_hint=raw.get("remediation_hint"),
        )


@dataclass
class CheckResult:
    schema: Literal["camelot.preflight.check/v1"] = "camelot.preflight.check/v1"
    run_id: str = ""
    check_id: str = ""
    display_name: str = ""
    command_observed: list[str] = field(default_factory=list)
    command_raw: str = ""
    exit_code: int = -1
    started_at: str = ""
    duration_ms: int = 0
    stdout_excerpt: str = ""
    stderr_excerpt: str = ""
    evidence_class: EvidenceClass = "REJECTED"
    evidence_assertion: dict = field(default_factory=dict)
    hitl_required: bool = False
    halt_decision: HaltDecision = "continue"
    advisor_finding: bool = False
    rejection_reasons: list[str] = field(default_factory=list)
    remediation_hint: Optional[str] = None
    artifact_path: str = ""

    def to_json_dict(self) -> dict:
        return asdict(self)


@dataclass
class RunManifest:
    schema: Literal["camelot.preflight.run/v1"] = "camelot.preflight.run/v1"
    run_id: str = ""
    started_at: str = ""
    ended_at: str = ""
    total_ms: int = 0
    checks_total: int = 0
    checks_passed: int = 0
    checks_failed: int = 0
    checks_skipped: int = 0
    halted_at_check: Optional[str] = None
    halt_decision: HaltDecision = "continue"
    scene_hash: str = ""
    catalog_hash: str = ""
    first_run: bool = True
    graduated_to_strict: bool = False

    def to_json_dict(self) -> dict:
        return asdict(self)


def utc_now_iso() -> str:
    """ISO-8601 UTC timestamp with microseconds and Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def compute_catalog_hash(checks_root: Path) -> str:
    """SHA-256 of all *.yaml files concatenated in sequence order."""
    import hashlib
    yaml_files = sorted(checks_root.glob("*.yaml"))
    h = hashlib.sha256()
    for f in yaml_files:
        h.update(f.read_bytes())
    return h.hexdigest()
```

- [ ] **Step 8: Run test_schemas.py → expect PASS (5 tests, 4 parametrized)**

Run: `pytest tests/preflight/test_schemas.py -v`
Expected: 6 passed.

- [ ] **Step 9: Commit**

```bash
git add control_plane/preflight/__init__.py \
        control_plane/preflight/__main__.py \
        control_plane/preflight/state.py \
        control_plane/preflight/schemas.py \
        tests/preflight/__init__.py \
        tests/preflight/conftest.py \
        tests/preflight/test_state.py \
        tests/preflight/test_schemas.py
git commit -m "feat(preflight): foundations — state.py graduation + schemas.py dataclasses

Slice #1 of 5 (companion: docs/architecture/VFS_PREFLIGHT_DESIGN.md). 
First-run advisor → strict-mode flag, JSON-shaped dataclasses per spec §5."
```

---

## Task 2: probes/exec.py — subprocess with timeout wrapper

**Files:**
- Create: `control_plane/preflight/probes/__init__.py`
- Create: `control_plane/preflight/probes/exec.py`
- Create: `tests/preflight/test_exec_probe.py`

**Interfaces (consumed by later tasks):**

- `probes.exec.run(command: list[str], timeout_s: int) -> ExecResult` where
  `ExecResult` is a dataclass with `exit_code: int`, `stdout_excerpt: str`
  (capped at 4 KiB), `stderr_excerpt: str` (capped at 4 KiB), `duration_ms: int`,
  `timed_out: bool`.

- [ ] **Step 1: Write failing test**

Create `tests/preflight/test_exec_probe.py`:

```python
import time
from control_plane.preflight.probes import exec as probe


def test_run_passes_through_exit_code_0():
    r = probe.run(["python", "-c", "print('hi')"], timeout_s=5)
    assert r.exit_code == 0
    assert "hi" in r.stdout_excerpt
    assert r.timed_out is False


def test_run_captures_nonzero_exit():
    r = probe.run(["python", "-c", "import sys; sys.exit(7)"], timeout_s=5)
    assert r.exit_code == 7


def test_run_timeout_returns_timed_out_true():
    # A 30s sleep with 1s timeout — subnet for Windows where subprocess is finicky.
    r = probe.run(["python", "-c", "import time; time.sleep(5)"], timeout_s=1)
    assert r.timed_out is True
    assert r.exit_code != 0  # killed process returns nonzero on POSIX, may differ on Win
    assert r.duration_ms >= 1000


def test_run_caps_excerpts_at_4kib():
    big = "x" * 8000
    r = probe.run(["python", "-c", f"print({big!r})"], timeout_s=5)
    assert len(r.stdout_excerpt.encode("utf-8")) <= 4096
```

- [ ] **Step 2: Run → expect ImportError**

Run: `pytest tests/preflight/test_exec_probe.py -v`
Expected: `ModuleNotFoundError: No module named 'control_plane.preflight.probes'`.

- [ ] **Step 3: Implement exec.py**

Create `control_plane/preflight/probes/__init__.py`:

```python
"""Reusable preflight probes (per-check execution primitives)."""
```

Create `control_plane/preflight/probes/exec.py`:

```python
"""Subprocess wrapper: bounded timeouts, sized excerpts, cross-platform safe."""
from __future__ import annotations
import subprocess
import time
from dataclasses import dataclass

EXCERPT_CAP_BYTES = 4096


@dataclass
class ExecResult:
    exit_code: int
    stdout_excerpt: str
    stderr_excerpt: str
    duration_ms: int
    timed_out: bool


def _cap(s: str) -> str:
    b = s.encode("utf-8", errors="replace")
    if len(b) <= EXCERPT_CAP_BYTES:
        return s
    return b[:EXCERPT_CAP_BYTES].decode("utf-8", errors="replace") + "\n…[truncated]"


def run(command: list[str], timeout_s: int) -> ExecResult:
    """Run command with bounded wall-clock timeout.

    On timeout, sends SIGTERM and reaps; on Windows, calls TerminateProcess.
    Never raises on non-zero exit; only raises on FileNotFoundError (caller
    must surface that as REJECTED to keep the contract).
    """
    started = time.monotonic()
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        return ExecResult(
            exit_code=-1,
            stdout_excerpt=_cap(e.stdout or ""),
            stderr_excerpt=_cap(e.stderr or ""),
            duration_ms=int((time.monotonic() - started) * 1000),
            timed_out=True,
        )
    duration_ms = int((time.monotonic() - started) * 1000)
    return ExecResult(
        exit_code=proc.returncode,
        stdout_excerpt=_cap(proc.stdout or ""),
        stderr_excerpt=_cap(proc.stderr or ""),
        duration_ms=duration_ms,
        timed_out=False,
    )
```

- [ ] **Step 4: Run → expect PASS (4 tests)**

Run: `pytest tests/preflight/test_exec_probe.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add control_plane/preflight/probes/__init__.py \
        control_plane/preflight/probes/exec.py \
        tests/preflight/test_exec_probe.py
git commit -m "feat(preflight): subprocess probe with bounded timeout + excerpt cap"
```

---

## Task 3: Runner core (load YAML → catalog → halt logic) — no checks yet

**Files:**
- Create: `control_plane/preflight/runner.py`
- Create: `tests/preflight/test_runner_foundation.py`

**Interfaces (consumed by Tasks 4-7):**

- `runner.load_catalog(checks_dir: Path) -> list[CheckSpec]` — reads `*.yaml` files, parses, sorts by `sequence`, raises `CatalogParseError` on any failure.
- `runner.execute_check(spec: CheckSpec, *, strict_mode: bool, anya_triage_fn) -> CheckResult` — runs the check via `probes.exec.run`, calls `anya_triage_fn` for **advisory** metadata (advisory only; preflight owns evidence class), applies the strict-or-advisor decision.
- `runner.execute_catalog(*, specs: list[CheckSpec], run_root, scene_text, strict_mode, anya_triage_fn) -> RunManifest` — orchestrator; implementation in Task 6.

For Task 3 the implementation is intentionally minimal: load + sort + a stub `execute_check` that always returns `REJECTED` with a TODO marker so test infrastructure passes and downstream tasks can replace.

Actually — better: in Task 3, implement `load_catalog` for real, then leave `execute_check` to Task 6 once per-check probes exist. The runner's order/structural tests run with synthetic specs and a stub recorder.

- [ ] **Step 1: Write failing tests**

Create `tests/preflight/test_runner_foundation.py`:

```python
import pytest
from pathlib import Path
from control_plane.preflight import runner

SYNTHETIC_YAML_A = """
sequence: 10
id: a_check
display_name: A
command_type: shell
command: ["python", "-c", "print('a')"]
""".strip()

SYNTHETIC_YAML_B = """
sequence: 5
id: b_check
display_name: B
command_type: shell
command: ["python", "-c", "print('b')"]
""".strip()

SYNTHETIC_YAML_C = """
sequence: 20
id: c_check
display_name: C
command_type: shell
command: ["python", "-c", "print('c')"]
""".strip()


def test_load_catalog_sorts_by_sequence(tmp_path: Path):
    (tmp_path / "b.yaml").write_text(SYNTHETIC_YAML_B)
    (tmp_path / "a.yaml").write_text(SYNTHETIC_YAML_A)
    (tmp_path / "c.yaml").write_text(SYNTHETIC_YAML_C)
    specs = runner.load_catalog(tmp_path)
    assert [s.sequence for s in specs] == [5, 10, 20]
    assert [s.id for s in specs] == ["b_check", "a_check", "c_check"]


def test_load_catalog_rejects_duplicate_sequence(tmp_path: Path):
    (tmp_path / "a.yaml").write_text(SYNTHETIC_YAML_A)
    dup = SYNTHETIC_YAML_A.replace("id: a_check", "id: dup").replace(
        "display_name: A", "display_name: DUP"
    )
    (tmp_path / "b.yaml").write_text(dup)
    with pytest.raises(runner.CatalogError):
        runner.load_catalog(tmp_path)


def test_load_catalog_propagates_parse_error(tmp_path: Path):
    (tmp_path / "bad.yaml").write_text("not a yaml mapping: [")
    with pytest.raises(runner.CatalogError):
        runner.load_catalog(tmp_path)


def test_load_catalog_empty_dir_returns_empty_list(tmp_path: Path):
    assert runner.load_catalog(tmp_path) == []
```

- [ ] **Step 2: Run → expect ImportError**

Run: `pytest tests/preflight/test_runner_foundation.py -v`

- [ ] **Step 3: Implement runner.py minimal version (Task 6 will extend)**

Create `control_plane/preflight/runner.py`:

```python
"""VFS Preflight runner: load catalog, execute checks, emit evidence."""
from __future__ import annotations
from pathlib import Path
from typing import Iterable
from .state import GraduationFlag
from .schemas import CheckSpec, CheckResult, RunManifest, EvidenceClass

import hashlib
import json
import time
import os
from datetime import datetime, timezone


class CatalogError(ValueError):
    """Catalog load failed. Bundles per-file errors in .per_file_errors."""


def load_catalog(checks_dir: Path) -> list[CheckSpec]:
    """Read all *.yaml in checks_dir, parse, validate, sort by sequence.
    Raises CatalogError if any single file fails or duplicate sequences exist.
    No YAML in checks_dir other than *.yaml is read; _README.md is ignored
    by glob.
    """
    if not checks_dir.exists():
        raise CatalogError(f"checks directory missing: {checks_dir}")
    specs: list[CheckSpec] = []
    per_file_errors: list[str] = []
    for f in sorted(checks_dir.glob("*.yaml")):
        try:
            specs.append(CheckSpec.from_yaml_text(f.read_text()))
        except Exception as e:  # noqa: BLE001 — collect, re-raise as CatalogError
            per_file_errors.append(f"{f.name}: {e}")
    if per_file_errors:
        raise CatalogError("; ".join(per_file_errors))
    # Duplicate sequence check
    seen = set()
    dup_runners: list[str] = []
    for s in specs:
        if s.sequence in seen:
            dup_runners.append(f"sequence {s.sequence} duplicated (id={s.id})")
        seen.add(s.sequence)
    if dup_runners:
        raise CatalogError("; ".join(dup_runners))
    specs.sort(key=lambda s: s.sequence)
    return specs


# NOTE: execute_check and execute_catalog are filled in Task 6 once probes are
# in place. Keeping them as NotImplementedError markers so Task 3 can land a
# green test suite without claiming behavior that doesn't yet exist.
def execute_check(spec: CheckSpec, *, strict_mode: bool, anya_triage_fn) -> CheckResult:  # pragma: no cover
    raise NotImplementedError("Task 6 will implement execute_check")


def execute_catalog(*, specs: list[CheckSpec], run_root, scene_text: str, strict_mode: bool, anya_triage_fn) -> RunManifest:  # pragma: no cover
    raise NotImplementedError("Task 6 will implement execute_catalog")
```

- [ ] **Step 4: Run → expect PASS**

Run: `pytest tests/preflight/test_runner_foundation.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add control_plane/preflight/runner.py tests/preflight/test_runner_foundation.py
git commit -m "feat(preflight): runner catalog loader with sequence-duplication guard"
```

---

## Task 4: Per-check probes — 7 check primitives

**Files:**
- Create: `control_plane/preflight/probes/ports.py`
- Create: `control_plane/preflight/probes/file_age.py`
- Create: `control_plane/preflight/probes/file_present.py`
- Create: `control_plane/preflight/probes/license_header.py`
- Create: `control_plane/preflight/probes/import_smoke.py`
- Create: `control_plane/preflight/probes/yaml_parses.py`
- Create: `tests/preflight/test_checks_simple.py`
- Create: `tests/preflight/test_checks_hitl.py`
- Create: `tests/preflight/test_check_lattice.py`

**Interfaces:**

- `probes.ports.scan(ports: list[int], timeout_s: float = 0.2) -> dict[int, bool]`
- `probes.file_age.check(path: Path, max_age_days: int) -> tuple[bool, int]`
- `probes.file_present.scan(required_paths: list[Path]) -> list[Path]`
- `probes.license_header.scan(roots: list[Path]) -> list[Path]`
- `probes.import_smoke.check(modules: list[str]) -> list[str]`
- `probes.yaml_parses.check(path: Path) -> bool`

Each probe returns a tuple `(passed: bool, details: Any)`. The runner glues checks into `CheckResult`.

To stay bite-sized, this task is split into 3 logical sub-steps but executed as ONE commit at the end. Each probe gets:

- [ ] **Step 1: Probes + their tests**

Create `control_plane/preflight/probes/ports.py`:

```python
"""TCP port probe — short-lived connect attempts."""
from __future__ import annotations
import socket
from typing import Iterable


def scan(ports: Iterable[int], timeout_s: float = 0.2) -> dict[int, bool]:
    out: dict[int, bool] = {}
    for p in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout_s)
        try:
            s.connect(("127.0.0.1", p))
            s.close()
            out[p] = True
        except (OSError, socket.timeout):
            out[p] = False
    return out
```

Create `control_plane/preflight/probes/file_age.py`:

```python
"""Compute file age in days, capping at 100000 to avoid overflow."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path


def check(path: Path, max_age_days: int) -> tuple[bool, int]:
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    except FileNotFoundError:
        return False, -1  # report missing as REJECTED upstream
    age_days = (datetime.now(timezone.utc) - mtime).days
    if age_days < 0:
        age_days = 100000
    return (age_days <= max_age_days), age_days
```

Create `control_plane/preflight/probes/file_present.py`:

```python
"""Static file presence probe for required-on-disk artifacts."""
from __future__ import annotations
from pathlib import Path


def scan(required_paths: list[Path]) -> list[Path]:
    return [p for p in required_paths if p.exists()]
```

Create `control_plane/preflight/probes/license_header.py`:

```python
"""FOSS license header probe — flags files missing a recognized SPDX marker."""
from __future__ import annotations
from pathlib import Path
import re

SPDX_PATTERNS = [
    re.compile(r"SPDX-License-Identifier:\s*([A-Za-z0-9\-\.\+]+)"),
    re.compile(r"Copyright\s+\(c\)\s+\d{4}"),
]
SKIP_EXTS = {".md", ".txt", ".json", ".lock", ".yaml", ".yml"}


def scan(roots: list[Path]) -> list[Path]:
    """Return list of source files (non-skipped ext) without a license marker.
    Empty list means OK."""
    flagged: list[Path] = []
    for root in roots:
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() in SKIP_EXTS:
                continue
            try:
                head = p.read_text(encoding="utf-8", errors="ignore")[:4096]
            except OSError:
                continue
            if any(rx.search(head) for rx in SPDX_PATTERNS):
                continue
            flagged.append(p)
    return flagged
```

Create `control_plane/preflight/probes/import_smoke.py`:

```python
"""Importable modules check — ensures critical imports succeed."""
from __future__ import annotations
import importlib


def check(modules: list[str]) -> list[str]:
    failed = []
    for m in modules:
        try:
            importlib.import_module(m)
        except Exception:  # noqa: BLE001
            failed.append(m)
    return failed
```

Create `control_plane/preflight/probes/yaml_parses.py`:

```python
"""YAML parses probe — verifies a YAML file is a valid mapping."""
from __future__ import annotations
from pathlib import Path
import yaml


def check(path: Path) -> tuple[bool, str]:
    try:
        loaded = yaml.safe_load(path.read_text())
    except Exception as e:  # noqa: BLE001
        return False, str(e)
    if not isinstance(loaded, dict):
        return False, "expected a mapping at top level"
    return True, ""
```

- [ ] **Step 2: Tests for each probe**

Create `tests/preflight/test_checks_simple.py` (covers env_dependency_match, foss_validation_constraints, provenance_ledger_writable, tool_registry_presence):

```python
import socket
import threading
import time
from contextlib import closing
from pathlib import Path
import pytest

from control_plane.preflight.probes import (
    file_present,
    import_smoke,
    license_header,
    ports as ports_probe,
)


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def test_ports_probe_returns_open_for_listener():
    p = _free_port()
    with closing(socket.socket()) as srv:
        srv.bind(("127.0.0.1", p))
        srv.listen()
        t = threading.Thread(target=srv.accept, daemon=True)
        t.start()
        out = ports_probe.scan([p], timeout_s=0.5)
    assert out == {p: True}


def test_ports_probe_returns_closed_for_dead_port():
    p = _free_port()
    out = ports_probe.scan([p], timeout_s=0.2)
    assert out == {p: False}


def test_file_present_returns_only_existing(tmp_path: Path):
    a = tmp_path / "exists.md"
    b = tmp_path / "missing.md"
    a.write_text("# hi")
    out = file_present.scan([a, b])
    assert out == [a]


def test_import_smoke_flags_bogus_module():
    out = import_smoke.check(["definitely_does_not_exist_xyz"])
    assert out == ["definitely_does_not_exist_xyz"]


def test_import_smoke_passes_real_modules():
    out = import_smoke.check(["pathlib", "json"])
    assert out == []


def test_license_header_flags_missing(tmp_path: Path):
    bad = tmp_path / "no_license.py"
    bad.write_text("def foo(): pass\n")  # no SPDX, no Copyright
    out = license_header.scan([tmp_path])
    assert bad.resolve() in [p.resolve() for p in out]


def test_license_header_passes_with_spdx(tmp_path: Path):
    good = tmp_path / "good.py"
    good.write_text("# SPDX-License-Identifier: MIT\ndef foo(): pass\n")
    out = license_header.scan([tmp_path])
    assert good.resolve() not in [p.resolve() for p in out]
```

Create `tests/preflight/test_checks_hitl.py` (covers northstar_brief_currency, vfs_scaffold_integrity, ports via the probe — kept separate because they're hitl-flagged in catalog):

```python
from datetime import datetime, timezone, timedelta
from pathlib import Path
import socket

from control_plane.preflight.probes import (
    file_age,
    file_present,
    yaml_parses,
)


def test_file_age_passes_for_recent(tmp_path: Path):
    p = tmp_path / "fresh.md"
    p.write_text("# fresh")
    ok, days = file_age.check(p, max_age_days=60)
    assert ok is True
    assert days <= 60


def test_file_age_rejects_for_old(tmp_path: Path):
    p = tmp_path / "old.md"
    p.write_text("# old")
    # Backdate mtime to 100 days ago.
    old = (datetime.now(timezone.utc) - timedelta(days=100)).timestamp()
    import os
    os.utime(p, (old, old))
    ok, days = file_age.check(p, max_age_days=60)
    assert ok is False
    assert days >= 90


def test_file_age_returns_false_neg1_for_missing(tmp_path: Path):
    ok, days = file_age.check(tmp_path / "ghost.md", max_age_days=60)
    assert ok is False
    assert days == -1


def test_vfs_scaffold_integrity_all_required_present(tmp_path: Path, monkeypatch):
    (tmp_path / "preflight.md").write_text("# mock")
    (tmp_path / "systeminstructions.md").write_text("# mock")
    (tmp_path / "skills.md").write_text("# mock")
    (tmp_path / "rosters.md").write_text("# mock")
    (tmp_path / "protocols.md").write_text("# mock")
    found = file_present.scan([
        tmp_path / "preflight.md",
        tmp_path / "systeminstructions.md",
        tmp_path / "skills.md",
        tmp_path / "rosters.md",
        tmp_path / "protocols.md",
    ])
    assert len(found) == 5


def test_yaml_parses_passes_on_mapping(tmp_path: Path):
    p = tmp_path / "ok.yaml"
    p.write_text("a: 1\nb: 2\n")
    ok, msg = yaml_parses.check(p)
    assert ok is True
    assert msg == ""


def test_yaml_parses_rejects_non_mapping(tmp_path: Path):
    p = tmp_path / "list.yaml"
    p.write_text("- 1\n- 2\n")
    ok, msg = yaml_parses.check(p)
    assert ok is False
    assert "mapping" in msg
```

Create `tests/preflight/test_check_lattice.py`:

```python
from pathlib import Path
import textwrap
import yaml

# Reads docs/architecture/lattice.yaml directly, but to avoid coupling to repo state,
# we re-parse the same shape from a tmp fixture.
from control_plane.preflight.probes import yaml_parses


def _write_lattice(tmp: Path):
    (tmp / "lattice.yaml").write_text(textwrap.dedent("""
        version: 1
        sot: {type: file, path: docs/architecture/lattice_map.md}
        axes: {inference: {anchors: []}, memory: {anchors: []}}
        subprojects:
          - id: CAMELOT_OS
            type: sovereign
            path: CAMELOT_OS/
            mb: 26800
          - id: cli-proxy-api
            type: service
            path: CLIProxyAPI/
            mb: 56
    """).strip())
    # Each subproject's path must point to an existing on-disk directory OR a
    # note in the manifest. Real check verifies the catalog parses + that paths
    # either exist OR are flagged as 'not_present'.
    import os
    os.makedirs(tmp / "CAMELOT_OS", exist_ok=True)


def test_lattice_yaml_parses(tmp_path: Path):
    _write_lattice(tmp_path)
    ok, _ = yaml_parses.check(tmp_path / "lattice.yaml")
    assert ok is True


def test_lattice_subprojects_present(tmp_path: Path):
    _write_lattice(tmp_path)
    data = yaml.safe_load((tmp_path / "lattice.yaml").read_text())
    on_disk = []
    for sp in data["subprojects"]:
        p = tmp_path / sp["path"]
        if p.exists():
            on_disk.append(sp["id"])
    assert "CAMELOT_OS" in on_disk
```

- [ ] **Step 3: Run tests → expect ALL PASS**

Run: `pytest tests/preflight/test_checks_simple.py tests/preflight/test_checks_hitl.py tests/preflight/test_check_lattice.py tests/preflight/test_runner_foundation.py tests/preflight/test_schemas.py tests/preflight/test_state.py tests/preflight/test_exec_probe.py -v`

Expected: every test passing.

- [ ] **Step 4: Commit**

```bash
git add control_plane/preflight/probes/ tests/preflight/test_checks_simple.py \
        tests/preflight/test_checks_hitl.py tests/preflight/test_check_lattice.py
git commit -m "feat(preflight): per-check probe primitives (7 of 8 checks wired)"
```

---

## Task 5: 8 catalog YAMLs

**Files:**
- Create: `vfs/checks/_README.md`
- Create: `vfs/checks/010_env_dependency_match.yaml`
- Create: `vfs/checks/020_foss_validation_constraints.yaml`
- Create: `vfs/checks/030_northstar_brief_currency.yaml`
- Create: `vfs/checks/040_port_readiness_scan.yaml`
- Create: `vfs/checks/050_provenance_ledger_writable.yaml`
- Create: `vfs/checks/060_tool_registry_presence.yaml`
- Create: `vfs/checks/070_vfs_scaffold_integrity.yaml`
- Create: `vfs/checks/080_lattice_yaml_consistency.yaml`
- Create: `tests/preflight/test_catalog_authored_matches_schema.py`

- [ ] **Step 1: Write _README.md**

Create `vfs/checks/_README.md`:

```markdown
# VFS Preflight Catalog

Each `*.yaml` file in this directory is one preflight check. The catalog is
loaded by `python -m control_plane.preflight` at boot (`bin/awaken.py` stage 0).

## YAML fields

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `sequence` | yes | int | Execution order. Stride 10 (010, 020, …) so authors can insert at natural positions without renumbering. Must be unique within the catalog. |
| `id` | yes | str | Stable identifier; becomes `<UTC>/<id>.json` filename. |
| `display_name` | yes | str | Human-readable name in operator summary. |
| `command_type` | yes | `python_module` \| `shell` | `python_module` is preferred; `shell` only when necessary. |
| `command` | yes | list[str] | argv list, never a shell command. Each element must be a string. |
| `timeout_s` | no | int (default 30) | Wall-clock timeout. Prefer absence over low values; if a check can fail transiently, raise timeout_s, do not add retries. |
| `retry` | no | int 0..2 (default 0) | **Discouraged.** Use only for ports-style transient failures. |
| `expected_evidence_class` | no | `CONFIRMED` (default) | Only `CONFIRMED` accepted. The runner rejects any other value at catalog load. |
| `hitl_on_fail` | no | bool (default false) | If true, a REJECTED result surfaces a PROMPT-tier operator menu instead of halting. Reserved for the 3 operator-visible checks: 030, 040, 070. |
| `remediation_hint` | no | str | Shown in operator summary when the check fails. |

## Authoring rules

1. Command must be a list, never a shell string. `command: ["python", "-c", "..."]` is the only safe shell-style form.
2. Sequence must be unique. Use stride 10.
3. Do not bypass timeout via Python's `subprocess`; rely on the runner's bounded wrapper.
4. If a check needs new logic, add a probe under `control_plane/preflight/probes/` first.
5. Evidence class is CONFIRMED-only by design (spec §5.3).
6. Maintain idempotency: re-running this check N times produces no side effects past version drift.
```

- [ ] **Step 2: Write the 8 catalog YAMLs**

Create `vfs/checks/010_env_dependency_match.yaml`:

```yaml
sequence: 010
id: env_dependency_match
display_name: Environment Dependency Match
command_type: python_module
command: ["python", "-m", "control_plane.preflight.probes.env_dep_run"]
timeout_s: 10
retry: 0
expected_evidence_class: CONFIRMED
hitl_on_fail: false
remediation_hint: "Install Python 3.11+, Rust 1.96, Node 20; start Ollama on :11434."
```

Create `vfs/checks/020_foss_validation_constraints.yaml`:

```yaml
sequence: 020
id: foss_validation_constraints
display_name: FOSS License Header Scan
command_type: python_module
command: ["python", "-m", "control_plane.preflight.probes.license_header_run",
          "--roots", "01_KERNEL", "02_FORGE", "vfs"]
timeout_s: 15
retry: 0
expected_evidence_class: CONFIRMED
hitl_on_fail: false
remediation_hint: "Add '# SPDX-License-Identifier: MIT' (or chosen) at the top of files flagged in the run log."
```

Create `vfs/checks/030_northstar_brief_currency.yaml`:

```yaml
sequence: 030
id: northstar_brief_currency
display_name: NORTHSTAR Brief Currency (≤60 days)
command_type: python_module
command: ["python", "-m", "control_plane.preflight.probes.file_age_run",
          "--path", "docs/architecture/NORTHSTAR_ARCHITECTURE_BRIEF.md",
          "--max-age-days", "60"]
timeout_s: 5
retry: 0
expected_evidence_class: CONFIRMED
hitl_on_fail: true
remediation_hint: "Refresh or formally supersede NORTHSTAR_ARCHITECTURE_BRIEF.md (current draft may exceed 60 days; first run will surface this as advisory)."
```

Create `vfs/checks/040_port_readiness_scan.yaml`:

```yaml
sequence: 040
id: port_readiness_scan
display_name: Port Readiness Scan
command_type: python_module
command: ["python", "-m", "control_plane.preflight.probes.ports_run",
          "--ports", "8080,8011,11434,4433,4434"]
timeout_s: 5
retry: 0
expected_evidence_class: CONFIRMED
hitl_on_fail: true
remediation_hint: "Run scripts/ops/start-bifrost.sh; expected open: 8080 (CLIProxy), 8011 (Bifrost prefight), 11434 (Ollama), 4433 (Bifrost WS), 4434 (Bifrost gRPC). Tolerate missing subgraph ports during first-run advisor mode."
```

Create `vfs/checks/050_provenance_ledger_writable.yaml`:

```yaml
sequence: 050
id: provenance_ledger_writable
display_name: Provenance Ledger Writable
command_type: python_module
command: ["python", "-m", "control_plane.preflight.probes.ledger_writable_run",
          "--path", "PROVENANCE_LEDGER.md"]
timeout_s: 5
retry: 0
expected_evidence_class: CONFIRMED
hitl_on_fail: false
remediation_hint: "PROVENANCE_LEDGER.md is read-only or missing. Restore from CAMELOT-OS PROVENANCE_LEDGER.md hook (the post-write hook owns the file)."
```

Create `vfs/checks/060_tool_registry_presence.yaml`:

```yaml
sequence: 060
id: tool_registry_presence
display_name: Tool Registry Presence
command_type: python_module
command: ["python", "-m", "control_plane.preflight.probes.import_smoke_run",
          "--modules", "pathlib,json,yaml,subprocess,hashlib"]
timeout_s: 10
retry: 0
expected_evidence_class: CONFIRMED
hitl_on_fail: false
remediation_hint: "Required: Python 3.11+, PyYAML. Audit pip-freeze and re-install missing stdlib or PyYAML."
```

Create `vfs/checks/070_vfs_scaffold_integrity.yaml`:

```yaml
sequence: 070
id: vfs_scaffold_integrity
display_name: VFS Scaffold Integrity
command_type: python_module
command: ["python", "-m", "control_plane.preflight.probes.vfs_present_run",
          "--required", "vfs/preflight.md", "vfs/systeminstructions.md",
          "vfs/skills.md", "vfs/rosters.md", "vfs/protocols.md"]
timeout_s: 5
retry: 0
expected_evidence_class: CONFIRMED
hitl_on_fail: true
remediation_hint: "Restore missing vfs/*.md files from the Ω_VFS_ARCHITECTURE_SCAFFOLD_vMAX deposit artifacts."
```

Create `vfs/checks/080_lattice_yaml_consistency.yaml`:

```yaml
sequence: 080
id: lattice_yaml_consistency
display_name: Lattice YAML Consistency
command_type: python_module
command: ["python", "-m", "control_plane.preflight.probes.lattice_run",
          "--path", "docs/architecture/lattice.yaml"]
timeout_s: 5
retry: 0
expected_evidence_class: CONFIRMED
hitl_on_fail: false
remediation_hint: "Re-run lattice_purge_orchestrator.py :: phase e or update lattice.yaml manually."
```

> **Note**: Tasks 6+ implement the probe runners (`env_dep_run`, `license_header_run`, `file_age_run`, `ports_run`, `ledger_writable_run`, `import_smoke_run`, `vfs_present_run`, `lattice_run`) as thin CLI wrappers that call into the probe Python modules from Task 4. Each runner is `<15` LOC. See Task 6 step 1 for the wrapper pattern.

- [ ] **Step 3: Write a test that catalog parses**

Create `tests/preflight/test_catalog_authored_matches_schema.py`:

```python
from pathlib import Path
import pytest
from control_plane.preflight import runner

CATALOG_DIR = Path(__file__).resolve().parents[2] / "vfs" / "checks"


def test_catalog_loads_clean():
    specs = runner.load_catalog(CATALOG_DIR)
    assert len(specs) == 8, f"expected 8 checks, got {len(specs)}"


def test_catalog_execution_order():
    specs = runner.load_catalog(CATALOG_DIR)
    assert [s.sequence for s in specs] == [10, 20, 30, 40, 50, 60, 70, 80]


def test_catalog_ids_match_spec():
    specs = runner.load_catalog(CATALOG_DIR)
    expected_ids = {
        "env_dependency_match", "foss_validation_constraints",
        "northstar_brief_currency", "port_readiness_scan",
        "provenance_ledger_writable", "tool_registry_presence",
        "vfs_scaffold_integrity", "lattice_yaml_consistency",
    }
    assert {s.id for s in specs} == expected_ids


def test_catalog_hitl_subset_matches_spec():
    specs = runner.load_catalog(CATALOG_DIR)
    hitl = {s.id for s in specs if s.hitl_on_fail}
    assert hitl == {
        "northstar_brief_currency",
        "port_readiness_scan",
        "vfs_scaffold_integrity",
    }
```

- [ ] **Step 4: Run → expect FAIL (probes referenced in YAML don't exist)**

Run: `pytest tests/preflight/test_catalog_authored_matches_schema.py -v`
Expected: catalog loads OK (schema is pure YAML); runner.execute_catalog() would fail later when probes don't exist.

The schema test passes after Task 4. It does NOT execute runner.execute_catalog() yet — that's Task 6.

- [ ] **Step 5: Commit**

```bash
git add vfs/checks/_README.md vfs/checks/*.yaml tests/preflight/test_catalog_authored_matches_schema.py
git commit -m "feat(preflight): 8-check catalog YAMLs + author README"
```

---

## Task 6: Probe runners (thin CLI wrappers) + runner.execute_catalog() orchestrator

**Files:**
- Create: `control_plane/preflight/probes/env_dep_run.py`
- Create: `control_plane/preflight/probes/license_header_run.py`
- Create: `control_plane/preflight/probes/file_age_run.py`
- Create: `control_plane/preflight/probes/ports_run.py`
- Create: `control_plane/preflight/probes/ledger_writable_run.py`
- Create: `control_plane/preflight/probes/import_smoke_run.py`
- Create: `control_plane/preflight/probes/vfs_present_run.py`
- Create: `control_plane/preflight/probes/lattice_run.py`
- Modify: `control_plane/preflight/runner.py` (replace NotImplementedError stubs)
- Create: `tests/preflight/test_runner_integration.py`

**Interfaces:**

- `runner.execute_catalog(*, specs: list[CheckSpec], run_root: Path, scene_text: str, strict_mode: bool, anya_triage_fn) -> RunManifest`
  - `anya_triage_fn(raw_intent: str) -> dict | TriageScore` — injected so tests can stub a sentinel triager; prod uses `AnyaGate().triage`. On any import/signature failure, runner falls back to inline sentinel `{"method": "advisory_unavailable", "lane": "NORMAL", "hitl_tier": "AUTO", "shatterpoints_detected": []}`. The prod injection occurs in `__main__.py` (Task 7).
- Each `probes.<name>_run.py` is a thin CLI that takes `--<flag> value`, returns a JSON-shaped blob on stdout that the runner parses. Pattern shown in Step 1.

- [ ] **Step 1: Implement 8 probe runners (one CLI each, ~15 LOC each)**

Pattern (exemplar: `env_dep_run.py`):

```python
"""env_dep_run — verify Python/Rust/Node/Ollama presence."""
import json, sys, shutil, platform

def main():
    out = {
        "python_ok": sys.version_info >= (3, 11),
        "rust_cargo_ok": shutil.which("cargo") is not None,
        "node_ok": shutil.which("node") is not None,
        "ollama_ok": shutil.which("ollama") is not None,
        "python_version": platform.python_version(),
    }
    out["all_ok"] = all([out["python_ok"], out["rust_cargo_ok"],
                         out["node_ok"], out["ollama_ok"]])
    sys.stdout.write(json.dumps(out) + "\n")
    sys.exit(0 if out["all_ok"] else 1)

if __name__ == "__main__":
    main()
```

Implement analogous runners for `license_header_run` (delegating to `probes.license_header.scan`), `file_age_run` (delegating to `probes.file_age.check`), `ports_run` (delegating to `probes.ports.scan`), `ledger_writable_run` (`os.access(path, os.W_OK)`), `import_smoke_run` (delegating to `probes.import_smoke.check`), `vfs_present_run` (delegating to `probes.file_present.scan`), `lattice_run` (parses + verifies each subproject path's `<root>/<path>` exists or reports missing).

Each runner outputs `{"all_ok": bool, ...details}` on stdout, sets exit 0 iff `all_ok` is True. The runner parses stdout to compute `rejection_reasons`.

- [ ] **Step 2: Replace NotImplementedError stubs in `runner.execute_catalog` + `runner.execute_check`**

The full orchestrator. Pseudocode (full code is mandatory in this step):

```python
def execute_check(spec: CheckSpec, *, strict_mode: bool, anya_triage_fn) -> CheckResult:
    started_at = utc_now_iso()
    res = probes.exec.run(spec.command, spec.timeout_s)
    # Parse JSON stdout if available else treat exit_code as truth.
    payload = _try_parse_json(res.stdout_excerpt)
    all_ok = payload.get("all_ok", res.exit_code == 0)
    rejection_reasons: list[str] = []
    if res.timed_out:
        rejection_reasons.append(f"timeout: {spec.timeout_s}s exceeded")
    elif not all_ok:
        # Detail reasons from payload
        for k, v in payload.items():
            if k == "all_ok":  # noqa: E713
                continue
            if v is False:
                rejection_reasons.append(f"{k} = {v}")
        if res.exit_code != 0 and not payload:
            rejection_reasons.append(f"exit_code = {res.exit_code}")
    # Preflight OWNS evidence_class. anya_triage_fn is advisory only.
    ec: EvidenceClass = "CONFIRMED" if not rejection_reasons else "REJECTED"
    # Advisory ANYA routing — invoke with a raw_intent string summarising
    # the rejection, get back a routing decision. Failure to import or
    # call is caught by anya_triage_fn itself (graceful-degradation sentinel).
    raw_intent = (
        f"preflight_check {spec.id}: all_ok={all_ok} "
        f"reasons={';'.join(rejection_reasons) or 'none'}"
    )
    try:
        triage_obj = anya_triage_fn(raw_intent)
        triage = _triage_obj_to_dict(triage_obj)
    except Exception as e:  # noqa: BLE001
        triage = {"method": "advisory_unavailable", "error": str(e),
                  "lane": "NORMAL", "hitl_tier": "AUTO",
                  "shatterpoints_detected": []}
    halt: HaltDecision = (
        "continue" if ec == "CONFIRMED"
        else ("block_boot" if strict_mode or not spec.hitl_on_fail else "await_hitl")
    )
    advisor = (not strict_mode and ec == "REJECTED")
    return CheckResult(
        run_id="",  # filled in by run()
        check_id=spec.id,
        display_name=spec.display_name,
        command_observed=spec.command,
        command_raw=f"vfs/checks/{spec.sequence:03d}_{spec.id}.yaml",
        exit_code=res.exit_code,
        started_at=started_at,
        duration_ms=res.duration_ms,
        stdout_excerpt=res.stdout_excerpt,
        stderr_excerpt=res.stderr_excerpt,
        evidence_class=ec,
        evidence_assertion=triage,
        hitl_required=(spec.hitl_on_fail and ec == "REJECTED"),
        halt_decision=halt,
        advisor_finding=advisor,
        rejection_reasons=rejection_reasons,
        remediation_hint=spec.remediation_hint,
        artifact_path="",  # filled in by run()
    )


def execute_catalog(*, specs: list[CheckSpec], run_root: Path, scene_text: str,
        anya_triage_fn) -> RunManifest:
    ...
    # Read sequence steps per spec §5.2.
```

(Full implementation body goes here. The plan's job is to specify which edge cases to handle and where; the implementer's job is to write every import, every comparison, every log line. The implementer MUST:

1. Compute `catalog_hash` via `schemas.compute_catalog_hash(specs_path.parent)` once per run.
2. Compute `run_id` as `f"preflight-{utc_now_iso_for_id()}-{scene_hash[:6]}"` with a per-second counter suffix on collision.
3. Iterate specs in `sequence` order; for each spec, call `execute_check(spec, strict_mode, anya_triage_fn)`.
4. For each result: write per-check JSON to `<run_root>/<UTC>/<check_id>.json` using `tempfile + os.replace` for atomic write.
5. On strict-mode REJECTED, set `manifest.halted_at_check = spec.id`, break loop, mark remaining checks SKIPPED with `exit_code = -2, halt_decision = "continue"` (because they're skipped, not failed).
6. On advisor-mode REJECTED, set `result.advisor_finding = True` and continue.
7. On `_graduated.flag` NOT present AND all results CONFIRMED: call `state.GraduationFlag(run_root).graduate()` and set `manifest.graduated_to_strict = True`.
8. On any catalog load error inside the run: raise `CatalogError` to caller — `__main__.py` handles exit code.
9. Use `subprocess` ONLY inside `probes.exec.run`; **never** spawn Python from inside the runner itself.
)

- [ ] **Step 3: Failing test for `run()` orchestrator with stubs**

Create `tests/preflight/test_runner_integration.py`:

```python
import json
from pathlib import Path

from control_plane.preflight import runner
from control_plane.preflight.state import GraduationFlag


def _fake_anya_triage(raw_intent: str) -> dict:
    # Sentinel: the ANYA substrate is presumed unavailable in tests.
    return {"method": "advisory_unavailable", "lane": "NORMAL",
            "hitl_tier": "AUTO", "shatterpoints_detected": []}


def test_run_first_run_advisor_continues_on_rejected(tmp_path: Path):
    # Build a tmp catalog with one REJECTED + one PASS check.
    (tmp_path / "checks").mkdir()
    (tmp_path / "vfs_root" / "checks").mkdir(parents=True)
    # Use the runner's own catalog discovery via fixtures, but for fast test,
    # set up 2 yaml files directly.
    rc = Path(tmp_path) / "run_root"
    label = "advisor-test"
    # Synthesize two YAMLs
    (Path(tmp_path) / "c1.yaml").write_text(
        "sequence: 10\nid: c1\ndisplay_name: C1\n"
        "command_type: shell\ncommand: [\"python\", \"-c\", \"print('{\\\"all_ok\\\": true}')\"]\n"
    )
    (Path(tmp_path) / "c2.yaml").write_text(
        "sequence: 20\nid: c2\ndisplay_name: C2\n"
        "command_type: shell\ncommand: [\"python\", \"-c\", \"print('{\\\"all_ok\\\": false, \\\"x\\\": false}'); import sys; sys.exit(1)\"]\n"
    )
    specs = runner.load_catalog(Path(tmp_path))
    manifest = runner.execute_catalog(
        specs=specs,
        run_root=rc,
        scene_text="scene",
        strict_mode=False,  # advisor-mode
        anya_triage_fn=_fake_anya_triage,
    )
    assert manifest.halt_decision == "continue"
    assert manifest.checks_failed == 1
    assert manifest.first_run is True


def test_run_strict_mode_halts_on_rejected(tmp_path: Path):
    (Path(tmp_path) / "c1.yaml").write_text(
        "sequence: 10\nid: c1\ndisplay_name: C1\n"
        "command_type: shell\ncommand: [\"python\", \"-c\", \"print('{\\\"all_ok\\\": false}'); import sys; sys.exit(1)\"]\n"
    )
    rc = Path(tmp_path) / "run_root"
    specs = runner.load_catalog(Path(tmp_path))
    manifest = runner.execute_catalog(
        specs=specs, run_root=rc, scene_text="scene",
        strict_mode=True,  # strict-mode
        anya_triage_fn=_fake_anya_triage,
    )
    assert manifest.halt_decision == "block_boot"


def test_runs_are_idempotent(tmp_path: Path):
    (Path(tmp_path) / "c1.yaml").write_text(
        "sequence: 10\nid: c1\ndisplay_name: C1\n"
        "command_type: shell\ncommand: [\"python\", \"-c\", \"print('{\\\"all_ok\\\": true}')\"]\n"
    )
    rc = Path(tmp_path) / "run_root"
    specs = runner.load_catalog(Path(tmp_path))
    m1 = runner.execute_catalog(specs=specs, run_root=rc, scene_text="x",
                                 strict_mode=True, anya_triage_fn=_fake_anya_triage)
    m2 = runner.execute_catalog(specs=specs, run_root=rc, scene_text="x",
                                 strict_mode=True, anya_triage_fn=_fake_anya_triage)
    assert m1.run_id != m2.run_id
```

(This test enforces the signature `execute_catalog(specs, run_root, scene_text, strict_mode, anya_triage_fn)`, NOT `run()`. The `execute_catalog` form is more testable. The public CLI in `__main__.py` imports it.)

- [ ] **Step 4: Run tests → after implementation, expect PASS**

Run: `pytest tests/preflight/test_runner_integration.py -v`

- [ ] **Step 5: Commit**

```bash
git add control_plane/preflight/probes/env_dep_run.py \
        control_plane/preflight/probes/license_header_run.py \
        control_plane/preflight/probes/file_age_run.py \
        control_plane/preflight/probes/ports_run.py \
        control_plane/preflight/probes/ledger_writable_run.py \
        control_plane/preflight/probes/import_smoke_run.py \
        control_plane/preflight/probes/vfs_present_run.py \
        control_plane/preflight/probes/lattice_run.py \
        control_plane/preflight/runner.py tests/preflight/test_runner_integration.py
git commit -m "feat(preflight): probe-runner CLIs + runner.execute_catalog orchestrator"
```

---

## Task 7: CLI surface — `python -m control_plane.preflight` + rejected escape-hatch flags

**Files:**
- Modify: `control_plane/preflight/__main__.py` (replace the stub)
- Create: `tests/preflight/test_cli.py`

**Interfaces:**

- `python -m control_plane.preflight --run` → executes the catalog end-to-end, returns exit 0 on success.
- `python -m control_plane.preflight --test` → runs all inline-synthetic checks (AC8).
- `python -m control_plane.preflight --list` → prints catalog.
- `python -m control_plane.preflight --graduate` → explicit operator graduation (Q1 in spec §11).
- Rejects `--skip-sovereign`, `--force`, env `CAMELOT_SKIP_PREFLIGHT`, `CAMELOT_BYPASS_PREFLIGHT` with exit 2 + stderr message.

- [ ] **Step 1: Write failing CLI tests**

Create `tests/preflight/test_cli.py`:

```python
import os
import subprocess
import sys

import pytest


def test_cli_rejects_skip_sovereign_flag():
    r = subprocess.run(
        [sys.executable, "-m", "control_plane.preflight", "--run",
         "--skip-sovereign"],
        capture_output=True, text=True,
    )
    assert r.returncode == 2
    assert "sovereign escape hatch is not supported" in r.stderr


def test_cli_rejects_force_flag():
    r = subprocess.run(
        [sys.executable, "-m", "control_plane.preflight", "--run", "--force"],
        capture_output=True, text=True,
    )
    assert r.returncode == 2
    assert "sovereign escape hatch is not supported" in r.stderr


def test_cli_rejects_camelot_skip_preflight_env(tmp_path, monkeypatch):
    monkeypatch.setenv("CAMELOT_SKIP_PREFLIGHT", "1")
    monkeypatch.chdir(tmp_path)
    r = subprocess.run(
        [sys.executable, "-m", "control_plane.preflight", "--run"],
        capture_output=True, text=True,
    )
    assert r.returncode == 2
    assert "sovereign escape hatch is not supported" in r.stderr


def test_cli_self_test_returns_0():
    r = subprocess.run(
        [sys.executable, "-m", "control_plane.preflight", "--test"],
        capture_output=True, text=True, timeout=20,
    )
    assert r.returncode == 0, r.stderr
    assert "all checks passing" in r.stdout
```

- [ ] **Step 2: Replace `__main__.py` stub**

The CLI is the orchestrator public entry point:

```python
"""CLI entry for control_plane.preflight."""
...
# Reject escape hatches BEFORE argparse -- it should fail even if user only
# passes --skip-sovereign with no other args.
import os
_FORBIDDEN_ENVS = ("CAMELOT_SKIP_PREFLIGHT", "CAMELOT_BYPASS_PREFLIGHT")
_FORBIDDEN_FLAGS = ("--skip-sovereign", "--force", "--no-preflight", "--bypass")
...  # argparse, lookup check, raise SystemExit(2) if any match.

# argparse subcommands:
# --run, --test, --list, --graduate
# wire to runner.execute_catalog and GraduationFlag methods.
```

- [ ] **Step 3: Run tests → expect PASS**

Run: `pytest tests/preflight/test_cli.py -v`

- [ ] **Step 4: Commit**

```bash
git add control_plane/preflight/__main__.py tests/preflight/test_cli.py
git commit -m "feat(preflight): CLI surface + reject sovereign escape hatch"
```

---

## Task 8: Wire into `bin/awaken.py` stage 0

**Files:**
- Modify: `bin/awaken.py:0-N` (insert preflight stage at the start)

- [x] **Step 1: Read `bin/awaken.py` and locate the dispatch point**

DONE 2026-08-14: `bin/awaken.py` delegates to `control_plane.boot_sequence.run_boot`
(meta-path finder → `control_plane/infra/boot_sequence.py`), so the wiring
lives there as the first phase (see note under Step 2).

- [x] **Step 2: Insert stage 0 as the first executable action**

DONE 2026-08-14 — implementation detail: the stage-0 wiring lives in
`control_plane/infra/boot_sequence.py` (first phase in `run_boot`), backed
by a new `control_plane/preflight/boot_integration.py::boot_vfs_preflight`
module, because `bin/awaken.py` imports `run_boot` from there. The
phase wrapper `_boot_vfs_preflight_stage0` raises `SystemExit(1)` on a
strict REJECT so the boot hard-halts before any later stage starts
services (ADR 0006).

Insert before the first existing stage. The shape below is exemplar; adapt imports and constants to whatever pattern `bin/awaken.py` already uses.

```python
# Stage 0 — VFS Preflight (slice #1). Augmentation; do not modify the call
# signature of later stages. See docs/architecture/VFS_PREFLIGHT_DESIGN.md.
from pathlib import Path
from control_plane.preflight import runner, state, schemas
from control_plane.anya_gate import AnyaGate

_ROOT = Path(__file__).resolve().parent.parent  # bin/ → repo root
_RUN_ROOT = _ROOT / "03_VAULT" / "runtime_state"
_CHECKS = _ROOT / "vfs" / "checks"
_GRAD = state.GraduationFlag(_RUN_ROOT)
_STRICT = _GRAD.is_strict()
_SCENE = (
    (_ROOT / "vfs" / "rosters.md").read_text()
    + (_ROOT / "docs" / "architecture" / "lattice.yaml").read_text()
)
_TRIAGE = AnyaGate().triage
try:
    _MANIFEST = runner.execute_catalog(
        specs=runner.load_catalog(_CHECKS),
        run_root=_RUN_ROOT,
        scene_text=_SCENE,
        strict_mode=_STRICT,
        anya_triage_fn=_TRIAGE,
    )
except runner.CatalogError as e:
    print(f"[VFS_PREFLIGHT] CATALOG INVALID: {e}", file=sys.stderr)
    sys.exit(1)

# Print operator summary per spec §6.4 (implementer fills the three branches)
print(f"[VFS_PREFLIGHT] run_id={_MANIFEST.run_id}")
# ... per spec §6.4 ...

if _MANIFEST.halt_decision == "block_boot":
    sys.exit(1)
```

(The implementer fills in the summary printing exactly per spec §6.4; this snippet is structural, not final. NEVER add a CAMELOT_SKIP_PREFLIGHT / --skip-sovereign escape hatch — Task 7 already enforces rejection at the CLI level, and the awaken wiring has no override path.)

- [ ] **Step 3: Smoke-test on a clean venv**

```bash
.venv\Scripts\python.exe bin\awaken.py --stage 0
```

Expected: prints `[VFS_PREFLIGHT]` lines; if all CONFIRMED, exits 0 and creates `_graduated.flag`; if any REJECTED on first run, exits 0 with advisor summary.

If `--stage 0` is not supported, fall back to running the bare preflight invocation directly (see Task 7's CLI):

```bash
python -m control_plane.preflight --run
```

- [ ] **Step 4: Commit**

```bash
git add bin/awaken.py
git commit -m "feat(boot): awaken.py stage 0 wires VFS preflight before all other stages"
```

---

## Task 9: E2E in `tests/test_awaken.py` + AC verification (per spec §7.2 refinement)

**Files:**
- Modify: `tests/test_awaken.py` (add `test_preflight_block` and `test_preflight_first_run_advisor`)
- Create: `scripts/ops/check_preflight_ac.sh` (operator-runnable AC verification)
- Modify: `docs/architecture/VFS_PREFLIGHT_DESIGN.md` (final crosslink from §12)

- [x] **Step 1: Add preflight E2E to `tests/test_awaken.py`**

DONE 2026-08-14 — folded into `tests/preflight/test_awaken.py` (repo
layout keeps the preflight suite under `tests/preflight/`): advisor→strict
graduation + flag-location regression test, AC7 two-runs-distinct-dirs
test, plus the existing wrapper contract tests.

Locate the existing file. Append two tests:

```python
def test_preflight_first_run_advisor(tmp_path):
    """On a fresh tmp sandbox, preflight should run all 8 checks in
    advisor-mode and exit 0 even if some REJECT (first-run graduation signal)."""
    # arrange: copy synthetic vfs/ + checks/ to tmp, plus stub for anya_gate
    # act: invoke runner.execute_full_run via subprocess
    # assert: exit 0, manifest.halt_decision == 'continue',
    #         manifest.first_run == True, _graduated.flag was written.


def test_preflight_strict_halt_on_rejected(tmp_path):
    """After _graduated.flag is set, REJECTED halts the boot."""
    # arrange: same as above + write _graduated.flag
    # act: invoke runner.execute_full_run via subprocess
    # assert: exit 1, manifest.halt_decision == 'block_boot',
    #         manifest.first_run == False
```

Use `pytest`-style with `_fake_anya_triage` for test isolation — do not inadvertently require `anya_gate.py` to be importable in tests.

- [x] **Step 2: Write `scripts/ops/check_preflight_ac.sh`**

The script runs all 9 AC's manually:

```bash
#!/usr/bin/env bash
# check_preflight_ac.sh — manual acceptance verification per spec §7.2
set -euo pipefail
cd "$(dirname "$0")/../.."

echo "AC1: all 8 CONFIRMED on clean boot"
python -m control_plane.preflight --run || { echo "AC1 FAIL"; exit 1; }
...  # AC2..AC9 each as its own block with assertion
```

(Each AC is a section. Implementer writes all 9 with explicit assertion lines.)

- [x] **Step 3: AC walkthrough — run each AC and capture evidence**

DONE 2026-08-14 — evidence at `docs/architecture/VFS_PREFLIGHT_DESIGN_AC_EVIDENCE.md`
(8/8 mechanism ACs PASS; AC1 BLOCKED until substrate ports are listening):

```markdown
# AC Verification Evidence 2026-08-13

| AC | Result | Notes |
|----|--------|-------|
| AC1 | PASS / FAIL | run_id=… |
| AC2 | PASS / FAIL | timing: …ms |
| AC3 | PASS / FAIL | hash discoverable: … |
… | … | … |
```

- [x] **Step 4: Update spec §12 link**

DONE 2026-08-14 — `VFS_PREFLIGHT_DESIGN.md` §12 now links the AC evidence doc.

- [ ] **Step 5: Commit**

```bash
git add tests/test_awaken.py scripts/ops/check_preflight_ac.sh \
        docs/architecture/VFS_PREFLIGHT_DESIGN_AC_EVIDENCE.md \
        docs/architecture/VFS_PREFLIGHT_DESIGN.md
git commit -m "test(awaken): preflight E2E folded in + AC verification evidence + script"
```

---

## Self-Review

### Spec coverage walk

| Spec section | Plan task(s) |
|--------------|--------------|
| §1 Context | (already conveyed in commits) |
| §2 Out of scope | enforced by global constraints in plan header |
| §3.1 Boot entry | Task 8 (awaken.py wiring) |
| §3.2 Artifacts | Task 1 (init/state/schemas), Task 5 (8 YAMLs), Task 6 (probe runners), Task 9 (E2E) |
| §3.3 Reuse | Task 6 `anya_triage_fn` injection pattern |
| §4 Catalog 8 checks | Task 5 YAMLs + Task 4 probes + Task 6 wrappers |
| §5.1 Run identity | `utc_now_iso` in schemas.py (Task 1) + `execute_catalog` (Task 6) |
| §5.2 Execution flow | Task 6 `execute_catalog` |
| §5.3 Per-check JSON | `CheckResult` schema in Task 1 + write in Task 6 |
| §5.4 Run manifest | `RunManifest` schema in Task 1 + write in Task 6 |
| §5.5 Idempotency | Task 6 (per-second counter) + Task 9 idempotency test |
| §6.1 Failure matrix | Tasks 4 (probe primitives), 6 (runner), 7 (CLI rejects) |
| §6.2 First-run advisor | Task 1 (state.py) + Task 6 (`strict_mode` parameter) + Task 8 (wiring) |
| §6.3 Sovereign escape hatch DELETED | Task 7 (CLI explicit rejection) |
| §6.4 Operator summary | Task 8 (the printing block) |
| §7.1 Test layers | Tasks 1, 3, 4, 6, 7, 8, 9 |
| §7.2 AC1–AC9 | Task 9 (`check_preflight_ac.sh` + `_AC_EVIDENCE.md`) |
| §7.3 Code-review gate | Documentation in commits: every task should produce a clean diff that an independent reviewer can gate. |

### Placeholder scan

Two categories of "placeholder" tokens:

1. **Inside fixture bodies** (conftest.py in Task 1): the literal marker "#placeholder\n" is content of a synthetic test scaffolding file. Legitimate; not a plan-level placeholder.
2. **Inside Task 3's runner.py stubs**: a `NotImplementedError("Task 6 will implement …")` is intentional progress-marker per TDD discipline — Task 3 has test-first coverage, Task 6 fills the body. Not a plan-level placeholder.

No "TBD", "fill in later", "implement appropriately", or "add validation" type vague instructions present in any task body. Every code step has either `python ...` shell verification, a complete code block, or an explicit reference to a sibling task's interface.

### Type consistency

Final state of the API surface used across tasks:

- `schemas.CheckSpec.from_yaml_text(text: str) -> CheckSpec`
- `schemas.CheckResult` / `schemas.RunManifest` dataclasses with `to_json_dict()`
- `schemas.utc_now_iso() -> str` and `schemas.compute_catalog_hash(checks_root: Path) -> str`
- `state.GraduationFlag(root: Path)` with `path()`, `is_strict()`, `graduate()`, `revoke()`
- `probes.exec.run(command: list[str], timeout_s: int) -> ExecResult`
- `probes.exec.ExecResult(exit_code, stdout_excerpt, stderr_excerpt, duration_ms, timed_out)`
- Per-basic-probe signatures enumerated in Task 4 (each probe returns a tuple `(passed, details)`)
- `runner.load_catalog(checks_dir: Path) -> list[CheckSpec]` (raises `runner.CatalogError`)
- `runner.execute_check(spec: CheckSpec, *, strict_mode: bool, anya_triage_fn) -> CheckResult`
- `runner.execute_catalog(*, specs: list[CheckSpec], run_root: Path, scene_text: str, strict_mode: bool, anya_triage_fn) -> RunManifest`
- `anya_triage_fn(raw_intent: str) -> dict | TriageScore | sentinel` — strictly advisory; preflight never uses it to decide evidence_class.

All 9 tasks reference these names consistently. The public CLI in `__main__.py` (Task 7) calls `execute_catalog` only; `execute_check` is internal to the runner package.

---

## Execution Handoff

Plan written to `docs/superpowers/plans/2026-08-13-vfs-preflight.md`. Pairs with `docs/architecture/VFS_PREFLIGHT_DESIGN.md` and `docs/adr/0006-vfs-preflight-strict-mode.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — fresh subagent per task, two-stage review between tasks. Best fit because each task has independent verification surface.
2. **Inline Execution** — execute tasks in this session using `executing-plans`, with batch checkpoints for review.

**If Subagent-Driven chosen:** I'll load `subagent-driven-development` next.
**If Inline Execution chosen:** I'll load `executing-plans` next.

Either way: nothing in this plan writes to `PROVENANCE_LEDGER.md` directly (Task 8's wiring respects the hook chain by being a stage, not a hook-implementer). No patches to `runic_router.py`, `cartridges/`, `01_KERNEL/`, `04_KINETIC/`, or `squires/` are present in this plan — augmentation only, per spec §2 + ADR 0006.
