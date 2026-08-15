"""mine_signal — bounded training-signal miner (Keys-Setup port).

Port of `train/mine_signal.py` from the vendored Keys-Setup stack into the
Camelot cartridge model, made deterministic + bounded:

- **Deterministic.** Same routing log in → byte-identical `train_signals.jsonl`
  out (stable sort by task hash + ts). `--self-test` asserts this against an
  embedded fixture so "self-improvement" is a reproducible pipeline, not a
  narrative claim (repo evidence gate).
- **Bounded.** Output rows are capped by `--limit` (default 5 000) and deduped
  on `(task_hash, chosen_agent, verdict)`. Records carry content hashes only —
  never raw transcripts.
- **Weight table** follows the Keys-Setup `lora-loop.md` contract for the kinds
  this bounded port can emit: `routing` 1.5 (improves routing logic),
  `specialist` 2.0 for cloud-gold pairs (the local stack got it wrong and a
  frontier model corrected it). Aggregation / task_outcome kinds need raw
  drafts or a task DB this port deliberately does not capture.

Output schema: {"kind", "weight", "task_hash", "chosen_agent", "verdict",
"source", "ts"} — signed downstream at review, quarantined per §15.1 L4.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from routing_capture import ROUTING_LOG_FIELDS, read_log

DEFAULT_LIMIT = 5_000

# Kind → weight, per lora-loop.md (only kinds this bounded port emits).
WEIGHTS = {"routing": 1.5, "specialist": 2.0}

_SELF_TEST_FIXTURE = [
    {"correlation_id": "cor_a", "ts": "2026-08-15T10:00:00.000+00:00",
     "effect_class": "ro.fetch", "risk_tier": "T0", "chosen_agent": "sir-ant",
     "intent_hash": "sha256:1111", "verdict": "pass", "latency_ms": 12,
     "cloud_gold": False, "evidence_refs": []},
    {"correlation_id": "cor_b", "ts": "2026-08-15T10:00:01.000+00:00",
     "effect_class": "internal.synth", "risk_tier": "T1",
     "chosen_agent": "merlin", "intent_hash": "sha256:2222",
     "verdict": "escalated", "latency_ms": 900, "cloud_gold": True,
     "evidence_refs": ["receipt://gideon/x"]},
]


def mine(lines: list[dict], limit: int = DEFAULT_LIMIT) -> list[dict]:
    """Produce deduped, weight-tagged, deterministically-ordered signals."""
    signals: dict[tuple, dict] = {}
    for line in lines:
        task_hash = line.get("intent_hash") or ""
        agent = line.get("chosen_agent") or ""
        verdict = line.get("verdict") or ""
        if not task_hash or verdict not in ("pass", "partial", "fail", "escalated"):
            continue
        key = (task_hash, agent, verdict)
        gold = bool(line.get("cloud_gold"))
        kind = "specialist" if gold else "routing"
        signals[key] = {
            "kind": kind,
            "weight": WEIGHTS[kind],
            "task_hash": task_hash,
            "chosen_agent": agent,
            "verdict": verdict,
            "source": line.get("effect_class") or "unknown",
            "ts": line.get("ts") or "",
        }
    ordered = sorted(signals.values(), key=lambda s: (s["task_hash"], s["ts"]))
    return ordered[:limit]


def _self_test() -> int:
    out = mine(_SELF_TEST_FIXTURE)
    expected = [
        {"kind": "routing", "weight": 1.5, "task_hash": "sha256:1111",
         "chosen_agent": "sir-ant", "verdict": "pass", "source": "ro.fetch",
         "ts": "2026-08-15T10:00:00.000+00:00"},
        {"kind": "specialist", "weight": 2.0, "task_hash": "sha256:2222",
         "chosen_agent": "merlin", "verdict": "escalated", "source": "internal.synth",
         "ts": "2026-08-15T10:00:01.000+00:00"},
    ]
    if out != expected:
        print(f"self-test FAILED:\n  got:      {out}\n  expected: {expected}", file=sys.stderr)
        return 1
    # Determinism: re-mine the fixture output (already-mining is idempotent-ish).
    if mine([{"intent_hash": "sha256:1111", "chosen_agent": "sir-ant",
              "verdict": "pass", "cloud_gold": False, "effect_class": "ro.fetch",
              "ts": "2026-08-15T10:00:00.000+00:00"}] * 3) != [
        {"kind": "routing", "weight": 1.5, "task_hash": "sha256:1111",
         "chosen_agent": "sir-ant", "verdict": "pass", "source": "ro.fetch",
         "ts": "2026-08-15T10:00:00.000+00:00"},
    ]:
        print("self-test FAILED: dedupe broken", file=sys.stderr)
        return 1
    print("self-test OK: deterministic, deduped, weighted")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--log", default=None, help="routing log JSONL (default: $MOA_ROUTING_LOG)")
    ap.add_argument("--out", default=None, help="output train_signals.jsonl (default: next to log)")
    ap.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="max signal rows")
    ap.add_argument("--self-test", action="store_true", help="run the determinism self-test and exit")
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()

    lines = read_log(args.log)
    signals = mine(lines, limit=args.limit)
    out_path = Path(args.out or (Path(args.log or "routing_log.jsonl").with_name("train_signals.jsonl")))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for s in signals:
            fh.write(json.dumps(s, sort_keys=True) + "\n")
    print(f"mined {len(signals)} signals from {len(lines)} routing lines -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
