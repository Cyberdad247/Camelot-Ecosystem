# ADR-0002: Assimilate OpenCodex as Universal Provider Proxy

**Status:** proposed  
**Date:** 2026-08-21  
**Source:** [lidge-jun/opencodex](https://github.com/lidge-jun/opencodex) (MIT, 11.7k ★, v2.29.0)  
**Actor:** SIR_CODEX (Freebuff / Codex)

---

## Executive Summary

OpenCodex is a lightweight local proxy that translates OpenAI's Responses API
into any provider's wire format — streaming, tool calls, reasoning tokens,
images — in both directions.  It lets Codex CLI/App/SDK, Claude Code, Claude
Desktop, and Grok Build run against **any LLM** (40+ providers) through a
single `localhost:10100` endpoint.

**Verdict: ASSIMILATE** — vendor as a dependency, not fork.  OpenCodex solves
the exact problem CAMELOT-OS's `cliproxy` (CLIProxyAPI :8080) was built for,
but with 40x the provider coverage, production-grade memory ownership, and a
battle-tested account pool.

---

## 1. What OpenCodex Does

### Core Capability
Translates between OpenAI Responses API wire format and any LLM provider's
native API.  A single proxy handles:

| Input surface | Output providers |
|---|---|
| Codex CLI / App / SDK | Anthropic, Gemini, Grok, DeepSeek, Kimi, Ollama, ... |
| Claude Code / Desktop | OpenAI, Azure, Google, xAI, ... |
| Grok Build | Any OpenAI-compatible endpoint |

### Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│  Client (Codex / Claude Code / Grok Build)           │
│  sends OpenAI Responses API or Chat Completions       │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP (localhost:10100)
┌──────────────────▼──────────────────────────────────┐
│  Server Layer (src/server/)                          │
│  ├── responses.ts      — Responses API handler       │
│  ├── chat-completions.ts — Chat Completions handler   │
│  ├── claude-messages.ts — Claude Messages handler     │
│  ├── relay.ts          — Streaming relay              │
│  ├── management-api.ts — Config hot-reload API        │
│  └── readiness.ts      — Health / readiness probes    │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  Router (src/router.ts)                               │
│  ├── Policy-based candidate evaluation                │
│  ├── Combo failover / weighted round-robin            │
│  ├── Account pool selection (quota-aware)             │
│  ├── Slug codec (provider/model wire encoding)        │
│  └── Route decision tracing (RI-01)                   │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  Bridge (src/bridge.ts)                               │
│  ├── Protocol translation (Responses ↔ provider)      │
│  ├── Streaming SSE ↔ SSE relay                        │
│  ├── Tool call argument assembly                      │
│  ├── Reasoning token replay cache                     │
│  ├── Bounded memory ownership (TranslatorBudget)      │
│  └── Stall timeout detection                          │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  Adapters (src/adapters/)                             │
│  ├── anthropic.ts      — Claude wire format           │
│  ├── google.ts         — Gemini / Vertex              │
│  ├── openai-chat.ts    — Chat Completions fallback    │
│  ├── openai-responses.ts — Responses API passthrough  │
│  ├── kiro.ts           — Kimi / Kiro                  │
│  ├── azure.ts          — Azure OpenAI                 │
│  └── base.ts           — Shared adapter interface     │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  Providers (src/providers/)                           │
│  ├── registry.ts       — 40+ provider definitions     │
│  ├── quota.ts          — Account quota tracking       │
│  ├── key-failover.ts   — Multi-key rotation           │
│  ├── model-discovery.ts — Live /models endpoint       │
│  ├── slug-codec.ts     — provider/model ID encoding   │
│  └── openai-tiers.ts   — Codex account tier routing   │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  Combos (src/combos/)                                 │
│  ├── failover.ts       — Failover chains              │
│  ├── resolve.ts        — Combo resolution             │
│  └── types.ts          — Combo config schema          │
└─────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Bun runtime** — single binary, no Node.js dependency, bundled on npm
   install.  Memory-efficient GC for long-lived proxy processes.

2. **Bounded memory ownership** — 36 categories of process-retained state,
   each with a documented bound (default 256 MiB budget).  No unbounded
   `Map` or `Set` survives a config reload.  Eviction sweeps run every 60s.

3. **Policy-based routing** — profiles define candidate requirements,
   compatibility suites, cost caps, and optimization targets.  The evaluator
   scores candidates against live evidence.

4. **Account pool** — manages multiple ChatGPT/Codex accounts with thread
   affinity, quota-aware auto-switching, cooldown, and fail-closed auth.
   Under-quota routing picks the lowest-usage healthy account.

5. **Combo system** — one virtual model ID with failover or weighted
   round-robin across providers.  Cooldown-aware: failed targets get
   temporary exclusion.

6. **Slug codec** — encodes `provider/model` into a single wire ID that
   Codex/Claude Code can pass through unchanged, then decodes on the
   server side.

---

## 2. CAMELOT-OS Current State

### What We Have Today

| Component | Location | Purpose |
|---|---|---|
| **CLIProxyAPI** | `apps/bifrost/src/` | Local proxy on `:8080`, Chat Completions only |
| **SoulRouter** | `control_plane/core/soul_router.py` | Intent → knight routing (keyword + MFOE scoring) |
| **llm_router.py** | `03_VAULT/training/configs/llm_router.py` | Knight → provider/model mapping |
| **omniroute.json** | `03_VAULT/training/configs/config/omniroute.json` | Static provider/model/fallback config |
| **CLIProxy provider config** | `config.json` | Boolean API key presence flags only |

### Pain Points

1. **cliproxy is a thin Chat Completions shim** — no Responses API, no
   streaming protocol translation, no reasoning token handling.

2. **4 hardcoded routing paths** — `camelot_cli.py`, `knight_session.py`,
   `camelot_portable.py`, `main.py` each use different routing tables
   (partially unified behind SoulRouter, but provider resolution still
   diverges).

3. **No account pooling** — single API key per provider, no quota-aware
   rotation, no failover on 429.

4. **No combo/failover** — if Gemini is down, the knight falls back to
   a hardcoded chain with no cooldown or health tracking.

5. **No model discovery** — static model lists in omniroute.json go stale.

---

## 3. Assimilation Plan

### Phase 1: Vendor as Dependency (0.5 day)

```bash
# Install opencodex as a project dependency
npm install --save @bitkyc08/opencodex
# OR: vendor the source into 02_FORGE/packages/opencodex/
```

Configure it to listen on `localhost:10100` alongside the existing cliproxy
on `:8080`.  Both can coexist — cliproxy handles existing knight-session
traffic, opencodex handles new integrations.

### Phase 2: Bridge SoulRouter → OpenCodex (1 day)

Replace the per-knight `model, base_url, api_key = _resolve(knight_id)`
pattern with an opencodex-backed resolver:

```python
# New: control_plane/core/ocx_bridge.py
import httpx

OCX_URL = "http://127.0.0.1:10100"

def resolve_knight_model(knight_id: str) -> dict:
    """Ask opencodex for the best model for a knight's tier."""
    resp = httpx.get(f"{OCX_URL}/api/providers")
    providers = resp.json()
    # Map knight tier → provider/model via policy profile
    ...
```

### Phase 3: Combo Failover for Knights (1 day)

Define combos for each knight tier:

| Knight tier | Combo definition |
|---|---|
| G3 (apex) | `google/gemini-3.1-pro` → `anthropic/claude-opus-5` → `openai/gpt-5.5` |
| G2 (pro) | `google/gemini-3-pro` → `openai/gpt-5.4` |
| G1 (flash) | `google/gemini-3-flash` → `openai/gpt-4.1-mini` |
| L0 (local) | `ollama/qwen3:8b` (harness-locked, no failover) |
| X1 (codex) | `openai/gpt-5.5-codex` (pinned) |

### Phase 4: Account Pool for Production (1 day)

For production deployments, configure opencodex's account pool with:

- Multiple ChatGPT accounts for quota rotation
- Thread affinity (existing sessions stay pinned)
- Under-quota routing (new sessions use lowest-usage account)
- Cooldown on 429 / quota exhaustion

### Phase 5: CLI Integration (0.5 day)

Update `knight_session.py` and `camelot_portable.py` to use opencodex:

```python
# Before
model, base_url, api_key = _resolve(knight_id)

# After
# opencodex handles provider resolution, auth, and failover
base_url = "http://127.0.0.1:10100"
api_key = "proxy-admin-key"  # local, no real key needed
model = f"{provider}/{model_id}"  # opencodex slug codec
```

---

## 4. What We Gain

| Capability | Before | After |
|---|---|---|
| Provider count | 3 (Gemini, OpenAI, Ollama) | 40+ |
| Protocol support | Chat Completions only | Responses API + Chat + Claude Messages |
| Streaming | Basic SSE | Full SSE with reasoning token relay |
| Failover | Hardcoded chain | Combo system with cooldown + health |
| Account pooling | None | Quota-aware rotation with thread affinity |
| Model discovery | Static (omniroute.json) | Live `/models` endpoint |
| Memory safety | Unbounded caches | Bounded 256 MiB budget with eviction |
| Health monitoring | None | `/healthz` + `/readyz` + readiness probes |

---

## 5. What We Don't Gain (and Don't Need)

| OpenCodex feature | CAMELOT-OS relevance | Verdict |
|---|---|---|
| Web dashboard (:10100 GUI) | Nice for debugging, not essential | Optional |
| Codex shim install | We don't use Codex CLI directly | Skip |
| ChatGPT account pool | Useful for production, not for dev | Phase 4 |
| OAuth for xAI/Anthropic | We use API keys via CLIProxy | Skip |
| Vision/web-search sidecars | Our sidecar is Bifrost WebRTC | Skip |

---

## 6. Security Considerations

- **Local-only binding** — opencodex binds to `127.0.0.1` by default, same
  as cliproxy.  No auth token needed for localhost.
- **No secrets in config** — API keys are resolved from environment variables
  via `${ENV_VAR}` references, matching CAMELOT-OS's boolean-only config.json
  convention.
- **Iron Gate compatible** — opencodex runs as a sidecar, not inline with
  the iron gate.  HITL prompts remain under Camelot control.
- **MIT license** — compatible with CAMELOT-OS's MIT license.

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Bun runtime not available on Windows | Low (bundled in npm) | Medium | Test on Cybertronia; fallback to Node.js adapter |
| Provider API changes break adapters | Medium | Low | opencodex community maintains adapters |
| Memory budget too tight for Camelot workloads | Low | Low | Configurable via `memoryBudgetMb` setting |
| Account pool adds operational complexity | Medium | Medium | Phase 4 only; dev uses single keys |

---

## 8. Decision

**ASSIMILATE** — vendor `@bitkyc08/opencodex` as a dependency.

### Immediate Actions

1. `npm install --save @bitkyc08/opencodex` in the monorepo root
2. Create `control_plane/core/ocx_bridge.py` — thin wrapper around opencodex
   management API
3. Update `llm_router.py` to resolve models via opencodex slug codec
4. Add `ocx start` to `bin/awaken.py` boot sequence
5. Update `knight_session.py` to use opencodex as upstream proxy

### Not In Scope (Yet)

- Forking opencodex source into CAMELOT-OS (use as dependency first)
- Account pool configuration (Phase 4)
- Dashboard integration (optional)
- Vision/web-search sidecars (use Bifrost instead)

---

## Appendix: OpenCodex File Map

```
opencodex/src/
├── server/           # HTTP server, endpoints, auth, CORS
│   ├── responses.ts  # OpenAI Responses API handler
│   ├── chat-completions.ts  # Chat Completions handler
│   ├── claude-messages.ts   # Claude Messages handler
│   ├── relay.ts      # Streaming relay
│   ├── management-api.ts    # Config hot-reload API
│   └── readiness.ts  # Health / readiness probes
├── router.ts         # Policy-based routing engine (758 lines)
├── bridge.ts         # Protocol translation layer (1986 lines)
├── adapters/         # Provider-specific wire format adapters
│   ├── anthropic.ts  # Claude
│   ├── google.ts     # Gemini / Vertex
│   ├── openai-chat.ts
│   ├── openai-responses.ts
│   ├── kiro.ts       # Kimi
│   ├── azure.ts
│   └── base.ts       # Shared adapter interface
├── providers/        # Provider registry, quota, key failover
│   ├── registry.ts   # 40+ provider definitions
│   ├── quota.ts      # Account quota tracking
│   ├── key-failover.ts
│   └── slug-codec.ts # provider/model wire encoding
├── combos/           # Failover / round-robin combos
├── routing/          # Policy profiles, evaluator, health, cost
├── codex/            # Codex account management
├── cli/              # CLI (ocx init, ocx start, ocx stop)
├── config/           # Config loading, provider-name resolution
├── lib/              # Shared utilities (errors, redact, translator-budget)
├── types/            # TypeScript type definitions
└── index.ts          # Entry point
```
