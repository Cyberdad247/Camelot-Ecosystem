# CUA (Computer-Use Agent) — REYA Fabric Integration
## Assimilation of `trycua/cua` into CAMELOT-OS

The CUA module integrates the high-performance OS-level input automation patterns of [trycua/cua](https://github.com/trycua/cua) into the **REYA Universal Knight Fabric Layer**.

### Components:
- `CUA_REYA_SPEC.md`: Architectural specification and Northstar goal.
- `cua_driver_bridge.py`: Core driver implementing normalized coordinate mapping (`[0.0, 1.0]`), mouse/keyboard execution, screenshot capture/diffing, and Sir Sentinel capability lease protection.
- `03_VAULT/runtime_state/open_notebook/vkg_crystals/vkg_cua_nexus.json`: Associated νKG knowledge crystal.

### Key Capabilities:
1. **Unified Coordinate Grounding**: `(x, y)` in `[0.0, 1.0]` seamlessly targeting Cybertronia Windows/Linux desktop and Excalibur Galaxy S26 Ultra mobile screens.
2. **Sentinel Safety Leases**: Strict bounding box isolation and red zone quarantine to protect credentials and critical OS assets.
3. **Voice-Driven Duplex Execution**: Channeled Knights (Merlin, Boris, Codex, Lukas) can narrate actions while real-time barge-in allows sub-30ms voice cancellation.
4. **S1 Reflex Macros**: Micro-action sequences execute locally without heavy LLM latency (<50ms per step).
