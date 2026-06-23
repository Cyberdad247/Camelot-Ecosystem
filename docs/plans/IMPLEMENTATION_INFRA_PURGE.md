# IMPLEMENTATION: Infrastructure Purge (Redis & Qdrant Decommissioning)
**Status:** DRAFT  
**Objective:** Decouple Camelot-OS Kernel from external infrastructure services to achieve absolute sovereignty and "Dark Mode" stability.

## 1. Architectural Changes
- **Memory Layer:** Replace `redis_store.py` and `qdrant_store.py` with a unified `local_sovereign_store.py` (SQLite-backed).
- **Context Hydration:** Migrate `HydrationManager` from Redis hashes to local file-based `tissue/` caching.
- **Boot Sequence:** Remove the `boot_hermes_omniroute_orchestrator` phase from the `awaken` lifecycle.

## 2. Phase 1: Qdrant Removal
- [ ] Delete `01_KERNEL/memory/qdrant_store.py`.
- [ ] Remove `qdrant_client` from `requirements.txt` and `pyproject.toml`.
- [ ] Clean up imports in:
    - `01_KERNEL/memory/agent_memory.py`
    - `01_KERNEL/merlin/merlin_omega.py`
    - `01_KERNEL/merlin/rag/chronos_haystack.py`

## 3. Phase 2: Redis Migration
- [ ] Refactor `01_KERNEL/memory/redis_store.py` -> `01_KERNEL/memory/local_store.py`.
- [ ] Implement SQLite backend for session memory and vector metadata.
- [ ] Update `HydrationManager` in `hydration_manager.py` to use `local_store.py`.
- [ ] Update `Memory_Squire` (FastAPI) to point at local SQLite instead of Redis.

## 4. Phase 3: Boot Streamlining
- [ ] Modify `control_plane/boot_sequence.py`:
    - Disable `boot_hermes_omniroute_orchestrator`.
    - Remove Redis health probes (`:6379`).
- [ ] Update `01_KERNEL/config/registry/chimera_unified_kernel.json` to remove Redis/Qdrant endpoints.
- [ ] Update `bin/awaken.py` to reflect simplified dependency tree.

## 5. Verification & Testing
- [ ] `pytest tests/test_hydration.py` (Must pass without Redis).
- [ ] `pytest tests/test_boot_omniroute.py` (Verify warning-free boot).
- [ ] Manual `//BOOT` check to confirm UI/HUD stability.

## 6. Rollback Strategy
- Keep backups of `redis_store.py` and `qdrant_store.py` in `99_ARCHIVE/infra_purge_backup/`.
- Maintain git checkpoints before each phase.

### 6.1 Verification (mandatory; non-negotiable)

A rollback that only lives on one developer's disk is not a rollback — it is a TODO. Every Phase 1/2/3 commit MUST satisfy the five checks below; the CI guard will block any commit that does not.

- [ ] **Local backup exists on disk** — read-only smoke test before each Phase commit:
  ```bash
  test -f 99_ARCHIVE/infra_purge_backup/redis_store.py && \
  test -f 99_ARCHIVE/infra_purge_backup/qdrant_store.py || \
  { echo "infra_purge_backup missing rollback files"; exit 1; }
  ```
- [ ] **Rollback contract is git-tracked** — the backups must be in `git ls-files`, not just the working tree. Self-enforcing; does not require caller to enable strict shell mode:
  ```bash
  git ls-files 99_ARCHIVE/infra_purge_backup/ \
    | grep -qE 'redis_store|qdrant_store' \
    || { echo "rollback not git-tracked"; exit 1; }
  ```
- [ ] **Rollback survives `git gc`** — unreachable blobs (from the deletion commit) must still resolve to the rollback files; recheck after every gc window. _Requires git ≥ 2.32 (Dec 2020) for `--no-reflogs`; older git fails this check unrelated to purge state._
  ```bash
  git fsck --unreachable --no-reflogs 2>&1 | grep -E '^unreachable blob' | head
  ```
- [ ] **Blob provenance — staged blob SHA-1 at this path matches the historical blob-id record (catches stub-replacement attacks)** — defends against a malicious PR replacing the rollback with a stub such as `print('ok')`. For each tracked rollback file, the staged (index) blob's **SHA-1** (from `git ls-files --stage`) must appear in the historical blob-id record for that exact file path. Git's content-addressed store guarantees identical content yields identical SHA-1, so a legitimate restore stages a blob whose SHA-1 already exists somewhere in the file's commit history. A stub replacement writes different bytes, producing a new SHA-1 that has never appeared at this path — caught by the hard-FAIL.

  **Primary check (hard-FAIL on stub):** for each tracked rollback file, walk every commit reachable from any ref that ever touched this path, collect the blob SHA-1 from each commit's tree, and require the staged SHA-1 to be in the deduplicated set. Costs O(commits) subprocess forks, capped at `MAX_HISTORICAL_COMMITS=1000` per file (rollback files in this repo have <100 historical commits in practice).
  **Advisory check (informational):** the staged SHA-1 also appears in `git fsck --unreachable --no-reflogs`. Once the safety-net window (~30 days) elapses and `git gc` prunes the unreachable set, this degrades to INFO without affecting the exit code. The PRIMARY check is durable and does not depend on the unreachable-bucket lifetime.
  ```bash
  # Get staged blob SHA-1 from the index (NOT the working tree).
  STAGED_SHA="$(git ls-files --stage \
      "99_ARCHIVE/infra_purge_backup/redis_store.py" | awk '{print $2}')"
  # Walk every commit reachable from any ref that ever touched this path.
  HISTORICAL_SHAS=()
  while read -r commit_sha; do
    [[ "${commit_sha}" =~ ^[0-9a-f]{40}$ ]] || continue
    blob_sha="$(git ls-tree "${commit_sha}" -- \
        "99_ARCHIVE/infra_purge_backup/redis_store.py" \
        | awk '$2=="blob" {print $3}')"
    [[ -n "${blob_sha}" && "${blob_sha}" =~ ^[0-9a-f]{40}$ ]] \
      && HISTORICAL_SHAS+=("${blob_sha}")
  done < <(git log --all --pretty=format:'%H' \
            -- "99_ARCHIVE/infra_purge_backup/redis_store.py")
  # PASS if ${STAGED_SHA} is in HISTORICAL_SHAS (deduplicated).
  ```

  **Why this survives git's SHA-1 deduplication invariant:** under the prior SHA-256 content-hash design, a legitimate restore stages a blob whose bytes match an unreachable blob's content; git deduplicates the staged blob to share the existing object, making it reachable-via-index. `git fsck --unreachable --no-reflogs` then returns empty, and the OLD Check 4 degraded to INFO mode. The new SHA-1 design preserves the same SECURITY GUARANTEE because blob SHA-1s are content-addressed and stable across both staged blobs and historical blobs — but it also stays durable as the unreachable-bucket ages out (~30 days).
- [ ] **CI guard** — add `scripts/check_infra_purge_rollback.sh` to the pre-commit chain and to CI; the build fails if any of the gating checks (1, 2, 4) above fails:
  ```bash
  #!/usr/bin/env bash
  set -euo pipefail
  test -f 99_ARCHIVE/infra_purge_backup/redis_store.py
  test -f 99_ARCHIVE/infra_purge_backup/qdrant_store.py
  git ls-files 99_ARCHIVE/infra_purge_backup/ | grep -qE 'redis_store|qdrant_store'
  git fsck --unreachable --no-reflogs 2>/dev/null | grep -qE '^unreachable blob' || true  # advisory
  echo "infra_purge rollback verification: PASS"
  ```

### 6.2 PR template requirement

**Precondition:** Section 6.2 is enforceable only if `.github/PULL_REQUEST_TEMPLATE.md` exists in the repo. Verify with `test -f .github/PULL_REQUEST_TEMPLATE.md`; if absent, Section 6.2 is non-binding until the template is added.

Any PR implementing Phase 1, 2, or 3 of this plan MUST list the five Section 6.1 verification results verbatim in its description. PRs missing this output are blocked at code review.

### 6.3 Verification log (2026-06-22, local Windows sim)

A local verification run was captured at [`verification/infra_purge_check_4_posix_sim.md`](../../verification/infra_purge_check_4_posix_sim.md). The run documented two non-trivial findings against the SHA-256 content-hash design that motivated the check rewrite:

> **Working-tree ledger note:** the original audit-trail entry for this verification (slug `infra_purge_check_4_posix_sim_20260622`) lived in the working tree, not in git HEAD. A subsequent ledger-recovery event (atomic-append bug, see rewrite entry below) restored from HEAD only; the uncommitted `posix_sim` line and 12 other uncommitted audit lines between HEAD and the working tree at that time are no longer recoverable from `03_VAULT/Missions/verification_ledger.jsonl`. The markdown verification log above (`verification/infra_purge_check_4_posix_sim.md`) is preserved on disk and remains the authoritative source for finding 1 (Windows fixture limitation) and finding 2 (SHA-1 dedup invariant).

1. **Git Bash on Windows does not reliably leave unreachable blobs after `git rm + commit`** even with explicit `git config gc.auto=0`. Phase-2 `git fsck --unreachable --no-reflogs` returned 0 lines, identical to the empty baseline. This blocked Scenario A's `OK: matched` branch locally.

2. **The old `OK: matched` branch was generally unreachable under normal git semantics**, due to git's SHA-1 deduplication invariant: when staging identically-authored content, the staged blob merges with the existing unreachable blob (one object, one SHA-1), becoming reachable via the index and disappearing from `git fsck --unreachable` even on POSIX systems. The old design's enforcement strength lived in the **stub-replacement FAIL path (Scenario B)**, not the OK pass path.

**These findings drove the rewrite to staged-blob-SHA-1 vs historical-blob-id-record PRIMARY + unreachable-blob ADVISORY** (described above). The SHA-1 historical walk does NOT depend on the unreachable-bucket lifetime — it persists as long as the file has any historical commits. The advisory unreachable-bucket check retains ~30-day coverage that complements the durable historical check.

Production-verification of Scenarios A/B/C, ideally with a fully populated unreachable-bucket AND a populated historical blob-id record, requires the GitHub Actions job [`infra-purge-rollback`](../../.github/workflows/verify_os.yml) (`ubuntu-latest`, `fetch-depth: 0`, dorny paths-filter). When that job's first PR-run lands, its log should be added as a sibling to the local file at `verification/` and supersede this local Windows simulation as the production truth.

**Local Windows verification of the rewrite (2026-06-22, post-rewrite smoke run):** the rewrite was syntax-checked via `bash -n` and smoke-tested against this repo. The script now correctly emits `INFO: redis_store.py not staged in index; skipping provenance` and exits via the unchanged Check 2 FAIL (`rollback files are not tracked by git`), with `RESULT: FAIL (exit 1)`. No syntax/runtime errors were introduced. Targeted temp-repo Scenarios A/B/C on this Windows Git Bash host remain unsuitable for fixture reliability (per finding 1 above) and should be evaluated via the GitHub Actions job.

**Companion audit entry for the rewrite:** `03_VAULT/Missions/verification_ledger.jsonl` slug `infra_purge_check_4_rewrite_20260622` chains off the prior `posix_sim` entry. It captures the rewrite design (PRIMARY vs ADVISORY), the local smoke-run results, the deferral-to-CI rationale for Scenarios A/B/C, and the cross-references to the prior verification log + this plan-doc section.
