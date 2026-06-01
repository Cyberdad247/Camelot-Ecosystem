"""GHOST squire — air-gapped file triage. Finds secrets, TODOs, large files. Zero cloud."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from .scan import FileRecord

# Secret patterns (no false-positive-heavy generic patterns)
_SECRET_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("anthropic_key",  re.compile(r"sk-ant-[a-zA-Z0-9\-_]{20,}")),
    ("openai_key",     re.compile(r"sk-[a-zA-Z0-9]{32,}")),
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z\-_]{35}")),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("aws_secret",     re.compile(r"(?i)aws.{0,20}secret.{0,20}['\"][0-9a-zA-Z/+]{40}['\"]")),
    ("generic_token",  re.compile(r"(?i)(?:api[_-]?key|bearer|token|password|passwd|secret)\s*[=:]\s*['\"][A-Za-z0-9+/\-_]{16,}['\"]")),
    ("private_key",    re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----")),
]

_TODO_PATTERN = re.compile(r"(?i)#\s*(?:todo|fixme|hack|xxx|note|warn)\b[^\n]*")

_LARGE_FILE_BYTES = 500 * 1024  # 500 KB


@dataclass
class GhostFlag:
    kind: str       # "secret" | "todo" | "large_file" | "binary"
    file: str
    line: int = 0
    detail: str = ""
    severity: str = "info"  # "critical" | "warning" | "info"


@dataclass
class GhostReport:
    flags: list[GhostFlag] = field(default_factory=list)

    @property
    def critical(self) -> list[GhostFlag]:
        return [f for f in self.flags if f.severity == "critical"]

    @property
    def warnings(self) -> list[GhostFlag]:
        return [f for f in self.flags if f.severity == "warning"]

    def summary(self) -> dict:
        return {
            "total": len(self.flags),
            "critical": len(self.critical),
            "warnings": len(self.warnings),
            "info": sum(1 for f in self.flags if f.severity == "info"),
        }


def _mask(val: str) -> str:
    if len(val) <= 8:
        return "***"
    return val[:4] + "..." + val[-4:]


def triage(records: Iterable[FileRecord]) -> GhostReport:
    report = GhostReport()
    for rec in records:
        # Large file check
        if rec.size > _LARGE_FILE_BYTES:
            report.flags.append(GhostFlag(
                kind="large_file",
                file=rec.rel,
                detail=f"{rec.size // 1024} KB",
                severity="warning",
            ))

        if rec.is_binary:
            report.flags.append(GhostFlag(
                kind="binary",
                file=rec.rel,
                detail=f"{rec.size} bytes",
                severity="info",
            ))
            continue

        text = rec.read_text()
        lines = text.splitlines()

        # Secret scan
        for name, pat in _SECRET_PATTERNS:
            for m in pat.finditer(text):
                line_no = text[: m.start()].count("\n") + 1
                report.flags.append(GhostFlag(
                    kind="secret",
                    file=rec.rel,
                    line=line_no,
                    detail=f"{name}: {_mask(m.group(0))}",
                    severity="critical",
                ))

        # TODO/FIXME scan
        for i, line in enumerate(lines, 1):
            m = _TODO_PATTERN.search(line)
            if m:
                report.flags.append(GhostFlag(
                    kind="todo",
                    file=rec.rel,
                    line=i,
                    detail=m.group(0).strip()[:80],
                    severity="info",
                ))

    return report
