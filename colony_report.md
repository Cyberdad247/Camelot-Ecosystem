# CLARITY_CORE Colony Report
**Generated:** 2026-08-12 14:01 UTC
**Root:** `C:\Users\vizio\CAMELOT_OS`

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Files scanned | 13,223 |
| Total lines | 3,709,429 |
| Symbols indexed | 36,091 |
| Risk Score | 100.0 / 100 |
| Risk Label | **CRITICAL** |
| HITL Required | Yes ⚠️ |

## Findings

- 134 potential secret(s) detected — CRITICAL
- 35 large file(s) (>500 KB) found
- 213 TODO/FIXME markers — technical debt accumulation
- 3375 duplicate file(s) detected
- 14 unused imports (dead code)
- Large codebase: 3,709,429 lines — context management critical

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
| Secrets (critical) | 134 |
| Warnings | 35 |
| Info | 222 |

### Critical Flags

- `02_FORGE/apps/lux11/firebase-applet-config.json:4` — secret: google_api_key: AIza...Zw4M
- `02_FORGE/apps/lux11/src/tests/smoke.test.ts:7` — secret: generic_token: secr...ugh'
- `02_FORGE/cartridge/bifrost_bridge.py:168` — secret: generic_token: secr...ook"
- `02_FORGE/cartridge/test_bifrost_bridge.py:32` — secret: generic_token: SECR...ret"
- `02_FORGE/kinetic/vizio-router/cmd/pulse/ops/TAILSCALE-KEY-MINT.md:65` — secret: generic_token: TOKE...XXX"
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
- ... and 114 more

## SWEEP Report

| Category | Count |
|----------|-------|
| Duplicate Content | 3375 |
| Unused Import | 14 |
| Unreferenced File | 10 |

## Language Breakdown

| Extension | Files |
|-----------|-------|
| `.md` | 2240 |
| `.py` | 2190 |
| `.rs` | 1931 |
| `.ts` | 1655 |
| `.json` | 1515 |
| `.h` | 816 |
| `.tsx` | 643 |
| `.go` | 493 |
| `.js` | 377 |
| `.cpp` | 239 |
| `.txt` | 234 |
| `.toml` | 229 |
| `.sh` | 189 |
| `.yml` | 174 |
| `.yaml` | 155 |

## Symbol Index (Top 30)

| Symbol | Kind | File | Line |
|--------|------|------|------|
| `main` | function | `chaos_engineer.py` | 451 |
| `ChaosTest` | class | `chaos_engineer.py` | 32 |
| `ChaosEngineer` | class | `chaos_engineer.py` | 40 |
| `_bootstrap_sys_path` | function | `excalibur.py` | 28 |
| `_parse_int_env` | function | `excalibur.py` | 43 |
| `main` | function | `excalibur.py` | 58 |
| `_parse_allowed_origins` | function | `excalibur_controller.py` | 71 |
| `_parse_allowed_origin_regex` | function | `excalibur_controller.py` | 78 |
| `_bundle_root` | function | `excalibur_controller.py` | 124 |
| `_data_root` | function | `excalibur_controller.py` | 133 |
| `_load_state` | function | `excalibur_controller.py` | 217 |
| `_save_state` | function | `excalibur_controller.py` | 236 |
| `_derive_client_ip` | function | `excalibur_controller.py` | 277 |
| `_emit_event` | function | `excalibur_controller.py` | 291 |
| `_require_token` | function | `excalibur_controller.py` | 328 |
| `get_telemetry_status` | function | `excalibur_controller.py` | 349 |
| `_commit_state` | function | `excalibur_controller.py` | 380 |
| `iron_gate_release` | function | `excalibur_controller.py` | 386 |
| `iron_gate_rollback` | function | `excalibur_controller.py` | 417 |
| `infer_command` | function | `excalibur_controller.py` | 448 |
| `_detect_tts_engine` | function | `excalibur_controller.py` | 491 |
| `_synth_chunk` | function | `excalibur_controller.py` | 507 |
| `_resample_wav_to_8k_mono` | function | `excalibur_controller.py` | 542 |
| `_real_tts_chunk_amplitude` | function | `excalibur_controller.py` | 602 |
| `_real_tts_chunks` | function | `excalibur_controller.py` | 607 |
| `_chunks_for_phrase` | function | `excalibur_controller.py` | 640 |
| `_build_audio_packet` | function | `excalibur_controller.py` | 650 |
| `event_generator` | function | `excalibur_controller.py` | 676 |
| `stream_avatar_faculty` | function | `excalibur_controller.py` | 739 |
| `health` | function | `excalibur_controller.py` | 750 |

*...and 36061 more symbols in full index.*

---

*Generated by CLARITY_CORE v1.0.0 — Squire Colony*
*Pipeline: SCAN → INDEX → GHOST → SWEEP → JUDGE → SENTINEL → MASON*