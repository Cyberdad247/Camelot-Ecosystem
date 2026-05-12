# Camelot Mission Control Hardening Verification

## Preflight

```powershell
git status --short
cmd /c .venv\Scripts\camelot.exe --json ledger status
cmd /c .venv\Scripts\camelot.exe --json cloudbrain queue status
```

Expected:

- Git starts clean or only contains this hardening branch's intentional edits.
- Ledger mirrors report `mirrors_aligned: true`.
- Cloud Brain queue reports `pending: 0`.

## Verify `security.warden`

```powershell
cmd /c .venv\Scripts\python.exe -m py_compile security\warden.py control_plane\camelot_cli.py
cmd /c .venv\Scripts\camelot.exe --json cloudbrain queue status
cmd /c .venv\Scripts\camelot.exe --json ledger status
```

Expected:

- Python compile succeeds.
- Low-risk status/sync commands do not prompt for approval.
- Risky actions are denied or require explicit approval.
- Non-interactive risky commands fail closed.

## Verify Heartbeat Relocation

```powershell
cmd /c .venv\Scripts\python.exe -m py_compile control_plane\harness.py
git status --short
```

Expected:

- Routine Harness heartbeat writes do not modify `PROVENANCE_LEDGER.md`.
- Heartbeat runtime state appears only in ignored runtime/log paths.
- Material state changes can still create explicit ledger entries.

## Verify Ledger And Cloud Brain Sync

```powershell
cmd /c .venv\Scripts\camelot.exe --json ledger reconcile
cmd /c .venv\Scripts\camelot.exe --json cloudbrain sync --summary "Mission Control hardening verification complete."
cmd /c .venv\Scripts\camelot.exe --json cloudbrain queue status
cmd /c .venv\Scripts\camelot.exe --json ledger status
```

Expected:

- Mirror ledgers are reconciled.
- Cloud Brain note updates successfully.
- Cloud Brain queue remains `pending: 0`.
- Final ledger status reports `mirrors_aligned: true`.

## Final Git Proof

```powershell
git status -sb
git log -1 --oneline
```

Expected:

- Branch is synced with origin after push.
- No unexpected dirty files remain.

