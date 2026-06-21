#!/usr/bin/env python3
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""scan_secrets.py — committed-secret gate for CI.

Scans **git-tracked** text files for high-confidence secret patterns and exits
non-zero if any are found. Only tracked files are scanned, so gitignored files
(e.g. real `.env`) are out of scope by design — this gate catches secrets that
have actually been committed.

Findings are printed with the secret value redacted. Lines that look like
placeholders/examples, or that carry an explicit `pragma: allowlist secret`
marker, are ignored.

Usage:
    python scripts/scan_secrets.py [path]   # default path: "."
Exit codes:
    0 — clean
    1 — one or more secrets found
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# High-confidence, low-false-positive vendor patterns. (name, regex)
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("AWS Access Key ID", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("AWS Secret Access Key", re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{40}")),
    ("Google API Key", re.compile(r"AIza[0-9A-Za-z\-_]{35}")),
    ("Slack Token", re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}")),
    ("Stripe Live Secret Key", re.compile(r"sk_live_[0-9A-Za-z]{24,}")),
    ("GitHub Token", re.compile(r"gh[pousr]_[0-9A-Za-z]{36,}")),
    ("OpenAI API Key", re.compile(r"sk-[A-Za-z0-9]{20,}T3BlbkFJ[A-Za-z0-9]{20,}")),
    ("Private Key Block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("Slack Webhook", re.compile(r"https://hooks\.slack\.com/services/T[0-9A-Z]+/B[0-9A-Z]+/[0-9A-Za-z]+")),
]

ALLOWLIST_MARK = "pragma: allowlist secret"

# Lines containing these markers are placeholders, not real secrets.
PLACEHOLDER = re.compile(
    r"(?i)(your[-_ ]?(api[-_ ]?)?key|example|sample|placeholder|dummy|changeme|"
    r"<[^>]+>|xxxx+|\.\.\.|redacted|test[-_]?secret|fake)"
)

SKIP_SUFFIX = {
    ".lock", ".min.js", ".map", ".png", ".jpg", ".jpeg", ".gif", ".pdf",
    ".ico", ".woff", ".woff2", ".ttf", ".bin", ".so", ".dll", ".exe", ".zip",
}
SKIP_NAME = {"package-lock.json", "uv.lock", "yarn.lock", "pnpm-lock.yaml"}
SKIP_PATH_PARTS = ("node_modules", ".git", "dist", "build", ".venv", "venv")
# These suffixes are expected to carry illustrative/placeholder secrets.
EXAMPLE_SUFFIX = (".example", ".sample", ".template")


def tracked_files(root: str) -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "ls-files", "--", root],
            capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [Path(p) for p in out.splitlines() if p]


def should_skip(path: Path) -> bool:
    if path.suffix in SKIP_SUFFIX or path.name in SKIP_NAME:
        return True
    if any(part in SKIP_PATH_PARTS for part in path.parts):
        return True
    if path.name.endswith(EXAMPLE_SUFFIX) or ".env.example" in path.name:
        return True
    return False


def scan_file(path: Path) -> list[tuple[int, str]]:
    findings: list[tuple[int, str]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return findings  # binary or unreadable — skip
    for lineno, line in enumerate(text.splitlines(), start=1):
        if ALLOWLIST_MARK in line or PLACEHOLDER.search(line):
            continue
        for name, pattern in PATTERNS:
            if pattern.search(line):
                findings.append((lineno, name))
                break
    return findings


def main(argv: list[str]) -> int:
    root = argv[1] if len(argv) > 1 else "."
    total = 0
    for path in tracked_files(root):
        if should_skip(path):
            continue
        for lineno, name in scan_file(path):
            total += 1
            print(f"[SECRET] {path}:{lineno} — {name}")
    if total:
        print(f"\n[FAIL] {total} potential secret(s) found in tracked files.")
        print("       Remove them, rotate the credential, and re-run. False "
              "positive? add a '# pragma: allowlist secret' marker on the line.")
        return 1
    print("[OK] No committed secrets detected in tracked files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
