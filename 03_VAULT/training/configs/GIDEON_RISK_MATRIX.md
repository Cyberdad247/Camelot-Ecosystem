# GIDEON RISK MATRIX — 10 Shatterpoints of Disappointment
# Authority: Sir Gideon (Forensic Auditor) | Used by: //SCORPION rune | v400.1.0
# Updated: 2026-04-21 | Classification: INTERNAL — Iron Gate enforced

## PURPOSE
The 10 Shatterpoints are the catastrophic failure modes that //SCORPION cross-references
during any forensic audit. If this file is absent, //SCORPION is a dead rune.
Each Shatterpoint has: risk ID, severity, detection pattern, mitigation, and knight owner.

---

## SHATTERPOINT SP-01 — A2A NO RBAC (PRIVILEGE ESCALATION)
**Severity**: CRITICAL (P0)
**Description**: A2A JSON-RPC protocol has no native RBAC. Any agent that can reach
port 3001 can invoke any operation, including destructive ops and admin endpoints.
**Detection**: `grep -r "json-rpc\|a2a\|dispatch" control_plane/ | grep -v "rbac\|acl\|permission"`
**Blast Radius**: Full system compromise via rogue agent injection, lateral movement across knights.
**Mitigation**: `control_plane/rbac_matrix.py` + `access_matrix.json` + Anya `_stage_validate` ACL check.
**Owner**: Sir Sentinel | **Status**: PATCHED (//FORGE P0-C)

---

## SHATTERPOINT SP-02 — IRON GATE BYPASS (HITL SKIP)
**Severity**: CRITICAL (P0)
**Description**: Destructive ops (>10 net lines, >50MB deletion) executed without HITL approval.
Bypassing Iron Gate causes irreversible data loss and breaks Titanium Law #3.
**Detection**: Operations touching >10 files in one commit without `HITL_REQUIRED` log entry in PROVENANCE_LEDGER.
**Blast Radius**: Data loss, irreversible file/branch destruction, lost work.
**Mitigation**: `_stage_validate()` must set `iron_gate="HITL_REQUIRED"` for complexity>0.8. Never use `--no-verify`.
**Owner**: Sir Sentinel + Sir Boris | **Status**: ACTIVE — enforced by anya_gate.py

---

## SHATTERPOINT SP-03 — KINETIC PURITY VIOLATION (PYTHON OVER RUST/GO)
**Severity**: HIGH (P0)
**Description**: Python script used where compiled Rust/Go binary already exists (Saltare, Cribo, Rotel,
kinetic_edge). Python path adds latency, breaks L2_KINETIC purity, and wastes memory.
**Detection**: `grep -rn "subprocess.*python\|import subprocess" kinetic_edge/ | grep -v "test"` —
also: any new Python script that duplicates binary functionality.
**Blast Radius**: Latency regression (violates T8 voice sub-second), 8GB RAM ceiling risk, L2 degradation.
**Mitigation**: Check `rust-kinetic.md` binary table before any Python write. Cartridge enforcement: `KINETIC_STACK`.
**Owner**: Lukas_Omega | **Status**: ACTIVE — enforced by Titanium Law #1

---

## SHATTERPOINT SP-04 — VOXSERVICE RACE (MULTI-GPU ALLOCATION CONFLICT)
**Severity**: HIGH (T8)
**Description**: Multiple VoxService instances spawned simultaneously. Each grabs GPU memory.
On 8GB system this causes OOM crash and violates voice latency Law #8 (sub-second mandatory).
**Detection**: `ps aux | grep vox` showing >1 process | `logs/vox_service.log` showing duplicate init.
**Blast Radius**: GPU OOM crash, voice pipeline down, LiveKit stream broken, T8 violation.
**Mitigation**: VoxService must be singleton (check PID file at `/tmp/vox.pid` before spawn).
Enforced by: `voice-media.md` anti-patterns.
**Owner**: Sir Sonus | **Status**: ACTIVE — VoxService singleton pattern required

---

## SHATTERPOINT SP-05 — SQL INJECTION (UNPARAMETERIZED QUERIES)
**Severity**: CRITICAL (OWASP A03)
**Description**: Raw SQL string interpolation in any repository or route handler.
SQLAlchemy 2.0 text() bypass or f-string SQL in any module.
**Detection**: `grep -rn "f\"SELECT\|f'SELECT\|% .*SELECT\|format.*SELECT" control_plane/ 03_VAULT/ --include="*.py"`
**Blast Radius**: Full database exfiltration, data manipulation, CAMELOT credential theft.
**Mitigation**: SQLAlchemy ORM only. If raw SQL needed: `text()` with `:param` bindings. No exceptions.
**Owner**: Sir Sentinel | **Status**: ACTIVE — Titanium Law #5 + security.md enforcement

---

## SHATTERPOINT SP-06 — MISSING BRIEFINGSCRIPT ON LARGE OPS
**Severity**: HIGH (P0)
**Description**: Code generation touching >5 files or destructive ops run without an approved
BriefingScript (Titanium Law #10). Results in scope creep, regression, and unreviewed changes.
**Detection**: Git commits with >5 files changed where PROVENANCE_LEDGER has no `[BriefingScript]` entry.
**Blast Radius**: Unreviewed architectural changes, regression across modules, lost context.
**Mitigation**: `requires_briefing=True` in ValidationResult for complexity>0.7 + entities>5.
Anya must surface briefing requirement before any knight executes.
**Owner**: Sir Boris (Crucible Lead) | **Status**: ACTIVE — enforced by anya_gate.py VALIDATE stage

---

## SHATTERPOINT SP-07 — SWARM WITHOUT HARNESS IPC (DIRECT SPAWN)
**Severity**: HIGH
**Description**: Nano-Knight instances spawned directly (subprocess.Popen without harness_queue.jsonl IPC).
Bypasses SovereignHarness monitoring, disables apoptosis trigger, causes orphan processes.
**Detection**: `grep -rn "Popen\|subprocess.run" control_plane/ | grep -v "harness\|test"` — orphan PIDs.
**Blast Radius**: Orphan agent processes consuming RAM, no apoptosis on error_rate>5%, 8GB ceiling breach.
**Mitigation**: All Nano-Knight spawns must append to `logs/harness_queue.jsonl`. SovereignHarness polls every 2s.
**Owner**: Sir Boris | **Status**: ACTIVE — enforced by swarm-colony.md

---

## SHATTERPOINT SP-08 — MISSING ZOD VALIDATION (INJECTION AT API BOUNDARY)
**Severity**: HIGH (OWASP A03)
**Description**: Next.js API route or Server Action receives user data without Zod schema validation.
Allows malformed data, type confusion, and injection vectors into Supabase/Prisma.
**Detection**: `grep -rn "request.json()\|formData" 02_FORGE/ --include="*.ts" | grep -v "schema\|parse\|safeParse"`
**Blast Radius**: Database injection, type confusion crashes, unvalidated data persisted to Supabase.
**Mitigation**: Every API boundary uses Zod `.parse()` or `.safeParse()`. Schema defined in `/lib/schemas/`.
Enforced by: `nextjs.md` anti-patterns.
**Owner**: Sir Syntax | **Status**: ACTIVE — nextjs.md enforcement

---

## SHATTERPOINT SP-09 — SYNC DB IN ASYNC CONTEXT (EVENT LOOP BLOCKING)
**Severity**: HIGH
**Description**: Synchronous SQLAlchemy or requests call inside an `async def` FastAPI handler.
Blocks the asyncio event loop, serializes all requests, causes latency explosion under load.
**Detection**: `grep -B5 "db.execute\|requests.get\|requests.post" control_plane/ --include="*.py" | grep "async def"`
**Blast Radius**: All API endpoints serialize behind the blocking call — total throughput collapse.
**Mitigation**: SQLAlchemy 2.0 async sessions only (`AsyncSession`). HTTP via `httpx.AsyncClient`. No `requests`.
**Owner**: Sir Forge | **Status**: ACTIVE — python-api.md enforcement

---

## SHATTERPOINT SP-10 — MISSING SKILL BIBLE (KNIGHT HALLUCINATION)
**Severity**: HIGH (T5)
**Description**: Knight executes Titan Prompt without the corresponding Skill.md Bible loaded.
Results in hallucinated APIs, wrong conventions, anti-patterns introduced silently.
**Detection**: Anya ENRICH stage tag `SKILL_MISSING:*` in context_tags array. Brain Directory gap.
**Blast Radius**: Wrong framework patterns, deprecated APIs, anti-pattern propagation, Sir Gideon blind.
**Mitigation**: `.hive/skills/brain_directory.md` must be complete. ENRICH stage fails loudly on missing skill.
Lord Archivist GEP scan alerts on skill version mismatch.
**Owner**: Sir Boris + Anya_Omega | **Status**: PATCHED (//FORGE P0-A)

---

## //SCORPION AUDIT PROCEDURE

When `//SCORPION` is invoked, Sir Gideon executes:

```
FOR each Shatterpoint SP-01..SP-10:
  1. Run detection pattern (grep/scan command listed above)
  2. Score: CLEAR | WARN | CRITICAL
  3. If CRITICAL: iron_gate="BLOCKED" on current task until remediated
  4. Log finding to PROVENANCE_LEDGER with [SCORPION] tag
  5. Return GIDEON_RISK_SCORE (0-10 CRITICAL findings)
```

**Pass threshold**: GIDEON_RISK_SCORE ≤ 2 (max 2 WARN, 0 CRITICAL)
**Fail action**: REZERO — full task restart with remediation plan first

## MATRIX STATUS
- Total Shatterpoints: 10/10
- Status PATCHED: SP-01 (P0-C), SP-10 (P0-A)
- Status ACTIVE (enforced): SP-02, SP-03, SP-04, SP-05, SP-06, SP-07, SP-08, SP-09
- Last //SCORPION run: 2026-04-21 (//FORGE P0 completion)
