# VPS Hub Opencode Parity — Design Spec (2026-09-22)

## Goal
Make Camelot VPS Hub a first-class opencode citizen, same standing as
camelot-os: agent definition, skill workflow, expanded commands, permission
allowlist, offline-safe defaults, validated against authority notebooks.

## Non-goals
- No new live transport. Reuse `control_plane/infra/vps_hub_client.py` and
  vendored `control_plane/dispatch/vps_hub_contracts/` (11 schemas, MANIFEST pins).
- No direct `main` pushes, no branch deletions, no `--live`/`--ssh` without
  explicit human approval.
- No secret values in config, prompts, skills, or reports (boolean presence
  flags only). `PROVENANCE_LEDGER.md` hand-edits forbidden (hook-owned).

## Authority validation (verified 2026-09-22, offline)
- `KNIGHT_NOTEBOOKS` (`01_KERNEL/memory/cloudbrain_connector.py:57`):
  `WORLD_TREE a0a4bfb9-e847-4c38-be39-7aee398f0795`,
  `HERMES_PRIME 28f89cb6-5048-4b5d-9e94-376082d24744`,
  `SIR_HEIMDALL 3205f189-91da-4272-96a9-3641fd642763`,
  `BIFROST cbbb0c32-3919-4b77-9158-1d9f9ebf359f`,
  `SIR_HERMES 5dc31b8d-169d-4d4d-ab90-d12724fca720`.
- Tissues (`03_VAULT/runtime_state/open_notebook/`): `world_tree`,
  `hermes_prime`, `sir_heimdall`, `bifrost`, `vps_hub_kvm563` all tethered to
  `worldtree_home a0a4bfb9…` (2026-09-22). Hub tissue pins
  `HERMES_PRIME` owner + `SIR_HEIMDALL` co-guardian, deployed commit
  `77c947e` (= `origin/main`), Bifrost bridge co-governors Hermes+Heimdall.
- `hub_status(live=False)`: `OK`, `OFFLINE`, 11/11 contracts VENDORED,
  11 endpoints, 66 knight nodes.
- Builders: `--lease-scope WS_TEST NB_TEST` →
  `cloudbrain://notebooklm/WS_TEST/NB_TEST`; receipt draft →
  `--validate receipt` = `ok:true`, zero errors.

## Architecture
Existing spine stays: `//VPS_HUB` →
`control_plane/runes/runic_router.py:211 _handle_vps_hub` →
`hub_status()` / `validate_artifact()` / `cloudbrain_lease_scope()`.
New opencode surface wraps it (agent + skill + commands + permissions).
Governance: HERMES_PRIME owns hub ops; SIR_HEIMDALL co-governs Bifrost
boundary (matches hub tissue + router guardians).

## Components
1. `.opencode/agents/hermes-prime.md` (new, `mode: subagent`):
   Mirror `sir-sentinel.md` frontmatter. Rules: offline default; `--live`,
   `--ssh`, hermes exec require explicit human approval; report with
   `file:line` refs; never emit secret values; hand `GH006`-class protection
   blocks to operator (do not bypass).
2. `.agents/skills/vps-hub/SKILL.md` (new): workflow
   status → validate → lease-scope → draft packet/receipt; offline validators;
   live-probe section fenced as HITL-gated; validation evidence required
   (contract count, `ok:true` output).
3. `.opencode/commands/vps-hub*.md` (expand): keep `vps-hub.md` offline
   status; add `vps-hub-validate.md` (`--validate <schema> <file>`) and
   `vps-hub-lease.md` (`--lease-scope <ws> <nb>`) mapping 1:1 to CLI flags.
4. `opencode.json` (edit): `bash` allowlist adds
   `python -m control_plane.infra.vps_hub_client --status`,
   `python -m control_plane.infra.vps_hub_client --validate *`,
   `python -m control_plane.infra.vps_hub_client --lease-scope *`,
   `python -m control_plane.runes.runic_router --rune VPS_HUB*`;
   `--live` / `--ssh` remain `ask` (default-deny live).

## Data flow
Command → runic_router `VPS_HUB` → `hub_status(live=False)` →
contracts inventory + endpoint table + lease format. Validate path fails
closed on unresolvable `$ref`. Builders emit LOCAL DRAFT artifacts (zeroed
hashes/signatures, never submittable). Live path returns `mode: LIVE`
envelope; command wrapper refuses `--live` without recorded approval.

## Error handling
- Unknown contract → `{"ok": false, errors: [...]}` exit 1 (no stack leak).
- Unreadable file → `unreadable file` JSON, exit 2.
- Stale pins → report `MANIFEST.json fetched_at` + blob SHA mismatch; never
  auto-refetch from `Cyberdad247/Camelot-VPS` without approval.
- Protection refusals (GH006-class) → report, do not bypass, do not push main.

## Testing (offline only)
- `python -m control_plane.infra.vps_hub_client --status` (no `--live`).
- `--validate receipt <draft>` → `ok:true`.
- `.venv\Scripts\python.exe -m pytest tests/control_plane/test_kinetic_trinity_vps_hub.py -x -q`
  plus canonical `tests/<file>.py` only (never repo-root sweep).
- Contract pin check: 11 schemas present, `MANIFEST.json` readable.

## Rollout
Spec review → writing-plans → implement agent/skill/commands/permissions →
scoped validation → PR (no direct main push).
