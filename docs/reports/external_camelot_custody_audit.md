# External Camelot Custody Audit

## Scope

Read-only shallow audit of likely Camelot-related files and folders in `C:\Users\vizio` outside `C:\Users\vizio\CAMELOT_OS`.

## High-Confidence External Artifacts

| Path | Classification | Recommendation |
| --- | --- | --- |
| `C:\Users\vizio\.camelot` | Active local runtime state with tokens, keys, config, revocations, traces | Reference from Camelot OS; do not blindly move or commit |
| `C:\Users\vizio\.notebooklm` | NotebookLM browser/auth/cache state and `storage_state.json` | Reference as external Cloudbrain state; mirror through controlled bridge |
| `C:\Users\vizio\.notebooklm-mcp-cli` | NotebookLM MCP auth, tags, profiles, pipelines | Reference as external service state; do not move into repo |
| `C:\Users\vizio\CAMELOT_DefenseGrid_Quarantine` | Quarantine/remediation records | Keep separate custody root unless explicitly importing reports |
| `C:\Users\vizio\camelot_kba_drone.zip` | Portable Camelot/KBA archive artifact | Move only after checksum and archive inventory |
| `C:\Users\vizio\CAMELOS` | Empty top-level folder | Candidate for removal or archived placeholder after confirmation |

## Existing Internal Counterpart

`C:\Users\vizio\CAMELOT_OS\.camelot` already exists and contains repo-local cartridges, projects, and vault staging content. It is not equivalent to `C:\Users\vizio\.camelot`.

## Key Finding

The external `.camelot` folder contains live secrets and runtime identity material:

- `bifrost.token`
- `cartridge_ed25519`
- `cartridge_ed25519.pub`
- `kba_drone.env`
- `secret.key`
- `revocations.json`
- `traces/camelot-os.jsonl`

These should not be absorbed into source control. The correct pattern is a repo manifest that points to external custody paths, not a bulk move.

## Optimized Assimilation Prompt

Use this prompt for the next migration pass:

```text
Anya, perform a fast custody-safe assimilation audit for Camelot OS.

Root: C:\Users\vizio
Target repo: C:\Users\vizio\CAMELOT_OS

Rules:
- Do not move, delete, rename, or rewrite files.
- Do not print secret contents.
- Inspect metadata first: path, type, size, modified time, and shallow children.
- Classify each external artifact as one of:
  1. repo-source candidate
  2. runtime-state external reference
  3. secret/custody material
  4. archive/import candidate
  5. quarantine/forensics material
  6. unrelated local tool state
- Compare external artifacts against existing CAMELOT_OS counterparts.
- Recommend copy, reference, ignore, quarantine, or delete-later only after classification.
- Produce a migration plan, not a mutation.

Priority paths:
- C:\Users\vizio\.camelot
- C:\Users\vizio\.notebooklm
- C:\Users\vizio\.notebooklm-mcp-cli
- C:\Users\vizio\CAMELOT_DefenseGrid_Quarantine
- C:\Users\vizio\camelot_kba_drone.zip
- C:\Users\vizio\CAMELOS

Output:
- P0 security/custody risks
- P1 high-value imports
- P2 cleanup candidates
- exact verification commands
- final operator decision table
```

## Fast Verification Commands

```powershell
Get-ChildItem -Force C:\Users\vizio | Where-Object { $_.Name -match 'camel|CAMELOT|notebook|cloudbrain|graphify|ledger|runic|excalibur' } | Select-Object Name,Mode,Length,LastWriteTime
```

```powershell
Get-ChildItem -Force C:\Users\vizio\.camelot | Select-Object Name,Mode,Length,LastWriteTime
```

```powershell
Get-ChildItem -Force C:\Users\vizio\CAMELOT_OS\.camelot | Select-Object Name,Mode,Length,LastWriteTime
```

## Recommended Next Step

Create a non-secret manifest at `CAMELOT_OS/docs/custody/external_state_manifest.md` that records external paths and their purpose. Do not move live credential material into the repository.

