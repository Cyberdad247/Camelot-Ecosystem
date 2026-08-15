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

## Local-first inference policy

### Local OpenAI-compatible tier (freellmapi / openai-oauth / LiteRT-LM)

Phase 1 integration: when the Bifrost/CLIProxy gateway is unreachable, the
router probes a **local OpenAI-compatible endpoint** before degrading to the
TinyLM stub. One protocol, three sources:

- **freellmapi** (recommended, `02_FORGE/KINETIC_ARMORY/freellmapi`) —
  OpenAI-compatible aggregator over 18 free providers / 161 models with
  per-key usage caps and failover, on `127.0.0.1:3001/v1`. See
  `docs/architecture/freellmapi-deployment.md` for the deploy.
- **openai-oauth** (`02_FORGE/KINETIC_ARMORY/openai-oauth`) — turns a ChatGPT
  account into an OpenAI-compatible dev proxy on `127.0.0.1:10531/v1`.
- **LiteRT-LM** (`02_FORGE/KINETIC_ARMORY/LiteRT-LM`) — Google's on-device LLM
  orchestration layer (SADD Inference Node); its CLI serves the same
  OpenAI-compatible protocol.

Configure with (freellmapi example):

```bash
OPENAI_COMPAT_BASE=http://127.0.0.1:3001/v1   # freellmapi; any OpenAI-compatible endpoint works
OPENAI_COMPAT_KEY=local                          # loopback credential, never a paid key
```

The tier is enabled automatically when the gateway probe fails and the local
endpoint answers `/models`. `CAMELOT_REQUIRE_GATEWAY=1` still fails closed when
the CLIProxy gateway is down — the local tier is a degradation path, not a
bypass. See `docs/architecture/integrations.md` and ADR-0002.

The CAMELOT Python LLM router now prefers Ollama before Bifrost/CLIProxy or any
remote provider. To make the policy fail closed and guarantee no remote egress
from that router, set the process environment variable:

```bash
CAMELOT_LOCAL_ONLY=1
```

On this RTX 2050 workstation, the verified low-memory launch is CPU-only and
cloud-disabled. It uses an already installed model and never pulls weights:

```bash
OLLAMA_NO_CLOUD=1 CUDA_VISIBLE_DEVICES=-1 OLLAMA_LLM_LIBRARY=cpu \
OLLAMA_HOST=127.0.0.1:11434 ollama serve
```

The verified smoke model is `qwen2.5-coder:3b`; it returned `LOCAL_OK` locally.
The 4B models are cataloged but currently fail GPU loading because the 4GB RTX
2050 cannot allocate their required CUDA/KV buffers.

In local-only mode, Ollama is the sole permitted provider; an explicit request
for a cloud provider is rejected instead of being silently rerouted. The
available workstation models are registered in
`03_VAULT/training/configs/sovereign_models.json`, including the air-gapped
`qwen3:4b` and `qwen2.5-coder:3b` assignments.

This policy is separate from the Go Multivoice gateway: the Go service still
requires an explicitly configured `CLIPROXY_BASE` when using Bifrost routing.

## Honest boundaries
- Default path is **zero-cost via the gateway** — no paid keys, no per-token billing.
  A direct paid OpenAI client also exists (`NewOpenAIProvider`, `CAMELOT_OPENAI_KEY`)
  for when you explicitly want it; real calls only happen once a gateway/key is present
  (CI tests use an httptest mock, never a live endpoint).
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
