# SKILL BIBLE — Swarm & Colony Operations
# Knight: Sir Boris (Colony) / Merlin_Omega (Swarm Oracle) | Layer: L5_AGENTIC | v400.1.0
# LOAD: SWARM_COLONY — instilled on //SWARM //FLEET colony/dispatch tasks

## SRDL — SWARM RAPID DEVELOPMENT LOOP

### PHASE A: MAP (Oracle Broadcast)
- Merlin decomposes prompt into DAG (Directed Acyclic Graph)
- Subtasks assigned to Nano-Knights by capability
- Spawner: `parallel --line-buffer -j <n>` or harness_queue.jsonl IPC

### PHASE B: REDUCE (Iron Gate)
- Sir Sentinel audits merged output
- 10-Line Rule: patch > 10 net lines → HITL_REQUIRED pause
- AST-Aware patching via tree-sitter (no brittle sed/regex)
- Antigravity v2.0 middleware: all I/O atomic writes + backup

### PHASE C: KINETIC EXECUTION
- Write to Shadow Branch first; merge only on SCORPION pass
- All output through anya_gate.validate_output() before user return

## BIO-SWARM ZOOLOGY (Nano-Knight Roster)
| Species | Role | Token Budget | Sandbox |
|---|---|---|---|
| Formica (Ant) | Map-Reduce parallel file ops | 150 tokens | gVisor/Docker |
| Pongid (Gorilla) | Heavy API integration, SDK calls | 300 tokens | Docker |
| Castor (Beaver) | Infrastructure, Dam (isolation env) builds | 200 tokens | Docker |
| Arachne (Spider) | Headless browser, MCP doc scraping | 200 tokens | Docker |
| Simian (Chaos Monkey) | Resilience/entropy injection testing | 150 tokens | isolated |
| Strigiform (Owl) | Swarm oversight, conflict/bloat detection | 100 tokens | none |

## IPC PROTOCOL
- Zero-server: append JSON to `logs/harness_queue.jsonl`
- Format: `{"id":"<uuid>","knight":"<id>","directive":"<task>","priority":<1-5>}`
- SovereignHarness polls every 2s, spawns KnightCell, runs task
- Apoptosis: error_rate > 5% after 10 tasks → cell pruned

## SQUIRE COLONY (CLARITY_CORE)
CLI: `python -m squires.colony [scan|index|ghost|vector|triage|status] [path]`
Pipeline: SCAN → JUDGE → SENTINEL (HITL gate)

| Squire | Function |
|---|---|
| INDEX | B-Tree directory scanner (<1% CPU) |
| GHOST | Alien process detector + quarantine |
| VECTOR | Semantic file clustering (19 intents) |
| SWEEP | Vault staging with HITL approval |
| SCAN | Ghost file vs active tissue detector |
| JUDGE | Keep/Compress/Purge classification |
| SENTINEL | Antigravity backup enforcer |
| MASON | Symbolect/UKG token compressor |

## RUNIC TRIGGERS
| Rune | Action |
|---|---|
| //SWARM | Full hive parallel debug/optimize vote |
| //FLEET | Map-Reduce swarm deployment |
| //SCORPION | Sir Gideon forensic audit (GIDEON_RISK_MATRIX.md) |
| //REZERO | Reject half-done, full restart |
| //ELEPHAS | Infinite Recall — hydrate agents from notebooks |

## ANTI-PATTERNS
- Skipping SENTINEL HITL gate for destructive ops → BLOCKED
- Running >50 Formica instances on 8GB system → RAM ceiling violation
- Swarm without harness IPC → use harness_queue.jsonl, not direct spawn
- Bypassing Shadow Branch for kinetic execution → Iron Gate violation
