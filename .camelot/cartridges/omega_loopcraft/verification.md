# Verification — omega_loopcraft

## Static Validation Checks

The Iron Gate validation enforces the following strict security and execution invariants:

### 1. Secret Exposure Invariant (Z3 Security Boundary)
No environment variable file (`.env`, `.env.local`, `.env.production`) or raw secret tokens must be stored or packaged inside the cartridge tree. All configurations must be derived dynamically from runtime host variables or interactive prompts.

```powershell
# Scan to verify no .env files exist in the cartridge
Get-ChildItem -Path .camelot/cartridges/omega_loopcraft -Filter ".env*" -Recurse | Measure-Object | % {
    if ($_.Count -ne 0) { throw "Verification Failed: Banned .env files detected inside the cartridge!" }
}
```

### 2. HITL Gate Verification (Interactive Approval Constraint)
The UI shell must expose an explicit, interactive "Approve" button before any stdio JSON-RPC payload is written or executed by the background host process. Auto-execution of mutating backend payloads is blocked by default.

```javascript
// Verification Rule: Interactive execution constraint
function verifyExecutionTrigger(payload) {
  if (payload.is_mutating && !payload.hitl_approved) {
    throw new Error("Execution Denied: Mutating actions require explicit user approval.");
  }
  return true;
}
```
