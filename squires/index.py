"""INDEX squire — builds symbol + file index from SCAN output."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from .scan import FileRecord

# Pattern map per extension
_SYMBOL_PATTERNS: dict[str, list[re.Pattern]] = {
    ".py": [
        re.compile(r"^(?:async\s+)?def\s+(\w+)", re.MULTILINE),
        re.compile(r"^class\s+(\w+)", re.MULTILINE),
    ],
    ".rs": [
        re.compile(r"^(?:pub\s+)?fn\s+(\w+)", re.MULTILINE),
        re.compile(r"^(?:pub\s+)?struct\s+(\w+)", re.MULTILINE),
        re.compile(r"^(?:pub\s+)?enum\s+(\w+)", re.MULTILINE),
        re.compile(r"^(?:pub\s+)?trait\s+(\w+)", re.MULTILINE),
    ],
    ".go": [
        re.compile(r"^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)", re.MULTILINE),
        re.compile(r"^type\s+(\w+)\s+(?:struct|interface)", re.MULTILINE),
    ],
    ".ts": [
        re.compile(r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)", re.MULTILINE),
        re.compile(r"^(?:export\s+)?class\s+(\w+)", re.MULTILINE),
        re.compile(r"^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=", re.MULTILINE),
    ],
}
# JS uses same patterns as TS
_SYMBOL_PATTERNS[".js"] = _SYMBOL_PATTERNS[".ts"]
_SYMBOL_PATTERNS[".tsx"] = _SYMBOL_PATTERNS[".ts"]
_SYMBOL_PATTERNS[".jsx"] = _SYMBOL_PATTERNS[".ts"]


@dataclass
class SymbolEntry:
    name: str
    kind: str  # "function" | "class" | "struct" | "enum" | "trait" | "const"
    file: str
    line_hint: int = 0


@dataclass
class ColonyIndex:
    files: list[dict] = field(default_factory=list)
    symbols: list[SymbolEntry] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "stats": self.stats,
            "files": self.files,
            "symbols": [
                {"name": s.name, "kind": s.kind, "file": s.file, "line": s.line_hint}
                for s in self.symbols
            ],
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")


def _kind_from_pattern(pat: re.Pattern) -> str:
    src = pat.pattern
    for word in ("def", "fn", "func", "function"):
        if word in src:
            return "function"
    for word in ("class", "struct"):
        if word in src:
            return word
    for word in ("enum", "trait", "interface"):
        if word in src:
            return word
    return "symbol"


def build_index(records: Iterable[FileRecord]) -> ColonyIndex:
    idx = ColonyIndex()
    total_lines = 0
    ext_counts: dict[str, int] = {}

    for rec in records:
        if rec.is_binary:
            continue
        idx.files.append({
            "path": rec.rel,
            "size": rec.size,
            "lines": rec.lines,
            "ext": rec.ext,
            "sha256": rec.sha256,
        })
        total_lines += rec.lines
        ext_counts[rec.ext] = ext_counts.get(rec.ext, 0) + 1

        patterns = _SYMBOL_PATTERNS.get(rec.ext, [])
        if not patterns:
            continue
        try:
            text = rec.read_text()
            if not text:
                continue
            for pat in patterns:
                kind = _kind_from_pattern(pat)
                for m in pat.finditer(text):
                    line = text[: m.start()].count("\n") + 1
                    idx.symbols.append(SymbolEntry(
                        name=m.group(1),
                        kind=kind,
                        file=rec.rel,
                        line_hint=line,
                    ))
        except Exception:
            pass

    idx.stats = {
        "total_files": len(idx.files),
        "total_symbols": len(idx.symbols),
        "total_lines": total_lines,
        "by_ext": ext_counts,
    }
    return idx
