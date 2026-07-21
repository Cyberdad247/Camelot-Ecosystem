# Scope Review — HiveIDE_Apex_v1000 ExecutionDAG

| Field | Value |
|---|---|
| Status | Sovereign-approved 2026-06-25 — Iron Gate v2 explicit scope review per AGENTS.md Iron Gate |
| Issued by | King Arthur (VaShawn O. Head / Vizion) |
| Origin | `camelot-os.dev/ukg/v1000/cybertron_ascension` (`@type=ExecutionDAG`, `@status=AWAITING_FORGE`) |
| Live runtime host | Windows win32 (per system info) — Phase 3 requires WSL2 with nested KVM |
| Reversibility of additive portion | Full — additive files only; destructive cut held under HUMAN_GATE |
| Triggered shatterpoints | `destructive_autonomy`, `verification_bypass`, `platform_reality` |

## Decision summary

| Phase | Triage class at gate | User choice | Hard gate | Reversibility |
|---|---|---|---|---|
| 1. RustClaw `pmcp` RIP_AND_REPLACE | planned → aspirational | **Full purge in one cut** | `CAMELOT_DASHBOARD_OPERATOR_TOKEN` + printed `[y/N]` | `git revert <cut-sha>`; additive scaffolding lands first |
| 2. Ouroboros Loop v1000 @ 6 GB | planned | Compression trigger = env-configurable ratio; **default 0.90** of 8 GB ceiling (~7.2 GB) honoring the DAG's 6 GB literal as a floor | None — env-var override | env-var flip |
| 3. libkrun + UFFD <12 ms cold boot | aspirational → blocked on `win32` | **WSL2 nested-virt KVM target** | `scripts/wsl2_preflight.sh` returns GO before cut | `forkd_runner.sh` remains fallback on Windows |
| 4. Tailwind v4 + Lucide-React enforcement | confirmed (Rule 1 already mandates) | **Build-fail AST lint** (`scripts/design_lint.py`) | None — opt-out via `CAMELOT_LINT_WAIVER_TOKEN` ≤ 24 h, logged | lint rule update |

## Risk register

### Phase 1 — Full purge of Node.js MCPs

- **Shatterpoints raised**: `destructive_autonomy`, `verification_bypass` — both appear in
  `_SHATTERPOINT_PATTERNS` of `control_plane/anya_gate.py` and force `risk_entropy ≥ 0.55`
  → HUMAN_GATE per Iron Gate v2 in `soul_oversight.pre_execute`.
- **Blast radius**: `bin/awaken.py`, `control_plane/boot_sequence.py`,
  `02_FORGE/cartridge/rustclaw/src/main.rs` (`camelot-mcp-edge.exe` spawn line),
  any `package.json` referencing `mcp` or `@modelcontextprotocol` in
  `02_FORGE/kinetic/*/`. Full inventory at
  `03_VAULT/runtime_state/node_mcp_cutlist.json`.
- **Rollback path**: `git revert <cut-sha>` brings the tree back to pre-cut state.
- **Hard prerequisite**: additive `02_FORGE/kinetic/pmcp/` scaffolding first lands and
  reproduces a noop boot in WSL2.
- **Final-cut lock**: requires `CAMELOT_DASHBOARD_OPERATOR_TOKEN` at execute time +
  printed `[y/N]` confirm with the cut list rendered.

### Phase 2 — Compression threshold 6 GB vs configured ratio

- **Conflict**: DAG writes 6 GB literal; `.agent/local_env.md` ceilings 8 GB.
- At 6/8 = 0.75 the ouroboros semantic-anchor compression loop thrashes against
  the 2 GB remaining working set.
- **Resolution**: env var `CAMELOT_COMPRESSION_TRIGGER_RATIO` (float ∈ [0.50, 0.95])
  honors DAG at 6 GB if set to 0.75. **Default is 0.90** (≈ 7.2 GB) so trigger fires
  only when the working set is genuinely nearing ceiling.

### Phase 3 — WSL2 KVM/UFFD substrate

- **Blocker on current host (`win32`)**: `libkrun` requires Linux kernel + KVM;
  `userfaultfd` is Linux-only. WSL2 with nested virtualization is the lowest-friction pivot.
- **Owner prerequisite**: install WSL2 kernel, enable nested virt in BIOS/UEFI,
  expose `/dev/kvm` to the WSL2 distro.
- **Forge action**: `scripts/wsl2_preflight.sh` returns a JSON verdict. Until verdict=GO,
  the forge stays at the `forkd_runner.sh` fallback (Windows coW microvm).
- **Target ground truth**: live `/dev/kvm` open + `userfaultfd(2)` syscall returning ≥ 0
  + `libkrun` installed + nested virt confirmed.

### Phase 4 — Build-fail lint

- **Rule scope**: scans TSX/JSX/CSS in `02_FORGE/PORTAL_CORE/**`,
  `02_FORGE/apps/**/src/**`, `01_KERNEL/dashboard/**`.
- **Rule set**:
  1. JSX `class="..."` strings must use Tailwind v4 utility prefixes; no inline
     `style={{ margin: '...' | color: '...' | padding: '...' | display: '... }}` props;
     palette refers to `#050505`, `#D4AF37`, royal-purple OR CSS vars from `theme.css`.
  2. `<svg>` icon literals require either a co-located `@lucide/react` import OR the
     `// CML_LUCIDE_OK` annotation.
- **Bypass**: `CAMELOT_LINT_WAIVER_TOKEN` env var for ≤ 24 h; waiver was logged to
  `.hive/design_lint_waivers.jsonl`.
- **Enforcement on current branch**: husky + pre-push hook. **Honest build-fail**, not
  silent warn. AGENTS.md Iron Gate hits the rule "any change > 10 net lines" — the
  enforcement script itself IS the scope review.

## Cross-cutting

- Per AGENTS.md Rule 2: a `code-reviewer-minimax-m3` review is run on every additive
  change before the destructive cut.
- Per AGENTS.md Iron Gate: any change > 10 net lines is scope-reviewed; **this document
  IS that review**.
- The HiveIDE_Apex_v1000 crystal is filed at evidence-class `aspirational` per AGENTS.md
  Codex Meta-Harness Adapter. Graduation gates to `planned` and `confirmed` are enumerated
  at `03_VAULT/runtime_state/hive_ide_apex_v1000/graduation-checklist.md`.

## Operator sign-off

For the actual destructive cut (Phase 1) and the WSL2 substrate transition (Phase 3) the
runtime will require:

1. `CAMELOT_DASHBOARD_OPERATOR_TOKEN=...` exported in the active shell.
2. `[y/N]` confirm on screen for Phase 1, asserting the cut list order.
3. WSL2 GO verdict from `scripts/wsl2_preflight.sh` for Phase 3.

If any precondition is unmet, the cut is held under HUMAN_GATE per
`soul_oversight._suspend` and the operator is notified via `logs/hitl_queue.jsonl`.

---

Sealed 2026-06-25 by King Arthur.

`AnyaGate.AUTO_HITL = HUMAN_GATE` — pending operator token + WSL2 GO verdict to release the
destructive cut.
