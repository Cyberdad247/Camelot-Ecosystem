# GCMN Stub Runtime Flip + Acceptance Report

**Run ISO:** `2026-07-15T06:19:28Z`

**Schema:** `camelot-os/audit/gcmn_runtime_flip/v1`

**Runic router module sha256:** `f99a848226f117848ef90b336d97f6278d91cc6cd98dae6b78fd36bd7cf47f0b`

**Artifact sha256:** `61c23b460e4ac29bff28f57e3f7c490558f014b793499539737eb127791d1921` (path: `C:\Users\vizio\CAMELOT_OS\_tmp\runtime_flip_envelopes.json`)

## Per-Rune Acceptance

| # | rune | snapshot_task_id | status | knight | passed/total | all_pass |
|---|---|---|---|---|---|---|
| 1 | `//SYNC_KBA_DATABASES_SQLCIPHER` | `gcmn-stub-8633da90` | STUB_INERT | sir_sentinel | 18/18 | True |
| 2 | `//LOCK_BIFROST_mTLS_KYBER768` | `gcmn-stub-686a2e38` | STUB_INERT | sir_heimdall | 18/18 | True |
| 3 | `//ENGAGE_RUST_IRON_DAEMON` | `gcmn-stub-d8b3316c` | STUB_INERT | sir_forge | 18/18 | True |
| 4 | `//CRYSTALLIZE_GCMN_vMAX` | `gcmn-stub-78f2269e` | STUB_INERT | sir_boris | 18/18 | True |

## Global Checks

- **task_ids_unique_set_size_equals_runes_count**: `True`
- **harness_subprocess_env_CAMELOT_GCMN_STUBS_ENABLED_1**: `True`
- **runic_router_module_sha256_recorded**: `True`
- **queue_unchanged_by_4_stub_dispatches**: `True`
- **canonical_rune_table_intact**: `True`

## Outcome

**ALL_PASS:** `True` — exit code: `0`
