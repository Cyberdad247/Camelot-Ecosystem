# ADR 0006: VFS Preflight Strict-Mode Without Sovereign Escape Hatch

**Status:** Accepted (companion to `docs/architecture/VFS_PREFLIGHT_DESIGN.md`)
**Date:** 2026-08-13
**Deciders:** Sovereign (VaShawn O. Head / Vizion), Merlin validating, Sentinel reviewing
**Slice:** #1 — VFS Preflight Scaffold

---

## Context

The VFS scaffolding under `vfs/*.md` was prose-only. Turning it into a
runtime gate required deciding what happens when the gate fails.

Three options were considered:

| Option | Description |
|---|---|
| Sovereign escape hatch (env / flag) | `CAMELOT_SKIP_PREFLIGHT=1`, `--skip-sovereign`, per-check bypass |
| Strict halt, no override | Failure ≡ boot halts; sovereign fixes the issue or restores from snapshot |
| First-run advisor → strict | First-ever run surfaces findings but proceeds; subsequent runs strict |

Final choice: **First-run advisor → strict**, with **no** in-band escape
hatch from strict-mode thereafter.

---

## Decision

1. First run of VFS preflight on a system with no
   `03_VAULT/runtime_state/preflight/_graduated.flag` file runs in **advisor
   mode**.
2. In advisor mode, a `REJECTED` check produces `halt_decision: "continue"`
   and `advisor_finding: true` for the affected check(s), and the boot
   proceeds.
3. The first run where **all 8 checks reach `CONFIRMED`** writes
   `_graduated.flag` and emits `graduated_to_strict: true` in the manifest.
4. Subsequent runs are **strict-mode**: a `REJECTED` check halts the boot
   (`halt_decision: "block_boot"` or `await_hitl`).
5. The runner explicitly rejects `CAMELOT_SKIP_PREFLIGHT=1`,
   `--skip-sovereign`, and any per-check bypass flag with a stderr message
   explaining the design choice. The environment and console help text do
   not advertise these paths.
6. Manual rollback to advisor-mode is documented as: delete
   `03_VAULT/runtime_state/preflight/_graduated.flag`.

---

## Rationale

**Why drop the sovereign escape hatch.**
- The preflight is meant to be the substrate's floor. An env-level bypass
  converts it from a *gate* into an *advisory*, which defeats the purpose.
- Sovereign keys (`CAMELOT_DASHBOARD_OPERATOR_TOKEN`, HITL tokens, mTLS)
  already provide acceptable override surfaces at higher layers. The gate
  itself should not duplicate them — defense in depth means each layer
  enforces its own invariant.
- An escape hatch that the sovereign can pull becomes an escape hatch that
  any compromised subprocess can pull, reducing the floor's value.

**Why first-run advisor instead of pure strict.**
- Strict-from-run-1 implies the operator has already validated the catalog,
  the runner, and the checks — but the catalog hasn't even been exercised
  yet. A first-run advisor surfaces real findings without trapping the
  sovereign in a "you must wire the gate before you can use the gate"
  dilemma, which every substrate bootstrap eventually hits.
- Graduation after first CONFIRMED run means the bookkeeping flag
  (`_graduated.flag`) is itself produced and consumed by an exercise of the
  substrate, not by an out-of-band manual flip. Self-confirming provenance.

**Why explicit rejection of removed flags in code, not just docs.**
- Docs-only removal leaves a foot-gun: a sovereign-or-script that has the
  muscle memory of `CAMELOT_SKIP_PREFLIGHT=1` thinks it is preserving known
  behavior, then hits an unexpected error. An explicit early rejection
  forces the error to surface at the same point a previous-version skip
  would have and surfaces the design rationale.

---

## Consequences

**Positive.**
- The gate is a real gate. A future change to `vfs/checks/` that is
  silently broken will halt the next strict boot.
- The boot log becomes a high-confidence signal that the substrate is
  sane, not a "we hope it ran OK" narrative.
- Investigative outages begin with `_manifest.json` reads, not with
  ad-hoc detective work.

**Negative.**
- First-time installations require a manual advisory pass; the operator
  must read advisor findings, decide which are acceptable, and only then
  graduate into strict. This adds 1 boot of friction.
- Rolling back to advisor requires filesystem-level ops on
  `_graduated.flag`. Not undoable through normal camelot tooling —
  intentionally so (the rollback is meant to be rare and considered).
- Sovereign cannot effectively skip preflight under time pressure. If
  preflight is broken and the system is down, the recovery path is to
  inspect + fix the catalog or the runner, not bypass preflight.

**Trade-offs accepted.**
- A failed/uncertain preflight takes the system offline until fixed. We
  accept this in exchange for guarantees about substrate health. If
  outage tolerance becomes a primary requirement, we revise via ADR.

---

## Alternatives Rejected

- **Pure strict from run 1 with sovereign env bypass** — provides
  operability but provides it through the wrong layer; the bypass reduces
  guarantee value.
- **Pure strict from run 1 with no escape hatch whatsoever** — correct
  principle, but increases bootstrap friction (must wire the runner BEFORE
  the catalog is exercised). Defers confidence too far.
- **Rolling-window advisory** (last N runs surface findings; Nth+1 strict)
  — duplicates the graduation state in time domain; harder to reason
  about than a single-bit flag.
- **Severity-tiered bypass** (allow override of WARN-severity fails but
  block ERROR-severity) — adds a severity taxonomy that preflight doesn't
  otherwise need.

---

## Cross-References

- Spec: `docs/architecture/VFS_PREFLIGHT_DESIGN.md` §6 (Failure Modes & First-Run Advisor) and §8 (Decisions Log row 4)
- Substrate: `docs/architecture/Ω_VFS_ARCHITECTURE_SCAFFOLD_vMAX.deposit_note.md`
- Augmentation partner: `control_plane/anya_gate.py` (evidence-class assertion)
- HITL partner: `control_plane/soul_oversight.py` (IronGateV2 at `GateKeys.PREFLIGHT`)

---

## Verification & Reversal

- Verification: present in `docs/architecture/VFS_PREFLIGHT_DESIGN.md`
  AC4, AC6, AC7.
- Reversal: edit this ADR to set status `Superseded` and write
  `docs/adr/000X-restore-escape-hatch.md` referencing this one.
