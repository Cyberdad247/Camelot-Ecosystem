# VFS Preflight Catalog

Each `*.yaml` file in this directory is one preflight check. The catalog is
loaded by `python -m control_plane.preflight` at boot (`bin/awaken.py` stage 0).

## YAML fields

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `sequence` | yes | int | Execution order. Stride 10 (010, 020, ...) so authors can insert at natural positions without renumbering. Must be unique within the catalog. |
| `id` | yes | str | Stable identifier; becomes `<UTC>/<id>.json` filename. |
| `display_name` | yes | str | Human-readable name in operator summary. |
| `command_type` | yes | `python_module` \| `shell` | `python_module` is preferred; `shell` only when necessary. |
| `command` | yes | list[str] | argv list, never a shell command. Each element must be a string. |
| `timeout_s` | no | int (default 30) | Wall-clock timeout. Prefer absence over low values; if a check can fail transiently, raise timeout_s, do not add retries. |
| `retry` | no | int 0..2 (default 0) | **Discouraged.** Use only for ports-style transient failures. |
| `expected_evidence_class` | no | `CONFIRMED` (default) | Only `CONFIRMED` accepted. The catalog-load layer (`schemas.CheckSpec.from_yaml_text`) rejects any other value. |
| `hitl_on_fail` | no | bool (default false) | If true, a REJECTED result surfaces a PROMPT-tier operator menu instead of halting. Reserved for the 3 operator-visible checks: 030 (northstar brief currency), 040 (port readiness scan), 070 (vfs scaffold integrity). |
| `remediation_hint` | no | str | Shown in operator summary when the check fails. |

## Authoring rules

1. Command must be a list, never a shell string. `command: ["python", "-c", "..."]` is the only safe shell-style form.
2. Sequence must be unique. Use stride 10.
3. Do not bypass timeout via Python's `subprocess`; rely on the runner's bounded wrapper.
4. If a check needs new logic, add a probe under `control_plane/preflight/probes/` first.
5. Evidence class is CONFIRMED-only by design (VFS_PREFLIGHT_DESIGN.md §5.3).
6. Maintain idempotency: re-running this check N times produces no side effects past version drift.

## Initial 8 checks (slice #1, this commit)

| seq | id | hitl_on_fail |
|-----|----|--------------|
| 010 | `env_dependency_match` | false |
| 020 | `foss_validation_constraints` | false |
| 030 | `northstar_brief_currency` | true |
| 040 | `port_readiness_scan` | true |
| 050 | `provenance_ledger_writable` | false |
| 060 | `tool_registry_presence` | false |
| 070 | `vfs_scaffold_integrity` | true |
| 080 | `lattice_yaml_consistency` | false |

Substrate reference: `docs/architecture/VFS_PREFLIGHT_DESIGN.md` §4.
