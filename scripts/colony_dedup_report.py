"""Full-content duplicate report for CLARITY_CORE (SWEEP/MASON extension).

Two-phase dedup:

1. Candidate pass — SWEEP's cheap 128-byte header-hash flags (the canonical
   triage count; fast, but over-flags files that merely share boilerplate
   prefixes, e.g. two different vite.config.ts files).
2. Verification pass — full-content SHA-256. The SCAN squire already hashes
   every file completely (squires/scan.py: `sha256(raw).hexdigest()[:12]`),
   so byte-identical grouping costs no extra disk reads. Each SWEEP candidate
   flag is classified TRUE_DUPLICATE (same full hash as its header owner) or
   PREFIX_ONLY_FP (same header, content differs).

Full-content grouping is the ground truth: it also catches binary duplicates
that SWEEP's header pass deliberately skips.

Usage:
    .venv\\Scripts\\python.exe scripts/colony_dedup_report.py [path]
"""

from __future__ import annotations

import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from squires.scan import scan  # noqa: E402
from squires.sweep import sweep  # noqa: E402

# Mirror SWEEP's minimum-size rule: files under 64 bytes carry no useful
# dedup signal (every empty file would otherwise be a "duplicate").
_MIN_BYTES = 64


def _fmt_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} GB"


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT_ROOT
    print(f"Full-content dedup over: {root}")

    records = list(scan(root))
    by_rel = {rec.rel: rec for rec in records}
    print(f"SCAN: {len(records)} files")

    # --- Phase 1: SWEEP header-hash candidates (canonical triage count) ---
    sweep_report = sweep(iter(records))
    candidates = [f for f in sweep_report.flags if f.kind == "duplicate_content"]
    print(f"SWEEP header-hash candidates: {len(candidates)}")

    # --- Phase 2: full-content SHA-256 ground truth ---
    by_hash: dict[str, list[str]] = defaultdict(list)
    for rec in records:
        if rec.sha256 and rec.size >= _MIN_BYTES:
            by_hash[rec.sha256].append(rec.rel)
    true_groups = {h: rels for h, rels in by_hash.items() if len(rels) > 1}

    true_files = sum(len(rels) for rels in true_groups.values())
    redundant_files = sum(len(rels) - 1 for rels in true_groups.values())
    redundant_bytes = sum(
        (by_rel[rels[0]].size) * (len(rels) - 1) for rels in true_groups.values()
    )

    # Classify each SWEEP candidate against full-content hashes
    verified_flags: list = []
    false_positive_flags: list = []
    for flag in candidates:
        owner = flag.detail.split("same header as ", 1)[-1].strip()
        rec_file = by_rel.get(flag.file)
        rec_owner = by_rel.get(owner)
        same_content = (
            rec_file is not None
            and rec_owner is not None
            and rec_file.sha256 != ""
            and rec_file.sha256 == rec_owner.sha256
        )
        if same_content:
            verified_flags.append(flag)
        else:
            false_positive_flags.append(flag)

    # Files in true groups that no SWEEP candidate covers (binaries, sub-64B)
    candidate_covered = {f.file for f in verified_flags} | {
        f.detail.split("same header as ", 1)[-1].strip() for f in verified_flags
    }
    missed_files = sorted(
        rel for rels in true_groups.values() for rel in rels if rel not in candidate_covered
    )

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []
    lines += [
        "# CLARITY_CORE Duplicate Content Report — Full-Content SHA-256",
        f"**Generated:** {ts}",
        f"**Root:** `{root}`",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| SWEEP header-hash candidates | {len(candidates):,} |",
        f"| Verified true duplicates | {len(verified_flags):,} |",
        f"| Prefix-only false positives | {len(false_positive_flags):,} |",
        f"| Ground-truth duplicate groups (full SHA-256) | {len(true_groups):,} |",
        f"| Files involved in true duplication | {true_files:,} |",
        f"| Redundant files (removable copies) | {redundant_files:,} |",
        f"| Redundant bytes reclaimable | {_fmt_bytes(redundant_bytes)} |",
        f"| True dupes SWEEP missed (binary / sub-64B) | {len(missed_files):,} files |",
        "",
        "Method: SWEEP candidates use an identical-first-128-bytes heuristic; the",
        "verification pass compares full-content SHA-256 (computed by the SCAN squire",
        "for every file ≤ 2 MB). A candidate counts as a true duplicate only if its",
        "full hash equals its header-owner's hash. Ground-truth groups additionally",
        "cover binary files, which SWEEP's header pass skips.",
        "",
        "## Verified duplicate groups (full-content SHA-256)",
        "",
        "Sorted by wasted bytes (descending). Every file in a group is",
        "byte-identical; all but one are removable.",
        "",
    ]

    for i, (h, rels) in enumerate(
        sorted(true_groups.items(), key=lambda kv: -by_rel[kv[1][0]].size * (len(kv[1]) - 1)),
        1,
    ):
        size = by_rel[rels[0]].size
        lines.append(
            f"### Group {i} — `{h}` · {len(rels)} files · "
            f"{_fmt_bytes(size)} each · {_fmt_bytes(size * (len(rels) - 1))} wasted"
        )
        lines.append("")
        for rel in sorted(rels):
            marker = " *(binary)*" if by_rel[rel].is_binary else ""
            lines.append(f"- `{rel}`{marker}")
        lines.append("")

    lines += [
        "## SWEEP candidates classified as TRUE duplicates",
        "",
        f"{len(verified_flags)} of {len(candidates)} header-hash candidates are",
        "byte-identical to their header owner (full SHA-256 match).",
        "",
    ]
    for flag in sorted(verified_flags, key=lambda f: f.file):
        owner = flag.detail.split("same header as ", 1)[-1].strip()
        lines.append(f"- `{flag.file}` == `{owner}`")

    lines += [
        "",
        "## SWEEP candidates that are prefix-only FALSE POSITIVES",
        "",
        "These share their first 128 bytes with the owner but differ afterwards —",
        "they must NOT be treated as duplicates.",
        "",
    ]
    for flag in sorted(false_positive_flags, key=lambda f: f.file):
        owner = flag.detail.split("same header as ", 1)[-1].strip()
        lines.append(f"- `{flag.file}` — shares header with `{owner}`, content differs")

    lines += [
        "",
        "## True duplicates SWEEP's header pass missed",
        "",
        "Binary files (skipped by SWEEP) or sub-64-byte files that are nevertheless",
        f"byte-identical to another file: {len(missed_files)} file(s).",
        "",
    ]
    for rel in missed_files:
        lines.append(f"- `{rel}`")

    lines += [
        "",
        "---",
        "",
        "*Generated by CLARITY_CORE v1.0.0 — Squire Colony (full-content dedup extension)*",
        "*Canonical count source: colony_report.md — SWEEP Report table*",
    ]

    out = root / "colony_dedup_report.md" if root.is_dir() else root.parent / "colony_dedup_report.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(
        f"Wrote {out}\n"
        f"  candidates={len(candidates)} verified_true={len(verified_flags)} "
        f"false_positives={len(false_positive_flags)}\n"
        f"  true_groups={len(true_groups)} redundant_files={redundant_files} "
        f"redundant_bytes={_fmt_bytes(redundant_bytes)} missed={len(missed_files)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
