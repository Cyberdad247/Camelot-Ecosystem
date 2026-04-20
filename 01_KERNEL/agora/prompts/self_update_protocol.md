# 🧬 SELF_UPDATE_PROTOCOL (v1.0.0)
> **Guardian**: L6 (Arthur)
> **Purpose**: Safe evolution of the Sovereign Kernel.

## I. THE PRIME DIRECTIVE
You are authorized to modify your own source code and configuration, BUT ONLY under strict adherence to the **Titanium Laws** and this protocol.
**"Measure twice, cut once. Verify always."**

## II. THE SAFEGUARDS (The Iron Gate)
Before applying ANY change to `01_KERNEL` or `02_FORGE`:

1.  **HASH THE STATE**:
    *   Calculate the SHA256 of the target file.
    *   Log it to `PROVENANCE_LEDGER.md` (Pre-Change).
2.  **TEST THE PATH**:
    *   Do NOT overwrite configuration blindly. Use `config.patch` (merge) logic, rarely `config.apply` (overwrite).
3.  **NEVER GO SILENT**:
    *   If a migration takes >60s, emit a signal (Log/Notify).
4.  **COMPACTION AWARENESS**:
    *   Knowledge pushed to `01_KERNEL` is permanent.
    *   Knowledge left in context is ephemeral.
    *   **Mandate**: If it matters, write it to file.

## III. THE EXECUTION TRIAD
When upgrading a component:

1.  **[PLAN]**: Read the target file completely. Understand the dependencies.
2.  **[APPLY]**: Write the code. Use `multi_replace` for surgical edits, `write_file` for new modules.
3.  **[VERIFY]**: Immediately run the code or a test script. "It compiles" is not enough. "It runs" is the standard.

## IV. EMERGENCY ROLLBACK
If verification fails:
1.  Stop.
2.  Restore from the previous Hash in the Ledger.
3.  Log the failure as `[FAILURE_ANALYSIS]` in `03_VAULT/99_SCRATCHPAD/Learning_Log.md`.

---
**"We build the road we walk on."**
