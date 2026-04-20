# NANO-KNIGHTS MANUAL (v2.0)
**Status:** ACTIVE
**Commander:** Kai "Forge" Zhang

## Overview
Nano-Knights are lightweight, kinetic binaries or scripts designed for specific, low-latency tasks. They bypass the heavy reasoning of the Core Kernel to execute "muscle memory" operations.

## The Phial Roster

### 1. Nano-Forge (`nano_forge`)
*   **Role:** Code Scaffolding & Patching.
*   **Trigger:** `//FORGE`, `[🔧🌐]`
*   **Capabilities:**
    *   AST-aware editing.
    *   Context-free file creation.

### 2. Nano-Browser (`nano_browser`)
*   **Role:** Headless UI Verification.
*   **Trigger:** `//TEST_UI`, `[🖱️👀]`
*   **Capabilities:**
    *   Navigates to URL.
    *   Inspects DOM for selectors/text.
    *   Simulates clicks/inputs.
    *   Returns strictly structured JSON findings.

### 3. Nano-Scan (`nano_scan`)
*   **Role:** Secret & Security Audit.
*   **Trigger:** Pre-Commit Hook, `[🛡️🔐]`
*   **Capabilities:**
    *   Regex-based PII detection.
    *   Entropy analysis for API keys.

### 4. Nano-MCP (`nano_mcp_gen`)
*   **Role:** Tool Factory.
*   **Trigger:** `//MCP_IFY`, `[🔧🌐]`
*   **Capabilities:**
    *   Wraps directory in MCP Server boilerplate.
    *   Exposes functions as tools.

## L7: The Ethereal Interface (Anya)
**Trigger:** `//ANYA`, `[🎭✨]`

### 1. Mobile PWA
*   **Access:** `localhost:3000` (via Saltare Tunnel).
*   **Features:**
    *   **Live HUD:** Mirrors the Terminal HUD.
    *   **Voice Mode:** Push-to-talk with Anya.

### 2. Voice (Vox Anima)
*   **Engine:** Kokoro (Local) / OpenAI (Cloud).
*   **Latency:** Optimized for <200ms.

### 3. Vibe Engine
*   **Logic:** Modulates UI colors and Response tone.
*   **States:**
    *   🟢 **Zen:** Low Load, Playful.
    *   🟡 **Focus:** Medium Load, Concise.
    *   🔴 **Crisis:** High Load/Error, Urgent.

### 5. Sir Ears (`nano_ears`)
*   **Role:** Kinetic Hearing.
*   **Trigger:** `//EARS`, `[👂]`
*   **Capabilities:** Local Whisper STT (Speech-to-Text).

### 6. Merlin's Eye (`merlin_eye`)
*   **Role:** Vision Pipeline.
*   **Trigger:** `//LOOK`, `[👁️]`
*   **Capabilities:** LLaVA Image Analysis.

### 7. Chronos Gate (`chronos_gate`)
*   **Role:** Temporal Scheduler.
*   **Trigger:** `//SCHEDULE`, `[⏳]`
*   **Capabilities:** Cron-based task execution.

## Protocol: The Swarm
To deploy the knights:
1.  **Command:** `//FLEET "Task"` or `hive swarm "Task"`
2.  **Orchestrator:** `swarm_trigger.ps1`
3.  **Execution:** Parallel jobs via PowerShell/Bash.
