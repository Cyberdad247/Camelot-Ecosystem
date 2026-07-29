#!/usr/bin/env python3
"""camelot-status.py — CAMELOT Apex OS v400.1.0 Full Health Check
==================================================================
Runs after awaken to verify all P0/P1/P2 components are operational.

Usage:
    python scripts/camelot-status.py          # full check, rich output
    python scripts/camelot-status.py --json   # machine-readable
    python scripts/camelot-status.py --quick  # pass/fail only
"""
from __future__ import annotations

import json
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "03_VAULT" / "training" / "configs"))
sys.path.insert(0, str(ROOT / "control_plane"))

_C = {"g": "\033[92m", "y": "\033[93m", "r": "\033[91m", "c": "\033[96m",
      "m": "\033[95m", "x": "\033[0m", "B": "\033[1m", "d": "\033[2m"}

results: list[dict] = []


def _probe_port(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _read_bifrost_token() -> str | None:
    token_path = Path.home() / ".camelot" / "bifrost.token"
    try:
        token = token_path.read_text(encoding="ascii").strip()
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        return None
    return token or None


def _http_status(url: str, *, token: str | None = None, timeout: float = 2.0) -> int:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["x-camelot-token"] = token
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)
    except (OSError, urllib.error.URLError, TimeoutError):
        return 0


def check(label: str, ok: bool, detail: str = "", warn_only: bool = False) -> dict:
    r = {"label": label, "ok": ok, "detail": detail, "warn_only": warn_only}
    results.append(r)
    if "--json" not in sys.argv:
        if ok:
            sym = f"{_C['g']}OK {_C['x']}"
        elif warn_only:
            sym = f"{_C['y']}WARN{_C['x']}"
        else:
            sym = f"{_C['r']}FAIL{_C['x']}"
        print(f"  [{sym}] {_C['B']}{label:<38}{_C['x']} {_C['d']}{detail}{_C['x']}")
    return r


def section(title: str):
    if "--json" not in sys.argv:
        print(f"\n{_C['c']}{_C['B']}-- {title} --{_C['x']}")


# ── PHASE CHECKS ──────────────────────────────────────────────────────────────

section("Boot Phases (6-phase awaken)")
check("CLIProxy :8080",        _probe_port("127.0.0.1", 8080), "control plane gateway")
check("Kinetic Edge :3001",    _probe_port("127.0.0.1", 3001), "MCP Rust Axum server")
check("Bifrost Sidecar :8011", _probe_port("127.0.0.1", 8011), "Go transport sidecar", warn_only=True)
check("Qdrant :6333",          _probe_port("127.0.0.1", 6333), "vector DB", warn_only=True)
check("Saltare :8085",         _probe_port("127.0.0.1", 8085), "gateway", warn_only=True)
check("Holotable :3000",       _probe_port("127.0.0.1", 3000), "UI dashboard", warn_only=True)
check("Sovereign Harness PID", (ROOT / "logs" / "harness.pid").exists(), "24/7 daemon")
token = _read_bifrost_token()
if token:
    sidecar_status = _http_status("http://127.0.0.1:8011/v1/bifrost/status", token=token)
    check("Bifrost Sidecar auth", sidecar_status == 200, f"/v1/bifrost/status={sidecar_status}", warn_only=True)
try:
    from control_plane.nano_swarm_runtime import write_runtime_status

    nano_swarm_status = write_runtime_status()
    check(
        "Nano Swarm Runtime",
        bool(nano_swarm_status.get("runtime_ready")),
        (
            f"{nano_swarm_status.get('status')} "
            f"nodes={nano_swarm_status.get('promoted_count')}/{nano_swarm_status.get('node_count')} "
            f"formal_gate={nano_swarm_status.get('formal_gate_status')}"
        ),
        warn_only=True,
    )
except Exception as e:
    check("Nano Swarm Runtime", False, str(e), warn_only=True)

section("P0 — Brain Directory + GIDEON + RBAC")
skills_dir = ROOT / ".hive" / "skills"
expected_skills = ["rust-kinetic", "security", "swarm-colony", "python-api",
                   "nextjs", "reasoning", "voice-media", "bitnet"]
for sk in expected_skills:
    check(f".hive/skills/{sk}.md", (skills_dir / f"{sk}.md").exists())
check("brain_directory.md",  (skills_dir / "brain_directory.md").exists())
check("GIDEON_RISK_MATRIX",  (ROOT / "03_VAULT" / "training" / "configs" / "GIDEON_RISK_MATRIX.md").exists())
check("access_matrix.json",  (ROOT / "03_VAULT" / "training" / "configs" / "config" / "access_matrix.json").exists())
check("rbac_matrix.py",      (ROOT / "control_plane" / "rbac_matrix.py").exists())
# RBAC smoke test
try:
    from rbac_matrix import RBACMatrix
    r = RBACMatrix()
    ok_chk, _ = r.check("sir_boris", "KINETIC", "rust/kinetic", 0.5)
    bad_chk, _ = r.check("rogue", "KINETIC", "security", 0.9)
    check("RBAC smoke test", ok_chk and not bad_chk, "sir_boris=PASS, rogue=BLOCKED")
except Exception as e:
    check("RBAC smoke test", False, str(e))

section("P1 — Lord Archivist + Runic Router + Bio-Swarm + Learnings")
check("lord_archivist.py",   (ROOT / "control_plane" / "lord_archivist.py").exists())
check("runic_router.py",     (ROOT / "control_plane" / "runic_router.py").exists())
check("Knights/learnings.md",(ROOT / "03_VAULT" / "Knights" / "learnings.md").exists())
check("swarm_spawner/",      (ROOT / "kinetic_edge" / "swarm_spawner" / "Cargo.toml").exists())
check("swarm-spawner binary",(ROOT / "bin" / "swarm-spawner.exe").exists(), warn_only=True)
# Runic router smoke test
try:
    from runic_router import list_runes, parse_rune
    runes = list_runes()
    required_runic = {
        "//BOOT",
        "//FORGE",
        "//CONTRACT",
        "//SWARM",
        "//PLAN",
        "//HEAL",
        "//SCAN",
        "//STATUS",
    }
    present_runic = set(runes["runic_commands"])
    missing_runic = sorted(required_runic - present_runic)
    rune_ok = not missing_runic and len(runes["omega_runes"]) >= 30
    detail = f"runic={len(runes['runic_commands'])} omega={len(runes['omega_runes'])}"
    if missing_runic:
        detail += f" missing={','.join(missing_runic)}"
    check("Runic Router core+30", rune_ok, detail)
    parsed = parse_rune("//FORGE test")
    check("Rune parse //FORGE", parsed is not None, str(parsed))
except Exception as e:
    check("Runic Router", False, str(e))
# Lord Archivist GEP smoke
try:
    from lord_archivist import _detect_skill_gaps, _scan_skill_versions
    skills = _scan_skill_versions()
    gaps = _detect_skill_gaps()
    check("GEP scan skills", len(skills) >= 7, f"{len(skills)} skills scanned")
    check("GEP no skill gaps", len(gaps) == 0, f"gaps={gaps or 'none'}")
except Exception as e:
    check("GEP scan", False, str(e))
# Harness loop count
try:
    harness_src = (ROOT / "control_plane" / "harness.py").read_text(encoding="utf-8")
    loop_count = harness_src.count("_loop()")
    check("Harness loops (7+)", loop_count >= 7, f"{loop_count} loops registered")
except Exception as e:
    check("Harness loop count", False, str(e))

section("P2 — Modal LT + BitNet + GPU TUI + PQCrypto")
check("modal_lt_server.py",  (ROOT / "03_VAULT" / "training" / "configs" / "modal_lt_server.py").exists())
check("bitnet_swarm.py",     (ROOT / "03_VAULT" / "training" / "configs" / "bitnet_swarm.py").exists())
check("bitnet.md skill",     (skills_dir / "bitnet.md").exists())
check("ollama_catalog.json", (ROOT / "03_VAULT" / "training" / "configs" / "ollama_catalog.json").exists())
check("pqcrypto Cargo.toml", (ROOT / "kinetic_edge" / "pqcrypto" / "Cargo.toml").exists())
check("pqcrypto_bridge.py",  (ROOT / "control_plane" / "pqcrypto_bridge.py").exists())
pq_bin = ROOT / "bin" / "camelot-pqcrypto.exe"
check("pqcrypto binary",     pq_bin.exists(), "build: cargo build --release in kinetic_edge/pqcrypto/", warn_only=True)
if pq_bin.exists():
    try:
        out = subprocess.run([str(pq_bin), "self-test"], capture_output=True, text=True, timeout=10)
        try:
            pq_json = json.loads(out.stdout)
            pq_ok = pq_json.get("status") == "PASS"
        except Exception:
            pq_ok = "PASS" in out.stdout
        check("PQCrypto self-test", pq_ok, "ML-KEM-768 + ML-DSA-65 NIST L3")
    except Exception as e:
        check("PQCrypto self-test", False, str(e))
# GPU TUI go build
vizion_src = ROOT / "01_KERNEL" / "senses" / "vizion-telemetry" / "main.go"
has_gpu = vizion_src.exists() and "gpuMsg" in vizion_src.read_text(encoding="utf-8", errors="replace")
check("Vizion GPU panel", has_gpu, "gpuMsg struct present in main.go")
check("vizion-telemetry.exe", (ROOT / "bin" / "vizion-telemetry.exe").exists(),
      "build: go build in 02_FORGE/vizion-telemetry/", warn_only=True)

section("P3 — Build Harness + Quarantine + Ollama")
check("scripts/build_kinetic.sh",  (ROOT / "scripts" / "build_kinetic.sh").exists())
check("scripts/build_kinetic.ps1", (ROOT / "scripts" / "build_kinetic.ps1").exists())
quarantine_plan = Path("C:/Users/vizio/CAMELOT_DefenseGrid_Quarantine/REMEDIATION_PLAN_2026-04-21.md")
check("DefenseGrid REMEDIATION_PLAN", quarantine_plan.exists(), "6 SSH keys flagged — HITL required")
check("Ollama catalog",    (ROOT / "03_VAULT" / "training" / "configs" / "ollama_catalog.json").exists())
# Ollama model check
try:
    ollama_bin = shutil.which("ollama")
    model_count = 0
    detail = ""
    if ollama_bin:
        out = subprocess.run([ollama_bin, "list"], capture_output=True, text=True, timeout=10)
        lines = [l_ for l_ in out.stdout.splitlines() if l_.strip()]
        model_lines = [l_ for l_ in lines if not l_.lstrip().startswith("NAME")]
        model_count = len(model_lines)
        detail = f"{model_count} models"
        if out.returncode != 0 and out.stderr.strip():
            detail += f" cli_err={out.stderr.strip()[:60]}"
    else:
        detail = "ollama not in PATH"

    if model_count == 0:
        try:
            with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as resp:
                payload = json.loads(resp.read().decode("utf-8", errors="replace"))
            model_count = len(payload.get("models", []))
            detail = f"{model_count} models via api"
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if not detail:
                detail = str(e)[:60]

    check("Ollama models loaded", model_count >= 4, f"{detail} (gemma3/qwen3/qwen3.5/qwen2.5-coder)")
except FileNotFoundError:
    check("Ollama binary", False, "ollama not in PATH", warn_only=True)
except Exception as e:
    check("Ollama", False, str(e)[:60], warn_only=True)

section("P4 — Sir Gideon + Switchboard + Anya Gate")
check("sir_gideon.py",      (ROOT / "03_VAULT" / "training" / "configs" / "knights" / "sir_gideon.py").exists())
check("switchboard.py",     (ROOT / "control_plane" / "switchboard.py").exists())
check("switchboard_manifest", (ROOT / "logs" / "switchboard_manifest.json").exists(), "run: python control_plane/switchboard.py")
check("anya_gate.py",       (ROOT / "control_plane" / "anya_gate.py").exists())
# Switchboard live count
try:
    import json as _json
    _mf = ROOT / "logs" / "switchboard_manifest.json"
    _m  = _json.loads(_mf.read_text(encoding="utf-8"))
    _live = sum(1 for v in _m.get("terminals", {}).values() if v.get("status") in ("live", "assumed_live"))
    _total = len(_m.get("terminals", {}))
    check("Switchboard terminals", _live >= 8, f"{_live}/{_total} live (sir_mnemo dark=expected)")
except Exception as _e:
    check("Switchboard terminals", False, str(_e)[:60], warn_only=True)
# SCORPION gate — GIDEON_RISK_SCORE <= 2
try:
    sys.path.insert(0, str(ROOT / "03_VAULT" / "training" / "configs"))
    from knights.sir_gideon import run_scorpion
    _rpt = run_scorpion()
    _score_ok = _rpt.gideon_risk_score <= 2
    check("//SCORPION gate", _score_ok,
          f"GIDEON_RISK_SCORE={_rpt.gideon_risk_score} ({'PASS' if _score_ok else 'FAIL — Iron Gate HITL'})")
except Exception as _e:
    check("//SCORPION gate", False, str(_e)[:80])

# ── SUMMARY ──────────────────────────────────────────────────────────────────

total = len(results)
passed = sum(1 for r in results if r["ok"])
failed = sum(1 for r in results if not r["ok"] and not r["warn_only"])
warned = sum(1 for r in results if not r["ok"] and r["warn_only"])

if "--json" in sys.argv:
    print(json.dumps({"passed": passed, "failed": failed, "warned": warned, "total": total,
                      "checks": results}, indent=2))
else:
    print()
    if failed == 0:
        color = _C["g"]
        status = "ALL SYSTEMS GO"
    elif failed <= 2:
        color = _C["y"]
        status = "DEGRADED"
    else:
        color = _C["r"]
        status = "CRITICAL"
    print(f"  {color}{_C['B']}{status}: {passed}/{total} checks green, "
          f"{warned} warn, {failed} fail{_C['x']}")
    if warned > 0:
        print(f"  {_C['y']}WARN items need: bash scripts/build_kinetic.sh (3 binaries){_C['x']}")
    if failed == 0 and warned == 0:
        print(f"  {_C['c']}CAMELOT Apex OS v400.1.0 — Lattice Radiant FULLY OPERATIONAL{_C['x']}")

sys.exit(0 if failed == 0 else 1)
