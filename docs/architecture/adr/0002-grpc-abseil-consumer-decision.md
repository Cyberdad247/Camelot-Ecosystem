# ADR-0002 — grpc / abseil-cpp: vendored dependencies, consumer deferred

**Status:** Accepted (2026-08-15)
**Context:** `grpc` and `abseil-cpp` were vendored (Phase 0) as part of the
Camelot-Ecosystem constellation. They are C++ build dependencies, not services.
The architecture references gRPC-class transport (Bifrost `:4434` gRPC in
runtime state; §12 Bifrost protocol) and a 16 MB Northstar control kernel in
C/Rust (Appendix B), but **no code in this repository currently builds against
them**.

## Decision

Keep both as shallow, untracked reference copies in `KINETIC_ARMORY` with NO
build wiring. Do not add them to `CMakeLists.txt`, `Cargo.toml`, or any CI
pipeline. Revisit only when a concrete native consumer exists:

1. **Bifrost gRPC transport shim** — a native service speaking `:4434` gRPC
   (requires grpc + abseil + protobuf, built via CMake, release-tagged).
2. **LiteRT-LM build** — the vendored LiteRT-LM repo builds with CMake and
   declares its own dependencies; if a LiteRT inference adapter needs a local
   build, abseil/grpc may be pulled transitively rather than from these copies.
3. **Northstar control-kernel prototype** — any Rust/C kernel that chooses
   gRPC transport instead of the current HTTP/SSE + WebSocket surface.

## Consequences

- Repo stays clean of multi-hundred-MB C++ sources (consistent with ADR-0001).
- When a consumer lands, pin a grpc release tag and the matching abseil release
  (Abseil LTS pairs with grpc per its `CMakeLists.txt` version checks) and build
  from those tags — the shallow HEAD clones are reference only.
- The integration map (`docs/architecture/integrations.md`) marks Phase 1
  grpc/abseil as "consumer decision" resolved by this ADR.
