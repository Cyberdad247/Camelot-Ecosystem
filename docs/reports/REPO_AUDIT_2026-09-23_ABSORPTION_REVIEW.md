# Branch Consolidation — Absorption Review (2026-09-23)

Follow-up to `REPO_AUDIT_2026-09-22_PRUNE_REBASE_DRYRUN.md`. HITL decisions taken
2026-09-23: (D4) dirty main committed to main; (D2) per-branch PR strategy —
security fixes first, then perf, then feat bundles, dependabot batch last;
(D1) PR-or-archive-report per old branch; (D3) full parity gates before any merge.

Method: for each branch, `git diff origin/main...<branch>` patch inspected, then
the target file on current main checked for absorption (same fix present at or
near the patched lines). Lockfile-only churn (`uv.lock`, 1703 lines from a
diverged dependency base) excluded from stats; it must be re-resolved on a
modern base, never merged as-is.

## 1. Absorbed into main — nothing to PR (7 branches)

Patches predate main's current state; the equivalent hardening is verified
present. Safe to archive after this report.

| Branch (origin/) | Fix | Evidence on main |
|---|---|---|
| `fix/chaos-engineer-ssh-exec-cmd-injection-11318835194895624429` | SSH `create_subprocess_shell` → `exec` argv form | `chaos_engineer.py:355` already `create_subprocess_exec` |
| `fix/bifrost-secret-vulnerability-9692439515697370356` | Remove hardcoded `BIFROST_BRIDGE_SECRET` fallback | `main.py:430` env-only, `:433` test-secret gated on CI/non-interactive, `:436-437` hard-fail in production |
| `fix/bifrost-path-traversal-12920532030833178479` | Sanitize upload/download filenames | `bin/bifrost_port.py:82-83` `os.path.basename` on upload, `:95-96` "CRITICAL FIX" sanitization on download |
| `fix/secure-ast-eval-6446032791505160235` | Replace bare `eval()` in extraction strategy | `01_KERNEL/merlin/Engines/crawl4ai/extraction_strategy.py:1004` `_safe_eval` AST whitelist walker |
| `fix/chat-session-message-count-6746660588984624685` | Raw thread-id extraction in session lists | `01_KERNEL/agora/Squires/Memory_Squire/routers/source_chat.py:135` identical `raw_id = session_id.split(":")[-1]` |
| `fix/store-grounding-id-3477205575185918070` | Persist Grounding ID during DOM traversal | `03_VAULT/Nano-Knights/buildDomTree.js:1492-1495` groundingId emitted in output format |
| `fix/connect-actual-llm-critique-3040656013081213332` | Wire real LLM into ReflectionEngine critique | `01_KERNEL/merlin/rag/recursive_search.py:26` `self.evaluator = MerlinGenerator(mode="Reasoning")`, `:64-65` actual LLM call — exact same lines the branch adds |

## 2. Open PR candidates — real, unabsorbed work (3 PRs from 4 branches)

All patch `01_KERNEL/agora|titan` query paths against a 2026-07-24 base. Rebase
each onto current main, drop any `uv.lock` churn, then run D3 full parity gates
before opening the PR.

1. **`perf/embedding-n-plus-1-optimization-15445770156298811611`**
   Batches notes AND sources fetches in `01_KERNEL/agora/Squires/commands/embedding_commands.py`
   (chunked `id IN` queries, 500-chunk). Supersedes `fix/n-plus-1-notes-11567502951563396669`,
   which batches notes only in the same file — do NOT open a second PR for the fix branch.
2. **`perf/optimize-n-plus-1-queries-13777398068298918860`**
   `Memory_Squire/routers/sources.py` + `open_notebook/domain/base.py` (adds
   `Notebook.get_many`, missing-id reconciliation). Sequencing note: PR 3 also
   touches `domain/base.py` — land this one first, rebase the next on it.
3. **`perf/optimize-get-all-data-9582424866941690986`**
   `01_KERNEL/titan/Data_Pipeline/storage.py` — collapses per-table get-all
   loops into single `conn.execute` queries.

   (`fix/n-plus-1-transformations-4638488964349460669` also patches
   `domain/base.py` for transformations validation batching; fold into PR 2's
   rebase review rather than a separate PR.)

## 3. Flagged — needs provenance review before any PR (1 branch)

- **`fix/crawl4ai-dynamic-props-10308585361983874934`** — commits titled
  "Task complete (ignoring billing issues)" (×2), 101-line deletion +
  dynamic-props caching in `model_loader.py`/`async_configs.py`. Commit
  provenance is suspect; review authorship and intent before deciding PR vs
  archive. Not absorbed into main (no `_get_signature` in `model_loader.py`).

## 4. Dependabot (15 branches, 2026-09-20)

Unchanged from the 09-22 audit: keep grouped, merge via batch PR last, never
rebase individually. Requires the JS gate order (`lint -> typecheck -> test -> build`).

## 5. Next actions

1. Rebase + gate + open the 3 perf PRs (order: 2 → 3, with 1 independent).
2. Provenance review of the crawl4ai branch (SIR_SENTINEL / squire ghost scan).
3. Archive-report accepted → the 7 absorbed branches plus consumed
   `fix/n-plus-1-notes` become archival-review candidates on origin (no
   auto-delete; deletion remains a separate HITL action).
4. Then proceed to the remaining feat bundles and `chore/sync-local-main-130`
   PR per the audit's grouping.
