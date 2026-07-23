
---

## [2026-07-23] Version v1.0.0 - Fix subprocess shell injection in QR Pill Orchestrator

**Status:** SECURITY FIX
**Hash:** 0x195fef765b61a5a5
**Actor:** Jules

### 🛡️ Atomic Commit
- **Action:** Modified qr_pill_orchestrator.py to replace shell=True with shell=False and used shlex to safely parse command arguments.
