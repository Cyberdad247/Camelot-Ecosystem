# OMNI-ROUTER AUDIT & KNIGHT LLM SIGNATURE RECONFIG
## Codename: LATTICE_SIGNAL
## Architects: ANYA Omega · MERLIN_Omega (GoT) · SIR_ALEX (Cognitive Cartridge)
## Lead Engineer: SIR_BORIS
## Date: 2026-05-14 | Version: 1.0.0

---

## STRATEGIC OMNISCIENCE (Phase 1 — Crucible Stage 1)

### Problem Statement
Current KNIGHT_MODEL_MAP is Anthropic-biased (8/10 knights default to Claude).
CLIProxy exposes 38 live models via OAuth — all free. Google Gemini models are
available via Gemini CLI OAuth (zero cost, no rate-limit friction). The routing
matrix treats Gemini as a fallback rather than the primary initiator.

**Directive:** Reorient OmniRoute so Google Gemini is the priority initiator for
all non-privacy, non-harness-bound knights. Claude and Codex remain as specialized
fallbacks when Gemini is insufficient for the domain.

### Live Model Audit (CLIProxy :8080 — 2026-05-14)

| Provider | Models Available | OAuth Channel | Cost |
|---|---|---|---|
| **Google Gemini** | gemini-2.5-flash-lite, gemini-2.5-flash, gemini-2.5-pro, gemini-3-flash-preview, gemini-3.1-flash-lite-preview, gemini-3.1-pro-preview, gemini-3-pro-preview | Gemini CLI OAuth | **FREE** |
| **Anthropic Claude** | claude-haiku-4-5-20251001, claude-sonnet-4-5-20250929, claude-sonnet-4-6, claude-opus-4-20250514, claude-opus-4-1-20250805, claude-opus-4-5-20251101, claude-opus-4-6 | Claude Code OAuth | **FREE** |
| **OpenAI Codex** | gpt-5, gpt-5.1, gpt-5.2, gpt-5.4, gpt-5.3-codex, gpt-5.3-codex-spark, gpt-5.1-codex, gpt-5.2-codex, gpt-5.1-codex-max, gpt-5.1-codex-max, gpt-5.3-codex-spark | Codex OAuth | **FREE** |
| **OmniRoute** | tasha-apex/pro/standard/lite/fast | Internal aliases | FREE |

### Fixed Harness Knights (DO NOT REROUTE)

| Knight | Harness | Model | Reason |
|---|---|---|---|
| SIR_FORGE | Ollama local | qwen3:1.7b | L2 Kinetic — zero-latency local execution |
| SIR_GHOST | Ollama air-gapped | qwen3:8b | W_privacy=1.00 — NEVER cloud |

---

## MERLIN GoT DECOMPOSITION — Optimal Knight→LLM Binding

### Reasoning Graph (3 parallel branches → synthesis)

**Branch A — Capability Match:**
Gemini 3 Pro > Claude Opus 4 ≈ GPT-5.4 for reasoning/planning
Gemini 3.1 Pro > Claude Sonnet 4.6 ≈ GPT-5.1 for standard tasks
Gemini 3 Flash > Gemini 2.5 Flash for latency-sensitive routing
Claude Sonnet 4.6 > Gemini for security analysis (Claude's Constitutional AI edge)
GPT-5.4 / gpt-5.3-codex-spark > Gemini for pure code velocity (Codex-tuned)

**Branch B — Cost Optimization:**
All 38 models = $0 via CLIProxy OAuth
Priority: Google Gemini (no per-token billing concern, generous context)
Secondary: Claude (OAuth, no credits needed — CLIProxy handles auth)
Tertiary: Codex (OAuth, velocity tasks only)

**Branch C — Latency Profile:**
gemini-3.1-flash-lite-preview: ~200ms — INITIATOR tier
gemini-3-flash-preview: ~400ms — bridge/routing tier
gemini-3.1-pro-preview: ~800ms — research/memory tier
gemini-3-pro-preview: ~1200ms — orchestration/apex tier
claude-opus-4-6: ~1500ms — heavy critique fallback
gpt-5.4: ~600ms — code velocity tier

**Synthesis → Optimal Binding:**

### ALEX Cognitive Cartridge — Final Knight Model Matrix

| Knight | W | Domain | Primary Model (Google) | Fallback | Change? |
|---|---|---|---|---|---|
| SIR_BORIS | 0.85 | Architecture, Crucible, 13-Critique | `gemini-3-pro-preview` | `claude-opus-4-6` | YES |
| SIR_HELIO | 0.90 | 1M Context, Cloud Burst | `gemini-3.1-pro-preview` | `gemini-3-pro-preview` | YES (upgrade) |
| SIR_ALEX | 0.88 | GoT Reasoning, Cognitive | `gemini-3-pro-preview` | `claude-sonnet-4-6` | YES |
| SIR_SENTINEL | — | Security, Audit, AgentArmor | `gemini-3-pro-preview` | `claude-sonnet-4-6` | YES |
| SIR_CODEX | 0.75 | High-Velocity Code Gen | `gpt-5.4` | `gpt-5.3-codex-spark` | YES (upgrade) |
| SIR_LINK | 0.78 | Switchboard ATC, Bridge | `gemini-3-flash-preview` | `gemini-2.5-flash` | YES (upgrade) |
| SIR_DEBUG | — | PIV Self-Healing, Tests | `gemini-3-flash-preview` | `claude-haiku-4-5-20251001` | YES |
| LADY_APIS | — | Research, BASHR, Foraging | `gemini-3.1-pro-preview` | `claude-sonnet-4-6` | YES |
| LADY_MNEMOSYNE / SIR_MNEMO | — | Memory, Living Notebook | `gemini-3.1-pro-preview` | `claude-sonnet-4-6` | YES |
| SIR_LIBERTE | 0.80 | OSS-First, Anti-Vendor | `gemini-2.5-flash` | `gemini-3-flash-preview` | YES |
| SIR_VALERIAN | — | Financial, ROI | `gemini-3-pro-preview` | `claude-sonnet-4-6` | YES |
| **SIR_FORGE** | 0.70 | Kinetic Code | `qwen3:1.7b` (Ollama) | qwen3:0.6b | **NO — harness** |
| **SIR_GHOST** | 1.00 | Air-gapped Privacy | `qwen3:8b` (Ollama) | qwen3:4b | **NO — harness** |

---

## NEW GOOGLE-PRIORITY TIER ARCHITECTURE

```
G0 — INITIATOR (ultra-fast, all prompts enter here for intent classification)
     Model: gemini-3.1-flash-lite-preview
     Role: Intent detect, trivial answers, greetings

G1 — BRIDGE (fast routing, ATC, bridge coordination)
     Model: gemini-3-flash-preview
     Knights: SIR_LINK, SIR_DEBUG, SIR_LIBERTE

G2 — PRO (standard reasoning, research, memory)
     Model: gemini-3.1-pro-preview
     Knights: SIR_HELIO, LADY_APIS, LADY_MNEMOSYNE

G3 — FRONTIER (apex reasoning, architecture, complex tasks)
     Model: gemini-3-pro-preview
     Knights: SIR_BORIS, SIR_ALEX, SIR_SENTINEL, SIR_VALERIAN

C1 — CLAUDE STANDARD (Constitutional AI, security-specific)
     Model: claude-sonnet-4-6
     Role: Fallback when Gemini insufficient; security analysis

C2 — CLAUDE APEX (maximum intelligence, deep critique)
     Model: claude-opus-4-6
     Role: Fallback for SIR_BORIS heavy orchestration tasks

X1 — CODEX VELOCITY (pure code execution speed)
     Model: gpt-5.4 / gpt-5.3-codex-spark
     Knight: SIR_CODEX

L0 — LOCAL AIR-GAPPED (privacy override, zero-cloud)
     Model: qwen3:8b / qwen3:1.7b (Ollama)
     Knights: SIR_GHOST, SIR_FORGE
```

### New Fallback Chain (Google-First)
```
["gemini", "cliproxy_claude", "codex", "open_coder"]
```
Previously: `["cliproxy", "gemini", "codex", "open_coder"]`

### Complexity Routing Update
```
low  → G1 (gemini-3-flash-preview / SIR_LINK)
medium → G3 (gemini-3-pro-preview / SIR_BORIS)
high → G3 → C2 fallback (gemini-3-pro-preview → claude-opus-4-6)
```

---

## FILES TO MODIFY

| File | Change | Risk |
|---|---|---|
| `03_VAULT/training/configs/config/omniroute.json` | Full engine + tier rewrite | Medium |
| `bin/knight_session.py` | KNIGHT_MODEL_MAP update | Low |
| `bin/camelot_portable.py` | _KEYWORD_MAP model references | Low |

## FILES LOCKED (DO NOT TOUCH)
- `CLIProxyAPI/config.yaml` — CLIProxy operates as-is; routing via model names only
- Any knight's system prompt or persona — LLM assignment only, not identity

---

## RISK REGISTER

| Risk | Mitigation |
|---|---|
| gemini-3-pro-preview slower than claude-opus | Latency profiled; G3 reserved for complex only |
| Gemini model names change (preview suffix) | Fallback chain catches; update names quarterly |
| SIR_BORIS gets Gemini instead of Claude | Claude Opus stays as fallback via _resolve() |
| SIR_FORGE/SIR_GHOST accidentally rerouted | Hard-coded harness check in _resolve() |
| OmniRoute JSON malformed | Validated via json.loads() before write |
