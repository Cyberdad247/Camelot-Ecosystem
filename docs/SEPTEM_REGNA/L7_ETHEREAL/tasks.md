# TASKS.md - Production Blueprint
*This file is the production execution board for Camelot-OS. Completed work is retained for traceability. Open items are the remaining gates to ship a supportable operator platform.*

> Historical planning note:
> Some tasks below reference older path names and architecture labels.
> For current live surfaces use `docs/architecture/SOURCE_OF_TRUTH_MAP.md`
> and `entiremap.md`.

## Current State
*   [X] **P0.1** - Canonical CLI online: `Camelot-OS` runs from the repo `.venv` and supports colored incremental streaming.
*   [X] **P0.2** - Control-plane routing online: typed cloud routing, SARDA augmentation, and policy-gated service access are implemented.
*   [X] **P0.3** - Hybrid cloudbrain online: Appwrite/Open Notebook bootstrap, Modal endpoints, and local fallback execution are implemented.
*   [X] **P0.4** - Northstar online: war-room planning, compute-tier selection, cartridge assignment, and Multilogin-style isolation surfaces are implemented.
*   [X] **P0.5** - Precise mode online: typed Nano-Knight browser swarm planning, omniroute symmetry, ephemeral session forging, bounded lane execution, and local ledgering are implemented.

## Production Goal
*   [ ] **G1** - One-command operator workflow: generate, deploy, monitor, stop, and sync a mission without manual code edits.
*   [ ] **G2** - Supportable runtime: every critical subsystem has health checks, bounded retries, logs, and fail-soft behavior.
*   [ ] **G3** - Auditable missions: every precise mission can be reconstructed from a ledger and synced to the vault.
*   [ ] **G4** - Safe browser execution: proxy, stealth, profile, and session lifecycle are explicit and operator-controlled.
*   [ ] **G5** - Release readiness: verification coverage exists for CLI, control plane, cloudbrain, extension runtime, and vault sync.

## Track A - Control Plane And CLI
*   [X] **A1** - Prompt-first CLI: `Camelot-OS` supports direct prompts, `chat`, `route`, `cloudbrain`, and `sarda`.
*   [X] **A2** - Streaming UX: colored incremental output and progress staging are implemented in `control_plane/camelot_cli.py`.
*   [X] **A3** - Typed cloud router: `control_plane/cloud_services.py` routes cloudbrain, research, Northstar, blueprint, and precise-mode services.
*   [X] **A4** - Result envelopes: control-plane cloud responses now include `result` and `error` payloads instead of only status.
*   [X] **A5** - Operator profiles in CLI: add first-class CLI flags or config presets for proxy, stealth, and session policy defaults.
*   [X] **A6** - Persisted operator config: add a canonical Camelot-OS config file for cloud URLs, browser policies, and default tiers.
*   [ ] **A7** - CLI smoke test suite: add automated tests for `status`, `research-health`, `northstar-health`, `blueprint-health`, and `precise-health`.

## Track B - Hybrid Cloudbrain
*   [X] **B1** - Long-term cloudbrain bootstrap: `cloud_orchestrator/long_term_cloudbrain.py` bootstraps Open Notebook and fail-soft Appwrite memory access.
*   [X] **B2** - Modal service surface: `cloud_orchestrator/modal_services.py` exposes typed endpoints for research, Northstar, blueprint, and precise-mode planning.
*   [X] **B3** - Local fallback execution: all typed services can execute locally through the control-plane router.
*   [ ] **B4** - Remote deployment contract: document and validate required environment variables for Modal, Appwrite, and remote health URLs.
*   [ ] **B5** - Health aggregation: add one production health command that rolls up cloudbrain, research, Northstar, blueprint, and precise-mode readiness.
*   [ ] **B6** - Cloud timeout policy: standardize timeouts, retries, and fallback thresholds for remote service invocation.

## Track C - Research And Northstar
*   [X] **C1** - Research agency tiers: `kinetic`, `hybrid`, and `apex` are implemented with typed profiles and cell definitions.
*   [X] **C2** - Northstar war-room: aspect routing, cartridge defaults, CHIMERA rounds, and browser-isolation strategy surfaces are implemented.
*   [X] **C3** - Development blueprint: resource-constrained blueprint generation is implemented and exposed through the CLI.
*   [ ] **C4** - Canonical mission templates: add reusable templates for research, architecture, audit, operations, and growth missions.
*   [ ] **C5** - Objective scoring: add confidence, risk, and completeness scoring to Northstar and blueprint outputs.
*   [ ] **C6** - Prompt contract tests: add regression tests for Northstar and blueprint response shape.

## Track D - Nano-Knights Precise Mode
*   [X] **D1** - Precise-mode planner: typed swarm capacity, omniroute engine/model symmetry, and browser isolation are implemented.
*   [X] **D2** - Extension bridge: the Nano-Knights extension accepts precise contracts, stores them, and deploys them.
*   [X] **D3** - Session forging: each Nano-Knight receives ephemeral session metadata, browser profile bias, and lane metadata.
*   [X] **D4** - First production runner: precise-mode lanes now run bounded multi-step browser loops with stop control and lane status.
*   [X] **D5** - Ledger layer: mission lifecycle and lane completion events are written to a local extension ledger and can sync through the vault bridge.
*   [X] **D6** - Replayable lane transcripts: store enough structured detail to reconstruct or replay a lane without rerunning live browser actions.
*   [X] **D7** - Retry policy: add bounded retry and backoff for navigation failures, action misses, and proxy failures.
*   [X] **D8** - Mission success criteria: add explicit completion conditions per lane instead of only bounded-step termination.
*   [X] **D9** - Extension test harness: add deterministic tests for contract ingest, mission deploy, stop, ledger append, and sync actions.
*   [X] **D10** - Secrets hardening: remove static dev token assumptions from the extension vault bridge and move credentials behind operator config.

## Track E - Ledger, Vault, And Auditability
*   [X] **E1** - Precise mission ledger: local extension ledger with lifecycle events is implemented.
*   [X] **E2** - Vault sync hook: precise ledger bundles can sync through `vault_bridge.js`.
*   [X] **E3** - Verification ledger: add a canonical verification run record with timestamp, operator, command, and result summary.
*   [X] **E4** - Mission provenance schema: define a stable JSON schema for precise mission records, lane events, and vault sync receipts.
*   [X] **E5** - Ledger retention policy: define cap, archive policy, and export format for mission ledgers.

## Track F - Security And Runtime Hardening
*   [X] **F1** - Cloud capability firewall: sensitive remote research is blocked unless explicitly permitted.
*   [X] **F2** - Browser isolation surface: `stealth`, `team`, and `agency` are modeled explicitly.
*   [X] **F3** - Proxy partitioning surface: precise-mode supports residential proxy policy and per-session configuration.
*   [ ] **F4** - Extension auth hardening: replace mock auth assumptions with a real operator auth or local secret retrieval path.
*   [ ] **F5** - Proxy auth strategy: support MV3-safe authenticated proxy flows without relying on fragile manual behavior.
*   [X] **F6** - Safe default policy: enforce direct mode unless a mission explicitly requires proxy-backed browser research.
*   [ ] **F7** - Mission stop guarantees: ensure stop requests interrupt long-running lane loops promptly and predictably.

## Track G - Verification And Release
*   [X] **G1** - Root verification document: `verification.md` must reflect the current product surfaces and required acceptance checks.
*   [X] **G2** - CLI acceptance run: verify every health command and one representative mission path in JSON and human-readable mode.
*   [X] **G3** - Extension acceptance run: verify precise contract save, deploy, stop, status refresh, ledger append, and ledger sync in Chrome.
*   [X] **G4** - Cloudbrain acceptance run: verify local fallback and remote configuration behavior separately.
*   [X] **G5** - Production cut checklist: define release prerequisites, rollback path, and post-release monitoring expectations.

## Recommended Order
*   [X] **R1** - Finish `D6`, `D7`, and `D8` before adding more agent types.
*   [X] **R2** - Finish `A5`, `A6`, and `F6` before enabling broader operator use.
*   [X] **R3** - Finish `G2`, `G3`, and `G4` before calling the platform production ready.
*   [X] **R4** - Finish `E3` and `E4` before relying on mission data for long-term auditability.

## Historical Completed Work
*   [X] **H1** - Swarm audit, settlement, SARDA, and kernel orchestration phases completed.
*   [X] **H2** - Structural purity, telemetry, and interface resonance phases completed.
*   [X] **H3** - Prior feature tracks retained in repo history and in legacy milestone records.
