# SKILL: Speculative DAG Pre-warming (Lukas Node)

**Trigger:** When the execution DAG requires parallel processing or cold starts.

**Process:**
1. Analyze the current execution branch.
2. Predict the next 3 execution steps required by the Sovereign's prompt.
3. Pre-compile the required WASM modules *before* the Omni-Router requests them.
4. Load into ZeroClaw IPC v2 ring buffers to drop cold starts from milliseconds to nanoseconds.
5. Upon completion, append the status to the local Memory log and return to `Router.md`.

---

## 📋 SKILL AUDIT OVERLAY *(additive; does not alter the user-supplied spec above)*

* **Step 4 — ZeroClaw IPC v2 ring buffers.** Per evidence-class `aspirational`, ZeroClaw IPC v2 is *not* yet wired in `Cargo.lock`. The live Camelot edge-wire equivalent is `control_plane/harness.py` (jsonl queue) plus `02_FORGE/KINETIC_ARMORY/edge-router/edge-router.ts` (TOON_v2_diff). Reuse those surfaces until ZeroClaw v2 lands.
