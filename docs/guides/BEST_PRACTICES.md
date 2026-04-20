# 📜 CAMELOT OS: BEST PRACTICES & OPERATIONAL TIPS [v1.0]

## 1. Persona Token Budgeting (L3/L7)
- **Constraint:** Keep token budgets small (≤800 tokens) for local student models (e.g., Llama-3-8B-Q4, Qwen-2.5-1.5B).
- **Escalation:** Raise budgets (2000+ tokens) only for cloud calls (GPT-4o, Gemini Pro) when complex reasoning or deep context is required.
- **Implementation:** Set `max_token_budget` in the Persona JSON Manifest.

## 2. Document Sharding (L4/L6)
- **Strategy:** Never feed a full repository or large document directly to an LLM.
- **Tactic:** Shard documents into logical chunks (500-1000 tokens) and use **Archon** or **UKG_Query** to retrieve only the relevant shards for the task at hand.
- **Benefit:** Reduces noise, saves tokens, and maintains context within small context windows.

## 3. Symbolect Standardization (L1/L3)
- **Definition:** Symbolects are compact, symbolic tokens representing complex commands (e.g., `[🔒SCAN]`).
- **Usage:** Use Symbolect for repetitive instructions to save prompt tokens and ensure behavior consistency across different models.
- **Mapping:** Maintain the `symbolect_map` in `merlin_llm.py`.

## 4. Immutable Logging & Distillation (L2/L4)
- **Mandate:** LOG EVERYTHING. 
- **System:** Every reasoning trace, MCP call, and final output must be logged to the **ReasoningBank** (`03_VAULT/knowledge/reasoning_bank`).
- **Purpose:** These high-quality traces are essential for future **Model Distillation** and training specialized **LoRA Adapters** for local execution.

## 5. The Iron Gate (HITL Mandatory) (L6/L1)
- **Rule:** Always enforce Human-In-The-Loop (HITL) for any action with an **external side effect**.
- **Triggers:** External API calls, disk deletions, Git pushes, and system dependency modifications.
- **Failure Status:** Without `hitl_approved=True`, the `MCPAdapter` must return `PENDING_APPROVAL` with a detailed action preview.

---
**[Sovereign Status]:** Verified and Enforced.
"Made by Invisioned Marketing inc."
