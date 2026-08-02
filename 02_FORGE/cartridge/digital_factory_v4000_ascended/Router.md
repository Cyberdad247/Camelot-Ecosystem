# V4000 OMNI-ROUTER: THE 14TH LAYER TRANSCENDENCE
*Any task not listed in this router must be returned to the root.*

## COGNITIVE CARTRIDGE COUNCIL (ROUTING GATES)

1. **STATE & PERSISTENCE -> Route to: `/Merlin_Ω/Agent.md`**
   * *Domain:* Zero-Copy Memory-Mapped (mmap) SQLite with WAL2.
   * *Directive:* Use this node for crash-proof, instantaneous data storage. Pydantic AI contracts must serialize via MsgPack directly into memory-mapped pages.

2. **LOGIC, MATH & COMPILATION -> Route to: `/Sir_Codex/Agent.md`**
   * *Domain:* WASM Polyglot Sandboxing.
   * *Directive:* Use this node to compile Rust, Go, or Python (via Wizer) directly into WASM components. Ensure memory remains strictly capped at 64MB per WASM linear memory instance.

3. **EXECUTION & KINETICS -> Route to: `/Lukas/Agent.md`**
   * *Domain:* Actor-Model Concurrency (Lunatic/Actix pattern).
   * *Directive:* Route here for isolated WASM Actor communication via lock-free ring buffers (ZeroClaw IPC v2). Use this node for Speculative DAG Pre-warming (predicting the next 3 execution steps).

4. **INTERFACE & UX -> Route to: `/Sir_Bard/Agent.md`**
   * *Domain:* WASM-native UI components.
   * *Directive:* Bypass JS-heavy DOM manipulation entirely. Generate UI via Dioxus/Leptos locked to the Sovereign's aesthetic (Obsidian #050505, Luxora Gold #D4AF37, Royal Purple) at 120fps.

5. **HYPERVISOR & SYSTEM INTEGRITY -> Route to: `/Anya_Ω/Agent.md`**
   * *Domain:* WASI Capability Handles & Pydantic AI Contracts.
   * *Directive:* see `/Anya_Ω/Agent.md` for the full directive body.

---

## 📋 ROUTER AUDIT OVERLAY *(additive; does not alter the user-supplied spec above)*

* **Item 1 (Merlin Ω) — WAL2.** Per evidence-class `rejected` from the v1 audit, `journal_mode = "wal2"` is not yet implemented in upstream `rusqlite` 0.31/0.32 + the bundled SQLite C library. Use `journal_mode = "WAL"`. Full corrigendum in `/Merlin_Ω/Agent.md`.
* **Item 3 (Lukas) — ZeroClaw IPC v2.** Per evidence-class `aspirational`, ZeroClaw IPC v2 is not wired in `Cargo.lock` today. The live equivalent is the `control_plane/harness.py` jsonl queue plus `02_FORGE/KINETIC_ARMORY/edge-router/edge-router.ts` (TOON_v2_diff wire protocol). Use those until ZeroClaw v2 ships. Full corrigendum in `/Lukas/Agent.md` and `/skills/Speculative_Pre_Warming.md`.
* **Path notation:** all paths are relative to repo root unless prefixed with `/`.
