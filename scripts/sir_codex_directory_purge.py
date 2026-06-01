#!/usr/bin/env python3
"""
Sir Codex Sovereign Directory Audit Forge.

Audit-first resource reduction utility for constrained local systems.
Default mode is non-destructive. Destructive purge requires --execute and a
typed confirmation phrase after the Scorpion forensic review is written.
"""

from __future__ import annotations

import argparse
import fnmatch
import gzip
import hashlib
import json
import logging
import os
import shutil
import sys
import tarfile
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


DEFAULT_EXCLUDES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "target",
    "dist",
    "build",
    ".next",
    ".turbo",
}

CACHE_DIR_NAMES = {
    ".cache",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".parcel-cache",
    ".vite",
    "__pycache__",
    "pip-cache",
    "npm-cache",
}

DEPENDENCY_DIR_NAMES = {
    "node_modules",
    ".venv",
    "venv",
    "target",
}

BINARY_EXTENSIONS = {
    ".dll",
    ".dylib",
    ".exe",
    ".lib",
    ".o",
    ".obj",
    ".pdb",
    ".rlib",
    ".so",
}

ARCHIVE_EXTENSIONS = {
    ".7z",
    ".gz",
    ".rar",
    ".tar",
    ".tgz",
    ".xz",
    ".zip",
    ".zst",
}

LOG_EXTENSIONS = {".log", ".trace", ".tmp", ".bak", ".old"}

SAFE_PURGE_REASONS = {
    "cache_sprawl",
    "dormant_log",
    "duplicate_binary",
}


@dataclass
class Finding:
    path: str
    kind: str
    reason: str
    size_bytes: int
    modified_utc: str
    sha256: str | None = None
    duplicate_of: str | None = None
    action: str = "review"
    entropy_score: int = 0


@dataclass
class AuditReport:
    root: str
    generated_utc: str
    scanned_files: int = 0
    scanned_dirs: int = 0
    total_bytes: int = 0
    candidate_bytes: int = 0
    findings: list[Finding] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def configure_logging(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "sir_codex_directory_purge.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def human_bytes(size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def should_exclude(path: Path, root: Path, exclude_globs: Iterable[str]) -> bool:
    rel = path.relative_to(root).as_posix()
    if any(part in DEFAULT_EXCLUDES for part in path.parts):
        return True
    return any(fnmatch.fnmatch(rel, pattern) for pattern in exclude_globs)


def file_sha256(path: Path, max_bytes: int | None = None) -> str:
    hasher = hashlib.sha256()
    remaining = max_bytes
    with path.open("rb") as handle:
        while True:
            if remaining is not None and remaining <= 0:
                break
            chunk_size = 1024 * 1024
            if remaining is not None:
                chunk_size = min(chunk_size, remaining)
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
            if remaining is not None:
                remaining -= len(chunk)
    return hasher.hexdigest()


def mtime_utc(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()


def classify_file(
    path: Path,
    root: Path,
    size: int,
    age_days: float,
    dormant_days: int,
    large_mb: int,
) -> tuple[str, str, str, int] | None:
    suffix = path.suffix.lower()
    parent_names = {part.lower() for part in path.parts}
    rel = path.relative_to(root).as_posix()

    if parent_names & CACHE_DIR_NAMES:
        return "cache", "cache_sprawl", "purge", 90

    if suffix in LOG_EXTENSIONS and age_days >= dormant_days:
        return "log", "dormant_log", "purge", 70

    if suffix in BINARY_EXTENSIONS and size >= large_mb * 1024 * 1024:
        return "binary", "large_binary_review", "review", 55

    if suffix in ARCHIVE_EXTENSIONS and age_days >= dormant_days:
        return "archive", "low_frequency_archive", "archive", 45

    if any(part.lower() in DEPENDENCY_DIR_NAMES for part in path.parts):
        return "dependency", "orphaned_dependency_review", "review", 50

    if size >= large_mb * 1024 * 1024 and not rel.startswith("03_VAULT/runtime_state"):
        return "large_file", "large_file_review", "archive", 40

    return None


def scan_directory(
    root: Path,
    output_dir: Path,
    exclude_globs: list[str],
    dormant_days: int,
    large_mb: int,
) -> AuditReport:
    report = AuditReport(root=str(root), generated_utc=utc_now())
    hashes_by_size: dict[int, list[tuple[Path, str]]] = {}
    now = time.time()

    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        current_dir = Path(dirpath)
        report.scanned_dirs += 1
        dirnames[:] = [
            name
            for name in dirnames
            if not should_exclude(current_dir / name, root, exclude_globs)
        ]

        for filename in filenames:
            path = current_dir / filename
            try:
                if should_exclude(path, root, exclude_globs):
                    continue
                stat = path.stat()
                size = stat.st_size
                age_days = (now - stat.st_mtime) / 86400
                report.scanned_files += 1
                report.total_bytes += size
                hashes_by_size.setdefault(size, []).append((path, ""))

                classification = classify_file(
                    path, root, size, age_days, dormant_days, large_mb
                )
                if classification is None:
                    continue
                kind, reason, action, score = classification
                report.findings.append(
                    Finding(
                        path=path.relative_to(root).as_posix(),
                        kind=kind,
                        reason=reason,
                        size_bytes=size,
                        modified_utc=mtime_utc(path),
                        action=action,
                        entropy_score=score,
                    )
                )
                report.candidate_bytes += size
            except OSError as exc:
                report.errors.append(f"{path}: {exc}")

    mark_duplicate_binaries(root, report, hashes_by_size)
    report.findings.sort(key=lambda item: (item.action != "purge", -item.size_bytes, item.path))
    return report


def mark_duplicate_binaries(
    root: Path, report: AuditReport, hashes_by_size: dict[int, list[tuple[Path, str]]]
) -> None:
    existing = {finding.path for finding in report.findings}
    for size, paths in hashes_by_size.items():
        if size <= 0 or len(paths) < 2:
            continue
        binary_paths = [path for path, _ in paths if path.suffix.lower() in BINARY_EXTENSIONS]
        if len(binary_paths) < 2:
            continue

        groups: dict[str, list[Path]] = {}
        for path in binary_paths:
            try:
                groups.setdefault(file_sha256(path), []).append(path)
            except OSError as exc:
                report.errors.append(f"{path}: {exc}")

        for digest, duplicates in groups.items():
            if len(duplicates) < 2:
                continue
            canonical = min(duplicates, key=lambda p: len(p.as_posix()))
            for duplicate in duplicates:
                if duplicate == canonical:
                    continue
                rel = duplicate.relative_to(root).as_posix()
                if rel in existing:
                    continue
                report.findings.append(
                    Finding(
                        path=rel,
                        kind="binary",
                        reason="duplicate_binary",
                        size_bytes=duplicate.stat().st_size,
                        modified_utc=mtime_utc(duplicate),
                        sha256=digest,
                        duplicate_of=canonical.relative_to(root).as_posix(),
                        action="purge",
                        entropy_score=95,
                    )
                )
                report.candidate_bytes += duplicate.stat().st_size
                existing.add(rel)


def write_reports(report: AuditReport, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "sir_codex_directory_purge_report.json"
    md_path = output_dir / "sir_codex_scorpion_review.md"

    json_path.write_text(
        json.dumps(asdict(report), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    lines = [
        "# Scorpion Sting Forensic Review",
        "",
        f"- Root: `{report.root}`",
        f"- Generated: `{report.generated_utc}`",
        f"- Scanned files: `{report.scanned_files}`",
        f"- Scanned dirs: `{report.scanned_dirs}`",
        f"- Total scanned: `{human_bytes(report.total_bytes)}`",
        f"- Candidate footprint: `{human_bytes(report.candidate_bytes)}`",
        "",
        "| Action | Entropy | Size | Reason | Path |",
        "|---|---:|---:|---|---|",
    ]
    for finding in report.findings[:500]:
        lines.append(
            f"| {finding.action} | {finding.entropy_score} | "
            f"{human_bytes(finding.size_bytes)} | {finding.reason} | `{finding.path}` |"
        )
    if len(report.findings) > 500:
        lines.append(f"| review | 0 | 0 B | truncated | `{len(report.findings) - 500} more findings in JSON` |")
    if report.errors:
        lines.extend(["", "## Scan Errors"])
        lines.extend(f"- `{error}`" for error in report.errors[:100])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def archive_review_candidates(root: Path, output_dir: Path, report: AuditReport) -> Path | None:
    archive_items = [item for item in report.findings if item.action == "archive"]
    if not archive_items:
        return None

    archive_path = output_dir / "sir_codex_low_frequency_archive.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:
        for finding in archive_items:
            source = root / finding.path
            if source.exists() and source.is_file():
                archive.add(source, arcname=finding.path)
    return archive_path


def gzip_dormant_logs(root: Path, report: AuditReport, execute: bool) -> list[str]:
    compressed: list[str] = []
    for finding in report.findings:
        if finding.reason != "dormant_log":
            continue
        source = root / finding.path
        target = source.with_suffix(source.suffix + ".gz")
        if target.exists():
            continue
        if execute:
            with source.open("rb") as src, gzip.open(target, "wb", compresslevel=9) as dst:
                shutil.copyfileobj(src, dst)
            compressed.append(str(target))
    return compressed


def purge_candidates(root: Path, report: AuditReport, execute: bool) -> list[str]:
    purged: list[str] = []
    for finding in report.findings:
        if finding.action != "purge" or finding.reason not in SAFE_PURGE_REASONS:
            continue
        target = root / finding.path
        if not target.exists() or not target.is_file():
            continue
        if execute:
            target.unlink()
        purged.append(finding.path)
    return purged


def require_interrupt_gate(report: AuditReport) -> None:
    purge_count = sum(1 for item in report.findings if item.action == "purge")
    phrase = f"SCORPION APPROVE {purge_count}"
    print("")
    print("INTERRUPT GATE: destructive purge is armed but paused.")
    print(f"Type exactly `{phrase}` to continue, or anything else to abort.")
    received = input("> ").strip()
    if received != phrase:
        raise SystemExit("HITL gate declined. No destructive purge executed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sir Codex directory purge forge")
    parser.add_argument("target", help="Directory to audit")
    parser.add_argument(
        "--output-dir",
        default="03_VAULT/runtime_state/sir_codex_directory_purge",
        help="Report/archive output directory",
    )
    parser.add_argument("--exclude", action="append", default=[], help="Extra glob exclusion")
    parser.add_argument("--dormant-days", type=int, default=30)
    parser.add_argument("--large-mb", type=int, default=100)
    parser.add_argument("--archive", action="store_true", help="Create tar.gz archive for archive candidates")
    parser.add_argument("--compress-logs", action="store_true", help="Gzip dormant logs before purge review")
    parser.add_argument("--execute", action="store_true", help="Allow destructive purge after HITL gate")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.target).resolve()
    output_dir = Path(args.output_dir).resolve()
    configure_logging(output_dir)

    if not root.exists() or not root.is_dir():
        logging.error("Target is not a directory: %s", root)
        return 2

    logging.info("PHASE 1 AUDIT MAP target=%s", root)
    report = scan_directory(root, output_dir, args.exclude, args.dormant_days, args.large_mb)
    json_path, md_path = write_reports(report, output_dir)
    logging.info("Scorpion review written: %s", md_path)
    logging.info("JSON report written: %s", json_path)

    if args.archive:
        logging.info("PHASE 3 ORGANIZE COMPRESS archive candidates")
        archive_path = archive_review_candidates(root, output_dir, report)
        if archive_path:
            logging.info("Archive written: %s", archive_path)
        else:
            logging.info("No archive candidates found")

    if args.compress_logs:
        logging.info("PHASE 3 ORGANIZE COMPRESS dormant logs")
        compressed = gzip_dormant_logs(root, report, execute=True)
        logging.info("Compressed dormant logs: %d", len(compressed))

    purge_count = sum(1 for item in report.findings if item.action == "purge")
    logging.info("PHASE 2 TRIAGE PURGE candidates=%d execute=%s", purge_count, args.execute)
    if args.execute:
        require_interrupt_gate(report)
        purged = purge_candidates(root, report, execute=True)
        logging.info("Purged files: %d", len(purged))
    else:
        logging.info("Dry run only. Re-run with --execute to arm HITL purge gate.")

    print(
        json.dumps(
            {
                "status": "DRY_RUN" if not args.execute else "EXECUTED",
                "root": str(root),
                "report": str(json_path),
                "scorpion_review": str(md_path),
                "scanned_files": report.scanned_files,
                "candidate_bytes": report.candidate_bytes,
                "purge_candidates": purge_count,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

