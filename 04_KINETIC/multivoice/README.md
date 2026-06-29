# Multivoice-Router — Cybertronia Switchboard (Go)

A Go-native, goroutine-parallel ingress switchboard that wires **Sovereign
Intent** (CLI · voice · WebMCP) to the **Polyglot Matrix** (OpenAI / Gemini /
Claude) by dynamically loading skills from the **World Tree** (Camelot-Ecosystem
registry) — honoring the 4GB Scarcity Protocol.

```
Intent ──► MultivoiceRouter ──VSS──► World Tree (vault.Ledger)
                  │                        │ skill cartridges
                  │                        ▼
                  │                 ZeroClaw arena (memfd, Scarcity-bounded)
                  ▼                        │ zero-copy
            APEEv6Router ◄─────────────────┘
              │  routes by keyword + skills
   ┌──────────┼───────────────┐
   ▼          ▼               ▼
SIR_CODEX  SIR_HELIOS     SIR_BORIS
 OpenAI     Gemini         Claude
```

## Packages
| Package | Role |
|---|---|
| `vault` | World Tree skill registry + Vector-Similarity-Search (in-memory default; SQLite drop-in) |
| `zeroclaw` | Shared-memory arena for skill cartridges; Scarcity-bounded leasing (memfd on Linux, portable fallback) |
| `orchestration` | `APEEv6Router` (Polyglot Matrix) + `MultivoiceRouter` (ingress + dispatch) |
| `cmd/multivoice` | Factory ignition entrypoint (Unix socket + HTTP/SSE) |

## Zero-cost routing (Bifrost / CLIProxy)
The Polyglot Matrix routes **free** through the local **Bifrost / CLIProxy** gateway
(`CLIPROXY_BASE`, default `http://127.0.0.1:8080/v1`) — an OpenAI-compatible endpoint
that serves models via **CLI OAuth** (your Claude/Gemini/Codex CLI subscriptions),
**not** pay-per-token API keys. All three Knights bind to free models on that gateway:

| Knight | slot | free model (env override) |
|---|---|---|
| SIR_CODEX | openai | `gpt-4o` (`CAMELOT_MODEL_CODEX`) |
| SIR_HELIOS | gemini | `gemini-2.5-flash` (`CAMELOT_MODEL_HELIOS`) |
| SIR_BORIS | claude | `claude-sonnet-4-6` (`CAMELOT_MODEL_BORIS`) |

If the gateway is offline each Knight **degrades gracefully** to the local TinyLM
stub (`NewLocalStubProvider`) — Kinetic Resilience, no hard failure. The loopback
`CLIPROXY_KEY` (`proxy-admin-key`) authorizes the local proxy only; it is **not** a
paid credential.

## Honest boundaries
- Default path is **zero-cost via the gateway** — no paid keys, no per-token billing.
  A direct paid OpenAI client also exists (`NewOpenAIProvider`, `CAMELOT_OPENAI_KEY`)
  for when you explicitly want it; real calls only happen once a gateway/key is present
  (CI tests use an httptest mock, never a live endpoint).
- **ZeroClaw** uses lease accounting identical across platforms; the Linux `memfd_create` region is a build-tagged drop-in (same approach as `control_plane/scarcity_protocol.py`).
- **World Tree** ships an in-memory starter registry; the SQLite CRIU ledger backend slots behind `vault.Ledger`.

## Build & test
```bash
cd 04_KINETIC/multivoice
go test ./...          # orchestration: routing + arena tests
go build ./...         # builds the multivoice binary
CAMELOT_ARENA_MB=128 go run ./cmd/multivoice   # ignite (Unix sock + :7680 SSE)
```
Paths are env-configurable: `CAMELOT_WORLD_TREE`, `CAMELOT_MV_SOCK`, `CAMELOT_MV_SSE`, `CAMELOT_ARENA_MB`.

## Roadmap to live
1. Real `Provider` clients (OpenAI/Gemini/Claude) behind the AI Gateway / Aperture.
2. SQLite CRIU `vault.Ledger` backend ingesting the Camelot-Ecosystem registry.
3. Linux `memfd_create` build tag + `MADV_DONTNEED` reclaim in `zeroclaw`.
4. Rust WASM registry parser feeding `zeroclaw` zero-copy.
