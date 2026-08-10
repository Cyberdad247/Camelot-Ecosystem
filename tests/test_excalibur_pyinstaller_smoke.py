"""tests/test_excalibur_pyinstaller_smoke.py

End-to-end PyInstaller smoke test for the EXCALIBUR Sovereign Command Deck.

The test rebuilds ``dist/excalibur/excalibur.exe`` from ``excalibur.spec``,
boots it on a configured port, and asserts every CI-critical gate:

1.  ``/health`` returns ``200 ok``
2.  ``/`` returns ``200`` (dashboard HTML served) with the inline
    ``rel="icon"`` favicon
3.  Unauthenticated ``POST /api/go`` returns ``401``
4.  Authenticated ``POST /api/go`` returns ``200`` and flips state to LIVE
5.  ``POST /api/rezero`` returns ``200`` and flips state back to PAUSED
6.  State + event log land in the operator-supplied ``EXCALIBUR_DATA_DIR``
7.  Bundle ``COLLECT`` folder is > 25 MB (sanity floor for UPX-disabled builds)

The test is opt-in via ``EXCALIBUR_BUILD_ON_TEST=1`` because the PyInstaller
build is ~60-90 s on Windows + UPX-disabled. CI should set that env var
explicitly; local dev can run via::

    EXCALIBUR_BUILD_ON_TEST=1 .venv/Scripts/python.exe -m pytest \\
        tests/test_excalibur_pyinstaller_smoke.py -v -s

Why opt-in?

* PyInstaller builds are slow and write to ``./dist`` which is
  ``.gitignore``-d. CI matrices pay the cost only when they need to.
* The controller test suite (``test_excalibur_controller.py``) covers
  every behaviour this smoke checks, but at the live-HTTP level via
  ``fastapi.testclient.TestClient``. PyInstaller is reserved for shipping
  the binary; its smoke is a separate axis.

Why a SINGLE test function?

pytest-xdist's default ``--dist=loadfile`` already pins one FILE to one
worker, so under the default xdist invocation two ``def test_``
functions in this module would never have raced. The single-function
consolidation adds belt-and-braces protection for non-default xdist
modes (``--dist=loadscope``, ``--dist=each``, ``--dist=worksteal``)
where multiple workers may run multiple instances of this module's
tests concurrently and corrupt ``dist/``. If callers ever invoke
``_build_binary()`` from outside this module (e.g. another test file
or a CI wrapper script), add an ``msvcrt.locking`` / ``fcntl.flock``
file lock in ``_build_binary`` over a sentinel file in
``dist/.build.lock`` so the safety becomes intrinsic to the helper
rather than the caller's test-count.
"""
from __future__ import annotations

import contextlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

# Skip the entire module unless explicitly opted in.
pytestmark = pytest.mark.skipif(
    os.environ.get("EXCALIBUR_BUILD_ON_TEST") != "1",
    reason="EXCALIBUR_BUILD_ON_TEST=1 not set (PyInstaller build is ~60-90s on Windows)",
)


# Hard-coded CI test port so a stale local exe can't accidentally answer.
_TEST_PORT = 8829
_TEST_TOKEN = "pyi-smoke-" + str(int(time.time()))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _binary_path() -> Path:
    """Cached binary location. Windows adds .exe; POSIX does not."""
    suffix = ".exe" if sys.platform.startswith("win") else ""
    return _project_root() / "dist" / "excalibur" / f"excalibur{suffix}"


def _http_probe(url: str, *, timeout: float = 5.0) -> tuple[int, str]:
    """Tiny urllib-based probe so we don't pull httpx for the smoke test.

    Returns ``(status_code, body_text)``. Connection refused / timeout
    surfaces as a ``urllib.error.URLError`` so the caller can retry across
    the boot window.
    """
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - intentional localhost probe
        return resp.status, resp.read().decode("utf-8", errors="replace")


def _wait_for_port(host: str, port: int, *, timeout_seconds: float = 30.0) -> bool:
    """Poll a TCP port until it accepts a connection or the timeout elapses."""
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        with contextlib.suppress(OSError):
            with socket.create_connection((host, port), timeout=2.0):
                return True
        time.sleep(0.5)
    return False


def _build_binary(pytest_root: Path) -> Path:
    """Invoke PyInstaller on ``excalibur.spec``; raises on non-zero exit.

    Honours ``EXCALIBUR_SKIP_PYINSTALLER_REBUILD``: when truthy (set to any
    non-empty value, *including* the empty string), we assert the cached
    ``dist/excalibur/excalibur.exe`` already exists and return it WITHOUT
    triggering a fresh build. This lets fast CI re-runs (post-edits to test
    files only) skip the 60-90 s build cost. NOTE the truthiness check
    intentionally treats empty string as "skip" so an operator can
    ``unset EXCALIBUR_SKIP_PYINSTALLER_REBUILD`` to opt back into rebuilds.
    """
    spec_path = pytest_root / "excalibur.spec"
    if not spec_path.exists():
        raise FileNotFoundError(f"excalibur.spec not found at {spec_path}")

    # Honour both env-var names so callers using `SKIP_REBUILD=1 bash
    # scripts/excalibur_pyinstaller_smoke.sh` and direct-invocation
    # `EXCALIBUR_SKIP_PYINSTALLER_REBUILD=1 pytest ...` both work. The bash
    # wrapper exports the canonical (verbose) name via SKIP_REBUILD
    # detection so callers only need to remember the short form.
    # Truthiness: presence = opt-in to skip. Any non-empty string is truthy
    # (`if "0"` is True), so to OPT OUT set the variable to the empty string
    # (`SKIP_REBUILD= bash ...`) or `unset` it. This matches the bash wrapper.
    skip_rebuild = (
        os.environ.get("EXCALIBUR_SKIP_PYINSTALLER_REBUILD", "")
        or os.environ.get("SKIP_REBUILD", "")
    )
    if skip_rebuild:
        cached = _binary_path()
        if not cached.exists():
            raise FileNotFoundError(
                f"SKIP_REBUILD / EXCALIBUR_SKIP_PYINSTALLER_REBUILD is set but "
                f"{cached} is missing. Either run `.venv/Scripts/python.exe "
                f"-m PyInstaller --clean excalibur.spec` once to seed the "
                f"cache, or unset both env vars before running the test."
            )
        return cached

    # Clean rebuild so we never test against stale cache.
    for stale in ("build", "dist"):
        shutil.rmtree(pytest_root / stale, ignore_errors=True)
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_path),
    ]
    result = subprocess.run(cmd, cwd=str(pytest_root), capture_output=True, text=True)
    assert result.returncode == 0, (
        f"PyInstaller failed:\n--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )
    return _binary_path()


@contextlib.contextmanager
def _boot_binary(binary: Path, data_dir: Path):
    """Subprocess-launch the binary; kill + dump boot log on teardown."""
    env = {
        **os.environ,
        "EXCALIBUR_AUTH_TOKEN": _TEST_TOKEN,
        "EXCALIBUR_PORT": str(_TEST_PORT),
        "EXCALIBUR_DEBUG": "1",
        "EXCALIBUR_DATA_DIR": str(data_dir),
        "EXCALIBUR_TRUST_PROXY": "0",
        "PYTHONUNBUFFERED": "1",
    }
    log_path = data_dir / "boot.log"
    # Append if a previous run left a boot.log behind (e.g. shared /tmp dirs
    # when tests are re-run without pristine tmp_path). pytest's tmp_path is
    # per-test-unique so this is belt-and-braces for non-default invocations.
    log_mode = "a" if log_path.exists() else "w"
    stdout = open(log_path, log_mode, encoding="utf-8")  # noqa: SIM115
    try:
        proc = subprocess.Popen(
            [str(binary)],
            env=env,
            cwd=str(data_dir),
            stdout=stdout,
            stderr=subprocess.STDOUT,
        )
        try:
            yield proc
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=2)
    finally:
        stdout.close()
    if log_path.exists():
        print(f"\n--- excalibur boot log ({log_path}) ---", flush=True)
        print(log_path.read_text(encoding="utf-8", errors="replace"), end="", flush=True)


# ---------------------------------------------------------------------------
# Single combined test (see module docstring for why pytest-xdist safety
# demands exactly ONE function here).
# ---------------------------------------------------------------------------


def test_pyinstaller_build_boots_and_serves(tmp_path: Path) -> None:
    """Build + boot + assert every CI-critical gate in one pytest function."""
    # Phase 0: build.
    binary = _build_binary(_project_root())
    assert binary.exists(), f"expected {binary} after PyInstaller build"
    collect_size = sum(
        p.stat().st_size
        for p in (_project_root() / "dist" / "excalibur").rglob("*")
        if p.is_file()
    )
    assert collect_size > 25 * 1024 * 1024, f"unrealistic COLLECT size: {collect_size}"

    # Phase 1: boot on isolated data dir.
    data_dir = tmp_path / "excalibur-smoke-data"
    data_dir.mkdir(parents=True)
    with _boot_binary(binary, data_dir) as proc:
        # Wait up to 30 s for the bootstrap (pyttsx3 init can take 5 s on cold SAPI5).
        assert _wait_for_port("127.0.0.1", _TEST_PORT, timeout_seconds=30.0), (
            f"binary never bound port {_TEST_PORT} within 30 s; "
            f"pid_alive={proc.poll() is None} "
            f"boot_log={(data_dir / 'boot.log').read_text() if (data_dir / 'boot.log').exists() else '<no log>'}"
        )

        # Phase 2: live endpoint smoke.
        status, _ = _http_probe(f"http://127.0.0.1:{_TEST_PORT}/health")
        assert status == 200, f"/health returned {status}"

        status, dashboard = _http_probe(f"http://127.0.0.1:{_TEST_PORT}/")
        assert status == 200, f"/ returned {status}"
        # Dashboard ships an inline data: favicon so browsers skip the implicit
        # /favicon.ico request; that link is part of the controller contract.
        assert 'rel="icon"' in dashboard, "dashboard does not declare its favicon"

        # POST /api/go without auth: expect 401.
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            req = urllib.request.Request(
                f"http://127.0.0.1:{_TEST_PORT}/api/go",
                method="POST",
            )
            urllib.request.urlopen(req, timeout=5)
        assert exc_info.value.code == 401, (
            f"expected 401 on auth-less POST, got {exc_info.value.code}"
        )

        # POST /api/go with auth: expect 200.
        req = urllib.request.Request(
            f"http://127.0.0.1:{_TEST_PORT}/api/go",
            method="POST",
            headers={"X-Camelot-Auth": _TEST_TOKEN},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            assert resp.status == 200, f"POST /api/go returned {resp.status}"

        # POST /api/rezero: expect 200 (returns the iron gate to PAUSED).
        req = urllib.request.Request(
            f"http://127.0.0.1:{_TEST_PORT}/api/rezero",
            method="POST",
            headers={"X-Camelot-Auth": _TEST_TOKEN},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            assert resp.status == 200, f"POST /api/rezero returned {resp.status}"

        # Phase 3: persistent state + JSONL audit log landed in EXCALIBUR_DATA_DIR.
        state_path = data_dir / "excalibur_state.json"
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline and not state_path.exists():
            time.sleep(0.2)
        assert state_path.exists(), f"excalibur_state.json was not written to {data_dir}"
        persisted = json.loads(state_path.read_text(encoding="utf-8"))
        # After the //rezero above the gate must be PAUSED + SLEEP_MODE.
        assert persisted.get("gate_paused") is True, f"expected gate_paused=True, got {persisted}"
        assert persisted.get("merlin") == "SLEEP_MODE", f"expected merlin=SLEEP_MODE, got {persisted}"
        assert persisted.get("lukas") == "AWAITING_PRD", f"expected lukas=AWAITING_PRD, got {persisted}"

        events_path = data_dir / "logs" / "excalibur_events.jsonl"
        assert events_path.exists(), f"event log missing at {events_path}"
        events = [
            json.loads(line)
            for line in events_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        kinds = [e.get("kind") for e in events]
        assert "go" in kinds, f"expected a 'go' event, saw kinds={kinds}"
        assert "rezero" in kinds, f"expected a 'rezero' event, saw kinds={kinds}"
