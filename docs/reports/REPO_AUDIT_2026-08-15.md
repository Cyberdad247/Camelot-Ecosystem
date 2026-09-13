# CAMELOT_OS — Repository Audit Report

**Date:** 2026-08-15
**Scope:** `C:\Users\vizio\CAMELOT_OS` (the live core repository, git HEAD `3d7bef66`)
**Method:** git-index analysis only (`git ls-files` + `os.stat`); no filesystem scans. All figures are from the tracked index at audit time.
**Totals:** 4,586 tracked files, 45.2 MB.

**Rule applied:** this report *recommends*; nothing is deleted or moved. Any execution follows the repo's own HITL gates — operator confirmation first.

---

## 1. Executive summary

| Category | Count | Bytes | Headline |
|---|---|---|---|
| 🧹 Duplicate provenance ledgers | 5 files (3 byte-identical) | ~2.44 MB | Consolidate to one canonical ledger |
| 🧹 Test scratch binaries committed | 24 files (`tests/tmp_*/`) | ~1.0 MB | Should be gitignored, not tracked |
| 🧹 Root scratch (22 .py + 7 .html + 3 stray outputs) | 32 files | ~0.5 MB | Move or delete; root is a release surface |
| 🧹 Root release artifacts (9 .zip/.patch) | 9 files | 241 KB | Move to a `releases/` or `dist/` home |
| 🧹 Committed databases | 4 files | ~0.4 MB | `dump.rdb`, sqlite, ledger.db |
| 🔧 Duplicate lockfiles | 9 files | ~2.4 MB | `01_KERNEL/uv.lock` vs root `uv.lock` |
| 🔧 Oversized PNG assets | 3 knight PNGs | ~1.9 MB | Lossy-optimize (PORTAL_CORE) |

Largest single wins, in order: **ledger dedup (~2.4 MB)**, **lockfile dedup (~2.4 MB)**, **test-scratch removal (~1.0 MB)**, **knight PNG optimization (~1.2 MB)**.

---

## 2. 🧹 Purge candidates (tracked, regenerable / transient / duplicate)

### 2.1 PROVENANCE_LEDGER.md — 5 copies, 3 byte-identical (highest-value dedup)

| File | Size | sha256 (first 12) |
|---|---|---|
| `PROVENANCE_LEDGER.md` (root) | 644,558 | `596a6e676b46` |
| `03_VAULT/PROVENANCE_LEDGER.md` | 637,759 | `d2a37aec0b7d` |
| `03_VAULT/training/configs/PROVENANCE_LEDGER.md` | 637,759 | `d2a37aec0b7d` |
| `docs/PROVENANCE_LEDGER.md` | 637,759 | `d2a37aec0b7d` |
| `control_plane/PROVENANCE_LEDGER.md` | 1,812 | `3cf2295c3e03` |
| **Total** | **2,559,647** | |

- Three files are **byte-identical** (`d2a37aec…`) — pure duplication. The root copy and `control_plane/` copy diverge.
- The ledger is hook-written ("agents must not edit directly"), so it is **regenerable by definition**.
- **Recommendation:** keep ONE canonical ledger (root, referenced by AGENTS.md), update the hook to write only there, delete the other four. Reclaim ~2.4 MB and end split-brain provenance.

### 2.2 Test scratch binaries — `tests/tmp_*/` (24 files, ~1.0 MB)

- `tests/tmp_l2_integration/`, `tests/tmp_mempalace_integrity/`, `tests/tmp_mempalace_isolation/`, `+12 more` — UUID-named dirs of `data_level0.bin`, `header.bin`, `length.bin`, `link_lists.bin`.
- These are **test temp outputs** (memory-palace/L2 integrity fixtures generated at test time).
- **Recommendation:** delete from tracking; add `tests/tmp_*/` to `.gitignore`. Tests regenerate them on run.

### 2.3 Committed databases (4 files, ~0.4 MB)

- `dump.rdb` (root, 16 KB) — Redis dump. Never commit; gitignore.
- `01_KERNEL/titan/Titan_Graph/chromadb/chroma.sqlite3` (323 KB) — vector DB checkpoint.
- `01_KERNEL/agora/Squires/data/sqlite-db/checkpoints.sqlite` — squire checkpoint DB.
- `01_KERNEL/titan/Data_Pipeline/titan_ledger.db` — pipeline ledger.
- **Recommendation:** remove from tracking; keep schema/migration files instead; gitignore the binary DBs.

### 2.4 Root-level scratch (32 files, ~0.5 MB)

- **22 root `.py`:** `test_validation.py`, `test_phase_f.py`, `test_phase_g_*.py` (×4), `test_distance_travel*.py` (×2), `test_qr_pill.py`, `test_cloudbrain.py`, `test_knight_memory.py`, `test_hardening.py`, `load_testing_suite.py`, `local_load_testing_suite.py`, `verify_pyramid.py`, `chaos_engineer.py`, `gradio_photo_viewer.py`, `navigator.py`, `ouroboros.py`, `excalibur.py`, `excalibur_controller.py`, `main.py`
- **7 root `.html`:** `gradio_page.html`, `gradio_debug.html`, `camelot-console-preview.html`, `excalibur_dashboard.html`, `onboarding.html`, `secret-photo-viewer.html`, `tower-scroll.html`
- **3 stray outputs:** `list_recheck.out`, `list_recheck.err`, `sarda_triage.err`
- **Recommendation:** move the test scripts into `tests/` (or delete the dead ones — most `test_phase_*` read as one-off phase validations), move the HTML/photo-viewer cluster into a single app folder (e.g. `02_FORGE/`), delete the stray output files.

### 2.5 Root release artifacts (9 files, 241 KB)

- `camelot-ecosystem-upgrade.zip`, `camelot-omega-bifrost.zip`, `bifrost-tower-r3f.zip`, `bifrost-control-plane.zip`, `bifrost-trust-plane.zip`, `camelot-console-pwa.zip` + `camelot-omega-bifrost.patch`, `bifrost-control-plane.patch`, `bifrost-upgrade.patch`
- **Recommendation:** move into a single `releases/` (or `dist/`) directory; root stays a clean release surface.

### 2.6 Transient root `.md` (execution records)

- `BRANCH_AUDIT_COMPLETION.md`, `SWARM_EXECUTION_COMPLETION.md`, `PR_BODY.md`, `colony_report.md`, `parallel_task_tree.md`, `pre-flight.md`, `tasks.md`, `README-photo-viewer.md`, `TODO.md`
- **Recommendation:** move to `docs/reports/` or `03_VAULT/99_SCRATCHPAD/` — they are records, not repo documentation.

### 2.7 Stray binaries

- `01_KERNEL/iron_gate/DEFENSE_GRID/watchtower.exe` — committed binary. **Recommendation:** build from source; never commit `.exe`.

---

## 3. 🔧 Enhancement opportunities

| Target | Issue | Recommendation |
|---|---|---|
| `01_KERNEL/uv.lock` (512 KB) vs root `uv.lock` (898 KB) | Two uv lockfiles; root package uses which? | Pick one canonical uv root; delete/align the other; document in `docs/adr/` |
| Knight PNGs (`merlin.png` 686 KB, `zenith.png` 657 KB, `anya.png` 528 KB) | Oversized for web delivery in PORTAL_CORE | Lossy-optimize to ≤200 KB each; keep originals in `03_VAULT` if needed |
| `03_VAULT/Missions/verification_ledger.jsonl` (1.1 MB, growing) | Unbounded runtime log tracked in git | Rotate/prune; gitignore the active file; archive finished runs to `99_HISTORY` |
| `03_VAULT/runtime_state/` (106 tracked files) | Telemetry, backups, evidence all mixed in git | Split: `.evidence.json` (keep, auditable) vs telemetry/tissue/backups (gitignore or `99_ARCHIVE`) |
| `docs/CAMELOT_OS_v400_SYSTEM_SPEC.pdf` (5.3 KB) | Superseded spec (v400 ≪ v10000.15) | Move to `99_HISTORY/` or delete; SADD v1.2 is authoritative |
| `01_KERNEL/memory/tissue/flash_context.toon` (532 KB) | Regenerable runtime tissue in git | Exclude from tracking; keep a seed template only |
| `NAVIGATOR_INDEX_2026-07-06.json` (206 KB) | Dated regenerable index | Regenerate on demand; don't track snapshots |
| `_tmp/` (13 files) | Explicit temp dir tracked in git | Add to `.gitignore`; delete tracked copies |

---

## 4. 🧹 Duplicate-lockfile inventory (dedup candidates)

| File | Size |
|---|---|
| `uv.lock` (root) | 898,063 |
| `package-lock.json` (root) | 773,093 |
| `02_FORGE/apps/anya-lyte/package-lock.json` | 729,731 |
| `02_FORGE/pnpm-lock.yaml` | 728,751 |
| `kickbox-audio/drone_bundle/Kickbox-audio/package-lock.json` | 707,640 |
| `01_KERNEL/uv.lock` | 512,321 |
| `02_FORGE/packages/pocket-squire/package-lock.json` | 364,816 |
| `cartridges/system-ui/package-lock.json` | 314,295 |
| `02_FORGE/PORTAL_CORE/Anya_Dashboard/package-lock.json` | 259,584 |
| `02_FORGE/holotable/package-lock.json` | 248,642 |

Lockfiles for separate packages are legitimate. The dedup question applies only to **`01_KERNEL/uv.lock` vs root `uv.lock`** — two uv lockfiles in one repo tree (see §3).

---

## 5. ✅ Do NOT touch (intentional retention)

- **`99_HISTORY/`** — intentional archive (e.g. `harness_queue.20260520-100450.jsonl.gz`, 1.3 MB). It exists to hold history; purging it defeats its purpose.
- **`03_VAULT/evidence/`** — `phantom_v2_test.png` (481 KB) and audit evidence are deliberate, auditable records.
- **`03_VAULT/LLM-Apps-Ref/`** — vendored reference material (ponyo.png, audio samples, vendored lockfiles); part of the assimilation library.
- **`docs/architecture/`, `docs/threat-models/`, `packages/contracts/`, `harness/`** — the canonical/spec surface; never purge.
- **`PROVENANCE_LEDGER.md` root copy** — the canonical ledger (after consolidation).
- **`cartridges/`, `Knights/`, `squires/`, `control_plane/`** — active code; enhancement only, no purging.

---

## 6. Recommended action plan (by value ÷ risk)

| # | Action | Est. reclaim | Risk |
|---|---|---|---|
| 1 | Consolidate PROVENANCE_LEDGER.md → 1 canonical file; update hook | ~2.4 MB | Low (regenerable; verify hook target first) |
| 2 | `git rm` `tests/tmp_*/` + gitignore `tests/tmp_*/` | ~1.0 MB | Low (regenerated by tests) |
| 3 | Remove committed DBs (`dump.rdb`, sqlite, ledger.db) + gitignore | ~0.4 MB | Low (verify no runtime needs tracked path) |
| 4 | Optimize knight PNGs | ~1.2 MB | Low (visual check after) |
| 5 | Move root zips/patches → `releases/` | 241 KB | Low |
| 6 | Move/cull root scratch .py/.html → `tests/` or `02_FORGE` | ~0.5 MB | Medium (verify each script is dead vs. live) |
| 7 | Resolve `01_KERNEL/uv.lock` vs root `uv.lock` | ~0.5 MB | Medium (needs an ADR) |
| 8 | Split `runtime_state/` evidence vs telemetry | — | Medium (policy change, not just cleanup) |
| 9 | `.gitignore` hygiene: `_tmp/`, `*.err`/`*.out`, `flash_context.toon`, `watchtower.exe`, `NAVIGATOR_INDEX_*.json` | ongoing | Low |

---

## 7. Hygiene rules to adopt

```gitignore
# (additions — draft)
tests/tmp_*/
_tmp/
dump.rdb
*.sqlite
*.sqlite3
*.db
*.exe
list_recheck.*
sarda_triage.*
03_VAULT/runtime_state/telemetry/
01_KERNEL/memory/tissue/*.toon
NAVIGATOR_INDEX_*.json
```

- **Ledger rule:** one canonical `PROVENANCE_LEDGER.md`; the writing hook targets only it.
- **Binary rule:** no `.exe`, `.db`, `.sqlite`, `.rdb`, `.bin` in tracking — build or generate on demand.
- **Root-surface rule:** root holds only the constitution (`AGENTS.md`, `CHANGELOG.md`, canonical ledger), entrypoints, and lockfiles; everything else lives in a layer.

---

*Generated 2026-08-15 from the git index of `C:\Users\vizio\CAMELOT_OS` (HEAD `3d7bef66`, 4,586 files, 45.2 MB). Recommendations only — execution awaits operator confirmation per repo HITL gates.*
