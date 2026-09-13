#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""add-spdx-headers.py — repo-wide SPDX header roll-out tool.

Prepends an `SPDX-License-Identifier: MIT` header to every file the VFS
preflight check 020 probe (`control_plane.preflight.probes.license_header`)
flags as missing one. It reuses the probe's own `scan()`, so the tool
and the boot gate always agree on the target set: same skip dirs, skip
extensions/names, gitlink/submodule boundaries, and binary sniff.

Comment syntax is chosen per file type so the header never breaks the
file's grammar (shebang lines stay first; CRLF is preserved; a UTF-8 BOM
stays first).

Usage:
    python scripts/ops/add-spdx-headers.py [root ...]

Idempotent: files already carrying a marker are never touched. Runs in
passes (the probe caps at MAX_FLAGGED); prints remaining count and exits
non-zero if any flagged file remains (e.g. an unhandled file type).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

from control_plane.preflight.probes.license_header import scan

_HEADER = "SPDX-License-Identifier: MIT"

# comment open/close per extension. Line comments use ("#", "").
_COMMENT_FOR: dict[str, tuple[str, str]] = {
_COMMENT_FOR: dict[str, tuple[str, str]] = {
    **{ext: ("#", "") for ext in (
        ".py", ".sh", ".bash", ".zsh", ".ps1", ".cmd", ".bat",
        ".rb", ".pl", ".php", ".nix", ".zig", ".zon", ".typed", ".tsbuildinfo",
    )},
        ".py", ".sh", ".bash", ".zsh", ".ps1", ".cmd", ".bat",
        ".rb", ".pl", ".php",
    )},
    ".jinja": ("{#", "#}"),  # Jinja templates: {# comment #}
    **{ext: ("//", "") for ext in (
        ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx",
        ".go", ".rs", ".c", ".h", ".cc", ".cpp", ".cs",
        ".java", ".swift", ".kt", ".zig", ".proto", ".prisma",
    )},
    **{ext: ("--", "") for ext in (
        ".lua", ".sql", ".surrealql", ".hs", ".elm",
    )},
    **{ext: ("<!--", "-->") for ext in (
        ".html", ".xml", ".svg", ".vue", ".svelte",
    )},
    **{ext: ("/*", "*/") for ext in (
        ".css", ".scss", ".less", ".sass",
    )},
}
_NAME_FOR: dict[str, tuple[str, str]] = {
    "Dockerfile": ("#", ""),
    "Makefile": ("#", ""),
    ".mk": ("#", ""),
}


def _comment_for(fp: Path) -> tuple[str, str] | None:
    if fp.name in _NAME_FOR:
        return _NAME_FOR[fp.name]
    return _COMMENT_FOR.get(fp.suffix.lower())


def _header_bytes(open_c: str, close_c: str, nl: bytes) -> bytes:
    line = f"{open_c} {_HEADER} {close_c}".strip().encode("utf-8")
    return line + nl + nl


def add_header(fp: Path) -> bool:
    """Prepend an SPDX header to fp. Returns True if modified."""
    comment = _comment_for(fp)
    if comment is None:
        return False  # unhandled type — surfaced by the caller
    raw = fp.read_bytes()
    nl = b"\r\n" if b"\r\n" in raw[:1024] else b"\n"
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    body = raw[len(bom):]
    header = _header_bytes(*comment, nl)
    if body.startswith(b"#!"):  # keep shebang on line 1
        eol = body.find(nl) if nl in body[:128] else body.find(b"\n")
        if eol == -1:
            return False
        body = body[: eol + len(nl)] + header + body[eol + len(nl):]
    else:
        body = header + body
    fp.write_bytes(bom + body)
    return True


def _default_roots() -> list[Path]:
    return [Path(r) for r in (
        "01_KERNEL", "control_plane", "bin", "vfs",
        "apps", "packages", "scripts", "tests", "docs",
    )]


def main(argv: Iterable[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    roots = [Path(a) for a in args] if args else _default_roots()
    total_added = 0
    total_skipped: list[Path] = []
    for _pass in range(1, 21):  # safety bound; each pass makes progress
        flagged = scan(roots)
        if not flagged:
            break
        added = 0
        for fp in flagged:
            if add_header(fp):
                added += 1
                total_added += 1
            else:
                total_skipped.append(fp)
        print(f"pass {_pass}: flagged={len(flagged)} added={added} "
              f"unhandled={len(total_skipped)}", file=sys.stderr)
        if not added:
            break  # no progress — avoid infinite loop
    print(f"added {total_added} SPDX headers", file=sys.stderr)
    if total_skipped:
        print("unhandled file types (need a comment mapping):",
              file=sys.stderr)
        for fp in total_skipped[:50]:
            print(f"  {fp}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
