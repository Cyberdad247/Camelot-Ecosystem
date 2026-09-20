# CLARITY_CORE Colony Report
**Generated:** 2026-09-20 00:16 UTC
**Root:** `C:\Users\vizio\CAMELOT_OS`

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Files scanned | 10,375 |
| Total lines | 2,440,498 |
| Symbols indexed | 30,354 |
| Risk Score | 100.0 / 100 |
| Risk Label | **CRITICAL** |
| HITL Required | Yes ⚠️ |

## Findings

- 19 potential secret(s) detected — CRITICAL
- 29 large file(s) (>500 KB) found
- 216 TODO/FIXME markers — technical debt accumulation
- 2059 duplicate file(s) detected
- 80 unused imports (dead code)
- Large codebase: 2,440,498 lines — context management critical

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
| Secrets (critical) | 19 |
| Warnings | 29 |
| Info | 369 |

### Critical Flags

- `02_FORGE/apps/lux11/firebase-applet-config.json:4` — secret: google_api_key: AIza...Zw4M
- `02_FORGE/PORTAL_CORE/Modal/morgana/local_modal.toml:3` — secret: generic_token: secr...iL3'
- `02_FORGE/tools/pi-mono/packages/coding-agent/examples/extensions/custom-provider-anthropic/index.ts:571` — secret: generic_token: apiK...KEY"
- `03_VAULT/credentials/identity_mirror/claude.json:1` — secret: anthropic_key: sk-a...5wAA
- `03_VAULT/credentials/identity_mirror/claude.json:1` — secret: anthropic_key: sk-a...cgAA
- `03_VAULT/Nano-Knights/background.iife.js:842` — secret: generic_token: ApiK...KEY"
- `03_VAULT/Nano-Knights/background.iife.js:870` — secret: generic_token: ApiK...KEY"
- `03_VAULT/Nano-Knights/background.iife.js:870` — secret: generic_token: apiK...KEY"
- `03_VAULT/Nano-Knights/background.iife.js:1093` — secret: generic_token: apiK...KEY"
- `03_VAULT/Nano-Knights/background.iife.js:1093` — secret: generic_token: apiK...KEY"
- `03_VAULT/Nano-Knights/background.iife.js:1096` — secret: generic_token: apiK...KEY"
- `04_KINETIC/nullclaw/config.example.json:27` — secret: private_key: ----...----
- `apps/excalibur-cmd-1/src/state/useEcosystemStore.ts:233` — secret: generic_token: Toke...ION'
- `deploy/multivoice-router/firebase-applet-config.json:4` — secret: google_api_key: AIza...Zw4M
- `harness/contracts/verify_operator_request.py:59` — secret: generic_token: TOKE...ied"
- `kinetic_edge/saltare/internal/gateway/http/middleware.go:133` — secret: generic_token: Toke...ken"
- `packages/policy-engine/schemas/approval-states.yaml:84` — secret: generic_token: toke...KEN"
- `scripts/verify_frozen_bundle.py:41` — secret: generic_token: TOKE...R-A"
- `tools/notebooklm-py/scripts/_live_auth_scenarios/rest_recovery.py:39` — secret: generic_token: TOKE...ken"

## SWEEP Report

| Category | Count |
|----------|-------|
| Duplicate Content | 2059 |
| Unused Import | 80 |
| Unreferenced File | 420 |

## Language Breakdown

| Extension | Files |
|-----------|-------|
| `.py` | 2883 |
| `.json` | 2685 |
| `.md` | 1993 |
| `.ts` | 1098 |
| `.tsx` | 425 |
| `.yaml` | 218 |
| `.js` | 209 |
| `.sh` | 178 |
| `.rs` | 144 |
| `.go` | 141 |
| `.c` | 88 |
| `.h` | 88 |
| `.txt` | 83 |
| `.toml` | 74 |
| `.ps1` | 37 |

## Symbol Index (Top 30)

| Symbol | Kind | File | Line |
|--------|------|------|------|
| `main` | function | `chaos_engineer.py` | 450 |
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

*...and 30324 more symbols in full index.*

---

*Generated by CLARITY_CORE v1.0.0 — Squire Colony*
*Pipeline: SCAN → INDEX → GHOST → SWEEP → JUDGE → SENTINEL → MASON*