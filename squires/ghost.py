"""GHOST squire — air-gapped file triage. Finds secrets, TODOs, large files. Zero cloud."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
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

# Path fragments marking intentionally-public templates — their placeholder
# content is never a real credential (config.example.json, *_template, ...).
_TEMPLATE_PATH_MARKERS = ("example", "template", "fixture", ".sample")

# Value-level mock markers. `your_` matters: `YOUR_PRIVATE_KEY` placeholders
# previously slipped through because only the hyphen form was checked.
_MOCK_VALUE_MARKERS = (
    "dummy", "mock", "example", "placeholder", "test",
    "your-", "your_", "xxx", "sample", "0000", "1234", "abcdef",
)


def _is_readable_constant(value: str) -> bool:
    """True when a generic_token match is a human-readable identifier, not an
    opaque credential.

    Env-var names (`CAMELOT_DASHBOARD_OPERATOR_TOKEN`), version tokens
    (`1000-EXCALIBUR-A`) and fixture strings (`operator_request_signature_…`)
    split into short word/number segments; real secrets are long base64/hex
    blobs that never pass the per-segment cap. Downgraded (not dropped) so the
    constant stays visible as a warning.
    """
    parts = [p for p in re.split(r"[_\-.]", value) if p]
    if not parts:
        return False
    return all(
        len(p) <= 12 and p.isalnum() and re.search(r"[aeiouAEIOU0-9]", p)
        for p in parts
    )


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
        is_test_file = any(p in rec.rel.lower() for p in ("/test/", "/tests/", "/fixtures/", "test_", "_test.", ".test.", "mock_")) or rec.ext == ".md"
        is_template_path = any(p in rec.rel.lower() for p in _TEMPLATE_PATH_MARKERS)
        for name, pat in _SECRET_PATTERNS:
            for m in pat.finditer(text):
                val = m.group(0)
                line_no = text[: m.start()].count("\n") + 1
                line_text = lines[line_no - 1] if 0 < line_no <= len(lines) else ""
                # Mock markers may sit outside the match itself (e.g. the
                # line's value is a BEGIN/END marker pair next to
                # YOUR_PRIVATE_KEY), so scan match + enclosing line.
                haystack = (val + " " + line_text).lower()
                is_mock = (
                    is_test_file
                    or is_template_path
                    or any(h in haystack for h in _MOCK_VALUE_MARKERS)
                )
                if is_mock:
                    report.flags.append(GhostFlag(
                        kind="mock_secret",
                        file=rec.rel,
                        line=line_no,
                        detail=f"{name} (test/fixture): {_mask(val)}",
                        severity="info",
                    ))
                    continue
                if name == "private_key" and "-----end " in line_text.lower():
                    # BEGIN + END markers on one line = PEM validation check or
                    # docstring example. Real key material spans many lines.
                    report.flags.append(GhostFlag(
                        kind="mock_secret",
                        file=rec.rel,
                        line=line_no,
                        detail=f"{name} (PEM marker pair): {_mask(val)}",
                        severity="info",
                    ))
                    continue
                if name == "generic_token":
                    # Match starts at the keyword (token: "…"), so evaluate
                    # readability on the quoted literal itself.
                    lit_m = re.search(r"['\"]([A-Za-z0-9+/\-_]{16,})['\"]", val)
                    lit = lit_m.group(1) if lit_m else val
                    if _is_readable_constant(lit):
                        report.flags.append(GhostFlag(
                            kind="token_constant",
                            file=rec.rel,
                            line=line_no,
                            detail=f"{name} (readable constant): {_mask(lit)}",
                            severity="warning",
                        ))
                        continue
                report.flags.append(GhostFlag(
                    kind="secret",
                    file=rec.rel,
                    line=line_no,
                    detail=f"{name}: {_mask(val)}",
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
