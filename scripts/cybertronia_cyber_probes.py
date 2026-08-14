#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""scripts/cybertronia_cyber_probes.py — Spectate the Phase 4 cybertronia-graph stubs.

Boots a real `cognitive_service.py` (subprocess or in-process) and hits all
four spec §8 endpoints to verify the server-side contract surface:

  /snapshot      — 501 + hand-off carrying spec §1 + §4.3 GraphSnapshotStub
  /stream        — 501 + cadence_floor_ms ≥ 160 + media_type=text/event-stream
  /sync-status   — 200 (real handler) with the 4 spec §8 row 4 fields
  /nodes/:id     — 501 + node_id echo; malformed ids → 400 defenders

The probe answers one consumer question: can the GraphSnapshotStub mount
deterministically (mountSurface() → "2d") without a flash of empty canvas?

CLI::

    python scripts/cybertronia_cyber_probes.py                    # subprocess, no phase 2
    python scripts/cybertronia_cyber_probes.py --in-process       # in-process, no phase 2
    python scripts/cybertronia_cyber_probes.py --with-phase2      # pre-stage Phase 2 cursor
    python scripts/cybertronia_cyber_probes.py --json             # machine-readable
"""
from __future__ import annotations

__version__ = "9000.16-CYB-2-probes"

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))


# ── helpers ─────────────────────────────────────────────────────────────────

def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _http_get_json(url: str, timeout: float = 5.0) -> tuple[int, dict]:
    """GET, returning (status_code, parsed_json) tolerating non-2xx."""
    try:
        resp = urllib.request.urlopen(url, timeout=timeout)
        return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def _color(s: str, code: str) -> str:
    return f"\033[{code}m{s}\033[0m" if sys.stdout.isatty() else s


def _green(s: str) -> str: return _color(s, "32")
def _red(s: str) -> str:   return _color(s, "31")
def _yellow(s: str) -> str: return _color(s, "33")


def _mount_surface(payload: dict) -> str:
    """Spec §4.3 — consumer branch: 2d when snapshot is null, 3d otherwise."""
    inner = payload.get("pre_sse_bootstrap") or payload
    return "2d" if inner.get("snapshot") is None else "3d"


def _stage_phase2_cursor(sandbox_root: Path, *, with_phase2: bool) -> Path:
    """Build the SAME tree that cybertronia_compile expects under
    ``CAMELOT_HOME``. Returns the cursor path; writes ``compile_cursor.json``
    only when ``with_phase2=True``.

    Phase 2 cursor lives at:
      <CAMELOT_HOME>/03_VAULT/runtime_state/cybertronia_graph_compile/compile_cursor.json
    """
    ph2 = sandbox_root / "03_VAULT" / "runtime_state" / "cybertronia_graph_compile"
    ph2.mkdir(parents=True, exist_ok=True)
    cursor_path = ph2 / "compile_cursor.json"
    if with_phase2:
        cursor = {
            "schema_version":     "cybertronia.snapshot/v1",
            "last_digest":        "sha256:" + ("0" * 64),
            "last_seen_at_ms":    int(time.time() * 1000),
            "lag_batches":        0,
            "divergence_pending": False,
            "contract_ref": {
                "spec":     "CAMELOT_OS/docs/cybertronia-graph-ui-spec.md",
                "section":  "§8 SSE endpoint shape · row 4 (sync-status)",
                "impl":     "control_plane/cybertronia_compile.py (Phase 2)",
                "consumer": "control_plane/cognitive_service.py sync-status handler",
            },
        }
        cursor_path.write_text(json.dumps(cursor, indent=2), encoding="utf-8")
    return cursor_path


# ── boot: subprocess ────────────────────────────────────────────────────────

class ProbeServer:
    """Spin a real cognitive_service on an ephemeral local port (subprocess)."""

    def __init__(self, *, sandbox_phase2: bool = False) -> None:
        self.sandbox_phase2 = sandbox_phase2
        self._proc: subprocess.Popen | None = None
        self._scratch_dir: tempfile.TemporaryDirectory | None = None
        self._port = _find_free_port()
        self._cursor_path: Path | None = None

    def start(self, timeout_seconds: float = 8.0) -> None:
        env = os.environ.copy()
        env["MEMCASTLE_DB"] = str(Path(tempfile.gettempdir()) / f"probes_{self._port}.db")
        # CAMELOT_HOME must point at the SAME directory tree cybertronia_compile
        # reads from. The prior version wrote to sandbox/phase2/ but the
        # subprocess's cybertronia_compile reads from CAMELOT_HOME/03_VAULT/...
        # — this fix stages the actual expected tree.
        self._scratch_dir = tempfile.TemporaryDirectory(prefix="cyber_probes_")
        sandbox = Path(self._scratch_dir.name)
        camelot_home = sandbox / "camelot_home_mock"
        ph1 = camelot_home / "03_VAULT" / "runtime_state" / "cybertronia_graph"
        ph1.mkdir(parents=True, exist_ok=True)  # ensure PHASE1 dir exists
        self._cursor_path = _stage_phase2_cursor(
            camelot_home, with_phase2=self.sandbox_phase2
        )
        env["CAMELOT_HOME"] = str(camelot_home)

        cmd = [sys.executable, "-m", "control_plane.cognitive_service"]
        self._proc = subprocess.Popen(
            cmd, cwd=str(_PROJECT_ROOT), env=env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        # Wait for /healthz to come up.
        deadline = time.monotonic() + timeout_seconds
        url = f"http://127.0.0.1:{self._port}/healthz"
        while time.monotonic() < deadline:
            try:
                code, _ = _http_get_json(url, timeout=0.5)
                if code == 200:
                    return
            except Exception:
                pass
            if self._proc.poll() is not None:
                _, err = self._proc.communicate(timeout=1)
                raise RuntimeError(
                    f"cognitive_service exited early: code={self._proc.returncode}; "
                    f"stderr=\n{err.decode('utf-8', errors='replace')}"
                )
            time.sleep(0.1)
        raise RuntimeError(f"Timed out waiting for :{self._port}/healthz")

    def stop(self) -> None:
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.send_signal(signal.SIGINT)
                self._proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._proc.kill()
                self._proc.wait(timeout=2)
        if self._scratch_dir is not None:
            self._scratch_dir.cleanup()

    def base(self) -> str:
        return f"http://127.0.0.1:{self._port}"


# ── boot: in-process ────────────────────────────────────────────────────────

class ProbeServerInProcess:
    """In-process boot of cognitive_service (no subprocess)."""

    def __init__(self, *, with_phase2: bool = False) -> None:
        self._port = _find_free_port()
        self._scratch_dir = tempfile.TemporaryDirectory(prefix="cyber_probes_inproc_")
        sandbox = Path(self._scratch_dir.name)
        ph2 = sandbox / "phase2"
        ph2.mkdir(parents=True, exist_ok=True)
        os.environ["MEMCASTLE_DB"] = str(sandbox / "memcastle.db")

        # Always stage the cursor; with_phase2 controls whether it's populated.
        cursor_path = ph2 / "compile_cursor.json"
        if with_phase2:
            cursor = {
                "schema_version":     "cybertronia.snapshot/v1",
                "last_digest":        "sha256:" + ("0" * 64),
                "last_seen_at_ms":    int(time.time() * 1000),
                "lag_batches":        0,
                "divergence_pending": False,
                "contract_ref":       {"spec": "CAMELOT_OS/docs/cybertronia-graph-ui-spec.md"},
            }
            cursor_path.write_text(json.dumps(cursor, indent=2), encoding="utf-8")

        sys.path.insert(0, str(_PROJECT_ROOT))
        import importlib.util
        # Load cognitive_service FIRST — its module-level _load("cybertronia_compile")
        # populates sys.modules["cybertronia_compile"]. The prior version pre-loaded
        # cybertronia_compile itself (under a different module name), which caused
        # cognitive_service to OVERWRITE our patched COMPILE_CURSOR via _load.
        svc_spec = importlib.util.spec_from_file_location(
            "cognitive_service",
            _PROJECT_ROOT / "control_plane" / "cognitive_service.py",
        )
        svc = importlib.util.module_from_spec(svc_spec)
        sys.modules["cognitive_service"] = svc
        svc_spec.loader.exec_module(svc)
        # Monkeypatch AFTER: cognitive_service's `cybertronia_compile` global
        # is `sys.modules["cybertronia_compile"]`, so this hits the same object.
        sys.modules["cybertronia_compile"].COMPILE_CURSOR = cursor_path

        self.svc = svc
        self.httpd = svc.serve("127.0.0.1", self._port)
        self._thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def start(self) -> None:
        self._thread.start()
        time.sleep(0.05)

    def stop(self) -> None:
        self.httpd.shutdown()
        try:
            self.httpd.server_close()
        except Exception:
            pass
        self._scratch_dir.cleanup()

    def base(self) -> str:
        return f"http://127.0.0.1:{self._port}"


# ── probes ───────────────────────────────────────────────────────────────────

def _probe_snapshot(base: str) -> tuple[bool, list[str]]:
    notes: list[str] = []
    code, body = _http_get_json(f"{base}/api/cybertronia-graph/snapshot")
    if code != 501:
        return False, [f"/snapshot: expected 501, got {code}"]
    if body.get("status") != "not_implemented":
        notes.append(f"/snapshot: status={body.get('status')!r}, expected 'not_implemented'")
    if body.get("endpoint") != "/api/cybertronia-graph/snapshot":
        notes.append(f"/snapshot: endpoint on payload is {body.get('endpoint')!r}")
    if body.get("contract_ref", {}).get("schema_version") != "cybertronia.snapshot/v1":
        notes.append("/snapshot: schema_version mismatch (expected cybertronia.snapshot/v1)")
    msg = body.get("expected_response_class", "")
    if "GraphSnapshot" not in msg or "304" not in msg:
        notes.append(f"/snapshot: expected_response_class missing 304 marker: {msg!r}")
    if body.get("phase", {}).get("audit") != "green":
        notes.append("/snapshot: phase.audit must be 'green' on a GREEN audit")
    if body.get("phase4_hand_off", {}).get("additive") is not True:
        notes.append("/snapshot: phase4_hand_off.additive must be True")
    stub = body.get("pre_sse_bootstrap", {})
    if stub.get("type") != "GraphSnapshotStub":
        notes.append("/snapshot: pre_sse_bootstrap.type must be 'GraphSnapshotStub'")
    if stub.get("snapshot") is not None:
        notes.append("/snapshot: pre_sse_bootstrap.snapshot must be null (sentinel)")
    if not stub.get("fallback_2d", False):
        notes.append("/snapshot: pre_sse_bootstrap.fallback_2d must be True")
    return len(notes) == 0, notes


def _probe_stream(base: str) -> tuple[bool, list[str]]:
    notes: list[str] = []
    code, body = _http_get_json(f"{base}/api/cybertronia-graph/stream")
    if code != 501:
        return False, [f"/stream: expected 501, got {code}"]
    if body.get("media_type_target") != "text/event-stream":
        notes.append(f"/stream: media_type_target={body.get('media_type_target')!r}")
    if body.get("cadence_floor_ms", 0) < 160:
        notes.append("/stream: cadence_floor_ms must be ≥ 160 (spec §2)")
    if body.get("contract_ref", {}).get("schema_version") != "cybertronia.delta/v1":
        notes.append("/stream: schema_version should be cybertronia.delta/v1")
    return len(notes) == 0, notes


def _probe_sync_status(base: str, *, with_phase2: bool) -> tuple[bool, list[str]]:
    notes: list[str] = []
    code, body = _http_get_json(f"{base}/api/cybertronia-graph/sync-status")
    if code != 200:
        return False, [f"/sync-status: expected 200 (real handler), got {code}"]
    for k in ("last_digest", "last_seen_at_ms", "lag_batches", "divergence_pending"):
        if k not in body:
            notes.append(f"/sync-status: spec §8 row 4 missing field {k!r}")
    if body.get("phase", {}).get("transport") != "live":
        notes.append("/sync-status: phase.transport should be 'live' (real handler)")
    if not with_phase2:
        if body.get("status") != "phase2_not_ready":
            notes.append(
                "/sync-status: status should be 'phase2_not_ready' "
                "when Phase 2 cursor is absent (fallback path)"
            )
        if body.get("last_digest") is not None:
            notes.append("/sync-status: last_digest should be null when Phase 2 absent")
        if body.get("last_seen_at_ms") != 0:
            notes.append("/sync-status: last_seen_at_ms should be 0 when Phase 2 absent")
    else:
        if body.get("status") != "ok":
            notes.append(
                f"/sync-status: status should be 'ok' with --with-phase2, got {body.get('status')!r}"
            )
        if not (body.get("last_digest") or "").startswith("sha256:"):
            notes.append("/sync-status: last_digest should be 'sha256:…' when Phase 2 ready")
    return len(notes) == 0, notes


def _probe_nodes(base: str) -> tuple[bool, list[str]]:
    notes: list[str] = []
    code, body = _http_get_json(f"{base}/api/cybertronia-graph/nodes/abc123")
    if code != 501:
        return False, [f"/nodes/:id: expected 501, got {code}"]
    if body.get("endpoint") != "/api/cybertronia-graph/nodes/:id":
        notes.append("/nodes/:id: endpoint payload mismatch")
    if body.get("node_id") != "abc123":
        notes.append(f"/nodes/:id: node_id echo wrong (got {body.get('node_id')!r})")
    msg = body.get("expected_response_class", "")
    if "NodeRef" not in msg or "404" not in msg:
        notes.append(f"/nodes/:id: expected_response_class missing 404 marker: {msg!r}")
    code2, body2 = _http_get_json(f"{base}/api/cybertronia-graph/nodes/")
    if code2 != 400:
        notes.append(f"/nodes/:id defenders: bare /nodes/ lost → {code2} (expected 400)")
    if body2.get("error") != "invalid or empty node id":
        notes.append("/nodes/:id defenders: error message mismatch")
    return len(notes) == 0, notes


# ── runner ───────────────────────────────────────────────────────────────────

def run_probes(*, with_phase2: bool, in_process: bool = False) -> dict:
    server = ProbeServerInProcess(with_phase2=with_phase2) if in_process \
        else ProbeServer(sandbox_phase2=with_phase2)
    server.start()
    base = server.base()
    results: dict[str, tuple[bool, list[str]]] = {}
    try:
        results["/snapshot"]    = _probe_snapshot(base)
        results["/stream"]      = _probe_stream(base)
        results["/sync-status"] = _probe_sync_status(base, with_phase2=with_phase2)
        results["/nodes/:id"]   = _probe_nodes(base)
        _, snap_body = _http_get_json(f"{base}/api/cybertronia-graph/snapshot")
        mount = _mount_surface(snap_body)
    finally:
        server.stop()
    return {
        "all_green":          all(ok for ok, _ in results.values()),
        "with_phase2":        with_phase2,
        "mount_surface":      mount,
        "results": {
            k: {"ok": ok, "notes": notes}
            for k, (ok, notes) in results.items()
        },
    }


def _render_report(report: dict, as_json: bool) -> int:
    if as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report["all_green"] else 1

    print(f"\nCybertronia cyber_probes (with_phase2={report['with_phase2']})")
    print(f"mountSurface(payload) → {report['mount_surface']!r}\n")
    for endpoint, verdict in report["results"].items():
        ok, notes = verdict["ok"], verdict["notes"]
        marker = _green("PASS") if ok else _red("FAIL")
        print(f"  [{marker}] {endpoint}")
        for n in notes:
            print(f"          {_yellow('note:')} {n}")
    print()
    if report["all_green"]:
        print(_green("✅ ALL PROBES GREEN — PWA Cockpit + Anya Stub mounts are deterministic."))
        return 0
    print(_red("❌ ONE OR MORE PROBES FAILED — see notes above."))
    return 1


def _swarm_invocation_hint() -> None:
    print("# Equivalent runic router invocation (informational):")
    print("#   python -m control_plane.runic_router --rune SWARM --task 'cyber_probes'")
    print("# Note: the runic router expects task strings dispatched to colony workers;")
    print("# the cyber_probes runner is a standalone script, not a registered colony node.")


# ── CLI ──────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python scripts/cybertronia_cyber_probes.py",
        description="Spectate Phase 4 cybertronia-graph stubs against a live cognitive_service.",
    )
    p.add_argument(
        "--with-phase2",
        action="store_true",
        help="Pre-stage Phase 2 compile_cursor.json (test the 'ok' sync-status path)",
    )
    p.add_argument(
        "--in-process",
        action="store_true",
        help="Boot cognitive_service in-process (hermetic; default subprocess)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of color report",
    )
    return p


def main() -> int:
    args = _build_parser().parse_args()
    try:
        report = run_probes(
            with_phase2=args.with_phase2,
            in_process=args.in_process,
        )
    except Exception as e:
        print(_red(f"probe runner crashed: {type(e).__name__}: {e}"))
        import traceback
        traceback.print_exc()
        return 2
    rc = _render_report(report, as_json=args.json)
    if not args.json and rc == 0:
        _swarm_invocation_hint()
    return rc


if __name__ == "__main__":
    sys.exit(main())
