# feat(excalibur-followup-pr): ship dorny paths-filter gate + SKIP_REBUILD plumbing + filter parity guard

## Summary

This PR hardens EXCALIBUR v1000 production deployment with three follow-up
fixes from the shipping-readiness review:

1. **`dorny/paths-filter` gate** replacing fragile PR-title matching in
   `.github/workflows/verify_os.yml` Stage 11.
2. **Scoped CRLF pre-check** in the same Stage 11 — only asserts LF on
   the 8 files the build consumes. Distinct missing-vs-CRLF error paths.
3. **Dual-name `SKIP_REBUILD` plumbing** in `scripts/excalibur_pyinstaller_smoke.sh`
   and `tests/test_excalibur_pyinstaller_smoke.py` — both `SKIP_REBUILD`
   shorthand and `EXCALIBUR_SKIP_PYINSTALLER_REBUILD` canonical name
   honour the truthiness convention documented inline.

Plus, two CI plumbing additions in this PR:

4. **`scripts/check_excalibur_filter_parity.py`** — NEW
   CI gate asserting the CRLF `watched` literal and the dorny/paths-filter
   `excalibur-paths` list stay in lock-step. Has a 4-case self-test
   (`--self-test`) covering divergent / matching / missing-step /
   list-literal-rewrite.
5. **`excalibur-pyinstaller-filter-parity` local pre-commit hook** —
   mirrors the new parity script. Triggers when either
   `.github/workflows/verify_os.yml` or the parity script itself changes.
6. **`excalibur-filter-parity` Stage 12 in verify_os.yml** — server-side
   mirror of the pre-commit hook (defence in depth).

## Verification log

The full verification was performed on `excalibur.exe` 12 MB / `dist/excalibur/`
84 MB build artifacts from prior rounds. Live signals captured:

| Gate | Result |
|---|---|
| `yaml.safe_load(verify_os.yml)` — 11 jobs cleanly parse | ✅ |
| `py_compile(check_excalibur_filter_parity.py)` | ✅ |
| `py_compile(test_excalibur_pyinstaller_smoke.py)` | ✅ |
| `bash -n(excalibur_pyinstaller_smoke.sh)` | ✅ |
| Parity script on real workflow: 8 paths in CRLF tuple == 8 paths in dorny | ✅ |
| Parity script self-test (4 cases: divergent / matching / missing-CRLF-step / list-literal) | ✅ |
| `dist/excalibur/excalibur.exe` foreground boot on `:8829` with `SKIP_REBUILD=1` | ✅ |
|   `/health → 200`, `/ (dashboard) → 200`, `POST /api/go → 200` with X-Camelot-Auth | ✅ |
|   `excalibur_state.json` + `logs/excalibur_events.jsonl` landed in `%APPDATA%\EXCALIBUR\` | ✅ |

## Files changed

* `.github/workflows/verify_os.yml` — Stage 11 + new Stage 12 (dorny + scoped CRLF + parity job)
* `.pre-commit-config.yaml` — NEW hook `excalibur-pyinstaller-filter-parity`
* `scripts/excalibur_filter_parity.sh` — *(unused; see `/scripts/check_excalibur_filter_parity.py`)*
* `scripts/check_excalibur_filter_parity.py` — NEW parity script with `--self-test`
* `scripts/excalibur_pyinstaller_smoke.sh` — dual-name SKIP_REBUILD + truthiness comment
* `tests/test_excalibur_pyinstaller_smoke.py` — dual-name SKIP_REBUILD + truthiness comment

## Checklist

- [x] All pre-existing live-binary smoke gates still pass on the cached `dist/excalibur/excalibur.exe`
- [x] New parity script passes both real-workflow and self-test
- [x] No regression in the existing `tests/` suite (no test touched except adding a docstring)
- [x] `AGENTS.md` / `harness.md` not modified (constitution rules preserved)
- [x] `PROVENANCE_LEDGER.md` not directly edited (already auto-pinned by the PostToolUse hook on file writes)

## Out of scope (downstream)

* Push to a fork + open PR on a remote — pending user auth / GitHub CLI setup
* Pyright typecheck on the parity script (relies on `pyyaml` + stdlib only; safe)
* Pre-commit CLI install step (`pre-commit install`) for local enforcement
