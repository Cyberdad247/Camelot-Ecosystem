# SPDX-License-Identifier: MIT
"""Operational files that run on Linux must not carry Windows line endings.

WHY THIS TEST EXISTS

A working copy of `scripts/vps_hub_bootstrap.sh` reached the hub with CRLF endings. The
shebang became `#!/usr/bin/env bash\r`, which Linux resolves to a file named `bash\r`:

    /usr/bin/env: 'bash\\r': No such file or directory
    exit 127

The script therefore never ran, and the audit above it recorded **zero failures** — which
is indistinguishable from a perfectly healthy hub. Nothing in the stack complained. The
monitor that exists to catch "a written claim and a live fact disagreeing" had, one
level down, become exactly that.

Three things made this invisible, and each shapes the test below:

1. `bash -n` parses a CRLF file happily. Syntax checking is not an execution check.
2. `.gitattributes` declares `*.sh text eol=lf`, but that only normalizes when git next
   touches the file — the working copy is what `scp` ships, and it is not normalized.
3. `grep '\\r'` is not trustworthy here. On this Windows host MSYS grep translates line
   endings while reading, so the same file reported 420 CR bytes by one measurement and
   0 by another. Only the raw bytes can settle it, so this test reads bytes.

The scan covers the files that are executed on Linux or parsed by systemd. A stray CRLF
in a markdown file is cosmetic; a stray CRLF here is a production outage that reports
itself as success.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Executed by a shell on the hub, or read by systemd.
SCAN_GLOBS = ("scripts/**/*.sh", "infra/systemd/*")


def _operational_files() -> list[Path]:
    found: set[Path] = set()
    for pattern in SCAN_GLOBS:
        found.update(p for p in REPO_ROOT.glob(pattern) if p.is_file())
    return sorted(found)


def _cr_bytes(path: Path) -> int:
    """Count CR bytes in the raw file — never via text mode, which hides them."""
    return path.read_bytes().count(b"\r")


def test_the_scan_actually_finds_files() -> None:
    """A glob that matches nothing would make every assertion below vacuous."""
    files = _operational_files()
    assert len(files) > 20, f"only found {len(files)} operational files; globs are wrong"
    assert any(p.name == "vps_hub_bootstrap.sh" for p in files)


@pytest.mark.parametrize("path", _operational_files(), ids=lambda p: p.name)
def test_operational_files_use_lf_line_endings(path: Path) -> None:
    cr = _cr_bytes(path)
    assert cr == 0, (
        f"{path.relative_to(REPO_ROOT)} carries {cr} CR byte(s). On Linux a CR in the "
        f"shebang makes the script unexecutable (exit 127) and an audit that never ran "
        f"reports zero failures — success and a missing interpreter look identical."
    )


def test_the_cr_detector_is_not_vacuous(tmp_path: Path) -> None:
    """Negative control: the detector must actually see a CR when one is present.

    This is the assertion that would have caught the original gap, because the failure
    was in the *measurement*, not the file.
    """
    crlf = tmp_path / "crlf.sh"
    crlf.write_bytes(b"#!/usr/bin/env bash\r\necho hi\r\n")
    assert _cr_bytes(crlf) == 2, "the detector cannot see CR bytes it is supposed to find"

    lf = tmp_path / "lf.sh"
    lf.write_bytes(b"#!/usr/bin/env bash\necho hi\n")
    assert _cr_bytes(lf) == 0, "the detector reports CR bytes in an LF file"


def test_the_deploy_refuses_to_report_success_when_the_audit_cannot_execute() -> None:
    """A deploy that ships an unexecutable script must fail, not print a status block.

    Reporting `failures: 0` from an audit that never ran is the precise false-green this
    whole monitoring layer exists to prevent.
    """
    deploy = REPO_ROOT / "scripts" / "ops" / "deploy-hub-selfcheck.sh"
    text = deploy.read_text(encoding="utf-8")
    assert "126" in text and "127" in text, (
        "the deploy does not distinguish 'could not execute' from 'post-condition failed'"
    )
    assert "exit 1" in text
    assert "tr -cd" in text, "the deploy does not check the deployed bytes for CR"
