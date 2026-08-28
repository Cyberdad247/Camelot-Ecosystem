# CLARITY_CORE Colony Report
**Generated:** 2026-08-26 19:34 UTC
**Root:** `C:\Users\vizio\CAMELOT_OS`

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Files scanned | 31,605 |
| Total lines | 7,086,803 |
| Symbols indexed | 70,059 |
| Risk Score | 100.0 / 100 |
| Risk Label | **CRITICAL** |
| HITL Required | Yes ⚠️ |

## Findings

- 198 potential secret(s) detected — CRITICAL
- 44 large file(s) (>500 KB) found
- 1493 TODO/FIXME markers — technical debt accumulation
- 10574 duplicate file(s) detected
- 285 unused imports (dead code)
- Large codebase: 7,086,803 lines — context management critical

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
| Secrets (critical) | 198 |
| Warnings | 44 |
| Info | 1503 |

### Critical Flags

- `02_FORGE/apps/lux11/firebase-applet-config.json:4` — secret: google_api_key: AIza...Zw4M
- `02_FORGE/apps/lux11/src/tests/smoke.test.ts:7` — secret: generic_token: secr...ugh'
- `02_FORGE/cartridge/bifrost_bridge.py:168` — secret: generic_token: secr...ook"
- `02_FORGE/cartridge/test_bifrost_bridge.py:32` — secret: generic_token: SECR...ret"
- `02_FORGE/kinetic/vizio-router/cmd/pulse/ops/TAILSCALE-KEY-MINT.md:65` — secret: generic_token: TOKE...XXX"
- `02_FORGE/KINETIC_ARMORY/ansible/test/integration/targets/ansible-config/tasks/main.yml:128` — secret: generic_token: toke...ken"
- `02_FORGE/KINETIC_ARMORY/ansible/test/integration/targets/ansible-vault/password-script.py:23` — secret: generic_token: PASS...ord'
- `02_FORGE/KINETIC_ARMORY/ansible/test/integration/targets/module_utils_Ansible.Basic/library/ansible_basic_tests.ps1:666` — secret: generic_token: pass...TER"
- `02_FORGE/KINETIC_ARMORY/ansible/test/integration/targets/user/tasks/test_create_user_password.yml:53` — secret: generic_token: pass...ord"
- `02_FORGE/KINETIC_ARMORY/ansible/test/units/parsing/vault/test_vault.py:159` — secret: generic_token: pass...ord"
- `02_FORGE/KINETIC_ARMORY/ansible/test/units/parsing/vault/test_vault.py:217` — secret: generic_token: pass...ord"
- `02_FORGE/KINETIC_ARMORY/ansible/test/units/parsing/vault/test_vault.py:610` — secret: generic_token: pass...ord"
- `02_FORGE/KINETIC_ARMORY/ansible/test/units/parsing/vault/test_vault_editor.py:52` — secret: generic_token: pass...ord"
- `02_FORGE/KINETIC_ARMORY/freellmapi/README.md:454` — secret: generic_token: api_...key"
- `02_FORGE/KINETIC_ARMORY/freellmapi/README.md:648` — secret: generic_token: TOKE...key"
- `02_FORGE/KINETIC_ARMORY/freellmapi/server/src/__tests__/lib/crypto-keyfile.test.ts:87` — secret: generic_token: secr...ret'
- `02_FORGE/KINETIC_ARMORY/goose/crates/goose/src/providers/gcpauth.rs:608` — secret: private_key: ----...----
- `02_FORGE/KINETIC_ARMORY/goose/crates/goose/src/providers/gcpauth.rs:879` — secret: private_key: ----...----
- `02_FORGE/KINETIC_ARMORY/goose/documentation/docs/guides/enhanced-code-editing.md:23` — secret: generic_token: API_...ere"
- `02_FORGE/KINETIC_ARMORY/goose/documentation/docs/guides/environment-variables.md:55` — secret: generic_token: API_...ere"
- ... and 178 more

## SWEEP Report

| Category | Count |
|----------|-------|
| Duplicate Content | 10574 |
| Unused Import | 285 |
| Unreferenced File | 383 |

## Language Breakdown

| Extension | Files |
|-----------|-------|
| `.py` | 7352 |
| `.rs` | 4506 |
| `.h` | 3527 |
| `.md` | 3056 |
| `.ts` | 2835 |
| `.json` | 2799 |
| `.yml` | 2292 |
| `.txt` | 938 |
| `.tsx` | 845 |
| `.sh` | 823 |
| `.c` | 565 |
| `.go` | 510 |
| `.js` | 449 |
| `.toml` | 407 |
| `.cpp` | 241 |

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

*...and 70029 more symbols in full index.*

---

*Generated by CLARITY_CORE v1.0.0 — Squire Colony*
*Pipeline: SCAN → INDEX → GHOST → SWEEP → JUDGE → SENTINEL → MASON*