---
name: freellmapi-zero-cost
description: Route non-sensitive, high-volume LLM queries, test generation, and background Squire reasoning to the FreeLLMAPI zero-cost pooled gateway (~34 free providers including DeepSeek, Qwen 2.5, Llama 3.3, GLM-4, Cerebras, and Groq). Strictly forbidden for secret-bearing prompts.
---

# FreeLLMAPI Zero-Cost Gateway Skill

The `freellmapi-zero-cost` skill enables Camelot-OS Knights, Squire swarms, and background pipelines to leverage a pooled gateway of ~34 free-tier LLM providers (from `tashfeenahmed/freellmapi`). It serves as an ultra-high-throughput, zero-financial-cost fallback layer when primary frontier token budgets are constrained or when running mass synthetic tasks.

---

## 🏛️ Sovereign Architectural Context

- **Source Repository**: `https://github.com/tashfeenahmed/freellmapi`
- **Substrate**: OpenAI-compatible Express gateway with SQLite-backed rate-limit ledger and Thompson-sampling Multi-Armed Bandit router.
- **Camelot Bridge Coordinate**: [`02_FORGE/assimilation/freellmapi/freellmapi_bridge.py`](file:///C:/Users/vizio/CAMELOT_OS/02_FORGE/assimilation/freellmapi/freellmapi_bridge.py)
- **FastMCP Tools**: `freellmapi_chat`, `freellmapi_status`, `freellmapi_list_models`
- **Runic Dispatch**: `//FREELLMAPI <prompt>`, `//ZERO_COST <prompt>`
- **CLI Subcommand**: `python bin/camelot.py freellmapi status | chat | models`

---

## 🔒 Iron Law: Strict Air-Gap Secret Sanitization

> [!CAUTION]
> **NEVER route prompts containing API keys, private tokens, passwords, or credentials through FreeLLMAPI.**
> FreeLLMAPI pools public/free-tier third-party endpoints.
> In accordance with Camelot-OS Titanium Law #1 and rule `AGENTS.md`:
> - Any prompt matching `api_key`, `token`, `secret`, `bearer`, or `password` will be blocked by `SecretSanitizationViolation`.
> - All secret-handling operations must strictly route to **`SIR_GHOST`** (local air-gapped container).

---

## 🌟 Supported Model Catalog & Fallback Tiers

| Alias / Model ID | Upstream Backends | Optimal Use-Case |
| :--- | :--- | :--- |
| `auto` | Thompson-Bandit dynamic select | General reasoning, highest availability |
| `deepseek-chat` | DeepSeek V3 / ModelScope | Deep architectural evaluation, code generation |
| `deepseek-reasoner` | DeepSeek R1 (Airforce / ModelScope) | Chain-of-Thought formal math / algorithmic proofs |
| `qwen-2.5-72b` | ModelScope / Groq | Multilingual code generation, structured JSON |
| `llama-3.3-70b` | Cerebras / Groq | Ultra-low latency responses (<200ms TTFT) |
| `gemini-2.5-flash` | Google Free / OpenRouter | Fast multimodal summarization & triage |
| `glm-4-flash` | Zhipu AI Free | High-volume batch text processing |

---

## 🛠️ Usage Patterns

### 1. FastMCP Tool Execution
Knights and agents invoke the tool directly:
```python
# FreeLLMAPI status check
status = freellmapi_status()

# Zero-cost chat completion
result = freellmapi_chat(
    prompt="Explain Thompson-sampling multi-armed bandits in three bullet points.",
    model="auto",
    system="You are an expert distributed systems engineer."
)
```

### 2. CLI Execution
```powershell
# Inspect gateway status
python bin/camelot.py freellmapi status

# List available models
python bin/camelot.py freellmapi models

# Query zero-cost model
python bin/camelot.py freellmapi chat --prompt "Generate 5 unit test cases for a LRU cache" --model deepseek-chat
```

### 3. Runic Dispatch
```powershell
python -m control_plane.runes.runic_router --rune ZERO_COST --task "Summarize recent git commit diffs"
```

---

## 📊 Glass Observatory Integration
Every invocation through `FreeLLMAPIBridge` automatically taps into the **Glass Observatory** (`Project Speculum`), recording the interaction behind the WORM glass wall and awarding **+35 XP** to the calling Knight under the `FREELLMAPI_GATEWAY` channel.
