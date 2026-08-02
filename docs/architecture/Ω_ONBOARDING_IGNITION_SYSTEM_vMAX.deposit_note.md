# Ω_ONBOARDING_IGNITION_SYSTEM_vMAX — nuKG_Crystal Deposit Note

**Deposited:** 2026-07-23
**Evidence class:** `confirmed`
**Source message:**
```
anya please with Merlin forge a onboarding system for users to comprehensively ignite and operate camelot-os
```

## What this note is

Per AGENTS.md Universal Bootstrap and `harness.md`'s Evidence Gates, every proposed νKG_Crystal routed through the camelot local backplane must be classified into one of four evidence classes before treating it as operational state.

The deposition of `Ω_ONBOARDING_IGNITION_SYSTEM_vMAX` is **confirmed** because:
- The corresponding high-density `.toon` file has been written under `03_VAULT/UKG/Ω_ONBOARDING_IGNITION_SYSTEM_vMAX.toon` matching exactly 11 lines.
- Conformance unit tests have been added to `tests/test_onboarding.py` and run successfully.
- It is successfully registered in the active memory mesh via `FirnFlow`.

## Architectural Feedback & Analysis

### 1. Interactive Diagnostic System
This configuration implements the onboarding system:
- **Python server backend**: [bin/onboarding.py](file:///C:/Users/vizio/CAMELOT_OS/bin/onboarding.py) spins up a local diagnostics server on port `8099`, querying host compiler states, active virtual envs, Appwrite bindings, and VFS status.
- **Vanilla web interface**: [onboarding.html](file:///C:/Users/vizio/CAMELOT_OS/onboarding.html) features:
  - Interactive stepper mapping the exact sequence: Diagnostics -> Cartridge -> VFS -> System Ignition.
  - Diagnostics status grid showing live/cached system states.
  - Interactive terminal simulator supporting runic commands (`//BOOT`, `//STATUS`, `//PLAN`, `//HELP`).

— Engineering Feedback (AGENTS.md → docs/architecture/)
