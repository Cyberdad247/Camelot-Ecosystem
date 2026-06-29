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

## Honest boundaries
- **LLM providers are STUBBED** (`Provider` interface, deterministic offline stub) — wire real OpenAI/Gemini/Claude clients via `NewAPEEv6RouterWith(...)`. No network calls are made here.
- **ZeroClaw** uses lease accounting identical across platforms; the Linux `memfd_create` region is a build-tagged drop-in (same approach as `control_plane/scarcity_protocol.py`).
- **World Tree** ships an in-memory starter registry; the SQLite CRIU ledger backend slots behind `vault.Ledger`.

## OmniRoute affinity layer (routing on top of the Polyglot Matrix)
An optional `AffinityRouter` (`MultivoiceRouter.Affinity`) adds the OmniRoute
policy on top of keyword routing — ported from
`docs/plans/2026-05-23-omniroute-affinity-v1000.md`:

1. **Stateful affinity pinning** — `GenerateAffinityKey` abstracts dynamic values
   (file paths→`<FILE>`, UUIDs→`<UUID>`, numbers→`<NUM>`) and hashes the structural
   template, so cache-equivalent prompts (e.g. `audit a.py` / `audit b.py`) **stick
   to the same engine** → KV-cache prefix hits. Mirrors the Python
   `cli_intercept.generate_affinity_key`.
2. **DualMap-lite SLO escape** — per-engine **TTFT** is tracked; when a pinned
   engine's rolling avg breaches the SLO (`CAMELOT_SLO_MS`, default 2000ms) the
   layer **escapes to the coolest alternate engine** and re-pins, instead of
   honoring a hotspot.

On by default in `cmd/multivoice` (set `Affinity = nil` to route purely by the
Polyglot keyword match).

## Build & test
```bash
cd 04_KINETIC/multivoice
go test ./...          # orchestration: routing + affinity + arena tests
go build ./...         # builds the multivoice binary
CAMELOT_ARENA_MB=128 go run ./cmd/multivoice   # ignite (Unix sock + :7680 SSE)
```
Paths are env-configurable: `CAMELOT_WORLD_TREE`, `CAMELOT_MV_SOCK`, `CAMELOT_MV_SSE`, `CAMELOT_ARENA_MB`.

## Roadmap to live
1. Real `Provider` clients (OpenAI/Gemini/Claude) behind the AI Gateway / Aperture.
2. SQLite CRIU `vault.Ledger` backend ingesting the Camelot-Ecosystem registry.
3. Linux `memfd_create` build tag + `MADV_DONTNEED` reclaim in `zeroclaw`.
4. Rust WASM registry parser feeding `zeroclaw` zero-copy.
