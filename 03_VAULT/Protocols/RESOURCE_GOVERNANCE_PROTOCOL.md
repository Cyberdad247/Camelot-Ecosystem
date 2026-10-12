# ⚖️ PROTOCOL: RESOURCE_GOVERNANCE (Law 03)
**[STATUS]:** SOVEREIGN_LAW  
**[CLASSIFICATION]:** HARD_RESOURCE_CONSTRAINT  
**[ENFORCEMENT]:** AUTOMATIC_JOB_OBJECTS / VFS_PRESSURE / TELEMETRY_AUDIT  

---

## 1. System Intent & Scope
This protocol codifies the foundational memory law across all nodes and server infrastructure within the Camelot-OS ecosystem. Due to strict physical hardware topologies (such as 8GB DDR5 host platforms) and distributed mesh scalability, memory consumption is bifurcated into two mutually exclusive allocation classes:
1. **Camelot-OS Node (Worker / Edge / Daemon / Agent Runner):** Hard upper ceiling of **4 GB RAM (4096 MB)**.
2. **Camelot-OS Sovereign Server (Central Hub / Bifrost Gateway / Core DB):** Hard upper ceiling of **8 GB RAM (8192 MB)**.

---

## 2. Topology Allocation Boundaries

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        CAMELOT-OS MEMORY LAW                           │
├───────────────────────────────────┬────────────────────────────────────┤
│   Camelot-OS Node (Edge / Worker) │   Camelot-OS Server (Central Hub)  │
│   Ceiling: 4096 MB (4 GB MAX)     │   Ceiling: 8192 MB (8 GB MAX)      │
├───────────────────────────────────┼────────────────────────────────────┤
│ • Edge drones (WASM/Voice/Pill)   │ • Central Bifrost Gateway (WS:3001)│
│ • Local VFS & Janitor daemons     │ • Sovereign Vector & Relational DB │
│ • Squire colony background sweeps │ • Multi-Agent Aggregation Bus      │
│ • Knight REPL & Persona executors │ • Global State Reconciliation      │
│ • Client PWA & Browser sessions   │ • High-dimensional Token Buffers   │
└───────────────────────────────────┴────────────────────────────────────┘
```

---

## 3. Operational Rules

### 3.1 Node Constraints (≤ 4096 MB)
- No individual worker process, containerized drone, or aggregated node group may exceed 4096 MB working set.
- **Preemptive Pressure Relief:**
  - **70% Threshold (2867 MB):** Background file caching in VFS transitions to direct I/O.
  - **85% Threshold (3481 MB):** Non-essential cache structures, intermediate AST nodes, and unreferenced embeddings are flushed immediately. Working set trimming (`EmptyWorkingSet` via `psapi.dll`) is triggered.
  - **95% Threshold (3891 MB):** Hard kill / task suspension of non-critical background jobs to prevent OS-level out-of-memory (OOM) aborts.

### 3.2 Server Exemption (≤ 8192 MB)
- Only the designated **Primary Hub / Server** running aggregated database layers (PostgreSQL / Qdrant / Prisma), cross-node Bifrost message routing, and centralized LLM inference buffers may operate within the 8192 MB window.
- The server node must continuously monitor its heap and enforce compaction to ensure no leak spills beyond 8 GB into host swap thrashing.

---

## 4. Telemetry and HUD Requirement
Every Camelot-OS agent response HUD must reflect compliance with this law:
```text
Telemetry on Resources: CPU: <used>% | RAM: <used_mb>MB / 4096MB [NODE]  (or 8192MB [SERVER])
```

---

## 5. Automated Verification
The enforcement script located at [`scripts/ops/check_ram_governance.py`](file:///C:/Users/vizio/CAMELOT_OS/scripts/ops/check_ram_governance.py) audits compliance:
- Validates system working sets against node (4GB) or server (8GB) profiles.
- Emits exit code `0` on compliant state, or triggers defensive working set flushes if approaching boundaries.
