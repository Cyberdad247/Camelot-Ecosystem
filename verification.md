# CAMELOT OS Publication Verification

**Compiler:** Anya Gate / Cognitive Council / Forge Titan Bootstrap  
**Date:** 2026-07-09

## V1 - Repo Health

```powershell
cd C:\Users\vizio\CAMELOT_OS
Get-Location
Get-ChildItem -Name
```

Pass:

- the repo root is correct,
- the expected GUI, CLI, control-plane, docs, and workflow directories exist,
- no publication work starts from the wrong checkout.

## V2 - CLI Surface

```powershell
cd C:\Users\vizio\CAMELOT_OS
python -m control_plane.camelot_cli --help
python -m control_plane.camelot_cli cloudbrain config show
python -m control_plane.camelot_cli cloudbrain status
python -m control_plane.camelot_cli ledger status
```

Pass:

- the CLI parses and prints the shipped command surface,
- cloudbrain commands resolve through the current control plane,
- status commands complete without requiring manual code edits.

## V3 - GUI Surface

```powershell
cd C:\Users\vizio\CAMELOT_OS\02_FORGE\PORTAL_CORE\Anya_Dashboard
npm run verify
```

Pass:

- the UI builds and verifies cleanly,
- the operator surface renders without runtime errors,
- dashboard changes do not break the publication path.

## V4 - Cloudbrain Sync

```powershell
cd C:\Users\vizio\CAMELOT_OS
python -m control_plane.camelot_cli cloudbrain config diagnose
python -m control_plane.camelot_cli cloudbrain sync
```

Pass:

- cloudbrain source selection is current,
- stale or missing config fails explicitly,
- the repo does not rely on hidden defaults for publication options.

## V5 - Autonomous Workflow Boundaries

```powershell
cd C:\Users\vizio\CAMELOT_OS
python -m control_plane.camelot_cli cockpit exec "//STATUS"
python -m control_plane.camelot_cli cockpit exec "plain shell text"
```

Pass:

- runic input routes through the approved workflow layer,
- non-runic input is treated as shell passthrough only when that behavior is intentional,
- Sir Hermes-style relays remain observable and bounded.

## V6 - Verification Gates

```powershell
cd C:\Users\vizio\CAMELOT_OS
npx tsc --ignoreConfig --noEmit --module nodenext --moduleResolution nodenext --target esnext --strict src/router/*.ts tests/router/*.test.ts
npx vitest run tests/router
```

Pass:

- the root TypeScript router workspace type-checks,
- router tests pass,
- publication-critical changes do not land without test evidence.

## V7 - Publication Block

Pass only if all of the following are true:

- GUI, CLI, and cloudbrain checks pass,
- autonomous workflow boundaries are explicit,
- missing or stale config fails cleanly,
- the human release gate is still required,
- `//GO` has been issued before any publication action.
