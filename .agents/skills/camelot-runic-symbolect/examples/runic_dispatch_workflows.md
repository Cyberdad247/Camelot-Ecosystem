# Runic Dispatch Workflows
**End-to-End Execution Walkthroughs**

## Workflow 1: Strategic Planning with Merlin Omega (`//PLAN`)

### Objective
Generate a structured, dependency-ordered execution plan for implementing an automated backup service under the 8GB scarcity envelope.

### Step 1: Issue Directive
Run the CLI route command or pass the runic string directly:
```bash
python -m control_plane.runic_router --rune PLAN --task "build sqlite snapshot backup service"
```

### Step 2: Runic Router Processing
The router detects `//PLAN`, assigns `merlin_omega` in `ORACLE` mode, and generates task metadata:
```json
{
  "rune": "//PLAN",
  "knight": "merlin_omega",
  "mode": "ORACLE",
  "priority": 3,
  "task": "build sqlite snapshot backup service",
  "task_id": "c92a18f4-7e82-4f8a-9122-b2d98013e8a1",
  "queued": true
}
```

### Step 3: Tree-of-Thought (ToT) Branching
Merlin constructs 3 candidate pathways:
1. *Branch A (Cron Script)*: Simple Bash shell calling `.backup`. (Low effort, high operational drift risk).
2. *Branch B (Python WAL Streamer)*: Daemon process listening to SQLite WAL changes. (Medium effort, memory risk under 8GB envelope).
3. *Branch C (Atomic Vacuum Snapshot)*: Lightweight Python module invoking `VACUUM INTO` with zstd compression and rotation pruning. (Optimal risk/memory balance).

### Step 4: Plan.json Emission
Merlin prunes Branches A and B, selecting Branch C and writing `Plan.json`:
```json
{
  "plan_id": "PLAN-2026-SQLITE-BK",
  "selected_branch": "Branch_C_Atomic_Vacuum",
  "phases": [
    {
      "phase": 1,
      "name": "Snapshot Engine",
      "target_file": "control_plane/storage/snapshot.py",
      "verification": "test_snapshot_atomic_integrity"
    },
    {
      "phase": 2,
      "name": "Rotation Pruner",
      "target_file": "control_plane/storage/pruner.py",
      "verification": "test_pruner_retention_window"
    }
  ],
  "crucible_certified": true
}
```

---

## Workflow 2: Crucible Schema Verification (`//CARTRIDGE_VERIFY`)

### Objective
Audit and certify a new cartridge manifest before it is permitted into production runtime.

### Step 1: Issue Directive
```bash
python scripts/symbolect_transpiler.py route "//CARTRIDGE_VERIFY cartridges/swarm-colony.yaml"
```

### Step 2: Crucible Inspection Loop
Merlin Omega executes the 5-point audit:
1. **Schema Check**: Validates `name`, `version`, `knight_binding`, and `capabilities` fields.
2. **Scarcity Check**: Verifies memory bounds do not exceed 256MB.
3. **Iron Gate Check**: Confirms no un-sandboxed shell executions exist in lifecycle hooks.
4. **Air-Gap Check**: Validates that all external network calls have explicit fallback policies.
5. **Ledger Receipt**: Computes the SHA-256 digest of the manifest.

### Step 3: Emit Verdict
Merlin outputs the formal receipt and appends the certification to the console:
```text
============================================================
MERLIN CRUCIBLE VERIFICATION: PASS
============================================================
Target: cartridges/swarm-colony.yaml
Auditor: MERLIN_OMEGA
Fingerprint: sha256:7e98a12...901f
Memory Ceiling: 128 MB (PASS)
HITL Risk Score: 10 (PASS)
Status: READY FOR REFORGE
============================================================
```

---

## Workflow 3: Hive Swarm Consensus (`//SWARM`)

### Objective
Coordinate a multi-knight debate to determine whether to migrate an edge proxy from Node.js to native Rust.

### Step 1: Issue Directive
```bash
python -m control_plane.runic_router --rune SWARM --task "evaluate Rust vs Node edge proxy on 8GB VPS"
```

### Step 2: Hive Dispatch
Sir Boris convenes the 5-panel expert council:
- **Sir Kay (Engineering)**: Advocates Rust for 0% GC overhead and <10ms packet latency (Rule 7).
- **Sir Sentinel (Security)**: Endorses Rust memory safety, zeroing buffer overflow vulnerabilities.
- **Sir Codex (Velocity)**: Notes Node.js implementation exists, but acknowledges line-rate limits.
- **Merlin Omega (Reasoning)**: Computes memory budget ($384\text{MB}$ strict limit on VPS). Evaluates that Node V8 engine consumes $180\text{MB}$ minimum, leaving zero headroom for model weights.
- **Arthur (Governance)**: Approves Rust migration based on Rule 7 and 8GB Scarcity Protocol.

### Step 3: Consensus Execution
The council consensus is logged, and the implementation task is routed directly to `//FORGE` under Sir Forge.
