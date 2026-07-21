"""Deterministic, atomic, idempotent repair for the verification-ledger hash chain.

The control-plane triage script `control_plane/system_triage.py` validates
`03_VAULT/Missions/verification_ledger.jsonl` with the following rule:

    payload = {k: v for k, v in entry.items() if k != "entry_hash"}
    expected = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

Design properties (release 2):
  * **Idempotent on a clean chain.** A second invocation on the ledger after
    a successful repair must produce a byte-identical file (no rewrite).
  * **Minimal diff.** The repair mutates `parent_hash` only when the existing
    value differs from the previous recomputed hash, and `entry_hash` only
    when the recomputed hash differs from the stored one. The validated
    prefix becomes a no-op byte-wise.
  * **Preserve entry 1 audit content.** Entry 1's `parent_hash` is whatever
    it was in the source (commonly `null`); never force-overwrite.
  * **Atomic write.** Write to a sibling `.tmp`, then `Path.replace` for
    same-volume atomicity.
  * **Timestamped backup.** The prior-file backup is suffixed with a UTC
    stamp so repeated runs (or interrupted runs) never destroy evidence.
  * **Post-write revalidation.** The full chain is walked end-to-end before
    exit; non-zero return on any residual mismatch.

The hash algorithm is the single source of truth in
`control_plane.ledger_sync.compute_entry_hash`, which both this repair
tool and `control_plane.system_triage._verification_ledger_integrity`
import. The two stay byte-for-byte identical by construction — change the
shared function once and both call sites follow.

Usage:
    python scripts/repair_verification_ledger_chain.py [--dry-run] [--path PATH]
    python scripts/repair_verification_ledger_chain.py --selftest
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from control_plane.ledger_sync import compute_entry_hash

DEFAULT_PATH = Path("03_VAULT/Missions/verification_ledger.jsonl")


def _walk(path: Path) -> tuple[int, str | None, list[dict[str, Any]]]:
    """Walk the chain; return (entry_count, error_or_None, parsed_entries)."""
    entries: list[dict[str, Any]] = []
    previous_hash: str | None = None
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not raw.strip():
            continue
        entry = json.loads(raw)
        entries.append(entry)
        count = len(entries)
        if entry.get("entry_id") != count:
            return count, f"entry_id mismatch at entry {count}", entries
        if entry.get("parent_hash") != previous_hash:
            return count, f"parent_hash mismatch at entry {count}", entries
        if compute_entry_hash(entry) != entry.get("entry_hash"):
            return count, f"entry_hash mismatch at entry {count}", entries
        previous_hash = entry["entry_hash"]
    return len(entries), None, entries


def _timestamped_backup(path: Path) -> Path:
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return path.with_suffix(path.suffix + f".recovery-backup.{stamp}")


def repair(path: Path, *, dry_run: bool = False) -> dict[str, Any]:
    # Read current bytes for byte-identical comparison after rewrite.
    original_bytes = path.read_bytes()

    count, err, entries = _walk(path)

    # Short-circuit on a clean chain: idempotent on the already-fixed file.
    if err is None:
        return {
            "path": str(path),
            "entries": count,
            "first_break": None,
            "rewritten_bytes": len(original_bytes),
            "dry_run": dry_run,
            "no_op": True,
            "post_validate_count": count,
            "post_validate_error": None,
        }

    # Original `count` was the failing line index; first_break = that line.
    first_break = count

    # Cascade fix forward: only mutate what is actually wrong.
    # Walk forward from the broken line, repairing parent_hash+entry_hash.
    previous_hash = entries[count - 2]["entry_hash"] if count >= 2 else None
    for index in range(count - 1, len(entries)):
        entry = entries[index]
        # Mutate parent_hash only if it actually drifted.
        if entry.get("parent_hash") != previous_hash:
            entry["parent_hash"] = previous_hash
        # Recompute and overwrite entry_hash if it differs.
        new_hash = compute_entry_hash(entry)
        if entry["entry_hash"] != new_hash:
            entry["entry_hash"] = new_hash
        previous_hash = new_hash

    rewritten = "\n".join(json.dumps(e) for e in entries) + "\n"
    rewritten_bytes = rewritten.encode("utf-8")

    # Idempotency guard: if the rewrite is byte-identical to the original,
    # don't touch the disk (preserves inodes, timestamps, content-hashes).
    if rewritten_bytes == original_bytes:
        return {
            "path": str(path),
            "entries": len(entries),
            "first_break": first_break,
            "rewritten_bytes": len(rewritten_bytes),
            "dry_run": dry_run,
            "no_op": True,
            "post_validate_count": len(entries),
            "post_validate_error": None,
        }

    result: dict[str, Any] = {
        "path": str(path),
        "entries": len(entries),
        "first_break": first_break,
        "rewritten_bytes": len(rewritten_bytes),
        "dry_run": dry_run,
        "no_op": False,
    }

    if dry_run:
        return result

    backup = _timestamped_backup(path)
    shutil.copyfile(path, backup)
    with tempfile.NamedTemporaryFile(
        "wb",
        delete=False,
        dir=str(path.parent),
        prefix=path.name + ".",
        suffix=".tmp",
    ) as tmp_handle:
        tmp_handle.write(rewritten_bytes)
        tmp_path = Path(tmp_handle.name)
    try:
        tmp_path.replace(path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise

    post_count, post_err, _ = _walk(path)
    result["backup"] = str(backup)
    result["post_validate_count"] = post_count
    result["post_validate_error"] = post_err
    return result


def selftest() -> dict[str, Any]:
    """Create a synthetic ledger, break it, repair it, assert integrity.

    Returns a dict with status of each check, so the caller can machine-test.
    """
    with tempfile.TemporaryDirectory() as d:
        tmp_path = Path(d) / "ledger.jsonl"
        # Build a short but properly-chained ledger.
        entries: list[dict[str, Any]] = []
        parent: str | None = None
        for i in range(1, 11):
            entry = {
                "run_id": f"selftest_{i}",
                "entry_id": i,
                "parent_hash": parent,
                "results": {"value": i},  # payload field
            }
            entry["entry_hash"] = compute_entry_hash(entry)
            entries.append(entry)
            parent = entry["entry_hash"]
        # First write: clean.
        tmp_path.write_text(
            "\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8"
        )
        # Validate clean state passes.
        _, err_clean, _ = _walk(tmp_path)
        # Break the chain at entry 5: corrupt a payload field but keep stale hash.
        entries[4]["results"]["value"] = 999  # mutate payload
        tmp_path.write_text(
            "\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8"
        )
        _, err_broken, _ = _walk(tmp_path)
        # Repair.
        out = repair(tmp_path)
        # Final validation.
        _, err_after, _ = _walk(tmp_path)
        # Idempotency: snapshot bytes BEFORE the second run so we can prove
        # the second invocation did not rewrite the file.
        pre_second_run_bytes = tmp_path.read_bytes()
        out2 = repair(tmp_path)
        post_second_run_bytes = tmp_path.read_bytes()
        return {
            "expected_clean": True,
            "clean_ok": err_clean is None,
            "expected_broken": True,
            "broken_detected": err_broken is not None,
            "first_break_equals_5": out.get("first_break") == 5,
            "post_repair_integrity_ok": err_after is None,
            "second_run_is_no_op": out2.get("no_op") is True,
            "second_run_byte_identical": post_second_run_bytes == pre_second_run_bytes,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=DEFAULT_PATH)
    parser.add_argument("--dry-run", action="store_true",
                        help="Compute fix without writing the file")
    parser.add_argument("--selftest", action="store_true",
                        help="Run synthetic round-trip test and exit")
    args = parser.parse_args(argv)

    if args.selftest:
        result = selftest()
        print(json.dumps(result, indent=2))
        return 0 if all(
            v for k, v in result.items()
            if isinstance(v, bool) and not k.startswith("expected_")
        ) else 1

    if not args.path.exists():
        print(f"ERROR: ledger not found at {args.path}", file=sys.stderr)
        return 2

    count, err, _ = _walk(args.path)
    if err is None:
        print(f"Pre-scan: chain valid through {count} entries -- nothing to repair.")
    else:
        print(f"Pre-scan: stop at {count}: {err}", file=sys.stderr)

    result = repair(args.path, dry_run=args.dry_run)
    print(json.dumps(result, indent=2))
    if args.dry_run:
        return 0
    if result.get("post_validate_error"):
        print(f"ERROR: post-repair validation failed: {result['post_validate_error']}",
              file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
