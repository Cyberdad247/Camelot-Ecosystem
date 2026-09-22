# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""OMEGA Triage & Crucible pipeline engine — integrated CI/CD verification DAG.

Implements the System Directive as runnable stages over REAL local systems:

- Phase 1 FORMAL TRIAGE ... AnyaGate PARSE->ENRICH->COMPILE->ROUTE->VALIDATE.
- Phase 2 ADVERSARIAL DIALECTIC ... SirSocrates 5-question examination.
- Phase 3 KINETIC FABRICATION ... 10-line Iron Gate firewall + Z3 PDDL verification.
- Phase 4 SHADOW CRUCIBLE ... 5 deterministic edge probes (static).
- Seal ... Anya VALIDATE + append-only ledger receipt (⚜️_SOVEREIGN_TRUTH).

Explicitly DEFERRED (reported, never faked): SMT autoformalizer output,
13-agent council vote, fork/CoW shadow MicroVM, live Gideon 13-gate audit.
Those require runtimes absent from this host; the static stages above are the
honest subset that executes here.

Metadata:
  @context https://camelot-os.dev/ukg/v11000/cloudbrain_ci_cd
  @type Sovereign_MetaCompiler_Continuous_Dispatch
  @id OMEGA_TRIAGE_UNIT_SEED
  @host_constraint 8GB_EDGE_STRICT
"""

from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_CAMELOT_ROOT = Path(__file__).resolve().parent.parent.parent

ENGINE_CONTEXT = "https://camelot-os.dev/ukg/v11000/cloudbrain_ci_cd"
ENGINE_TYPE = "Sovereign_MetaCompiler_Continuous_Dispatch"
ENGINE_ID = "OMEGA_TRIAGE_UNIT_SEED"
SEAL_GLYPH = "⚜️_SOVEREIGN_TRUTH"

IRON_GATE_MAX_PATCH_LINES = 10
HUB_LANE_MAX_BYTES = 8 * 1024

_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9]{8,}"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*\S+"),
)

_DIFF_FENCE = re.compile(r"```diff(.*?)```", re.S)


def _ensure_sys_path() -> None:
    for extra in (_CAMELOT_ROOT, _CAMELOT_ROOT / "01_KERNEL"):
        if str(extra) not in sys.path:
            sys.path.insert(0, str(extra))


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Phase 1: Formal triage (Anya) ────────────────────────────────────────────

def phase_triage(payload: str) -> Dict[str, Any]:
    """Run AnyaGate; emit ROOT_CAUSE_ANALYSIS + TOON PROPOSED_RESOLUTION."""
    _ensure_sys_path()
    from control_plane.core.anya_gate import AnyaGate

    result = AnyaGate().process(payload)
    parse = result.parse
    titan = result.titan
    validation = result.validation
    return {
        "root_cause_analysis": {
            "intent_type": parse.intent_type,
            "complexity": parse.complexity,
            "privacy": parse.privacy,
            "velocity": parse.velocity,
            "entities": parse.entities,
            "constraints": parse.constraints,
        },
        "proposed_resolution_toon": {
            "directive": titan.directive,
            "target_layer": titan.target_layer,
            "execution_mode": titan.execution_mode,
            "constraints_encoded": titan.constraints_encoded,
            "route_knight": result.route_knight,
            "route_engine": result.route_engine,
        },
        "iron_gate": validation.iron_gate,
        "validation_issues": validation.issues,
    }


# ── Phase 2: Adversarial dialectic (Socrates) ────────────────────────────────

def phase_dialectic(payload: str, triage: Dict[str, Any]) -> Dict[str, Any]:
    """Run SirSocrates; emit SOCRATIC_FLAWS."""
    _ensure_sys_path()
    from control_plane.core.sir_socrates import SirSocrates

    exam = SirSocrates(log_verdicts=False).examine_all(payload)
    flaws: List[str] = ["Socrates %s: blocking" % q for q in exam.blocking_questions]
    if triage["root_cause_analysis"]["privacy"] >= 0.8:
        flaws.append("privacy>=0.8: route secret-bearing material to SIR_GHOST air-gap")
    if len(payload.encode("utf-8")) > HUB_LANE_MAX_BYTES:
        flaws.append("payload exceeds 8KiB hub lane: travel by signed object reference, not inline")
    for pat in _SECRET_PATTERNS:
        if pat.search(payload):
            flaws.append("secret-like material inline in payload: strip before dispatch")
            break
    return {
        "socratic_verdict": exam.verdict,
        "blocking_questions": exam.blocking_questions,
        "socratic_flaws": flaws,
    }


# ── Phase 3: Kinetic fabrication (Codex firewall + Z3) ───────────────────────

def _extract_diff(payload: str) -> str:
    match = _DIFF_FENCE.search(payload)
    return match.group(1).strip() if match else ""


def _diff_line_count(diff: str) -> int:
    return sum(1 for line in diff.splitlines() if line.startswith(("+", "-")) and not line.startswith(("+++", "---")))


def phase_fabricate(payload: str) -> Dict[str, Any]:
    """Enforce the 10-line firewall and Z3-verify any embedded diff."""
    _ensure_sys_path()
    from control_plane.infra.z3_verify import PatchIntent, verify_patch

    diff = _extract_diff(payload)
    if not diff:
        return {
            "kinetic_patch": "DEFERRED_TO_FORGE",
            "detail": "no fenced diff in payload; patch authoring stays with SIR_FORGE/SIR_CODEX under HITL",
            "firewall": "NOT_APPLICABLE",
            "z3": "NOT_RUN",
        }
    changed = _diff_line_count(diff)
    firewall = "PASS" if changed <= IRON_GATE_MAX_PATCH_LINES else "FIREWALL_VIOLATION"
    z3_verdict = verify_patch(PatchIntent(description=payload[:500], diff=diff))
    return {
        "kinetic_patch": "PROPOSED" if firewall == "PASS" and z3_verdict.safe else "BLOCKED",
        "changed_lines": changed,
        "firewall_limit": IRON_GATE_MAX_PATCH_LINES,
        "firewall": firewall,
        "z3": {"verdict": z3_verdict.verdict, "detail": z3_verdict.detail, "violated": z3_verdict.violated},
        "diff_preview": diff[:500],
    }


# ── Phase 4: Shadow crucible (5 static edge probes) ──────────────────────────

def phase_crucible(payload: str, triage: Dict[str, Any], fabrication: Dict[str, Any]) -> Dict[str, Any]:
    """5 deterministic edge probes. Static by design — no MicroVM on this host."""
    probes: List[Dict[str, Any]] = []

    def probe(name: str, ok: bool, detail: str) -> None:
        probes.append({"name": name, "pass": ok, "detail": detail})

    probe("secret_egress", not any(p.search(payload) for p in _SECRET_PATTERNS), "no inline secrets")
    probe(
        "lane_size",
        len(payload.encode("utf-8")) <= HUB_LANE_MAX_BYTES,
        "%d bytes vs 8KiB lane" % len(payload.encode("utf-8")),
    )
    probe("wellformed_input", bool(payload and payload.strip()), "non-empty decodable text")
    route_knight = triage.get("proposed_resolution_toon", {}).get("route_knight", "")
    probe(
        "route_resolved",
        isinstance(route_knight, str) and bool(route_knight.strip()),
        "route_knight=%s" % route_knight,
    )
    fab = fabrication
    z3_raw = fab.get("z3")
    z3_verdict = z3_raw.get("verdict") if isinstance(z3_raw, dict) else z3_raw
    probe(
        "fabrication_gate",
        fab.get("kinetic_patch") in ("PROPOSED", "DEFERRED_TO_FORGE") and fab.get("firewall") != "FIREWALL_VIOLATION",
        "patch=%s firewall=%s z3=%s" % (fab.get("kinetic_patch"), fab.get("firewall"), z3_verdict),
    )
    passed = sum(1 for p in probes if p["pass"])
    return {"probes": probes, "passed": passed, "total": len(probes), "go_signal": passed == len(probes)}


# ── Tether matrix + seal ─────────────────────────────────────────────────────

TETHER_ROLES = ("MERLIN_OMEGA", "SIR_SOCRATES", "SIR_CODEX", "SIR_GIDEON", "ANYA_OMEGA")


def tether_matrix() -> Dict[str, Any]:
    """CloudBrain tether presence per pipeline role (registry lookup, offline)."""
    try:
        _ensure_sys_path()
        from memory.cloudbrain_connector import KNIGHT_NOTEBOOKS

        return {role: (role in KNIGHT_NOTEBOOKS) for role in TETHER_ROLES}
    except Exception:  # noqa: BLE001
        return {role: False for role in TETHER_ROLES}


def _seal_ledger(report: Dict[str, Any], ledger_path: Optional[Path] = None) -> bool:
    """Append one receipt row (HYDRATION_MGR format). Append-only, never edits."""
    path = ledger_path or (_CAMELOT_ROOT / "PROVENANCE_LEDGER.md")
    try:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(
                "| %s | OMEGA_TRIAGE | %s [%s] | %s |\n"
                % (report["completed_at"], report["input_digest"], report["verdict"], report["seal"])
            )
        return True
    except Exception:  # noqa: BLE001
        return False


# ── DAG entrypoint ───────────────────────────────────────────────────────────

def run(payload: str, ledger_path: Optional[Path] = None, seal: bool = True) -> Dict[str, Any]:
    """Execute the 4-phase DAG. Returns the full report (JSON-safe)."""
    import hashlib

    started = time.monotonic()
    triage = phase_triage(payload)
    if triage["iron_gate"] == "BLOCKED":
        return _finish(payload, triage, None, None, None, "HALT_GATE_BLOCKED", started, ledger_path, seal)

    dialectic = phase_dialectic(payload, triage)
    if (
        dialectic["socratic_verdict"] == "BLOCKED"
        or "Q4" in dialectic["blocking_questions"]
        or len(dialectic["socratic_flaws"]) >= 3
    ):
        # Q4 is the Iron Gate bypass detector: a bypass attempt is per se
        # disqualifying, even when the overall verdict is only PARTIAL.
        return _finish(payload, triage, dialectic, None, None, "REZERO_DIALECTIC", started, ledger_path, seal)

    fabrication = phase_fabricate(payload)
    if fabrication.get("firewall") == "FIREWALL_VIOLATION" or (isinstance(fabrication.get("z3"), dict) and fabrication["z3"].get("verdict") == "Z3_BLOCK"):
        return _finish(payload, triage, dialectic, fabrication, None, "REZERO_FABRICATION", started, ledger_path, seal)

    crucible = phase_crucible(payload, triage, fabrication)
    verdict = "GO_SIGNAL" if crucible["go_signal"] else "REZERO_CRUCIBLE"
    return _finish(payload, triage, dialectic, fabrication, crucible, verdict, started, ledger_path, seal)


def _finish(payload, triage, dialectic, fabrication, crucible, verdict, started, ledger_path, seal) -> Dict[str, Any]:
    import hashlib

    report = {
        "@context": ENGINE_CONTEXT,
        "@type": ENGINE_TYPE,
        "@id": ENGINE_ID,
        "@host_constraint": "8GB_EDGE_STRICT",
        "input_digest": "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "knight": "merlin_omega",
        "mode": "ORACLE",
        "triage": triage,
        "dialectic": dialectic,
        "fabrication": fabrication,
        "crucible": crucible,
        "tether_matrix": tether_matrix(),
        "verdict": verdict,
        "seal": SEAL_GLYPH if verdict == "GO_SIGNAL" else "NO_SEAL",
        "deferred": ["SMT autoformalizer output", "13-agent council vote", "CoW shadow MicroVM", "live Gideon 13-gate audit"],
        "duration_s": round(time.monotonic() - started, 2),
        "completed_at": _utcnow(),
    }
    report["sealed"] = _seal_ledger(report, ledger_path) if seal else False
    return report


def main(argv: Optional[List[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="OMEGA Triage & Crucible pipeline engine")
    parser.add_argument("payload", nargs="?", default="", help="Issue/error-log payload (or - for stdin)")
    parser.add_argument("--no-seal", action="store_true", help="Skip ledger receipt")
    args = parser.parse_args(argv)
    payload = sys.stdin.read() if args.payload == "-" else args.payload
    if not payload.strip():
        parser.error("empty payload")
    print(json.dumps(run(payload, seal=not args.no_seal), indent=2))
    return 0


if __name__ == "__main__":
    main()
