"""cartridges.v4000_trio — shared V4000 trio template.

The V4000 trio (blueprint.md / task.md / verification.md) is the
scaffolding for a Camelot Digital Factory stage. This module is the
single source of truth for:

  - The trio filenames (``TRIO_FNAMES``).
  - The default scaffold body for each filename (``default_scaffold_body``).
  - The byte-equality check that distinguishes an "unmodified default
    scaffold" from a "user-modified" trio file
    (``is_default_scaffold_unmodified``).

Why a shared module? The portable CLI's ``cmd_cartridge`` preflight guard
compares the on-disk trio bytes against the default scaffold body to
decide whether to allow a silent rewrite or require ``--force``. The
write path then re-emits the same body. If the body lived only inside
``bin/camelot_portable.py`` as a module-private function, any future
consumer (MCP server tool schema, IDE extension scaffold preview,
documentation linter) would have to maintain a parallel copy — a class
of bug where the preflight check and the actual write drifted.

Iron Gate conformance
---------------------
- ``is_default_scaffold_unmodified`` tolerates Windows text-mode newline
  translation (``\\r\\n``) so dev-mode runs on Windows don't false-positive
  refuse an untouched re-emit.
- Empty (0-byte) trio files count as trivially fillable stubs.
- Any genuine user addition — even a single extra line — fails byte
  equality and triggers the ``--force`` requirement in the portable CLI.
"""
from __future__ import annotations

from pathlib import Path


# Canonical V4000 trio filenames, in display order. Single source of
# truth across portable CLI + any future consumer (MCP tool description,
# IDE extension, etc.).
TRIO_FNAMES: tuple[str, ...] = (
    "blueprint.md",
    "task.md",
    "verification.md",
)


def default_scaffold_body(fname: str, stage: str) -> str:
    """Body of a freshly-emitted trio file.

    Kept byte-identical between ``default_scaffold_body`` and the
    write path (``bin.camelot_portable.cmd_cartridge``) so the preflight
    helper can detect "unmodified default vs. user-edited" by
    byte-compare.

    Any change to this string is a behavior change — re-runs of
    ``cartridge --emit`` against an untouched trio will pick up the new
    body byte-for-byte.
    """
    return (
        f"# {fname[:-3].title()} — {stage}\n\n"
        f"## Status\n\n"
        f"Scaffold emitted by `camelot_portable cartridge --emit` "
        f"via OmniRoute. Integrate with item-3 isolation namespacing "
        f"per `docs/architecture/camelot_v1000_paper/"
        f"items_2_3_decision_matrix.md`.\n"
    )


def is_default_scaffold_unmodified(existing: Path, fname: str, stage: str) -> bool:
    """True iff emitting the default scaffold would be non-destructive.

    Returns True (safe to overwrite without --force) in three cases:
      - The file does NOT exist (nothing to clobber).
      - The file is empty (a 0-byte stub user wants filled).
      - The file's bytes are equal to the default scaffold body the emit
        path WOULD write, with CRLF/CR normalized to LF so the comparison
        survives ``Path.write_text``'s Windows text-mode newline
        translation (which converts every ``\\n`` to ``\\r\\n`` on write
        but leaves the f-string source's ``\\n`` unchanged).

    Returns False otherwise — any genuine user addition, even a single
    extra line, fails the normalized byte equality. OSError on read is
    also False (be safe when we cannot inspect).
    """
    if not existing.exists():
        return True
    try:
        actual = existing.read_bytes()
    except OSError:
        return False
    if len(actual) == 0:
        return True
    expected = default_scaffold_body(fname, stage).encode("utf-8")
    # Normalize CRLF + lone CR to LF on both sides. The default scaffold
    # body uses ``\n`` (Python str literal), but ``Path.write_text`` on
    # Windows translates it to ``\r\n`` on disk, so a naïve byte compare
    # against the unchanged f-string would always fail in dev mode.
    actual = actual.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    expected = expected.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return actual == expected
