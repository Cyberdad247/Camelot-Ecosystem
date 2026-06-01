"""SCAN squire — codebase walker. Emits file metadata for downstream squires."""
from __future__ import annotations
import os
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

# File types that carry code/content worth indexing
_CODE_EXTS = {
    ".py", ".rs", ".go", ".ts", ".tsx", ".js", ".jsx",
    ".toml", ".yaml", ".yml", ".json", ".md", ".txt",
    ".sh", ".ps1", ".bat", ".c", ".cpp", ".h",
}
_IGNORE_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "dist", "build", ".antigravity", "CAMELOT_DefenseGrid_Quarantine",
    ".mypy_cache", ".ruff_cache", "target",
}
_MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB ceiling


@dataclass
class FileRecord:
    path: Path
    rel: str
    size: int
    ext: str
    sha256: str = ""
    lines: int = 0
    is_binary: bool = False

    def read_text(self) -> str:
        try:
            return self.path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""


def scan(root: Path, *, extensions: set[str] | None = None) -> Iterator[FileRecord]:
    exts = extensions or _CODE_EXTS
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored dirs in-place
        dirnames[:] = [d for d in dirnames if d not in _IGNORE_DIRS and not d.startswith(".")]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fpath.suffix not in exts:
                continue
            try:
                st = fpath.stat()
            except OSError:
                continue
            if st.st_size > _MAX_FILE_BYTES:
                continue
            rel = str(fpath.relative_to(root)).replace("\\", "/")
            rec = FileRecord(
                path=fpath,
                rel=rel,
                size=st.st_size,
                ext=fpath.suffix,
            )
            try:
                raw = fpath.read_bytes()
                rec.sha256 = hashlib.sha256(raw).hexdigest()[:12]
                # Detect binary heuristic
                rec.is_binary = b"\x00" in raw[:1024]
                if not rec.is_binary:
                    rec.lines = raw.count(b"\n")
            except OSError:
                pass
            yield rec
