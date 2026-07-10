# CLARITY_CORE Colony Report
**Generated:** 2026-07-10 01:36 UTC
**Root:** `C:\Users\vizio\CAMELOT_OS`

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Files scanned | 27,431 |
| Total lines | 5,987,347 |
| Symbols indexed | 94,992 |
| Risk Score | 100.0 / 100 |
| Risk Label | **CRITICAL** |
| HITL Required | Yes ⚠️ |

## Findings

- 997 potential secret(s) detected — CRITICAL
- 29 large file(s) (>500 KB) found
- 211 TODO/FIXME markers — technical debt accumulation
- 5487 duplicate file(s) detected
- 14 unused imports (dead code)
- Large codebase: 5,987,347 lines — context management critical

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
| Secrets (critical) | 997 |
| Warnings | 29 |
| Info | 220 |

### Critical Flags

- `02_FORGE/apps/lux11/src/tests/smoke.test.ts:7` — secret: generic_token: secr...ugh'
- `02_FORGE/cartridge/bifrost_bridge.py:169` — secret: generic_token: secr...ook"
- `02_FORGE/cartridge/test_bifrost_bridge.py:31` — secret: generic_token: SECR...ret"
- `02_FORGE/KINETIC_ARMORY/goose/crates/goose/src/providers/gcpauth.rs:608` — secret: private_key: ----...----
- `02_FORGE/KINETIC_ARMORY/goose/crates/goose/src/providers/gcpauth.rs:879` — secret: private_key: ----...----
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
- ... and 977 more

## SWEEP Report

| Category | Count |
|----------|-------|
| Duplicate Content | 5487 |
| Unused Import | 14 |
| Unreferenced File | 295 |

## Language Breakdown

| Extension | Files |
|-----------|-------|
| `.ts` | 14979 |
| `.md` | 2814 |
| `.py` | 2043 |
| `.rs` | 1913 |
| `.json` | 1854 |
| `.h` | 816 |
| `.tsx` | 661 |
| `.go` | 488 |
| `.js` | 381 |
| `.sh` | 280 |
| `.txt` | 258 |
| `.cpp` | 238 |
| `.toml` | 226 |
| `.yml` | 173 |
| `.yaml` | 168 |

## Symbol Index (Top 30)

| Symbol | Kind | File | Line |
|--------|------|------|------|
| `main` | function | `chaos_engineer.py` | 450 |
| `ChaosTest` | class | `chaos_engineer.py` | 31 |
| `ChaosEngineer` | class | `chaos_engineer.py` | 39 |
| `_bootstrap_sys_path` | function | `excalibur.py` | 27 |
| `_parse_int_env` | function | `excalibur.py` | 42 |
| `main` | function | `excalibur.py` | 57 |
| `_parse_allowed_origins` | function | `excalibur_controller.py` | 72 |
| `_parse_allowed_origin_regex` | function | `excalibur_controller.py` | 79 |
| `_bundle_root` | function | `excalibur_controller.py` | 125 |
| `_data_root` | function | `excalibur_controller.py` | 134 |
| `_load_state` | function | `excalibur_controller.py` | 218 |
| `_save_state` | function | `excalibur_controller.py` | 237 |
| `_derive_client_ip` | function | `excalibur_controller.py` | 278 |
| `_emit_event` | function | `excalibur_controller.py` | 292 |
| `_require_token` | function | `excalibur_controller.py` | 329 |
| `get_telemetry_status` | function | `excalibur_controller.py` | 345 |
| `_commit_state` | function | `excalibur_controller.py` | 376 |
| `iron_gate_release` | function | `excalibur_controller.py` | 382 |
| `iron_gate_rollback` | function | `excalibur_controller.py` | 413 |
| `_detect_tts_engine` | function | `excalibur_controller.py` | 477 |
| `_synth_chunk` | function | `excalibur_controller.py` | 511 |
| `_resample_wav_to_8k_mono` | function | `excalibur_controller.py` | 546 |
| `_real_tts_chunk_amplitude` | function | `excalibur_controller.py` | 606 |
| `_real_tts_chunks` | function | `excalibur_controller.py` | 611 |
| `_chunks_for_phrase` | function | `excalibur_controller.py` | 644 |
| `_build_audio_packet` | function | `excalibur_controller.py` | 654 |
| `event_generator` | function | `excalibur_controller.py` | 680 |
| `stream_avatar_faculty` | function | `excalibur_controller.py` | 743 |
| `health` | function | `excalibur_controller.py` | 754 |
| `version` | function | `excalibur_controller.py` | 759 |

*...and 94962 more symbols in full index.*

---

*Generated by CLARITY_CORE v1.0.0 — Squire Colony*
*Pipeline: SCAN → INDEX → GHOST → SWEEP → JUDGE → SENTINEL → MASON*