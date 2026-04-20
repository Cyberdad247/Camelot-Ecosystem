# Small LLM Integration Enhancements for Grid Oversight

## Objective
Use a local/small LLM as a low-cost reasoning layer on top of existing telemetry to improve triage quality without changing safety gates.

## Recommended Architecture
1. Keep all hard controls deterministic:
- ledger lock + atomic sync
- scope filters
- defense grid thresholds
- scheduled task cadence

2. Add an advisory micro-layer:
- New input: latest `ledger_sync_status.json`
- New input: latest `defense_grid_cycle_*.json`
- Output: structured advisory JSON only (no direct mutation rights)

3. Route advisory through HITL:
- Squire produces proposed actions
- Sentinel enforces backup/human approval
- Human approves execution

## Suggested Small LLM Use Cases
1. Bottleneck compression:
- Summarize top 3 blockers from Defense Grid reports.

2. Drift anomaly detection:
- Detect unusual changes in discovered ledger count or terminal/process patterns.

3. Priority ranking:
- Rank cleanup actions by estimated impact and risk.

4. Cross-platform intent normalization:
- Map Claude/Codex/Gemini session notes into one canonical ledger entry proposal.

## Candidate Integration Points
1. `squires/cloud/squire_grid_council.py`
- Add optional `advisor` section populated by small LLM inference.

2. New module proposal:
- `squires/cloud/squire_micro_advisor.py`
- `analyze(status_json, defense_json) -> advisory_json`

3. New telemetry artifact:
- `logs/defense_grid/grid_advisory_latest.json`

## Minimal Advisory Schema (Strict JSON)
```json
{
  "summary": "short status summary",
  "risk_level": "LOW|MEDIUM|HIGH",
  "top_actions": [
    {"action": "string", "reason": "string", "priority": 1}
  ],
  "confidence": 0.0
}
```

## Model Strategy
1. Default:
- Small local model (3B-8B) for advisory summaries.

2. Escalation:
- If confidence < threshold, escalate to larger model for second opinion.

3. Cost control:
- Run only on schedule boundaries (every N cycles) or when grid != GREEN.

## Safety Rules
1. LLM never writes ledgers directly.
2. LLM never changes scheduler/task configuration.
3. LLM output must be schema-valid; invalid output is discarded.
4. All destructive recommendations must pass Sentinel + HITL.

## Phase Plan
1. Phase 1:
- Add advisory reader/writer with mocked responses.

2. Phase 2:
- Wire real small LLM inference (local runtime) with strict schema validation.

3. Phase 3:
- Add historical trend analysis over last 24h of reports.
