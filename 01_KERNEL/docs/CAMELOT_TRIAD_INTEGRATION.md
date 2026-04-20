# 💎 SYSTEM ARTIFACT: CAMELOT_TRIAD_INTEGRATION.md

## 1. THE BRAIN: Videneptus LaC Implementation (Cloud/Modal)
**Implementation:** A Python decorator in the Modal Cloud function that manages the Temperature Oscillation.

### File: `/modal/logic/lac_protocol.py`
The Videneptus Engine manages the 3-Phase Loop:
1.  **DIVERGENCE** ($T=1.2$): Explore divergent paths.
2.  **CRITICALITY** ($T=0.9$): Critique via First Principles.
3.  **CONVERGENCE** ($T=0.2$): Synthesize execution plan.

## 2. THE HAND: Cribo Integration (Local/Rust)
**Implementation:** A Go wrapper around the `cribo` binary. This runs on the **Morgana (Local)** server to optimize context before sending it to the Cloud.

### File: `/internal/kinetic/cribo_wrapper.go`
*   **Role:** "Don't send the hay; send the needle."
*   **Action:** Executes `cribo --tree-shake` to compress context.

## 3. THE SOUL: UKG Logic Preservation (Shared JSON-LD)
**Implementation:** The "Save State" logic. Every time LaC finishes or Cribo executes, we write a **Truth Node**.

### File: `/pkg/brain/ukg_schema.go`
*   **Entity:** `KnowledgeItem`
*   **LogicState:** `ACTIVE` / `ARCHIVED`
*   **Provenance:** Tracks source (Merlin) and Hash.

---

## ⚔️ EXECUTION: THE NEW WORKFLOW

**Scenario:** User asks, *"Architect a new scalable backend..."*

1.  **SENSE (Anya/Local):** Route to **Merlin (Cloud)**.
2.  **PREPARE (Lukas/Local):** Executes `cribo` to compress files.
3.  **THINK (Merlin/Cloud):** Activates **Videneptus LaC** (3-Phase Temp Loop).
4.  **REMEMBER (Chronos/UKG):** Writes decision to `ukg_graph.json`.
