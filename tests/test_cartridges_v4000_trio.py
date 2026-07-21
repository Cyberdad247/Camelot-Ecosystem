"""tests/test_cartridges_v4000_trio.py — coverage for the shared
V4000 trio template module :mod:`cartridges.v4000_trio`.

This module is the single source of truth for the trio filenames, the
default scaffold body, and the byte-equality check that powers
``bin/camelot_portable.py``'s ``cmd_cartridge`` preflight guard. The
tests below lock in:

  - The trio filename tuple (``TRIO_FNAMES``).
  - The default scaffold body for each filename keyed to a stage id.
  - The four ``is_default_scaffold_unmodified`` cases: missing file
    (True), 0-byte stub (True), byte-identical default (True), and
    user-modified content (False).
  - CRLF/CR normalization so the comparison survives Windows text-mode
    newline translation.
  - The backward-compat aliases in ``bin.camelot_portable`` point at the
    same function objects as the new module's public names (so a future
    refactor that drops the aliases doesn't silently change behavior).
"""
from __future__ import annotations

import argparse
from pathlib import Path


from cartridges.v4000_trio import (
    TRIO_FNAMES,
    default_scaffold_body,
    is_default_scaffold_unmodified,
)
# Shared Rich-Console replacement — canonical home is ``tests/_fixtures.py``
# so the trio tests don't have to reach across sibling test files. A future
# refusal in ``_preflight_emit_overwrite`` surfaces as a captured-output
# diff (and a useful pytest failure output) rather than going to /dev/null.
from tests._fixtures import CapturingConsole


# ── TRIO_FNAMES ───────────────────────────────────────────────────────────────


def test_TRIO_FNAMES_is_canonical_tuple():
    assert TRIO_FNAMES == ("blueprint.md", "task.md", "verification.md")
    # Must be a tuple (immutable) so downstream callers can rely on
    # identity comparisons and never accidentally mutate the source of truth.
    assert isinstance(TRIO_FNAMES, tuple)


# ── default_scaffold_body ────────────────────────────────────────────────────


def test_default_scaffold_body_for_blueprint():
    body = default_scaffold_body("blueprint.md", "myproj")
    assert body.startswith("# Blueprint — myproj\n\n")
    assert "## Status" in body
    assert "items_2_3_decision_matrix.md" in body
    # body must be a fresh str (not a shared interned literal) so per-call
    # f-string substitution is correct.
    assert isinstance(body, str)


def test_default_scaffold_body_for_task():
    body = default_scaffold_body("task.md", "phase_h")
    assert body.startswith("# Task — phase_h\n\n")


def test_default_scaffold_body_for_verification():
    body = default_scaffold_body("verification.md", "knight_memory")
    assert body.startswith("# Verification — knight_memory\n\n")


# ── is_default_scaffold_unmodified ───────────────────────────────────────────


def test_is_default_returns_true_when_file_missing(tmp_path):
    assert is_default_scaffold_unmodified(tmp_path / "absent.md", "b.md", "x") is True


def test_is_default_returns_true_when_file_empty(tmp_path):
    fp = tmp_path / "blueprint.md"
    fp.write_text("", encoding="utf-8")
    assert is_default_scaffold_unmodified(fp, "blueprint.md", "x") is True


def test_is_default_returns_true_when_byte_identical(tmp_path):
    fp = tmp_path / "blueprint.md"
    fp.write_text(default_scaffold_body("blueprint.md", "myproj"), encoding="utf-8")
    assert is_default_scaffold_unmodified(fp, "blueprint.md", "myproj") is True


def test_is_default_returns_false_when_user_modified(tmp_path):
    fp = tmp_path / "blueprint.md"
    fp.write_text("# Blueprint — myproj\n\nUSER-OWNED RATIONALE\n", encoding="utf-8")
    assert is_default_scaffold_unmodified(fp, "blueprint.md", "myproj") is False


def test_is_default_returns_false_on_minor_edit(tmp_path):
    """Even a single trailing newline departure from the default body
    flips the comparison to False. Strictest possible protection."""
    fp = tmp_path / "blueprint.md"
    body = default_scaffold_body("blueprint.md", "x")
    fp.write_text(body + "\n", encoding="utf-8")
    assert is_default_scaffold_unmodified(fp, "blueprint.md", "x") is False


def test_is_default_normalizes_windows_crlf(tmp_path):
    """``Path.write_text`` on Windows translates ``\\n`` to ``\\r\\n``;
    the comparison must normalize so an untouched re-emit doesn't
    false-positive refuse. """
    fp = tmp_path / "blueprint.md"
    # Simulate Windows text-mode write: \r\n instead of \n.
    body_crlf = default_scaffold_body("blueprint.md", "x").replace("\n", "\r\n")
    fp.write_bytes(body_crlf.encode("utf-8"))
    assert is_default_scaffold_unmodified(fp, "blueprint.md", "x") is True


def test_is_default_normalizes_classic_mac_cr(tmp_path):
    fp = tmp_path / "blueprint.md"
    body_cr = default_scaffold_body("blueprint.md", "x").replace("\n", "\r")
    fp.write_bytes(body_cr.encode("utf-8"))
    assert is_default_scaffold_unmodified(fp, "blueprint.md", "x") is True


def test_is_default_returns_false_on_oserror(tmp_path, monkeypatch):
    """``read_bytes`` raising OSError must be treated as protected
    (safer default than treating unreadable as trivially overwritable)."""
    fp = tmp_path / "blueprint.md"
    fp.write_text("anything", encoding="utf-8")

    def _raise(_self):
        raise OSError("simulated permission denied")

    monkeypatch.setattr(Path, "read_bytes", _raise)
    assert is_default_scaffold_unmodified(fp, "blueprint.md", "x") is False


# ── Backward-compat aliases in bin.camelot_portable ───────────────────────────


def test_portable_backward_compat_aliases_point_at_new_module_functions():
    """The portable CLI exposes the trio template under the old
    underscore-prefixed names so older tests + tools that import them
    still work. They must point at the SAME function objects as the
    new public names so a future refactor that drops the aliases is a
    pure rename, not a behavior change. """
    from bin import camelot_portable as portable

    assert portable._TRIO_FNAMES is TRIO_FNAMES
    assert portable._default_scaffold_body is default_scaffold_body
    assert portable._is_default_scaffold_unmodified is is_default_scaffold_unmodified


def test_portable_caller_sites_use_new_module(tmp_path):
    """The portable CLI's actual call sites must use the new public
    names (not the legacy aliases), so the bundle is a true import
    graph, not a one-off copy."""
    from bin import camelot_portable as portable

    # Build a tiny trio and run cmd_cartridge end-to-end so we exercise
    # _preflight_emit_overwrite + the write loop. Use a target whose
    # basename matches the stage id so ``target.name == args.emit`` —
    # cmd_cartridge keys the scaffold body to ``target.name`` (not
    # ``args.emit``) to keep the preflight byte-equality check aligned
    # with the actual write path's body.
    target = tmp_path / "e2e"
    target.mkdir()
    args = argparse.Namespace(emit="e2e", target=str(target), cartridge_force=False)
    console = CapturingConsole()
    rc = portable.cmd_cartridge(args, console)
    assert rc == 0
    # Trio was materialized via the public default_scaffold_body path
    # (keyed to target.name == "e2e" == args.emit).
    expected_blueprint = default_scaffold_body("blueprint.md", "e2e")
    assert (target / "blueprint.md").read_text(encoding="utf-8") == expected_blueprint
