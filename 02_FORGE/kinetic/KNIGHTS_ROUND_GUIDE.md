# ⚔️ THE ROUND TABLE: KINETIC GUIDE
> **Guardian**: Merlin (The Magician)
> **Layer**: L2 (Kinetic)

This guide explains how to use the **Phase 4 & 5** capabilities of the Titan System.

## 🧙‍♂️ Merlin Dispatch (`merlin_dispatch.py`)
The **Merlin Dispatcher** is the central command router.

### Usage
- **Interactive Mode**: Run `python merlin_dispatch.py` to enter the tower.
- **Aliases**: Use shorthand commands for speed:
  - `up` -> `upgrade`
  - `ls` -> `scout`
  - `xp <knight> <amount>` -> `scribe --xp <knight> <amount>`
  - `evo <knight>` -> `evolve <knight>`
  - `loom` -> `weave`

---

## 🔝 XP & Leveling (Evolution)
Agents grow through XP and unlock new tiers of mastery.

### Level Thresholds
- **Level 2 (100 XP)**: Unlocks `Advanced Reasoning (System 2)`
- **Level 3 (300 XP)**: Unlocks `Multimodal Analysis (Ocular)`
- **Level 4 (600 XP)**: Unlocks `Kinetic Refactoring (The Hand)`
- **Level 5 (1000 XP)**: Unlocks `Sovereign Autonomy (Merlin's Voice)`

### 🧬 Evolution (`titan_evolve.py`)
When a Knight reaches a new level, use the evolution spell to unlock their new skills:
`python merlin_dispatch.py evo Sir_Forge`

---

## 🧵 Titan Loom (Durable Workflows)
The **Loom** ensures long-running tasks survive interruptions.

### Mechanism
- **State**: Tracks progress in `03_VAULT/99_SCRATCHPAD/loom_state.json`.
- **Integration**: Auto-updates the **Learning Log** on failure and awards **XP** on success.
- **Execution**: 
    `python merlin_dispatch.py loom start --name "Repo Assimilation" --agent Sir_Forge --steps "Scout" "Plan" "Clone" "Alchemize"`

---

## 📜 The Scroll of Wisdom
Every error encountered by a Kinetic tool is recorded in `03_VAULT/99_SCRATCHPAD/Learning_Log.md`. 
**Law**: "No failure shall go unrecorded."
