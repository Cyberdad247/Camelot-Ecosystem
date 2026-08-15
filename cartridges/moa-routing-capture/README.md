# moa-routing-capture

Bounded port of the Keys-Setup **two-hook routing-capture pattern**
(`02_FORGE/KINETIC_ARMORY/Keys-Setup-Autonomous-Self-Improving-Local-Inference-Stack`,
pinned `3fda3e85`) into the Camelot cartridge model.

**Pattern:** pre-hook classifies a call into a routing decision; post-hook
records the outcome; a miner converts the log into weighted training signals
for a self-improvement loop. Keys-Setup's loop runs on DGX Spark hardware with
raw transcripts; this port keeps the **pattern** while bounding every part that
Camelot's evidence gates and privacy rule require.

## Boundedness contract

| Keys-Setup original | This port |
|---|---|
| Logs `user_message` / `assistant_response` verbatim | Logs `intent_hash` (sha256) + `verdict` enum only — raw content never enters the log |
| Passes pre→post decisions via `_last_routing.json` side file | `pre_route()` hands the decision dict directly to `post_route()` (atomic, correlation_id-bound) |
| Unbounded append to `~/.hermes/routing_log.jsonl` | Rotates at `MOA_LOG_MAX_LINES` (default 10 000) |
| `mine_signal.py` emits raw `messages` pairs | Emits content-hash-keyed signal records, deduped, capped by `--limit` |
| Weights: routing 1.5, aggregation 1.2, specialist 0.8–2.0, task_outcome 1.0 | Emits the kinds this bounded port can prove: **routing 1.5**, **specialist (cloud-gold) 2.0**. Aggregation/task_outcome need raw drafts or a task DB this port deliberately doesn't capture |
| "Self-improving" claimed by the stack | `--self-test` proves determinism + dedupe on an embedded fixture — a reproducible pipeline, not a narrative claim |

Mined signals are **quarantined** (`memory.write_l4_quarantine`, SADD §15.1
Tier 4) — untrusted until a verifier passes them; nothing self-promotes.

## Usage

```python
from routing_capture import pre_route, post_route

decision = pre_route("summarize the audit", "internal.synth", "T1", "merlin")
post_route(decision, verdict="pass", latency_ms=320,
           evidence_refs=["receipt://gideon/9"], target="/path/to/routing_log.jsonl")
```

```bash
# Mine weighted training signals (deterministic; deduped; capped at 5000)
python cartridges/moa-routing-capture/mine_signal.py \
  --log ~/.camelot/routing_log.jsonl --out ~/.camelot/train_signals.jsonl

# Prove the pipeline is deterministic + bounded
python cartridges/moa-routing-capture/mine_signal.py --self-test
```

Environment: `MOA_ROUTING_LOG` (default `~/.camelot/routing_log.jsonl`),
`MOA_LOG_MAX_LINES` (default 10000).

## Manifest

`manifest.json` — signed §8.2/§8.3 (`camelot-community`, cap **T1**, research
node profile, entrypoints `audit`/`summarize`, rollback
`destroy_ephemeral_worktree`). Signature verified by
`tests/test_cartridge_manifests.py`; behavior covered by
`tests/test_moa_routing_capture.py`.
