# Skill: vps-hub

# VPS Hub Skill

Operate the Camelot VPS Hub (KVM563) from opencode. Offline-safe by default.
Owner: HERMES_PRIME. Bifrost boundary co-governor: SIR_HEIMDALL.

## Status (offline)

```powershell
python -m control_plane.infra.vps_hub_client --status
python -m control_plane.runes.runic_router --rune VPS_HUB --task "<task>"
```

Expect `mode: OFFLINE`, 11/11 contracts VENDORED, 11 endpoints.

## Validate (offline, fail-closed)

```powershell
python -m control_plane.infra.vps_hub_client --validate receipt <file>
```

`ok:true` with zero errors required. Unknown contract or unresolvable
`$ref` fails closed — report, do not retry with different schema.

## Lease scope

```powershell
python -m control_plane.infra.vps_hub_client --lease-scope <workspace> <notebook>
```

Produces `cloudbrain://notebooklm/<workspace>/<notebook>`.

## Draft builders (LOCAL DRAFT only)

`build_context_packet` / `build_receipt_draft` emit structurally valid,
unsigned artifacts (zeroed hashes/signatures) — never submittable. The hub
verifies Ed25519 + hash chain itself.

## Live (HITL-gated)

`--live` TCP probes and `--ssh` hit the production hub. Never add them
without explicit human approval for that invocation.

Base directory for this skill: C:\Users\vizio\CAMELOT_OS\.agents\skills\vps-hub
