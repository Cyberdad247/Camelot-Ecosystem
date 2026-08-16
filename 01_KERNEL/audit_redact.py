#!/usr/bin/env python3
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-
"""
01_KERNEL/audit_redact.py — CAMELOT-GCMN activation ADR §8 Step 2/3 CLI.

Activation ADR §8 contract:
  Step 2 — Audit Recall
    python 01_KERNEL/audit_redact.py --namespace GCMN_STUB --tombstone STUB_REVOKED
    For each `[GCMN-STUB]` log line emitted while the flag was ON, emit to stdout:
      <original>  // tombstone_id=<sha256[:16]> tombstone={<json>}

  Step 3 — Dead-Letter (opt-in relocate)
    python 01_KERNEL/audit_redact.py --namespace GCMN_STUB --tombstone STUB_REVOKED --relocate /var/camelot/cold/...
    Records the relocation in PROVENANCE_LEDGER.md (via operator; this script
    writes the archive file but not the ledger).

Idempotency contract (CAMELOT-GCMN-GOVERNANCE §8.2):
  * True idempotency via tombstone_id = sha256(original_line_content)[:16].
  * Every emitted marker carries the tombstone_id field.
  * Re-runs skip lines whose fingerprint already appears anywhere in the file
    (either as a tombstone_id in a marker OR as legacy tombstoned_at marker
    that survived from prior tooling runs).
  * Lines whose bare content contains "tombstoned_at" are also skipped —
    defensive fallback for legacy markers without tombstone_id.

Exit codes:
  0 — success (matched lines processed, OR zero matches).
  1 — invalid arguments (legacy; argparse choices handle this with exit 2).
  2 — file/IO error (source missing, relocate target not writable, etc.).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_DECISION_DOC = "docs/adr/gcmn_stubs_activation.md"

# Namespace-to-tag map. The canonical namespace `GCMN_STUB` is the public
# surface. Adding new namespaces requires adding the corresponding tag here
# + adjusting control_plane/runic_router._dispatch_gcmn_stub to emit the tag.
_NAMESPACE_TAG: dict[str, str] = {
    "GCMN_STUB": "[GCMN-STUB]",
}

# Fingerprint detection — matches a tombstone_id field embedded in any marker.
_TOMBSTONE_ID_RE = re.compile(r"tombstone_id=([0-9a-f]{16})")


def _line_fingerprint(original: str) -> str:
    """Deterministic tombstone_id. SHA-256 of the cleaned original line, truncated.

    `original` is the line content BEFORE any tombstone marker was appended.
    """
    return hashlib.sha256(original.encode("utf-8")).hexdigest()[:16]


def _strip_marker(raw_line: str) -> str:
    """Return the original line content, removing any tombstone marker suffix.

    Handles both the new shape `// tombstone_id=... tombstone={...}` and the
    legacy shape `// tombstone={...tombstoned_at......}`.
    """
    # New shape: strip from the first `// tombstone_id=` onward.
    sep = "  // tombstone_id="
    if sep in raw_line:
        raw_line = raw_line.split(sep, 1)[0]
    # Legacy / step-1 shape: strip from the first `// tombstone=` onward.
    sep2 = "  // tombstone="
    if sep2 in raw_line:
        raw_line = raw_line.split(sep2, 1)[0]
    return raw_line.rstrip()


def _collect_existing_fingerprints(text: str) -> set[str]:
    """Scan the ledger text for any tombstone_id already in any marker.

    Also scans for the legacy `tombstoned_at=YYYY-...` form so legacy
    tombstoned lines are recognized and skipped on re-run.
    """
    fps: set[str] = set()
    for raw in text.splitlines():
        for m in _TOMBSTONE_ID_RE.finditer(raw):
            fps.add(m.group(1))
        # Also record a deterministic fingerprint for each legacy tombstoned
        # line that lacks an inline tombstone_id. This way legacy-marked lines
        # are still skipped on re-run.
        if "tombstoned_at" in raw and "// tombstone_id=" not in raw:
            cleaned = _strip_marker(raw)
            fps.add(_line_fingerprint(cleaned))
    return fps


def _scan_and_tombstone(
    src_path: Path,
    namespace: str,
    marker: str,
    out_fp=None,
) -> list[str]:
    """Read src_path line-by-line; emit tombstoned copies of fresh matches.

    Returns the list of tombstoned lines (used by tests + dry-run).
    """
    tag = _NAMESPACE_TAG[namespace]
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = src_path.read_text(encoding="utf-8")
    existing_fps = _collect_existing_fingerprints(text)
    out_lines: list[str] = []
    for raw_line in text.splitlines():
        if tag not in raw_line:
            continue
        original = _strip_marker(raw_line)
        fp = _line_fingerprint(original)
        # Already tombstoned: skip on re-run (the new shape's tombstone_id
        # appears in the existing_fps set; the legacy shape's tombstoned_at
        # substring is caught explicitly as a fallback).
        if fp in existing_fps or "tombstoned_at" in raw_line:
            continue
        tombstone_obj = {
            "tombstone_id": fp,
            "tombstoned_at": now_iso,
            "tombstone": marker,
            "decision_doc": _DECISION_DOC,
            "namespace": namespace,
            "tombstoned_by": "01_KERNEL/audit_redact.py",
        }
        tombstone_json = json.dumps(tombstone_obj, ensure_ascii=False)
        out_line = f"{original}  // tombstone_id={fp} tombstone={tombstone_json}"
        out_lines.append(out_line)
        if out_fp is not None:
            out_fp.write(out_line + "\n")
    return out_lines


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="01_KERNEL.audit_redact",
        description=(
            "CAMELOT-GCMN activation ADR §8 audit redactor. Emits tombstone "
            "markers for previously emitted `[GCMN-STUB]` log lines (default "
            "namespace `GCMN_STUB`); optionally relocates to a cold archive."
        ),
    )
    parser.add_argument(
        "--namespace",
        default="GCMN_STUB",
        choices=list(_NAMESPACE_TAG.keys()),
        help="Logical namespace to scope the redactor (default: GCMN_STUB).",
    )
    parser.add_argument(
        "--tombstone",
        default="STUB_REVOKED",
        help="Tombstone marker to emit on each match (default: STUB_REVOKED).",
    )
    parser.add_argument(
        "--ledger-path",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "docs" / "PROVENANCE_LEDGER.md",
        help="Source ledger/log file to scan (default: docs/PROVENANCE_LEDGER.md).",
    )
    parser.add_argument(
        "--relocate",
        type=Path,
        default=None,
        help=(
            "If set, write tombstoned lines to <relocate>/cold_archive_<ns>_<iso>"
            ".jsonl INSTEAD OF stdout. Creates the directory if missing."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview tombstone counts without writing.",
    )
    args = parser.parse_args()

    if not args.ledger_path.exists():
        print(
            f"FATAL: ledger path {args.ledger_path} not found.",
            file=sys.stderr,
        )
        return 2

    if args.dry_run:
        matched = _scan_and_tombstone(args.ledger_path, args.namespace, args.tombstone)
        print(f"DRY-RUN: would tombstone {len(matched)} matching lines", file=sys.stderr)
        for line in matched:
            print(line)
        return 0

    if args.relocate is not None:
        try:
            args.relocate.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"FATAL: could not create relocate dir {args.relocate}: {e}", file=sys.stderr)
            return 2
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out_path = args.relocate / f"cold_archive_{args.namespace}_{ts}.jsonl"
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                matched = _scan_and_tombstone(args.ledger_path, args.namespace, args.tombstone, f)
        except OSError as e:
            print(f"FATAL: could not write to {out_path}: {e}", file=sys.stderr)
            return 2
        print(
            f"RELOCATE: tombstoned {len(matched)} lines to {out_path} "
            f"(tombstone={args.tombstone!r}, namespace={args.namespace!r})",
            file=sys.stderr,
        )
        return 0

    # Default — audit recall: emit to stdout. Consumer SIEMs filter on
    # `tombstone != null` to skip.
    matched = _scan_and_tombstone(args.ledger_path, args.namespace, args.tombstone)
    for line in matched:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
