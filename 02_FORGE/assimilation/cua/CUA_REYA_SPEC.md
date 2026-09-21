# CUA (COMPUTER-USE AGENT) REYA INTEGRATION SPECIFICATION
## v10001.00-CYBERTRONIA — trycua/cua Assimilation Protocol
@ctx|camelot-os.dev/ukg/v10001/cua_reya @typ|Sovereign_Assimilation_Spec id|Ω_CUA_REYA_NEXUS

---

## 1. Executive Summary & Prime Directive

This specification integrates key architectural patterns from **trycua/cua** into Camelot-OS's **REYA Universal Fabric Layer** (`02_FORGE/assimilation/reya/reya_fabric_layer.py`).

By synthesizing CUA's core capabilities:
1. **`cua-driver`**: Cross-platform OS-level input actuation (mouse, keyboard, scroll, drag, hotkeys, screen capture).
2. **`cua-s1`**: Local System 1 reflex decision loop for micro-actions without expensive LLM token round-trips.
3. **`cua-fleets`**: Multi-environment sandboxed execution (local OS, containerized desktop, remote VM).
4. **`cua-bench`**: Closed-loop state verification via visual screenshot diffing and bounding box validation.

We establish the **Northstar Goal for the REYA Fabric Layer**:
> **"Universal Sovereign Computer-Use Agent (CUA) Fabric — Unifying Duplex Voice Guidance, Normalized Cross-Platform Actuation (Desktop + Mobile), and System 1 Reflex Execution under Sentinel Safety Leases (<350MB RAM, sub-50ms action loop)."**

---

## 2. Feedback & Assimilation Analysis of `trycua/cua`

### Strengths Extracted
- **Open-Source MIT Foundation**: Unlike closed, proprietary computer use APIs (e.g., Anthropic Computer Use API, OpenAI operator), `trycua/cua` provides an unencumbered, developer-owned driver layer.
- **Dual-Speed Reasoning (`cua-s1`)**: Separates slow deliberative planning (System 2) from rapid mechanical actuation (System 1), cutting action latency from seconds to milliseconds.
- **Decoupled Architecture**: Clean separation between input driver (`cua-driver`), fleet management (`cua-fleets`), and evaluation benchmarking (`cua-bench`).
- **High-Performance Rust Core**: Native OS mouse/keyboard event injection with zero python GIL contention.

### Sovereign Gaps Addressed in CAMELOT-OS
1. **Absence of Real-Time Voice Duplex**:
   - `trycua/cua` is text/script driven. CAMELOT-OS binds CUA directly to **Omni S2S** and **Multivoice Interchange**, enabling hands-free voice directing ("Reya, click the blue export button") and instant barge-in cancellation ("Stop! Don't click that!").
2. **Missing Sentinel Security Boundaries & Capability Leases**:
   - Raw OS drivers can click any coordinate on the screen. CAMELOT-OS wraps all CUA actuation in **Sir Sentinel Capability Leases** (AgentArmor Z3 bounds, red-zone quarantine for credential fields and system-critical buttons, HITL gate triggers for unverified destructive actions).
3. **Desktop-Only vs Unified Cross-Platform (Desktop + Mobile)**:
   - `trycua/cua` focuses on macOS/Linux desktop sandboxes. CAMELOT-OS unifies Desktop OS (Windows / Linux) and Mobile (Android Galaxy S26 Ultra via Excalibur QtScrcpy / ADB) into a single **Normalized Coordinate Space** (`[0.0, 1.0]`).
4. **Edge Memory Footprint Compliance**:
   - `trycua/cua` fleet provisioning can consume gigabytes of RAM. Camelot's CUA bridge enforces strict **Rule 7 edge compliance (<350MB RAM ceiling)** using direct OS win32/uinput calls and shared memory frame buffers.

---

## 3. The 4-Pillar Architecture

```
                    ┌─────────────────────────────────────────────────────────┐
                    │            VOICE & RUNIC DISPATCH INGRESS               │
                    │  - Realtime Omni S2S ("Reya, click the run button")      │
                    │  - Runic Router (//CUA, //REYA_ACT, //FORGE)            │
                    │  - Channeled Knight (Boris, Codex, Lukas, Arthur)        │
                    └───────────────────────────┬─────────────────────────────┘
                                                │
                                                ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │         SIR SENTINEL CAPABILITY LEASE GATE              │
                    │  - Bounded Execution Rectangles (App window sandbox)    │
                    │  - Red Zone Quarantine (Password, CreditCard, System)   │
                    │  - Iron Gate HITL Escalation (Risk >= 50)               │
                    └───────────────────────────┬─────────────────────────────┘
                                                │ Verified Safe Coordinates
                                                ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │          UNIFIED GROUNDED COORDINATE TRANSLATOR         │
                    │  - Normalized Space: (nx, ny) in [0.0, 1.0]             │
                    │  - Target Desktop: Res (W_d, H_d) -> Physical Pixels     │
                    │  - Target Mobile:  Res (W_m, H_m) -> ADB / QtScrcpy Tap │
                    └───────────────────────────┬─────────────────────────────┘
                                                │
                                                ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │               CUA DRIVER BRIDGE & S1 ENGINE             │
                    │  - mouse_click, mouse_drag, mouse_scroll                │
                    │  - keyboard_type, key_press, hotkey                     │
                    │  - S1 Reflex Macro Execution (<50ms execution)          │
                    │  - Screen Capture & State Diff Verification             │
                    └───────────────────────────┬─────────────────────────────┘
                                                │
                                                ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │            GLASS OBSERVATORY WORM TAP                   │
                    │  - Actions transcribed into LIVING_COMPENDIUM.md        │
                    │  - Zero hotpath contention; Knight XP awarded           │
                    └─────────────────────────────────────────────────────────┘
```

---

## 4. Supported Action Primitives

| Action Primitive | Parameters | Description |
| :--- | :--- | :--- |
| `mouse_click` | `norm_x, norm_y, button="left", clicks=1` | Clicks normalized coordinate on target display |
| `mouse_double_click`| `norm_x, norm_y, button="left"` | Double-clicks normalized coordinate |
| `mouse_move` | `norm_x, norm_y` | Moves cursor smoothly to normalized position |
| `mouse_drag` | `start_x, start_y, end_x, end_y, button="left"` | Performs drag-and-drop gesture |
| `mouse_scroll` | `dx, dy` | Emits horizontal or vertical scroll units |
| `keyboard_type` | `text, delay_ms=10` | Types character sequence with optional keystroke delay |
| `key_press` | `key` | Presses and releases single key (e.g., `Return`, `Tab`, `Escape`) |
| `hotkey` | `keys=["ctrl", "c"]` | Presses simultaneous hotkey combo |
| `screen_capture` | `target="desktop|mobile", bounding_box=None` | Captures viewport screenshot buffer |
| `screen_diff_verify`| `pre_hash, post_hash, min_delta_pct=0.01` | Verifies visual state transition after action |
| `cua_s1_chain` | `actions=[...]` | Executes rapid sequence of micro-actions (<50ms loop) |

---

## 5. Security & Sentinel Guardrails

1. **Capability Leases (`SentinelLease`)**:
   - Every CUA session requires an active lease specifying allowed bounding rectangles `(min_x, min_y, max_x, max_y)` and target device (`desktop` or `mobile`).
2. **Red Zones**:
   - Designated areas on screen (e.g. browser password managers, bank login screens, OS credential prompts) are marked red zones. Any action targeting a red zone throws `SentinelViolationError` and halts the action.
3. **Emergency Interruption (Barge-In)**:
   - Omni S2S VAD barge-in triggers immediate termination of any in-flight S1 action chain in <30ms.
