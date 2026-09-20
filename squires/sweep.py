"""SWEEP squire — dead code & orphan file detection."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

from .scan import FileRecord


@dataclass
class OrphanFlag:
    kind: str       # "unused_import" | "unreferenced_file" | "duplicate_content"
    file: str
    line: int = 0
    detail: str = ""


@dataclass
class SweepReport:
    flags: list[OrphanFlag] = field(default_factory=list)

    def summary(self) -> dict:
        kinds: dict[str, int] = {}
        for f in self.flags:
            kinds[f.kind] = kinds.get(f.kind, 0) + 1
        return {"total": len(self.flags), **kinds}


_UNUSED_IMPORT_PY = re.compile(r"^import\s+(\w+)|^from\s+[\w.]+\s+import\s+(\w+)", re.MULTILINE)
_DUPLICATE_WINDOW = 128  # bytes — check first N bytes for duplicate detection


_WORD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def sweep(records: Iterable[FileRecord]) -> SweepReport:
    report = SweepReport()
    recs = list(records)

    # 1. Duplicate content detection (header hash — fast, zero text decode)
    header_seen: dict[str, str] = {}
    for rec in recs:
        if rec.is_binary or rec.size < 64:
            continue
        try:
            header = rec.path.read_bytes()[:_DUPLICATE_WINDOW]
        except OSError:
            continue
        key = header.hex()
        if key in header_seen:
            report.flags.append(OrphanFlag(
                kind="duplicate_content",
                file=rec.rel,
                detail=f"same header as {header_seen[key]}",
            ))
        else:
            header_seen[key] = rec.rel

    # 2. Target python module base names for unreferenced detection
    py_modules = {
        rec.rel.replace("/", ".").removesuffix(".py")
        for rec in recs
        if rec.ext == ".py" and "/__" not in rec.rel
    }
    targets = {
        mod.rsplit(".", 1)[-1]
        for mod in py_modules
    } - {"__init__", "colony", "main", "__main__"}
    found_bases: set[str] = set()

    # 3. Stream through records: check unused imports and resolve module references
    for rec in recs:
        if rec.is_binary:
            continue
        text = rec.read_text()
        if not text:
            continue

        # Unused Python imports (per-file)
        if rec.ext == ".py":
            lines = text.splitlines()
            for i, line in enumerate(lines, 1):
                m = re.match(r"^import\s+(\w+)$", line.strip())
                if m:
                    name = m.group(1)
                    rest = text.replace(line, "", 1)
                    if name not in rest:
                        report.flags.append(OrphanFlag(
                            kind="unused_import",
                            file=rec.rel,
                            line=i,
                            detail=f"'{name}' imported but not referenced",
                        ))

        # Check target module mentions via word tokens
        if targets:
            words = set(_WORD_RE.findall(text))
            matched = words & targets
            if matched:
                found_bases.update(matched)
                targets -= matched

    # 4. Flag unreferenced modules
    for mod in py_modules:
        base = mod.rsplit(".", 1)[-1]
        if base in ("__init__", "colony", "main", "__main__"):
            continue
        if base not in found_bases:
            rel = mod.replace(".", "/") + ".py"
            report.flags.append(OrphanFlag(
                kind="unreferenced_file",
                file=rel,
                detail="module name not imported anywhere",
            ))

    return report
