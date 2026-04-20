# Maximum Compression Strategy (Defense Grid + Ledger Runtime)

## Objective
Reduce storage, I/O, and maintenance overhead while preserving auditability and fast recovery.

## Tiered Policy
1. Hot tier: keep latest 12 Defense Grid cycle JSON files uncompressed for immediate inspection.
2. Warm tier: compress older cycle files with `gzip -9` (`.json.gz`) once older than 30 minutes.
3. Cold tier: retain compressed archives for up to 30 days.
4. Budget cap: enforce max compressed archive budget of 256 MB; purge oldest archives when over budget.

## Integrity and Safety Controls
1. Single-writer lock (`compression_guardian.lock`) prevents parallel corruption.
2. Atomic writes (`tmp -> replace`) for status and compressed outputs.
3. Deterministic gzip output (`mtime=0`) enables stable hash-based deduplication.
4. Deduplicate archived cycles by SHA-256 hash, keeping newest copy.

## Runtime Integration
Compression is executed by:
- `squires/compression_guardian.py`

Integrated into:
- `tools/run_bootstrap_maintenance.ps1`

Startup and recurring execution paths already invoke maintenance; compression now runs automatically each cycle.

## Config and Status
Config:
- `logs/defense_grid/compression_config.json`

Status and metrics:
- `logs/defense_grid/compression_status.json`

## Tuning Recommendations
1. Increase `keep_recent_uncompressed` if frequent manual log inspection is needed.
2. Reduce `compress_older_than_minutes` to 10 for more aggressive footprint reduction.
3. Lower `max_total_archive_bytes` for stricter disk budgets.
4. Lower `max_gzip_age_days` for stronger long-term minimization.
