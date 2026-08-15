"""moa_routing_capture — bounded two-hook routing capture (Keys-Setup port).

Port of the Keys-Setup MoA routing-capture pattern
(02_FORGE/KINETIC_ARMORY/Keys-Setup-.../router/routing_router.py +
router/routing_log.py) into the Camelot cartridge model, made BOUNDED:

- **No raw content.** Keys-Setup logs `user_message` / `assistant_response`
  verbatim; this port logs only `intent_hash` (sha256) + a `verdict` enum.
  Raw transcripts are memory-plane data and stay out of the routing log
  (SADD §15.1 L4 quarantine; privacy rule).
- **Explicit correlation, no shared state file.** Keys-Setup passes the
  pre-hook decision through a `_last_routing.json` side file; this port hands
  the decision dict straight from `pre_route()` to `post_route()` so the pair
  is atomic and testable.
- **Bounded retention.** Log rotates at `MOA_LOG_MAX_LINES` (default 10 000);
  the miner dedupes by `(intent_hash, chosen_agent, verdict)` and caps output
  with `--limit`.

The two hooks together produce exactly the routing-log schema
`mine_signal.py` consumes: a routing decision pair per LLM call, ready to be
weighted (routing 1.5, cloud-gold specialist 2.0) and quarantined for review —
the training pipeline stays a verified pipeline, not an observed self-claim.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

LOG_ENV = "MOA_ROUTING_LOG"
MAX_LINES_ENV = "MOA_LOG_MAX_LINES"
DEFAULT_LOG = str(Path.home() / ".camelot" / "routing_log.jsonl")
DEFAULT_MAX_LINES = 10_000

# §5.5 effect classes used by the classifier.
EFFECT_CLASSES = frozenset({
    "ro.fetch", "ro.audit", "internal.synth", "workspace.test",
    "workspace.patch", "promote.worktree.merge", "promote.deploy",
    "external.publish.draft", "external.publish.publish", "external.email.send",
    "payment.invoice.draft", "payment.invoice.issue", "payment.capture",
    "payment.refund", "device.calendar.write", "device.sms.send",
    "device.call.initiate", "promote.failover",
})

TIERS = ("T0", "T1", "T2", "T3", "T4")

# Canonical routing-log line. Raw content NEVER appears here.
ROUTING_LOG_FIELDS = (
    "correlation_id",
    "ts",
    "effect_class",
    "risk_tier",
    "chosen_agent",
    "intent_hash",
    "verdict",
    "latency_ms",
    "cloud_gold",
    "evidence_refs",
)

VERDICTS = ("pass", "partial", "fail", "escalated")


def intent_hash(intent: str) -> str:
    return "sha256:" + hashlib.sha256(intent.encode("utf-8")).hexdigest()


def log_path() -> str:
    return os.environ.get(LOG_ENV, DEFAULT_LOG)


def max_lines() -> int:
    try:
        value = int(os.environ.get(MAX_LINES_ENV, DEFAULT_MAX_LINES))
    except ValueError:
        return DEFAULT_MAX_LINES
    # Honor the configured cap; only reject non-positive values (which would
    # rotate on every append). A small cap like 5 is legitimate for tests.
    return value if value >= 1 else DEFAULT_MAX_LINES


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _line(line: dict[str, Any]) -> dict[str, Any]:
    """Project onto the canonical schema, dropping anything extra."""
    return {k: line.get(k) for k in ROUTING_LOG_FIELDS}


def pre_route(
    intent: str,
    effect_class: str,
    tier: str,
    chosen_agent: str,
    correlation_id: str | None = None,
) -> dict[str, Any]:
    """Pre-hook: classify an intent into a routing decision (no side effects).

    Effect class + tier come from the caller (Sentinel's §13.1 classification);
    this hook binds them to a chosen agent and returns the decision for the
    post-hook. Mirror of Keys-Setup's `routing_router.py` pre_llm_call hook,
    minus the shared state file.
    """
    if effect_class not in EFFECT_CLASSES:
        raise ValueError(f"unknown effect class: {effect_class}")
    if tier not in TIERS:
        raise ValueError(f"unknown tier: {tier}")
    return {
        "correlation_id": correlation_id or f"cor_{abs(hash(intent)):x}",
        "ts": _now_iso(),
        "effect_class": effect_class,
        "risk_tier": tier,
        "chosen_agent": chosen_agent,
        "intent_hash": intent_hash(intent),
        "verdict": None,
        "latency_ms": None,
        "cloud_gold": False,
        "evidence_refs": [],
    }


def post_route(
    decision: dict[str, Any],
    verdict: str,
    latency_ms: int = 0,
    cloud_gold: bool = False,
    evidence_refs: Iterable[str] = (),
    target: str | None = None,
) -> dict[str, Any]:
    """Post-hook: append ONE bounded routing-log line for the call.

    Mirror of Keys-Setup's `routing_log.py` post_llm_call hook. `verdict` is
    an enum (not free text) and `evidence_refs` are receipt-style refs, so the
    line stays redacted and chain-traceable. Returns the written line.
    """
    if verdict not in VERDICTS:
        raise ValueError(f"verdict must be one of {VERDICTS}, got {verdict!r}")
    line = _line({**decision, "verdict": verdict, "latency_ms": int(latency_ms),
                  "cloud_gold": bool(cloud_gold),
                  "evidence_refs": list(evidence_refs)})
    _append_bounded(target or log_path(), line)
    return line


def _append_bounded(path: str, line: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    limit = max_lines()
    if p.exists() and p.stat().st_size > 0:
        count = sum(1 for _ in p.open("r", encoding="utf-8"))
        if count >= limit:
            rotated = p.with_name(p.name + ".1")
            rotated.write_bytes(p.read_bytes())  # keep last full window, drop oldest
            p.write_text("", encoding="utf-8")
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, sort_keys=True) + "\n")


def read_log(path: str | None = None) -> list[dict[str, Any]]:
    p = Path(path or log_path())
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
