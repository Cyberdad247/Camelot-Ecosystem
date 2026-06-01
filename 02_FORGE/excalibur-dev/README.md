# EXCALIBUR v1000.0.0 — `nitro-v15-cpu`
CPU-substrate build of the Camelot-OS apex stack, delivered as an **agent-analyzable folder**.

## Use it
1. Unzip into your dev dir on the Nitro.
2. `bash bootstrap.sh`            # pre-flight GO/NO-GO -> build -> test
   - `bash bootstrap.sh --scaffold-only`   # run gate only
   - `bash bootstrap.sh --force`           # build despite NO-GO
3. Open in Claude Code. It auto-reads `CLAUDE.md`. To kick off, paste `.claude/bootstrap.md`.

The agent analyzes the whole folder and develops end-to-end from in-repo context:
`CLAUDE.md` (laws + roles), `tasks.md` (phased DAG), `verification.md` (gates),
`core/excalibur_topology.md` (architecture).

## Layout
- `core/`         pre-flight audit + GO/NO-GO adjudicator (verified)
- `crates/`       Rust workspace: conductor, ouroboros, trellis, aegis, omega-root
- `orchestrator/` Python layer: CLI + Aegis regex PII (WIRED)
- `CLAUDE.md` `AGENTS.md` `.claude/`  agent orientation
- `Makefile` `justfile`  task runners
