# VERIFICATION.md - Production Verification Matrix
*This file defines the acceptance checks required before Camelot-OS should be called production ready.*

## Verification Policy
*   Every production-facing surface must have at least one manual acceptance path and one repeatable command or test path.
*   Local fallback and remote configuration must be verified separately.
*   Browser mission execution is not considered verified until deploy, runtime, stop, and ledger sync have all been exercised.

## Definition Of Done
*   [X] **V1** - `Camelot-OS` launches from the repo `.venv` and returns valid output for core health commands.
*   [X] **V2** - The control plane returns typed `result` payloads for cloud services and not only status envelopes.
*   [X] **V3** - Local fallback works for cloudbrain, research, Northstar, blueprint, and precise-mode paths.
*   [ ] **V4** - The Nano-Knights extension can load, save, deploy, stop, and sync a precise mission without code changes.
*   [ ] **V5** - Precise mission ledger entries are created for mission start, lane completion, and mission completion.
*   [X] **V6** - A vault sync can be triggered successfully or fail cleanly while preserving local ledger state.

## Command Verification
Run from `C:\Users\vizio\CAMELOT_OS`.

### CLI Health
*   `Camelot-OS cloudbrain status`
*   `Camelot-OS cloudbrain research-health`
*   `Camelot-OS cloudbrain northstar-health`
*   `Camelot-OS cloudbrain blueprint-health`
*   `Camelot-OS cloudbrain precise-health`

Expected:
*   each command exits successfully
*   each command reports `status: COMPLETE`
*   the appropriate service name is shown
*   local fallback should report `source: local` when no remote URL is configured

### CLI JSON Contracts
*   `Camelot-OS --json cloudbrain research "compare agent runtimes" --tier apex`
*   `Camelot-OS --json cloudbrain northstar "production-ready transformable research agency" --aspect architecture --tier apex --cartridge HAWK --browser-isolation agency`
*   `Camelot-OS --json cloudbrain blueprint "resource constrained blueprint for Camelot-OS" --tier hybrid --budget-mode lean --team-size 2 --horizon-days 60`
*   `Camelot-OS --json cloudbrain precise "ephemeral nano-knights with multilogin-style researchers" --tier hybrid --browser-isolation agency --operator-count 2 --memory-gb 8`

Expected:
*   JSON output is valid
*   `payload.result.service` matches the requested service
*   typed fields are present
*   no unhandled exception text appears in output

### Python Parse Check
*   `& .\.venv\Scripts\python.exe -m py_compile .\cloud_orchestrator\modal_services.py .\control_plane\cloud_services.py .\control_plane\main.py .\control_plane\camelot_cli.py`

Expected:
*   command exits successfully
*   no syntax or import-time parse failures occur

### Extension Parse Check
*   `node --check .\03_VAULT\Nano-Knights\background.js`
*   `node --check .\03_VAULT\Nano-Knights\side_panel\research_panel.js`

Expected:
*   both commands exit successfully
*   no syntax errors are reported

## Manual Verification - Nano-Knights Precise Mode
### Prerequisites
*   Reload the unpacked extension from [03_VAULT/Nano-Knights](C:/Users/vizio/CAMELOT_OS/03_VAULT/Nano-Knights)
*   Ensure the extension side panel opens correctly
*   Ensure operator auth is active if the extension requires it

### Contract Load
1. Run:
   `Camelot-OS --json cloudbrain precise "ephemeral nano-knights with multilogin-style researchers" --tier hybrid --browser-isolation agency --operator-count 2 --memory-gb 8`
2. Paste the JSON into the Precise Mission panel.
3. Click `Save Contract`.
4. Click `Load Saved`.

Expected:
*   contract is stored and restored
*   safe swarm units are displayed
*   no panel crash occurs

### Mission Deploy
1. Optionally enter proxy credentials.
2. Click `Deploy Precise`.

Expected:
*   deployment status updates in the panel
*   forged tabs are opened for the configured lane count
*   runtime line shows mission id, status, lane state, and ledger count
*   each lane gets a browser page and begins bounded execution

### Mission Stop
1. Click `Stop` while a precise mission is active.

Expected:
*   panel shows stop requested
*   runtime status transitions to `STOPPING` then `STOPPED` or mission completes cleanly
*   a `mission_stop_requested` ledger entry is created

### Ledger Sync
1. Click `Sync Ledger`.

Expected:
*   panel reports sync result
*   successful sync reports `SUCCESS`
*   offline kernel behavior reports failure cleanly without deleting the local ledger

## Ledger Verification
### Local Ledger
Verify the extension runtime can expose:
*   ledger count
*   latest ledger entry
*   mission lifecycle entries

Expected ledger event types:
*   `mission_start`
*   `lane_complete`
*   `mission_complete`
*   `mission_stop_requested`

### Vault Sync Contract
Expected synced payload shape:
*   `agent: "PRECISE_LEDGER"`
*   `content.type: "precise_mission_ledger"`
*   `content.entries: [...]`

## Remote Configuration Verification
### Cloud URLs
If remote URLs are configured, verify:
*   `CAMELOT_CLOUDBRAIN_URL`
*   `CAMELOT_RESEARCH_AGENCY_URL`
*   `CAMELOT_RESEARCH_AGENCY_HEALTH_URL`
*   `CAMELOT_NORTHSTAR_URL`
*   `CAMELOT_NORTHSTAR_HEALTH_URL`
*   `CAMELOT_BLUEPRINT_URL`
*   `CAMELOT_BLUEPRINT_HEALTH_URL`
*   `CAMELOT_PRECISE_MODE_URL`
*   `CAMELOT_PRECISE_MODE_HEALTH_URL`

Expected:
*   remote invocation succeeds when URLs are valid
*   failure path returns a clean error instead of crashing the CLI

## Production Gaps To Close
These are not yet verified merely by the current implementation.

*   [X] **PG1** - Mission replay from ledger (Implemented via `TranscriptManager`)
*   [X] **PG2** - Retry and backoff policy for lane failures (Implemented in `ActionExecutor`)
*   [ ] **PG3** - Real authenticated proxy strategy under MV3 constraints
*   [X] **PG4** - Real operator auth path instead of mock assumptions (Implemented via dynamic token handshake)
*   [X] **PG5** - Automated test coverage for extension mission flows (Implemented in `tests/test_precise_mode.js`)

## Verification Record
When running a release verification, record:
*   date and operator
*   git or version identifier if available
*   commands run
*   manual checks performed
*   pass/fail per section
*   unresolved risks
