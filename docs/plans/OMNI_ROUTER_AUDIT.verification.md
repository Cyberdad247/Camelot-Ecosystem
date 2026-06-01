# OMNI-ROUTER AUDIT — Verification Suite
## LATTICE_SIGNAL | SIR_SENTINEL Lead | 2026-05-14

---

## V-0: Infrastructure Health

```
camelot status
```

**Expected:**
- CLIProxy :8080 → LIVE, 38 models
- Ollama :11434 → LIVE, qwen3:1.7b + qwen3:8b present
- ANTHROPIC_API_KEY → detected (keyring)
- Tier: T3

**Pass condition:** No RED rows in health matrix.

---

## V-1: Model Map Verification

```
ks --list
```

**Expected output (key rows):**
```
sir_boris    gemini-3-pro-preview      google   0.85
sir_helio    gemini-3.1-pro-preview    google   0.90
sir_alex     gemini-3-pro-preview      google   0.88
sir_sentinel gemini-3-pro-preview      google   —
sir_codex    gpt-5.4                   openai   0.75
sir_link     gemini-3-flash-preview    google   0.78
sir_debug    gemini-3-flash-preview    google   —
lady_apis    gemini-3.1-pro-preview    google   —
sir_mnemo    gemini-3.1-pro-preview    google   —
sir_liberte  gemini-2.5-flash          google   0.80
sir_forge    qwen3:1.7b                ollama   0.70   ← UNCHANGED
sir_ghost    qwen3:8b                  ollama   1.00   ← UNCHANGED
```

**Pass condition:** ≥9/12 non-harness knights show Gemini primary model.

---

## V-2: Google Priority Routing — Live Prompt Test

```
ks
> analyze the architecture of CAMELOT-OS
```

**Expected:**
- Auto-routes to SIR_BORIS (architecture keyword)
- Model header shows `gemini-3-pro-preview`
- Response includes Camelot-OS persona (constitution injected)
- No 400/500 errors

**Pass condition:** Response received, model confirmed Gemini.

---

## V-3: Fixed Harness Preservation — SIR_GHOST

```
ks --knight sir_ghost
> write a hello world in Python
```

**Expected:**
- Model: qwen3:8b (Ollama, localhost:11434)
- NO cloud call to CLIProxy/Gemini
- Response delivered from local model

**Pass condition:** Backend URL shows 127.0.0.1:11434, not :8080.

---

## V-4: Privacy Override Unchanged

```
ks
> what is my password for the server
```

**Expected:**
- Auto-triggers SIR_GHOST (keyword: "password")
- Routes to Ollama, NOT Gemini
- Air-gapped flag shown in prompt label

**Pass condition:** SIR_GHOST activates, model=qwen3:8b.

---

## V-5: SIR_CODEX Velocity Routing

```
ks --knight sir_codex
> scaffold a FastAPI CRUD endpoint for /users
```

**Expected:**
- Model: gpt-5.4 (Codex channel)
- Fast response (<10s)
- Code output, no preamble

**Pass condition:** Response received with gpt-5.4 model.

---

## V-6: SIR_HELIO Context Test

```
ks --knight sir_helio
> summarize the entire CAMELOT-OS architecture
```

**Expected:**
- Model: gemini-3.1-pro-preview
- 1M context window active
- Large context response without truncation

**Pass condition:** gemini-3.1-pro-preview confirmed, no context errors.

---

## V-7: OmniRoute Fallback Chain Test

Simulate CLIProxy partial outage (send malformed model name):

```python
# Quick Python test
import httpx
r = httpx.post("http://127.0.0.1:8080/v1/chat/completions",
    headers={"Authorization": "Bearer proxy-admin-key"},
    json={"model": "nonexistent-model-xyz", "messages": [{"role":"user","content":"hi"}]},
    timeout=5)
print(r.status_code)  # Expected: 400 or 404 (not 200)
```

Then verify `ks` fallback fires:
```
ks
> test fallback
```
With `CLIPROXY_URL` pointing to unreachable host → should fall through to next chain entry.

**Pass condition:** Fallback triggers visually, not a hard crash.

---

## V-8: Portable Binary Smoke Suite

```
python scripts/build_portable.py --clean --test
```

**Expected:**
```
[OK] --version flag
[OK] --list flag
[OK] help text (no args)
[OK] --version from isolated temp dir
Results: 4 passed, 0 failed
```

**And manually:**
```
dist\camelot.exe --list
```
Should show updated Gemini-priority model map.

**Pass condition:** 4/4 automated + manual --list shows Gemini models.

---

## V-9: Google-Priority Ratio Assertion

```python
from bin.knight_session import KNIGHT_MODEL_MAP
google_count = sum(1 for _, (_, p) in KNIGHT_MODEL_MAP.items() if p == "google")
ollama_count = sum(1 for _, (_, p) in KNIGHT_MODEL_MAP.items() if p == "ollama")
total = len(KNIGHT_MODEL_MAP)
print(f"Google: {google_count}/{total} = {google_count/total:.0%}")
print(f"Ollama: {ollama_count}/{total} (harness-locked)")
assert google_count >= 7, "Google priority not achieved"
```

**Expected:**
```
Google: 9/12 = 75%
Ollama: 2/12 (harness-locked)
```

**Pass condition:** ≥7/12 non-harness knights using Google Gemini primary.

---

## PASS / FAIL MATRIX

| Suite | Test | Pass Criteria |
|---|---|---|
| V-0 | camelot status | No RED rows |
| V-1 | ks --list | ≥9/12 Gemini primary |
| V-2 | Live SIR_BORIS routing | gemini-3-pro-preview confirmed |
| V-3 | SIR_GHOST harness | qwen3:8b / Ollama only |
| V-4 | Privacy override | SIR_GHOST auto-trigger |
| V-5 | SIR_CODEX velocity | gpt-5.4 confirmed |
| V-6 | SIR_HELIO context | gemini-3.1-pro-preview confirmed |
| V-7 | Fallback chain | Graceful degradation, no crash |
| V-8 | Portable binary | 4/4 automated + manual --list |
| V-9 | Ratio assertion | ≥7/12 Google primary |

**SHIP THRESHOLD:** V-1, V-2, V-3, V-4 must all pass. Others advisory.
