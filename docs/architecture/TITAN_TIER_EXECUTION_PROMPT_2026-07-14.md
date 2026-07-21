---
id: titan-camelot-mnemosyne-filemcp-v1
status: ACTIVE
owner: VaShawn O. Head (cyberdad247)
schema: camelot.titan-execution-prompt/v1
date: 2026-07-14
target_ide:
  - cursor
  - cline
  - roo_code
target_ide_format: yaml-list
assumed_state: PR #1 infra landed (compose + env + bootstrap + pyproject.toml:46 pin)
pivot: NotebookLM MCP destination = LOCAL FILE SYSTEM (NOT Bifrost bridge)
follows_from: CAMELOT_OS/docs/architecture/NOTES_MNEMOSYNE_WIRING.md §7-RESOLVED
supersedes: null
operator_clarification_log:
  - "2026-07-14 turn-2: NotebookLM MCP destination = Bifrost Bridge"
  - "2026-07-14 turn-6: destination upgraded to LOCAL FILE SYSTEM (PIVOT)"
  - "2026-07-14 turn-7: scope = 'Code + tests + docs' (most-aggressive rollout)"
---

# 🪢 TITAN-TIER KINETIC EXECUTION PROMPT — v1
## Mnemosyne Wiring: Appwrite (self-host) + Bifrost (zero-trust) + NotebookLM MCP → FILE SYSTEM

# ── 0. IDENTITY ─────────────────────────────────────────────────────────────────────────────
ID:            titan-camelot-mnemosyne-filemcp-v1
DATE:          2026-07-14
OWNER:         VaShawn O. Head (cyberdad247)
ASSUMED STATE: PR #1 infra ✅ LANDED (compose + env + bootstrap + pyproject.toml:46 pin) per
               CAMELOT_OS/docs/architecture/NOTES_MNEMOSYNE_WIRING.md §1–§7 RESOLVED
PIVOT (NEW):   NotebookLM MCP destination = LOCAL FILE SYSTEM (03_VAULT/runtime_state/notebooklm_cache/)
               NOT the Bifrost bridge — per operator re-statement 2026-07-14.
TARGET IDE:    Cursor / Cline / Roo Code — paste as system prompt OR as the first user message.
HALT SIGNAL:   any explicit "[HUMAN_GATE]" inline marker OR operator `::stop` keyword.

# ── 1. READ FIRST — BOUNDARY FILES (do NOT modify) ──────────────────────────────────────────
Before writing anything, the IDE-agent must first read the SYSTEM-tier prompt:
  • CAMELOT_OS/docs/architecture/SYSTEM_PROMPT_v2_2026-07-14.md
    (the persistent framing; §0-§7 invariants + Phase 1.7-1.10 server-spin-up
    command templates are owned by SYSTEM, NOT by this USER-tier prompt).

Then READ (READ-ONLY in Phase 1):
  • CAMELOT_OS/docs/architecture/NOTES_MNEMOSYNE_WIRING.md        (the durable blueprint)
  • CAMELOT_OS/control_plane/bifrost_gateway.py                   (HMAC envelope at line 62)
  • CAMELOT_OS/control_plane/bifrost_sandbox_adapter.py           (signed-RPC ingress)
  • CAMELOT_OS/control_plane/heimdall_bifrost_governance.py        (nano-knight scope at line 51)
  • CAMELOT_OS/control_plane/heimdall_knight.py                    (mesh LLM agent — DO NOT extend)
  • CAMELOT_OS/control_plane/soul_oversight.py                     (pre_execute Iron Gate v2 at lines 177–209)
  • CAMELOT_OS/control_plane/mnemosyne_chimera.py                  (Lady Mnemosyne orchestrator)
  • CAMELOT_OS/control_plane/notebooklm_graphify_bridge.py        (existing NB→graph pipeline)
  • CAMELOT_OS/01_KERNEL/titan/memory/appwrite_sync.py             (existing Appwrite sync bridge)
  • CAMELOT_OS/03_VAULT/                                           (local file-system lake)

# ── 2. STATE IN (PR #1 GREEN) ──────────────────────────────────────────────────────────────
  • docker-compose.appwrite.yml              (5 services: appwrite/mariadb/redis/minio/traefik)
  • .env.appwrite.example                    (templated secrets; 6 placeholder groups)
  • bin/appwrite_bootstrap.sh                (idempotent first-boot)
  • docs/architecture/Appwrite_SelfHost_2026-07-14.md
  • pyproject.toml:46                        → "appwrite>=2.0.0,<3.0.0"
  • §7 RESOLVED:
      Q1 = loose SemVer (already correct on line 46, no edit)
      Q2 = same-host compose (already shipped)
      Q3 = carve INTO heimdall_bifrost_governance.py via new nano-knight

# ── 3. PHASE 1 — §8 LIVE VERIFICATION (AUTO HITL) ──────────────────────────────────────────
3.1  Run `bin/appwrite_bootstrap.sh` (must complete idempotent restart)
3.2  `docker compose -f CAMELOT_OS/docker-compose.appwrite.yml ps`  → expect 5 HEALTHY
3.3  `curl -fsS https://appwrite.local/v1/health`                   → 200 within 120s
3.4  Confirm 4 named volumes persist across restart:
        - camelot_appwrite_mariadb_data
        - camelot_appwrite_redis_data
        - camelot_appwrite_minio_data
        - camelot_appwrite_traefik_acme
3.5  Issue APPWRITE_API_KEY via `bin/appwrite_bootstrap.sh --issue-key` → write `.env.appwrite` (chmod 600)
3.6  HITL: [HUMAN_GATE] operator must type `::continue-phase-2` before Phase 2 runs.

# ── 4. PHASE 2 — PR #2 (typed appwrite_client.py wrapper) ──────────────────────────────────
SCOPE:        MEDIUM risk · AUTO HITL tier · ~280 LoC
NEW FILES:
  • CAMELOT_OS/control_plane/appwrite_client.py
      - class AppwriteClient (wraps appwrite.Services.Databases)
      - retry semantics via tenacity (already in pyproject deps list)
      - Z3-gate hand-off via soul_oversight.pre_execute callback
      - Authorization header injected from APPWRITE_API_KEY env var
      - env-toggle via APPWRITE_ENDPOINT_PUBLIC
  • CAMELOT_OS/tests/control_plane/test_appwrite_client.py
      - golden-path: connect → list-databases → return list
      - retry-semantics: simulate 5xx → expect tenacity retry
      - masked-auth: redact Authorization header from log output
CONSTRAINTS:
  • Use pyproject.toml:46 pin VERBATIM. Do NOT bump pin.
  • ZERO-TOUCH on heimdall_bifrost_governance.py this phase (Phase 3 carve-into).
  • Type-hint everything; ruff --select F401,E402 must return zero on the new file.
  • At most ONE __init__ side-effect import; everything else explicit.
GATE:
  • pytest tests/control_plane/test_appwrite_client.py  → 100% pass
  • soul_oversight --test                              → ALL PASS
  • ruff check --statistics control_plane/appwrite_client.py → 0 errors

# ── 5. PHASE 3 — PR #3 (Bifrost→Appwrite envelope glue + 6th nano-knight) ───────────────────
SCOPE:        HIGH risk · HUMAN_GATE tier · ~220 LoC (Python) + ~10 LoC (nano-knight tuple edit)
NEW FILES:
  • CAMELOT_OS/control_plane/bifrost_appwrite_dispatch.py
      - dispatch_to_appwrite(intent: str, payload: dict, signature: str) -> dict
      - Calls hmac.compare_digest against bifrost_gateway HWEBHOOK_SECRET
      - Forwards to AppwriteClient (Phase 2 module) with retry
  • CAMELOT_OS/tests/control_plane/test_bifrost_appwrite_dispatch.py
      - HMAC parity test (Python sign vs TS gateway verify; same SHA-256 hex)
      - signed-RPC smoke test (mock AppwriteClient)
MODIFIED FILES:
  • CAMELOT_OS/control_plane/bifrost_sandbox_adapter.py
      - Register new dispatch_to_appwrite entry in ToolRegistry (1 line)
  • CAMELOT_OS/control_plane/heimdall_bifrost_governance.py
      - Append 6th nano-knight to HEIMDALL_NANO_KNIGHTS tuple:
        {
          "id":          "heimdall.appwrite_egress",
          "callsign":    "Appwrite Egress",
          "channel":     "bifrost.policy.appwrite",
          "mission":     "Gate Bifrost→Appwrite egress against zero-trust policy; rotate APPWRITE_API_KEY per `appwrite_bootstrap.sh --rotate`.",
          "tier":        "S2"
        }
      - Confirm self-test bumped threshold: `>= 6` (was `>= 5`)
GATE:
  • HMAC parity test PASS
  • Signed-RPC smoke test PASS
  • python HMAC output equals TS gateway output for the same input/random
  • [HUMAN_GATE] per dispatch — operator acks via CAMELOT_DASHBOARD_OPERATOR_TOKEN

# ── 6. PHASE 4 — PR #4 PIVOTED (NotebookLM MCP → FILE SYSTEM) ──────────────────────────────
NEW CLARIFICATION (operator 2026-07-14, 5th-occurrence re-statement):
  • NotebookLM MCP destination = LOCAL FILE SYSTEM, NOT Bifrost bridge.
  • Specifically: output is written to 03_VAULT/runtime_state/notebooklm_cache/<slug>.md
  • MCP transport: stdio (local process), not Bifrost-HMAC-bridged.
SCOPE:        HIGH risk · PROMPT HITL tier · ~240 LoC
NEW FILES:
  • CAMELOT_OS/bin/notebooklm_mcp_server.py
      - FastMCP("notebooklm-camelot-bridge")
      - Tools:
          export_notebook(url: str) -> str             # Playwright scrape + cache write
          delete_local_notebook(slug: str) -> bool     # rm 03_VAULT/runtime_state/notebooklm_cache/<slug>.md
          list_local_notebooks() -> list[str]          # glob 03_VAULT/runtime_state/notebooklm_cache/*.md
      - Transport: stdio (local)
      - Cache TTL: 30 days; configurable via NOTEBOOK_CACHE_TTL env var
  • CAMELOT_OS/tests/control_plane/test_notebooklm_mcp.py
      - Mock Playwright fixture (no real Google login)
      - Golden-path: golden_notebook.html ⇄ golden_notebook.md roundtrip
      - TTL eviction: 31-day-old fixture auto-purges
  • CAMELOT_OS/docs/architecture/NotebookLM_MCP_Bridge_2026-07-14.md
      - Operator-facing caveat: Playwright DOM-selector drift WILL happen.
      - Manual export alternative documented.
CONSTRAINTS:
  • Use playwright>=1.40.0 (already in pyproject deps).
  • MCP transport: stdio OR SSE-local; NOT Bifrost.
  • Output dir: 03_VAULT/runtime_state/notebooklm_cache/ — gitignored as ephemeral.
  • soul_oversight pre_execute lookup now includes:
        notebooklm.export            → PROMPT
        notebooklm.delete_local      → HUMAN_GATE
        notebooklm.list              → AUTO
GATE:
  • pytest tests/control_plane/test_notebooklm_mcp.py → 100% pass
  • ruff check --select F401,E402 → 0 errors
  • Manual Playwright smoke: scrape one public notebook URL, validate .md written under cache/

# ── 7. PHASE 5 — COMMIT SEQUENCE ─────────────────────────────────────────────────────────────
7.1  Each phase commits independently (Conventional Commit prefixes).
7.2  Verify all ruff + pytest gates pass before each commit.
7.3  Update CAMELOT_OS/docs/architecture/NOTES_MNEMOSYNE_WIRING.md §8 with phase-completion timestamps:
        §8-A: PR #1 ✅ verified-live
        §8-B: PR #2 ✅ merged  2026-07-XX
        §8-C: PR #3 ✅ merged  2026-07-XX
        §8-D: PR #4 ✅ merged  2026-07-XX
7.4  Final basher: ruff --statistics CAMELOT_OS/control_plane/ → expect ≥15-23 post-PR residue (E702 / E701 / E741 / E402 / F841 are Tier-N+2+ scope; F401 reduced for newly-created files only; the residual set is the legacy TIER-2 footprint documented in CAMELOT_OS/control_plane/SELF_IMPROVEMENT_TIER2_2026-07-14.md).

# ── 8. STOP CONDITIONS ───────────────────────────────────────────────────────────────────────
- Appwrite SDK release-breaks the 2.x line mid-run                → STOP and surface to operator
- pyproject.toml:46 pin drifts away from `>=2.0.0,<3.0.0`         → STOP and surface
- §7 resolutions are violated                                     → STOP and re-resolve per §7
- NotebookLM Playwright DOM-selector drift breaks e2e export    → STOP and surface (manual export fallback per docs)
- soul_oversight pre_execute queue grows > 20 without drain      → STOP and reduce parallel pressure
- Bifrost HMAC parity test fails (Python ≠ TS gateway)           → STOP — DO NOT BYPASS

# ── 9. EXPECTED END STATE ───────────────────────────────────────────────────────────────────
Files created:  4 (appwrite_client.py + test, notebooklm_mcp_server.py + test)
Files modified: 2 (bifrost_sandbox_adapter.py + heimdall_bifrost_governance.py)
Docs added:     1 (NotebookLM_MCP_Bridge_2026-07-14.md)
Blueprint upd:  1 (NOTES_MNEMOSYNE_WIRING.md §8 timestamps)
pyproject:      UNCHANGED (pin stays `>=2.0.0,<3.0.0` per §7.1)
Bifrost:        HMAC envelope canonical (one new ToolRegistry entry)
Heimdall:       +1 nano-knight (6 total: heimdall.appwrite_egress)
Soul_oversight: +3 gate_policy entries (notebooklm.export, delete, list)
Total LoC:      ~720 Python + ~30 YAML + ~140 docs

# ── 10. HITL GATE SCHEDULE ──────────────────────────────────────────────────────────────────
- Phase 1 §8 LIVE VERIFY               → operator `::continue-phase-2`
- Phase 3 PR #3 each dispatch          → operator ack (CAMELOT_DASHBOARD_OPERATOR_TOKEN)
- Phase 4 PR #4 each notebook export   → PROMPT surfaced via running-CLI prompt (auto-confirm after 60s OR operator `::abort-cache-write` keyword); NOT via CAMELOT_DASHBOARD_OPERATOR_TOKEN (which is reserved for the Appwrite-targeted HUMAN_GATE in Phase 3 — stdio MCP transport can't reach the dashboard anyway).
- Phase 5 final commit                 → operator review before push

END OF PROMPT.
