# 2026-06-22: CAMELOT-OS TUI Launcher Design Document

**Status:** APPROVED | **Author:** MERLIN_Ω (Kernel Intelligence) | **Sovereign:** Vashawn O. Head (Vizion)

---

## 1. Objective

Provide a lightweight, high-performance Terminal User Interface (TUI) command launcher for Camelot-OS. The launcher simplifies typing repetitive runic commands by presenting an interactive, keyboard-navigated dashboard.

## 2. Architecture & Layout

The TUI is implemented in **Go** using the **Bubble Tea** framework. It compiles to a standalone, zero-dependency executable (`cos-tui.exe`) conforming to the v1000 edge-node constraint.

### UI Structure

```
+───────────────────────────────────────────────────────────────+
| [⚡] CAMELOT-OS APEX TUI LAUNCHER             [Kernel: Active] |
+───────────────────────────────────────────────────────────────+
| Select a Runic Command to Execute:                            |
|                                                               |
|  [ ] //BOOT         (Rehydrate session & UKG memory)          |
|  [>] //STATUS       (Probe active ports & service health)     |
|  [ ] //HEAL         (Execute test self-repair loops)          |
|  [ ] //SWARM        (Launch parallel swarm crusades)          |
|  [ ] //NANO_SWARM   (Expand and rehydrate UKG nodes)          |
|                                                               |
+───────────────────────────────────────────────────────────────+
| Argument Input (Press Esc to cancel):                         |
| > _                                                           |
+───────────────────────────────────────────────────────────────+
| System Logs & Output:                                         |
| [18:46:58] Kernel sync initiated.                             |
+───────────────────────────────────────────────────────────────+
| [Enter] Run  |  [r] Refresh  |  [q] Quit  |  [Esc] Cancel     |
+───────────────────────────────────────────────────────────────+
```

### Components
1. **Header Panel:** System status, active branch, and `MORGANA_BIFROST_GATEWAY` online checks.
2. **Command Selector:** Key-navigated selection lists of standard runic commands.
3. **Dynamic Prompt Input:** Gated text input for command-line arguments.
4. **Console Output:** Non-blocking async stdout/stderr streaming from execution.

---

## 3. Data & Execution Flow

1. **Subprocess Invocation:** Select command ➔ spawn `os/exec` background runner:
   `python -m control_plane.runic_router --rune <RUNE> --task "<argument>"`
2. **Output Capture:** Concurrently stream standard output and error buffers. Dispatch updates using Go channels directly to the model state loops (`tea.Msg`).
3. **Gateway Probe:** Execute asynchronous TCP connection check to `127.0.0.1:8001` every 10 seconds.

---

## 4. Design Aesthetics
* **Theme:** Obsidian (`#000000`) backgrounds with Luxora Gold (`#D4AF37`) border highlights.
* **Typing:** Strict key binding mappings (`q` to quit, `enter` to run, `esc` to reset input).
