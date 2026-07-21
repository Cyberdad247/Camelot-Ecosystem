---
id: notebooklm-mcp-bridge-v1
status: ACTIVE
owner: VaShawn O. Head (cyberdad247)
schema: camelot.notebooklm-mcp/v1
date: 2026-07-14
follows_from: CAMELOT_OS/docs/architecture/NOTES_MNEMOSYNE_WIRING.md §7-RESOLVED + TITAN_TIER_EXECUTION_PROMPT_2026-07-14.md Phase 4
supersedes: null
---

# 🪢 NotebookLM MCP Bridge — File-System Pivot

> Operator clarification, 2026-07-14, prior to PR #4 landing:
>
> *"connecting the NotebookLM MCP directly into the file system"*
> → destination = LOCAL FILE SYSTEM (NOT the Bifrost Bridge).

This document is the operator-facing companion to PR #4
(`bin/notebooklm_mcp_server.py`). It covers the file-system destination,
Playwright fragility caveats, and the manual export alternative when the
scraper breaks.

## 1. Why this exists

Google has not published a public NotebookLM API or official MCP server.
The only viable integration path for an autonomous agent is browser-driven
scraping via Playwright, with the scraped corpus written to a cache
directory the agent can later ingest. The scraping itself is fragile;
this document captures the failure modes and the manual fallback.

## 2. Destination layout

```
03_VAULT/runtime_state/notebooklm_cache/
├── <slugified-url1>.md         # e.g. notebooklm-google-com-test-page.md
├── <slugified-url2>.md
└── ...
```

Each `.md` file is the raw HTML→Markdown roundtrip of one NotebookLM
notebook (Playwright scrape → `html2text`). Slugification rule:
lowercase alphanumeric + hyphens, repeated hyphens collapsed, leading
and trailing dashes stripped. Empty slugs fall back to `untitled.md`.

TTL: `NOTEBOOK_CACHE_TTL` env var (default 30 days). Expired entries are
evicted on every `list_local_notebooks()` call.

## 3. MCP transport

`stdio` (local process) — NOT Bifrost-bridged. The MCP server runs
inside the Bifrost Sandbox context if invoked by a knight, but its
stdio stream is purely local; there is no HMAC envelope because stdio
never crosses a wire boundary.

The Bifrost HMAC envelope is still canonical for the Appwrite egress
path (PR #3 `bifrost_appwrite_dispatch.py`); do NOT add HMAC
signature verification to the NotebookLM MCP tools.

## 4. Tools exposed

| Tool | Tier | Behavior |
|---|---|---|
| `export_notebook(url: str) -> str` | **PROMPT** | Playwright scrape → Markdown roundtrip → write to cache. Auto-confirm after 60s. |
| `delete_local_notebook(slug: str) -> bool` | **HUMAN_GATE** | `Path.unlink()` on the cache file. Requires explicit operator ack via `soul_oversight.pre_execute`. |
| `list_local_notebooks() -> list[str]` | **AUTO** | TTL-evict, then glob cache/*.md. Idempotent. |

HITL decision surface: the running CLI prompts the operator; the
`CAMELOT_DASHBOARD_OPERATOR_TOKEN` env var does NOT apply here (stays
Appwrite-HUMAN_GATE-bound).

## 5. Playwright fragility

This is the [KNOWN-BAD] axis. Google NotebookLM is a Web app, not an
API. DOM selectors drift between deploys. Failure modes:

- **Selector drift** — NotebookLM renames `div.notebook-source-list` to
  `div[data-test="source-list"]` mid-cycle. The Playwright selectors
  in `_scrape_notebook_html()` need to be updated.
- **Login state lost** — the operator session cookie expires between
  Playwright runs; the MCP server hits the login wall and returns
  the stub HTML.
- **JS-only render** — NotebookLM's notebook content is rendered
  client-side after a network call; `wait_until="networkidle"`
  catches most cases but not all.

When Playwright fails, the stub fallback (`<!-- notebooklm-mcp stub
for {url} -->`) appears in the cache `.md` file. Operators MUST
verify each export and re-run if a stub appears.

## 6. Manual export alternative

When Playwright fails repeatedly, the operator can manually export via:

1. Open `https://notebooklm.google.com/` in Chrome.
2. Select the notebook → ⋯ menu → **Export**.
3. Save the resulting `.md` to
   `03_VAULT/runtime_state/notebooklm_cache/<manual-slug>.md`.
4. Verify the file appears via `list_local_notebooks()` (AUTO tier).

This is the canonical "offline" path when the scraper is broken;
the operator workflow is documented in §5 of
`NOTES_MNEMOSYNE_WIRING.md`.

## 7. soul_oversight Iron Gate v2 entries (this PR adds)

```python
# control_plane/soul_oversight.pre_execute() lookup table extension:
"notebooklm.export":            "PROMPT",     # 60s auto-confirm
"notebooklm.delete_local":      "HUMAN_GATE", # destructive
"notebooklm.list":              "AUTO",       # idempotent
```

These three entries are added to the pre_execute triage.hitl_tier
lookup as part of PR #4. They are observable in
`03_VAULT/runtime_state/soul_oversight_lookup.jsonl`.

## 8. Reversibility

- **Rollback**: `git revert SHA` reverts this PR.
- **Cache wipe**: `rm -rf 03_VAULT/runtime_state/notebooklm_cache`.
- **TTL knob**: `NOTEBOOK_CACHE_TTL=N bash bin/notebooklm_mcp_server.py`
  changes the eviction horizon for the running session.

## 9. References

- TITAN_TIER_EXECUTION_PROMPT_2026-07-14.md Phase 4 — IDE-agent execution spec
- NOTES_MNEMOSYNE_WIRING.md §7.3 — Heimdall responsibility split
- control_plane/notebooklm_graphify_bridge.py — sibling local-graph pipeline
- control_plane/soul_oversight.py — pre_execute Iron Gate v2 lookup
- bin/notebooklm_mcp_server.py — the implementation itself
