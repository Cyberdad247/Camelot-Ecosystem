# Verification & Governance Gate — v10001.00-CYBERTRONIA
@ctx|camelot-os.dev/ukg/v10001/verification @typ|Quality_Verification_Protocol id|Ω_VERIFY_V10001

## 🛡️ Sovereign Verification Protocol (Evidence Before Assertions)

Every architectural migration, code mutation, and hypermedia deployment must pass the following 5 verification checkpoints before state transition is acknowledged under `⚜️_SOVEREIGN_TRUTH`:

---

### Checkpoint 1: Hardware Scarcity & Edge RAM Boundary
* **Command**: `.venv\Scripts\python.exe -m control_plane.infra.agent_slab_sync --status`
* **Invariants**:
  - `CYBERTRONIA_IS_EDGE_NODE == True`
  - `process_rss_mb < 480.0 MB` (Active allocation floor)
  - `system_used_mb <= 4096.0 MB` (Edge node budget ceiling)
  - `heaviside_gc_trigger == 3686.4 MB` (90% ceiling interrupt)
* **Pass Criteria**: `edge_ceiling_exceeded == False`.

---

### Checkpoint 2: IPC Shared Slabs & Concurrency Assurance
* **Command**: `.venv\Scripts\python.exe -m pytest tests/control_plane/test_agent_slab_sync.py -x -q`
* **Invariants**:
  - All 6 canonical slabs present: `local_env.md`, `system_instructions.md`, `Agents.md`, `Skills.md`, `Swarm.md`, `workflows.md`.
  - Atomic exclusive locks prevent concurrent write collisions.
  - Stale locks held by deceased PIDs automatically reclaimed within $30\text{s}$.
  - Zero-copy `mmap` reads return valid bytes without disk contention.
* **Pass Criteria**: 7/7 tests passing with exit code 0.

---

### Checkpoint 3: Canonical HTMX 2-Strand Semantic & A11y Gate
* **Reference**: Canonical specification at `https://htmx-docs.vercel.app/`
* **Invariants**:
  - All dynamic fragment targets specify `aria-live="polite"`.
  - No client-side JavaScript state management (Redux, Zustand, MobX == NULL).
  - Hypermedia responses return pure semantic HTML snippets (not raw JSON payloads).
  - Color styling complies with Obsidian Void (`#050505`), Cinzel serif typography, and Luxora Gold (`#D4AF37`) accents.
* **Pass Criteria**: `render_htmx_status_fragment()` validates against DOM parsing and CSS token schema.

---

### Checkpoint 4: Squire Colony Codebase & Privacy Triage
* **Command**: `.venv\Scripts\python.exe -m squires.colony status`
* **Invariants**:
  - File index: `11,953+` files indexed with symbols mapped.
  - PageKeeper compliance: Node compliance reports `Ceiling 4096 MB — PASS`.
  - GHOST air-gap: Zero plain-text credentials written to git-tracked files.
* **Pass Criteria**: Zero untracked critical leaks in active working branch.

---

### Checkpoint 5: Worktree & Provenance Ledger Audit
* **Command**: `.venv\Scripts\python.exe scripts/sync_provenance.py --check`
* **Invariants**:
  - Root `PROVENANCE_LEDGER.md` is strictly authoritative.
  - 6 tracked mirrors reconcile upon staging.
  - Worktree `C:\Users\vizio\camelot-wt\trunk` remains on `main` branch with clean git tree.
* **Pass Criteria**: No corrupted ledger hashes; worktrees unpolluted.
