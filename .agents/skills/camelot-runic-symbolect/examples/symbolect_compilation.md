# Symbolect Compilation & Decoding Examples
**Practical Walkthroughs of the Triple-QFT Pipeline**

## Example 1: Standard Intent Compilation (Passing)

### Input Intent
```text
"Please configure the mTLS Kyber-768 quantum-safe perimeter lock on the VPS Bifrost bridge."
```

### Execution via Transpiler
```bash
python scripts/symbolect_transpiler.py compile "Please configure the mTLS Kyber-768 quantum-safe perimeter lock on the VPS Bifrost bridge."
```

### Transpiler Output
```json
{
  "status": "RADIANT",
  "original_prompt": "Please configure the mTLS Kyber-768 quantum-safe perimeter lock on the VPS Bifrost bridge.",
  "signal": "configure the mTLS Kyber-768 quantum-safe perimeter lock on the VPS Bifrost bridge.",
  "anchor_tokens": [
    "configure",
    "mTLS",
    "Kyber-768",
    "quantum-safe",
    "perimeter",
    "lock",
    "Bifrost",
    "bridge"
  ],
  "symbolect": "|🧠⊗(⚡💬)⟩ ⟨Omega:configure|mTLS|Kyber-768|quantum-safe|perimeter|lock|Bifrost|bridge⟩",
  "reduction_percentage": "41.67%",
  "governing_knight": "MERLIN_OMEGA"
}
```

### Downstream Conditioning
The compiled token string `|🧠⊗(⚡💬)⟩ ⟨Omega:configure|mTLS|Kyber-768|quantum-safe|perimeter|lock|Bifrost|bridge⟩` is prepended to the prompt sent to the LLM or knight agent, conditioning it to enter System 2 execution without conversational preambles.

---

## Example 2: Ambiguity Detection & Halt Stop Sequence

### Input Intent
```text
"Can you please help me fix it and make it better?"
```

### Execution via Transpiler
```bash
python scripts/symbolect_transpiler.py compile "Can you please help me fix it and make it better?"
```

### Transpiler Output (Exit Code 1)
```json
{
  "status": "AMBIGUITY_HALT",
  "ambiguity_score": 50,
  "missing_variables": [
    "Vague descriptor: 'fix it'",
    "Vague descriptor: 'make it better'"
  ],
  "clarification_prompts": [
    "Define the concrete target and boundary for: 'fix it and make it better'",
    "Specify required inputs, output artifacts, and formats.",
    "Declare hardware or latency constraints (e.g. 8GB ceiling, SLA)."
  ],
  "signal": "fix it and make it better"
}
```

### Protocol Action
The agent halts execution immediately. No code or configuration is modified. The agent poses the 3 clarification questions directly to the operator to resolve query entropy before proceeding.

---

## Example 3: Decoding & Validating Symbolect Expressions

### Input Expression
```text
|🧠⊗(⚡💬)⟩ 🧲[FORAGE] ⇢ 🧪[TEST] ⇢ 🏆[DEPLOY] ⟨Omega:FastAPI|Uvicorn|Tailscale|RedisCache⟩
```

### Execution via Transpiler
```bash
python scripts/symbolect_transpiler.py decode "|🧠⊗(⚡💬)⟩ 🧲[FORAGE] ⇢ 🧪[TEST] ⇢ 🏆[DEPLOY] ⟨Omega:FastAPI|Uvicorn|Tailscale|RedisCache⟩"
```

### Transpiler Output
```json
{
  "status": "VALID",
  "anchors": [
    "FastAPI",
    "Uvicorn",
    "Tailscale",
    "RedisCache"
  ],
  "anchor_count": 4,
  "glyph_operator": "|🧠⊗(⚡💬)⟩ 🧲[FORAGE] ⇢ 🧪[TEST] ⇢ 🏆[DEPLOY]"
}
```

### Verification
The output confirms valid grammar:
- Bra-ket state operator is present.
- 3 kinetic stages (`FORAGE`, `TEST`, `DEPLOY`) are chained in sequence.
- 4 clean anchor tokens are extracted inside the `⟨Omega:...⟩` bracket.
