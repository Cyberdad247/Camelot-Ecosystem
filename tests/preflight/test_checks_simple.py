"""TDD-first tests for the 'simple' per-check probes.

Covers:
- file_present.scan (used by check 050 ledger presence and 070 vfs scaffold)
- import_smoke.check (used by check 060 tool registry)
- license_header.scan (used by check 020 foss validation)

Note: the 'simple' moniker comes from the plan §Task 4 — these three
checks share a uniform executor (probe function called directly without
the hitl_on_fail path). Hitl-on-fail checks (030, 040, 070 in §4) are
covered in test_checks_hitl.py.
"""
import socket
import threading
import time
from contextlib import closing

from control_plane.preflight.probes import (
    file_present,
    import_smoke,
    license_header,
    ports as ports_probe,  # tested here too — covers check 040 logic
)


# ---- ports_probe ----------------------------------------------------------

def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def test_ports_probe_returns_open_for_listener():
    p = _free_port()
    with closing(socket.socket()) as srv:
        srv.bind(("127.0.0.1", p))
        srv.listen()
        # Accept in a thread so the test doesn't deadlock.
        t = threading.Thread(target=srv.accept, daemon=True)
        t.start()
        out = ports_probe.scan([p], timeout_s=0.5)
        # Give the connection time to register.
        time.sleep(0.05)
        assert out.get(p) is True


def test_ports_probe_returns_closed_for_dead_port():
    p = _free_port()  # acquired but never bound to a listener
    out = ports_probe.scan([p], timeout_s=0.2)
    assert out.get(p) is False


# ---- file_present ---------------------------------------------------------

def test_file_present_returns_only_existing(tmp_path):
    from pathlib import Path
    a = tmp_path / "exists.md"
    b = tmp_path / "missing.md"
    a.write_text("# hi")
    out = file_present.scan([a, b])
    assert out == [a]
    assert b not in out


# ---- import_smoke ---------------------------------------------------------

def test_import_smoke_flags_bogus_module():
    out = import_smoke.check(["definitely_does_not_exist_xyz"])
    assert "definitely_does_not_exist_xyz" in out


def test_import_smoke_passes_real_modules():
    out = import_smoke.check(["pathlib", "json"])
    assert out == []


# ---- license_header -------------------------------------------------------

def test_license_header_flags_missing(tmp_path):
    from pathlib import Path
    bad = tmp_path / "no_license.py"
    bad.write_text("def foo(): pass\n")  # no SPDX, no Copyright
    out = license_header.scan([tmp_path])
    assert any(p.resolve() == bad.resolve() for p in out)


def test_license_header_passes_with_spdx(tmp_path):
    from pathlib import Path
    good = tmp_path / "good.py"
    good.write_text(
        "# SPDX-License-Identifier: MIT\ndef foo(): pass\n"
    )
    out = license_header.scan([tmp_path])
    assert not any(p.resolve() == good.resolve() for p in out)


def test_license_header_skips_md_and_yaml(tmp_path):
    from pathlib import Path
    md = tmp_path / "README.md"
    yaml = tmp_path / "config.yaml"
    md.write_text("# README\n")
    yaml.write_text("a: 1\n")
    out = license_header.scan([tmp_path])
    assert out == []
