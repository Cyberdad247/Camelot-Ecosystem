"""Tests for 01_KERNEL/audit_redact.py — CAMELOT-GCMN activation ADR §8 Step 2/3 CLI.

Subprocess-based black-box tests. Each test uses ``tmp_path`` to keep the
PROVENANCE_LEDGER fixture isolated from the live ledger.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT_REDACT = REPO_ROOT / "01_KERNEL" / "audit_redact.py"
PY = sys.executable


@pytest.fixture
def seed_ledger(tmp_path: Path) -> Path:
    """Synthetic ledger carrying 3 fresh `[GCMN-STUB]` lines + 1 pre-tombstoned."""
    lines = [
        "## [2026-07-15] GCMN_ACTIVATION_OPERATOR_HITL_RATIFIED",
        "| 2026-07-15T05:30:00Z | SIR_SENTINEL | general health-check",
        "[GCMN-STUB] rune=//SYNC_KBA_DATABASES_SQLCIPHER status=STUB_INERT entry=alpha",
        "[GCMN-STUB] rune=//LOCK_BIFROST_mTLS_KYBER768 status=STUB_INERT entry=beta",
        "[GCMN-STUB] rune=//ENGAGE_RUST_IRON_DAEMON status=STUB_INERT entry=gamma",
        "| 2026-07-15T06:00:00Z | SIEM | general-health-check",
        "[GCMN-STUB] tombstoned_at=2026-07-15T07:00:00Z tombstone=STUB_REVOKED pre-tombstoned",
    ]
    target = tmp_path / "ledger.md"
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def _run(args: list[str], ledger: Path, **kwargs) -> subprocess.CompletedProcess:
    cmd = [
        PY,
        str(AUDIT_REDACT),
        "--namespace=GCMN_STUB",
        "--tombstone=STUB_REVOKED",
        "--ledger-path",
        str(ledger),
    ] + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=20,
        **kwargs,
    )


def test_dry_run_counts_matches_without_writing(tmp_path: Path, seed_ledger: Path) -> None:
    res = _run(["--dry-run"], seed_ledger)
    assert res.returncode == 0
    assert "DRY-RUN" in res.stderr
    # The post-fix marker shape is `<original>  // tombstone_id=<fp> tombstone={<json>}`.
    # A line carrying the new marker contains both `// tombstone_id=` and ` tombstone=`
    # (the JSON delimiter). Detect via the latter (`<space>tombstone=<brace>`).
    matched = sum(1 for line in res.stdout.splitlines() if " tombstone=" in line)
    assert matched == 3  # 4 GCMN-STUB lines, 1 already tombstoned → 3 fresh
    assert not list(tmp_path.glob("cold_archive_*.jsonl"))


def test_default_stdout_emits_tombstone_markers(seed_ledger: Path) -> None:
    res = _run([], seed_ledger)
    assert res.returncode == 0
    matched = sum(1 for line in res.stdout.splitlines() if " tombstone=" in line)
    assert matched == 3
    for line in res.stdout.splitlines():
        if " tombstone=" in line:
            assert '"tombstone": "STUB_REVOKED"' in line
            assert '"decision_doc": "docs/adr/gcmn_stubs_activation.md"' in line
            assert '"namespace": "GCMN_STUB"' in line


def test_relocate_writes_cold_archive_and_suppresses_stdout(
    seed_ledger: Path, tmp_path: Path
) -> None:
    target = tmp_path / "cold"
    res = _run(["--relocate", str(target)], seed_ledger)
    assert res.returncode == 0
    archives = list(target.glob("cold_archive_GCMN_STUB_*.jsonl"))
    assert len(archives) == 1
    payload = archives[0].read_text(encoding="utf-8")
    matched = sum(1 for line in payload.splitlines() if " tombstone=" in line)
    assert matched == 3
    assert res.stdout.strip() == ""
    assert "RELOCATE" in res.stderr


def test_idempotent_against_double_tombstoning(seed_ledger: Path) -> None:
    """Re-running the redactor must produce 0 new tombstone lines (already-tombstoned is skipped)."""
    first = _run([], seed_ledger)
    assert first.returncode == 0
    # Now replay the lines into the fixture (simulating a SIEM re-emission)
    replayed = seed_ledger.read_text(encoding="utf-8") + "\n" + first.stdout
    seed_ledger.write_text(replayed, encoding="utf-8")
    second = _run([], seed_ledger)
    assert second.stdout == "", f"expected idempotent no-op, got: {second.stdout!r}"


def test_unknown_namespace_rejected_at_argparse(seed_ledger: Path) -> None:
    res = _run(["--namespace", "FAKE_NS"], seed_ledger)
    assert res.returncode == 2
    assert "argument --namespace" in res.stderr


def test_missing_ledger_path_returns_2(tmp_path: Path) -> None:
    res = _run([], tmp_path / "does-not-exist.md")
    assert res.returncode == 2
    assert "FATAL: ledger path" in res.stderr


def test_canonical_tombstone_marker_shape(seed_ledger: Path) -> None:
    """Every emitted marker must carry the canonical keys + the byline."""
    import json as _json

    res = _run([], seed_ledger)
    for line in res.stdout.splitlines():
        if " tombstone=" in line:  # matches both `tombstone_id=` and JSON `tombstone={`
            payload_str = line.split(" tombstone=", 1)[1].strip()
            payload = _json.loads(payload_str)
            assert set(payload.keys()) >= {
                "tombstone_id",
                "tombstoned_at",
                "tombstone",
                "decision_doc",
                "namespace",
                "tombstoned_by",
            }
            assert payload["tombstoned_by"] == "01_KERNEL/audit_redact.py"
            # ISO 8601 UTC
            assert payload["tombstoned_at"].endswith("Z")
            # tombstone_id is a 16-hex-char SHA-256 prefix.
            assert len(payload["tombstone_id"]) == 16
            assert all(c in "0123456789abcdef" for c in payload["tombstone_id"])


def test_tombstone_id_round_trip(seed_ledger: Path) -> None:
    """tombstone_id == sha256(original_clean_line)[:16]. Idempotency anchor."""
    import hashlib as _hash

    res = _run([], seed_ledger)
    assert res.returncode == 0
    tombstone_lines = [line for line in res.stdout.splitlines() if "// tombstone_id=" in line]
    assert len(tombstone_lines) == 3  # alpha, beta, gamma
    for line in tombstone_lines:
        # Reconstruct the original line (everything before `  // tombstone_id=`).
        original = line.split("  // tombstone_id=", 1)[0]
        # Split on `<space>tombstone=` (no slashes) to land on the JSON delimiter.
        payload_segment = line.split(" tombstone=", 1)[1].strip()
        import json as _json
        payload = _json.loads(payload_segment)
        expected_fp16 = _hash.sha256(original.encode("utf-8")).hexdigest()[:16]
        assert payload["tombstone_id"] == expected_fp16
        assert f"// tombstone_id={expected_fp16}" in line
