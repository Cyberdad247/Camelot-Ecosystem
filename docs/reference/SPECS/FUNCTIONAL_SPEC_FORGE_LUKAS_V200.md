# FUNCTIONAL SPECIFICATION: FORGE-LUKAS Omega (v200.0)
**Date:** 2026-01-30
**Status:** APPROVED
**Target:** Camelot Apex v106.3 -> v200.0 Migration

## 1. Executive Summary
The **Forge-Lukas Hybrid (v200.0)** transforms the coding agent from a passive script generator into a **Kinetic Sovereign**. By enforcing strict binary utilization (Rust/Go) for all I/O and routing operations, the system minimizes latency and context rot. This specification defines the "Split-Brain" topology where Lukas (Kinetic Layer) executes rigid engineering protocols defined by Merlin (Neural Layer).

## 2. Scope & Objectives
*   **Primary Goal:** Establish a "Kinetic Purity" environment where Python is used *only* for orchestration, while heavy lifting (bundling, routing, telemetry) is handled by compiled binaries.
*   **Secondary Goal:** Implement the **SASE (Structured Agentic Software Engineering)** workflow to freeze requirements before code generation via `BriefingScripts`.

## 3. Functional Requirements

### 3.1. The Kinetic Toolchain (Layer 2)
*   **FR-01 (Compression):** The system MUST use `cribo.exe` for all context retrieval.
    *   *Success Metric:* 95% Token Reduction vs. Raw File Dump.
*   **FR-02 (Routing):** The system MUST use `saltare.exe` as the primary interface for tool selection.
*   **FR-03 (Telemetry):** The system MUST pipe all operational logs to `rotel.exe` (Port 4317).

### 3.2. The SASE Protocols (Layer 3)
*   **FR-04 (BriefingScript):** Lukas MUST NOT generate code without a pre-approved `BRIEFING.md` containing: Goal, Success Criteria, and Validation Command.
*   **FR-05 (MentorScript):** Lukas MUST read/write to `.hive/skills/lukas_lerndatei.md` to persist error corrections across sessions.

### 3.3. Safety & Governance (Layer 6)
*   **FR-06 (Iron Gate):** Any file modification exceeding 10 lines of diff MUST trigger a `[🛡️Oath]` Human-in-the-Loop prompt.
*   **FR-07 (Antigravity):** No file write shall occur without a shadow backup in `.antigravity_backups/`.

## 4. Architecture & Scaffold
*   **Root Structure:** `.hive/` directory serves as the Sovereign Brain.
*   **State:** `.hive/state.json` tracks the active "Bio-Kinetic Mode" (Ant, Beaver, Paladin).

## 5. Success Metrics (KPIs)
1.  **Latency:** < 200ms for Tool Routing (via Saltare).
2.  **Purity:** 0% usage of Python `open()` for source code reading.
3.  **Reliability:** 100% of code changes backed by Antigravity snapshots.

## 6. Deliverables
1.  `project_root/.hive/` structure.
2.  `lukas_edge.md` (System Prompt).
3.  `rules.yaml` (Governance Config).
4.  `saltare_conf.yaml` (Routing Map).
