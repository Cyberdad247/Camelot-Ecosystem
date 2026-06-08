# CLARITY_CORE Colony Report
**Generated:** 2026-06-05 15:01 UTC
**Root:** `C:\Users\vizio\CAMELOT_OS`

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Files scanned | 20,489 |
| Total lines | 5,136,881 |
| Symbols indexed | 71,862 |
| Risk Score | 100.0 / 100 |
| Risk Label | **CRITICAL** |
| HITL Required | Yes ⚠️ |

## Findings

- 797 potential secret(s) detected — CRITICAL
- 34 large file(s) (>500 KB) found
- 206 TODO/FIXME markers — technical debt accumulation
- 4283 duplicate file(s) detected
- 209 unused imports (dead code)
- Large codebase: 5,136,881 lines — context management critical

## Recommendations

- Remove secrets from source, rotate credentials, use `camelot keys set`
- Consider moving large files to .gitignore or media storage
- Triage TODOs: assign to squires or create PROVENANCE_LEDGER entries
- Run MASON to generate dedup report
- Run `ruff check --select F401` or equivalent linter
- Enable //ELEPHAS mode for memory-first execution

## GHOST Triage

| Category | Count |
|----------|-------|
| Secrets (critical) | 797 |
| Warnings | 34 |
| Info | 209 |

### Critical Flags

- `.modal.toml:3` — secret: generic_token: secr...RET"
- `verification.md:49` — secret: generic_token: TOKE...ken"
- `02_FORGE/KINETIC_ARMORY/goose/crates/goose/src/providers/gcpauth.rs:608` — secret: private_key: ----...----
- `02_FORGE/KINETIC_ARMORY/goose/crates/goose/src/providers/gcpauth.rs:879` — secret: private_key: ----...----
- `02_FORGE/KINETIC_ARMORY/goose/crates/goose-mcp/src/developer/editor_models/EDITOR_API_EXAMPLE.md:10` — secret: generic_token: API_...ere"
- `02_FORGE/KINETIC_ARMORY/goose/documentation/docs/guides/enhanced-code-editing.md:23` — secret: generic_token: API_...ere"
- `02_FORGE/KINETIC_ARMORY/goose/documentation/docs/guides/environment-variables.md:55` — secret: generic_token: API_...ere"
- `02_FORGE/KINETIC_ARMORY/goose/documentation/docs/guides/security/prompt-injection-detection.md:84` — secret: generic_token: TOKE...KEN"
- `02_FORGE/KINETIC_ARMORY/goose/documentation/docs/mcp/filesystem-mcp.md:130` — secret: generic_token: SECR...456'
- `02_FORGE/KINETIC_ARMORY/goose/documentation/src/pages/prompt-library/data/prompts/api-documentation-generator.json:8` — secret: generic_token: pass...123'
- `02_FORGE/KINETIC_ARMORY/goose/documentation/src/pages/prompt-library/data/prompts/multi-project-security-audit.json:8` — secret: aws_access_key: AKIA...CDEF
- `02_FORGE/KINETIC_ARMORY/goose/documentation/src/pages/prompt-library/data/prompts/multi-project-security-audit.json:8` — secret: aws_secret: aws_...890'
- `02_FORGE/KINETIC_ARMORY/hermes-agent/agent/redact.py:68` — secret: private_key: ----...----
- `02_FORGE/KINETIC_ARMORY/hermes-agent/optional-skills/email/agentmail/SKILL.md:44` — secret: generic_token: API_...ere"
- `02_FORGE/KINETIC_ARMORY/hermes-agent/optional-skills/security/1password/SKILL.md:61` — secret: generic_token: TOKE...ken"
- `02_FORGE/KINETIC_ARMORY/hermes-agent/skills/mcp/native-mcp/SKILL.md:278` — secret: generic_token: TOKE...xxx"
- `02_FORGE/KINETIC_ARMORY/hermes-agent/skills/mcp/native-mcp/SKILL.md:313` — secret: generic_token: TOKE...xxx"
- `02_FORGE/KINETIC_ARMORY/hermes-agent/skills/mlops/inference/guidance/references/backends.md:28` — secret: generic_token: api_...ere"
- `02_FORGE/KINETIC_ARMORY/hermes-agent/skills/mlops/inference/guidance/references/backends.md:95` — secret: generic_token: api_...ere"
- `02_FORGE/KINETIC_ARMORY/hermes-agent/skills/mlops/inference/guidance/references/backends.md:155` — secret: generic_token: api_...key"
- ... and 777 more

## SWEEP Report

| Category | Count |
|----------|-------|
| Duplicate Content | 4283 |
| Unused Import | 209 |
| Unreferenced File | 284 |

## Language Breakdown

| Extension | Files |
|-----------|-------|
| `.ts` | 9652 |
| `.md` | 2378 |
| `.rs` | 1909 |
| `.py` | 1809 |
| `.json` | 1037 |
| `.h` | 816 |
| `.tsx` | 639 |
| `.go` | 472 |
| `.js` | 344 |
| `.sh` | 259 |
| `.txt` | 248 |
| `.cpp` | 238 |
| `.toml` | 225 |
| `.yml` | 169 |
| `.yaml` | 164 |

## Symbol Index (Top 30)

| Symbol | Kind | File | Line |
|--------|------|------|------|
| `test_pipeline` | function | `test_cloudbrain.py` | 21 |
| `health` | function | `01_KERNEL/agora/brain_worker.py` | 20 |
| `process_intent` | function | `01_KERNEL/agora/brain_worker.py` | 24 |
| `query_memory` | function | `01_KERNEL/agora/brain_worker.py` | 39 |
| `ExcaliburBridge` | class | `01_KERNEL/agora/bridge.py` | 7 |
| `SovereignContext` | class | `01_KERNEL/agora/context.py` | 10 |
| `HUDNode` | class | `01_KERNEL/agora/hud_bridge.py` | 12 |
| `AgentNode` | class | `01_KERNEL/agora/node.py` | 9 |
| `ANPEnvelope` | class | `01_KERNEL/agora/protocol.py` | 13 |
| `ProtocolDocument` | class | `01_KERNEL/agora/protocol.py` | 33 |
| `AgoraRouter` | class | `01_KERNEL/agora/router.py` | 9 |
| `test_swarm` | function | `01_KERNEL/agora/swarm_controller.py` | 56 |
| `SwarmController` | class | `01_KERNEL/agora/swarm_controller.py` | 10 |
| `Videneptus` | class | `01_KERNEL/agora/videneptus.py` | 9 |
| `watchtower_pulse` | function | `01_KERNEL/agora/war_room_protocol.py` | 12 |
| `forge_file` | function | `01_KERNEL/agora/agents/armory.py` | 53 |
| `refactor_file` | function | `01_KERNEL/agora/agents/armory.py` | 64 |
| `create_blueprint` | function | `01_KERNEL/agora/agents/armory.py` | 81 |
| `deploy_system` | function | `01_KERNEL/agora/agents/armory.py` | 93 |
| `execute_test_cycle` | function | `01_KERNEL/agora/agents/armory.py` | 104 |
| `web_search` | function | `01_KERNEL/agora/agents/armory.py` | 110 |
| `forge_svg` | function | `01_KERNEL/agora/agents/armory.py` | 123 |
| `audit_perf` | function | `01_KERNEL/agora/agents/armory.py` | 134 |
| `get_security_constraints` | function | `01_KERNEL/agora/agents/armory.py` | 139 |
| `reconcile_state` | function | `01_KERNEL/agora/agents/armory.py` | 144 |
| `canary_deploy` | function | `01_KERNEL/agora/agents/armory.py` | 149 |
| `clean_system` | function | `01_KERNEL/agora/agents/armory.py` | 155 |
| `symbolect_tool` | function | `01_KERNEL/agora/agents/armory.py` | 164 |
| `TemplateLibrary` | class | `01_KERNEL/agora/agents/armory.py` | 40 |
| `SecurityLevel` | class | `01_KERNEL/agora/agents/knight_base.py` | 30 |

*...and 71832 more symbols in full index.*

---

*Generated by CLARITY_CORE v1.0.0 — Squire Colony*
*Pipeline: SCAN → INDEX → GHOST → SWEEP → JUDGE → SENTINEL → MASON*