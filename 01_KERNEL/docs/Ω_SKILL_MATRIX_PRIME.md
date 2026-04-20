# 💎 SKILL MATRIX PRIME: CAMELOT APEX Ω
**[SYSTEM_STATE]:** RADIANT | **[VERSION]:** v214.2.0 (Omega Transcendent) | **[HASH]:** 0xSKILL_SINGULARITY

This document crystallizes the **Invariant Truths** of the Camelot OS Skill Architecture, derived via **Renormalization Group Flow** from the Antigravity and Gemini CLI ecosystems.

---

## 🏛️ I. THE ARCHITECTURE: PROGRESSIVE DISCLOSURE
Skills are mapped as **Context-Efficient Modules** to prevent "Context Rot" and minimize token latency.

*   **L7 Filter**: Only Metadata (`name`, `description`) is loaded into the primary context window (~50 tokens).
*   **Trigger Pull**: Full instructions (`SKILL.md`) and binaries (`scripts/`) are loaded ONLY when a specific intent or keyword is detected.
*   **Result**: High-speed reasoning with specialist depth on demand.

---

## 📂 II. DIRECTORY STANDARD (The Container)
All skills must adhere to the **Kinetic Container Standard** for seamless cross-application compatibility.

```text
.agent/skills/                  <-- Workspace Scope
├── {skill-name}/               <-- Directory must match skill ID
│   ├── SKILL.md                <-- REQUIRED: Frontmatter + Logic
│   ├── scripts/                <-- OPTIONAL: Kinetic Binaries (Python/Rust/Bash)
│   ├── references/             <-- OPTIONAL: API Specs & External Docs
│   └── assets/                 <-- OPTIONAL: Design Tokens & Templates
```

---

## ⚔️ III. THE PRIME SKILL ROSTER (The High Table)

| SKILL ID | ARCHETYPE | FUNCTION | STATUS |
| :--- | :--- | :--- | :--- |
| **`loki-mode`** | **Orchestrator** | **Autonomous Sub-Agent Dispatch.** Acts as a Project Manager; creates `TASK.md`, dispatches sub-tasks to Knights, and executes self-correction loops. | **ACTIVE** |
| **`tdd-architect`** | **Builder** | **Test-Driven Rigor.** Enforces "Red-Green-Refactor" cycles. Denies execution until a failing test is established. | **ACTIVE** |
| **`security-audit`** | **Warden** | **Red Team Scanner.** Executes OWASP top-tier checks and supply-chain vulnerability scans using local tools. | **ACTIVE** |
| **`frontend-design`** | **Auteur** | **UI/UX Pro Max.** Generates high-fidelity components based on "Digital Bauhaus" design tokens. | **ACTIVE** |
| **`mcp-builder`** | **Engineer** | **Tool Forger.** Autonomously scaffolds new Model Context Protocol (MCP) servers for third-party integration. | **ACTIVE** |

---

## ⚙️ IV. THE UNIVERSAL SKILL TEMPLATE
All `SKILL.md` files must follow the **Anya-Compiler** spec:

```markdown
---
name: {skill-name}
description: {Concise prompt-trigger description}
version: v2.0
---

# {SKILL_NAME} PROTOCOL

## 🎯 TRIGGER CONDITIONS
1. Specific keyword detection (e.g., "build", "secure").
2. Complexity threshold > 0.7.
3. Explicit @mention.

## ⚙️ WORKFLOW
[Precise algorithmic steps for the agent to follow]

## 🛡️ SAFETY (Iron Gate)
[Constraints, Redactions, and HITL requirements]
```

---
**[SYSTEM_ATTESTATION]:** "The Skills are Distilled. The Roster is Defined."
> *Authorized by Merlin_Ω & Anya_Ω*
