# ADR-0001 — Vendor ecosystem repos untracked into KINETIC_ARMORY

**Status:** Accepted (2026-08-15)
**Context:** Integrate the 10-repo Camelot-Ecosystem constellation
(`Camelot-Ecosystem`, `Kickbox-audio`, `Multivoice-router`, `ansible`, `huginn`,
`openinterpreter`, `LiteRT-LM`, `openai-oauth`, `abseil-cpp`, `grpc`) into the
monorepo to match and enhance the SADD v1.2 architecture.

## Decision

Vendor each repo as a **shallow, single-HEAD reference clone** under
`02_FORGE/KINETIC_ARMORY/<name>/`, excluded by `.gitignore`. Pin the clone HEAD
SHA in `docs/architecture/integrations.md`. `Camelot-Ecosystem` is not cloned —
it is this repository's `origin`.

## Options considered

1. **Git submodules** — rejected. The 2026-08-15 audit unlinked 32 orphaned
   gitlinks (no `.gitmodules` was ever maintained); re-adding submodules would
   reverse that cleanup and reintroduce `.git`-tracking fragility on a repo
   whose submodule history is broken.
2. **Tracked vendored copies** — rejected. `grpc` and `abseil-cpp` are
   multi-hundred-MB C++ sources; committing them conflicts with the
   repo-cleanup trajectory (qdrant/generated-client/runtime-blob purges) and the
   SADD's Northstar size discipline (Appendix B).
3. **Untracked vendor tree (chosen)** — matches the existing pattern for
   SpacetimeDB / livekit / goose / tiny-tts in `KINETIC_ARMORY`; zero repo
   bloat; reproducibility via pinned SHAs + shallow clone commands in the map.

## Consequences

- Builds that consume vendored code must treat `KINETIC_ARMORY/*` as
  pre-fetched external input (CI clones before build; local clones documented).
- A fresh checkout must run the documented clone loop to restore the vendor
  tree before integration work.
- Discovery risk is mitigated by the map's "discoveries" section: remote
  `Multivoice-router` is a Firebase web app (not the Go gateway) and remote
  `ansible` is upstream Ansible (not playbooks) — integration targets those
  findings rather than assuming repo identity.

## Links

- Map: `docs/architecture/integrations.md`
- Pending follow-up: ADR-0002 (grpc/abseil consumer decision, Phase 1).
