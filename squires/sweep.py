"""SWEEP squire — dead code & orphan file detection."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
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


def sweep(records: Iterable[FileRecord]) -> SweepReport:
    report = SweepReport()
    recs = list(records)

    # Build a set of all referenced file names (cross-reference sweep)
    all_text_by_file: dict[str, str] = {}
    for rec in recs:
        if not rec.is_binary:
            all_text_by_file[rec.rel] = rec.read_text()

    all_content = "\n".join(all_text_by_file.values())

    # Duplicate content detection (header hash)
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

    # Unused Python imports (naive: import name not found elsewhere in file)
    for rec in recs:
        if rec.ext != ".py" or rec.is_binary:
            continue
        text = all_text_by_file.get(rec.rel, "")
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            m = re.match(r"^import\s+(\w+)$", line.strip())
            if m:
                name = m.group(1)
                # Check if name appears anywhere else in the file
                rest = text.replace(line, "", 1)
                if name not in rest:
                    report.flags.append(OrphanFlag(
                        kind="unused_import",
                        file=rec.rel,
                        line=i,
                        detail=f"'{name}' imported but not referenced",
                    ))

    # Unreferenced files — Python modules not imported anywhere
    py_modules = {
        rec.rel.replace("/", ".").removesuffix(".py")
        for rec in recs
        if rec.ext == ".py" and "/__" not in rec.rel
    }
    for mod in py_modules:
        base = mod.rsplit(".", 1)[-1]
        if base in ("__init__", "colony", "main", "__main__"):
            continue
        # Check if base name appears in any file text
        if not re.search(r"\b" + re.escape(base) + r"\b", all_content):
            # Only flag if not an obvious entry point
            rel = mod.replace(".", "/") + ".py"
            report.flags.append(OrphanFlag(
                kind="unreferenced_file",
                file=rel,
                detail="module name not imported anywhere",
            ))

    return report
