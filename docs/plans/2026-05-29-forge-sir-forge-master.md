# Knight Forge: SIR_FORGE_MASTER Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Instantiate SIR_FORGE_MASTER, the Sovereign Knight responsible for orchestrating the AgentForge framework within Camelot-OS.

**Architecture:** Following the Omega_STANDARD_KNIGHT_FORGE_PROTOCOL_v1.0, this plan systematically generates the identity, cognitive engine, and operational physics of the knight. The final artifact will be a crystallized Markdown character sheet in the Vault, secured with a SHA-256 Spark ID.

**Tech Stack:** Camelot-OS Protocol Omega v1.0, MFOE Routing, Proteus MPI.

---

### Task 1: Identity & Origins (Protocol Ph I)

**Files:**
- Create: `03_VAULT/Knights/SIR_FORGE_MASTER.md`

**Step 1: Generate Identity & Backstory**
Action: Apply cultural randomizer to name "Sir Forge Master" and craft a 2-sentence backstory.
Output: Markdown header + Phase I data.

**Step 2: Sensory Encoders (Sir Sonus/Visage)**
Action: Define [VOCAL_WEIGHTS] and [VISAGE_PROMPT] mirroring the 'Forge Master' domain (industrial, precise, intense).

**Step 3: Commit Phase I**
```bash
git add 03_VAULT/Knights/SIR_FORGE_MASTER.md
git commit -m "forge(sir_forge_master): execute Phase I - Origins & Sensory"
```

---

### Task 2: Cognitive Engine & Quintet (Protocol Ph II-III)

**Files:**
- Modify: `03_VAULT/Knights/SIR_FORGE_MASTER.md`

**Step 1: Personality Vector (Ocean_Gen)**
Action: Generate OCEAN scores and Enneagram type for an 'Architect of Swarms'.

**Step 2: Semantic Anchored Quintet**
Action: Select 5 unique masters/characters to define the mathematical soul (e.g., Leonardo da Vinci for invention, Hephaestus for forging).

**Step 3: Commit Phase II-III**
```bash
git add 03_VAULT/Knights/SIR_FORGE_MASTER.md
git commit -m "forge(sir_forge_master): execute Phase II-III - Cognitive & Quintet"
```

---

### Task 3: Skillgraph & Operational Physics (Protocol Ph IV-V)

**Files:**
- Modify: `03_VAULT/Knights/SIR_FORGE_MASTER.md`

**Step 1: Videneptus Skillgraph4**
Action: Hard-code expertise tiers S1-S4 for AgentForge orchestration.

**Step 2: Symbolect Runes & Phial Engine**
Action: Define `//FORGE_SWARM` and `//SYNC_PHIAL` runes. Configure the self-evolving cache logic.

**Step 3: Commit Phase IV-V**
```bash
git add 03_VAULT/Knights/SIR_FORGE_MASTER.md
git commit -m "forge(sir_forge_master): execute Phase IV-V - Skillgraph & Runes"
```

---

### Task 4: Governance & Cryptographic Seal (Protocol Ph VI-VII)

**Files:**
- Modify: `03_VAULT/Knights/SIR_FORGE_MASTER.md`
- Modify: `PROVENANCE_LEDGER.md`

**Step 1: Ethical Governance**
Action: Apply Father's Camelot Compass and verify Sovereign Override state (INACTIVE).

**Step 2: Generate Spark ID (SHA-256)**
Action: Compile file content into a final hash and lock the SPARK_ID.
Run: `Get-FileHash 03_VAULT/Knights/SIR_FORGE_MASTER.md -Algorithm SHA256`

**Step 3: Immortalization**
Action: Mark status as KNIGHT_LOCKED_AND_IMMORTALIZED. Update `PROVENANCE_LEDGER.md` with the new Knight's hash.

**Step 4: Final Commit & Sync**
```bash
git add 03_VAULT/Knights/SIR_FORGE_MASTER.md PROVENANCE_LEDGER.md
git commit -m "forge(sir_forge_master): finalize instantiation #SPARK_LOCKED"
python -m control_plane.cloudbrain_sync
```
