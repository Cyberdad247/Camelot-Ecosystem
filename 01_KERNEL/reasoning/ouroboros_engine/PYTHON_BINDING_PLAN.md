# Ouroboros Engine — Rust ↔ Python Binding Plan

**Status:** Planning only. SQLite fallback remains the source of truth until the binding lands and Phase 1 verifies the wire format.

**Owner:** SIR_CODEX (Codex / Antigravity) — pending sovereign review of Rust↔Python security posture.
**Target crate:** `01_KERNEL/reasoning/ouroboros_engine`
**Shim collaborator:** `<repo>/ouroboros.py` (top-level Python shim introduced in the previous turn)

---

## 1. Disambiguation problem (must be addressed first)

The repo currently uses "Ouroboros" for **two unrelated systems**:

| Layer | Component | Purpose | Public API |
|---|---|---|---|
| Python | `03_VAULT/training/configs/ouroboros.py` (fronted by `<repo>/ouroboros.py` shim) | SQLite-backed execution ledger for Camelot boot/dispatcher | `log_execution`, `get_history`, `get_stats`, `export_all` |
| Rust | `01_KERNEL/reasoning/ouroboros_engine` | Mamba-2 / BitNet 1.58b / KV prefetcher / TrellisPool neural compression engine | `OuroborosEngine::new(...)`, `submit_prefetch_sqe`, `poll_and_dequantize`, `mamba_forward`, `quantize_1_58b`, `compress_to_latent`, `trellis::TrellisPool` |

These share only the `ouroboros_` prefix. They do **not** exchange data today.

The user's question — *"the Python shim can thinly delegate to compiled Rust instead of SQLite"* — is therefore one of two possible architectural intents:

- **(A) Cross-system bridging** — pretend the Mamba engine has logging methods. *Semantically wrong — no logging API exists in the Rust crate.*
- **(B) Extend the Rust crate** — add a `ledger` module inside `ouroboros_engine` that owns the same persistence methods as the Python SQLite layer, expose them via PyO3, and let the Python shim dispatch. *Architecturally cleaner: one crate is the source of truth for both RAM compression and execution ledger.*
- **(C) Leave Python SQLite alone** — build a *separate* Rust↔Python bridge just for the engine consumers (`mamba_forward`, `prefetcher`, etc.). `ouroboros_loop_starter.py` already implies these consumers are planned, but the bridge has nothing to do with the Python logger.

**Disposition: Option (B).** Camelot's long-term architecture positions Ouroboros as a **unified hybrid memory system** — the same system that compresses hot RAM (Mamba / Trellis) becomes the high-speed ingest for agent execution episodes. The Rust crate's existing ring-buffer primitives (`src/prefetcher.rs::RingBuffer`) and the Python logger's contract (`log_execution` → stats roll-up) share enough structure to converge.

---

## 2. Migration ladder (three additive phases)

### Phase 1 — Shadow mode (additive)

- Add `pyo3 = "0.22"` to `ouroboros_engine/Cargo.toml` behind `#[cfg(feature = "pyo3")]`.
- Build the Python wheel with `maturin build --release --features pyo3`.
- The root `<repo>/ouroboros.py` shim **imports** `ouroboros_engine` for side-effect, **does not use** any of its symbols, and continues to dispatch all reads / writes through the SQLite path.
- Validation: `cargo test --quiet` still PASSES (the Rust-side tests do not require the Python build). `_targeted_python_tests` still PASSES (Python shim unchanged from current behaviour).

### Phase 2 — Offload write path

- `ouroboros.py` reads `ouroboros_engine` symbols; if present, it calls the binding's `log_execution(directive, intent=None, domain=None, complexity, knight, status, result=None, duration_ms=0, files_created=None)` alongside the existing SQLite INSERT. The full arg list mirrors the §3 `#[pyo3(signature = (directive, intent=None, domain=None, complexity, knight, status, result=None, duration_ms=0, files_created=None))]` attribute verbatim — only `directive`, `complexity`, and `knight` are required at the Python call site; the rest default to `None` / `0`. The Python shim is the conversion boundary — it serializes `files_created` (a Python list) to a JSON string before invoking, matching the `Option<String>` shape declared on the Rust side. Reads stay SQLite.
- **Divergence contract:** if the binding call raises (poisoned `Mutex`, OOM during JSON serialise, etc.), the SQLite INSERT must STILL proceed; the binding failure is logged via `logging.warning` but never blocks the ledger write. The reverse would silently drop audit rows.- **Parity test:** add `tests/test_ouroboros_parity.py` that invokes 1000 `log_execution` calls with a sentinel prefix and asserts (a) SQLite row count == 1000, (b) Rust ring length == 1000 (queried via `ouroboros_engine.flush_pending()` — the §3 binding exposes this as `PyResult<u64>` already). Failure of either assertion blocks the Phase-2 cutover. This is the only way to detect silent skew between the two backing stores.

### Phase 3 — Replace reads with Rust in-memory ring + WAL

- A new `pub mod ledger` inside `ouroboros_engine` owns a Rust `Ring` of recent executions and a write-ahead log under `03_VAULT/memory/ouroboros/ouroboros.wal`.
- SQLite is removed from the Python shim; the shim becomes a literal forwarder.
- **Cold cutover & historical data policy:** explicit choice — read-only archive. The existing `03_VAULT/training/configs/ouroboros.db` is NOT migrated into the WAL; it is preserved as a historical read-only archive (the file path stays, but the Python shim stops writing to it). Backfill tools that need historical rows: read the SQLite `.db` directly via `sqlite3.Connection`. This refrains from a one-shot write-time migration that would inflate scope; the parity window between the two stores will reveal any discrepancy naturally.
- Validation: `pytest tests/test_ouroboros.py -q` PASS, history query latency at the 1000-row mark ≤ 250 µs (baseline computation deferred to Phase 3 itself).

---

## 3. Skeleton — concrete files

### `01_KERNEL/reasoning/ouroboros_engine/Cargo.toml` (diff)

```diff
@@ -3,4 +3,12 @@
 version = "0.1.0"
 edition = "2021"

+[lib]
+name = "ouroboros_engine"
+crate-type = ["cdylib", "rlib"]   # rlib keeps the existing cargo test path green

 [dependencies]
-# Future: pyo3, torch-sys
+pyo3 = { version = "0.23", features = ["extension-module", "abi3-py39"], optional = true }
+
+[features]
+default = []
+pyo3 = ["dep:pyo3"]
```

> **Why `optional` + feature flag?** The crate already participates in `_deep_rust_tests` (`cargo test --quiet` over the whole workspace). Adding a hard `pyo3` dep would force every test machine to have Python dev headers. Gating behind a feature keeps the existing green path intact.
>
> **Why `0.23` and not `0.22`?** PyO3 0.23 (Oct 2024) was the last stable release whose `abi3-py39` wheel matrix matches the Camelot-supported interpreter range (3.9–3.13). 0.22 was EOL by 2025-Q4. The §6 audit gate freezes the exact version in `Cargo.lock`; any bump to 0.24+ must repeat the audit cycle.

### `01_KERNEL/reasoning/ouroboros_engine/pyproject.toml` (new)

```toml
[build-system]
requires = ["maturin>=1.5,<2.0"]
build-backend = "maturin"

[project]
name = "ouroboros_engine"
requires-python = ">=3.9"   # matches the abi3-py39 wheel matrix above
dynamic = ["version"]

[tool.maturin]
features = ["pyo3"]
module-name = "ouroboros_engine"
```

### `01_KERNEL/reasoning/ouroboros_engine/src/lib.rs` (diff)

```diff
@@ -1,7 +1,36 @@
+#[cfg(feature = "pyo3")]
+use pyo3::prelude::*;
+
 pub mod prefetcher;
 pub mod quantizer;
 pub mod mamba;
 pub mod trellis;
+#[cfg(feature = "pyo3")]
+pub mod ledger;
+
+#[cfg(feature = "pyo3")]
+#[pyfunction]
+#[pyo3(signature = (directive, intent=None, domain=None, complexity, knight, status, result=None, duration_ms=0, files_created=None))]
+#[allow(clippy::too_many_arguments)]
+fn log_execution(
+    directive: String,
+    intent: Option<String>,
+    domain: Option<String>,
+    complexity: i64,
+    knight: String,
+    status: String,
+    result: Option<String>,
+    duration_ms: i64,
+    files_created: Option<String>,
+) -> PyResult<()> {
+    ledger::append(directive, intent, domain, complexity, knight, status, result, duration_ms, files_created)
+        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
+}
+
+#[cfg(feature = "pyo3")]
+#[pyfunction]
+fn trigger_pending_compression() -> PyResult<u64> {
+    ledger::flush_pending().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
+}
+
+#[cfg(feature = "pyo3")]
+#[pymodule]
+fn ouroboros_engine(m: &Bound<'_, PyModule>) -> PyResult<()> {
+    m.add_function(wrap_pyfunction!(log_execution, m)?)?;
+    m.add_function(wrap_pyfunction!(trigger_pending_compression, m)?)?;
+    Ok(())
+}
```

> `ouroboros_loop_starter.py`'s `_emit_threshold_cross` already emits `engine_target: "01_KERNEL/reasoning/ouroboros_engine"` — keep that contract intact. `trigger_pending_compression` is the daemon-side trigger the starter may call once the engine owns the WAL.

---

## 4. Risk register

1. **Third-party dep audit (mandatory before merge).** `pyo3 0.22` is the first external dep on this crate. *Per AGENTS.md (Genoma Evolution) the audit must precede addition.* Action: run `cargo audit` against `crates.io`-published advisory DB BEFORE merging Phase 1; freeze the exact `pyo3` version in `Cargo.lock`.
2. **GIL / threading deadlocks.** `ouroboros_loop_starter.py` polls in a daemon loop; Rust panics on GIL violation if any binding function acquires Python objects from a non-GIL thread. Mitigation: every Rust function that does NOT touch Python objects wraps its body in `py.allow_threads(|| ...)`. The `ledger::append` path is pure Rust and can release the GIL entirely.
3. **Workspace dependency drift.** Adding `pyo3` to one crate can change the resolved version for sibling workspace members. Mitigation: bump the resolution in root `Cargo.toml` once after Phase 1; `cargo update -p pyo3 --workspace` and commit the lockfile diff.
4. **Silent degradation on machines without Rust toolchain.** `maturin build` requires `rustc` + cargo + Python dev headers at install time. If absent, the Python shim must catch the *full* set of failure modes on `import ouroboros_engine` and continue dispatching through SQLite. Maturin-built wheels can fail with:
   - `ImportError` (module not on sys.path) — covered.
   - `OSError` (DLL load failure on Windows when `python3X.dll` is missing) — covered.
   - `RuntimeError` (ABI / interpreter-version mismatch between wheel and the running interpreter) — **commonly missed**.
   - `ValueError` (occasionally raised for ABI mismatches by older maturin).
   Catch all four in the shim with `except (ImportError, OSError, RuntimeError, ValueError)`. Fall back to a single-emit warning so the SQLite path is last-resort.
5. **`cargo test` breaks because Python.h is missing.** Adding `pyo3` as an `optional` dependency behind a feature GATE avoids this — the dependency is not compiled unless `cargo test --features pyo3` is invoked. Phase 1's matrix: `cargo test --quiet` (no feature) PASS; `maturin develop` (with feature) PASS. Two-track CI.

---

## 5. File diffs

### `<repo>/ouroboros.py` (the shim — Phase 1 idempotent injection)

```diff
@@ -52,6 +52,21 @@
     #      during its own load (or any helper it triggers does so), Python
     #      already finds the impl in sys.modules and skips re-execution.
     sys.modules[__name__] = impl
+
+    # Phase 1 (shadow mode): surface the Rust binding as a private attribute
+    # of the loaded impl so callers can opt in incrementally. We swallow
+    # ImportError AND OSError (the latter when python3X.dll is missing on
+    # Windows / maturin wheel was never built). On success, `_rust_engine`
+    # is a Python module exposing `log_execution` and
+    # `trigger_pending_compression`. On failure, it is None and the SQLite
+    # path stays authoritative.
+    try:
+        import ouroboros_engine as _oe  # noqa: F401
+    except (ImportError, OSError):
+        _oe = None
+    impl._rust_engine = _oe
+
     spec.loader.exec_module(impl)
```

### `01_KERNEL/reasoning/ouroboros_engine/src/ledger.rs` (new, behind feature gate)

```rust
// Phase 1 stub: pure in-memory ring of recent executions, no persistence yet.
// Phase 3 will add WAL under 03_VAULT/memory/ouroboros/ouroboros.wal.

use std::sync::Mutex;

// Use `std::sync::LazyLock` (stable since Rust 1.80) — no `once_cell` crate needed.
use std::sync::LazyLock;

#[derive(Default)]
pub struct Ledger {
    inner: Mutex<Vec<Entry>>,
}

pub struct Entry {
    pub directive: String,
    pub intent: Option<String>,
    pub domain: Option<String>,
    pub complexity: i64,
    pub knight: String,
    pub status: String,
    pub result: Option<String>,
    pub duration_ms: i64,
    pub files_created: Option<String>,
}

static LEDGER: LazyLock<Ledger> = LazyLock::new(Ledger::default);

pub fn append(
    directive: String, intent: Option<String>, domain: Option<String>,
    complexity: i64, knight: String, status: String, result: Option<String>,
    duration_ms: i64, files_created: Option<String>,
) -> Result<(), String> {
    let mut g = LEDGER.inner.lock().map_err(|e| e.to_string())?;
    g.push(Entry { directive, intent, domain, complexity, knight, status, result, duration_ms, files_created });
    Ok(())
}

pub fn flush_pending() -> Result<u64, String> {
    // Phase 3 will iterate the WAL buffer; Phase 1 returns the current ring size.
    let g = LEDGER.inner.lock().map_err(|e| e.to_string())?;
    Ok(g.len() as u64)
}
```

> We use `std::sync::LazyLock` (stable since Rust 1.80) — no third-party `once_cell` dependency needed. The `Mutex<Vec<Entry>>` is single-process; a multi-writer WAL will be introduced in Phase 3 via `parking_lot::Mutex` if the Phase-2 parity test surfaces contention.

---

## 6. Audit gate (per AGENTS.md)

Before Phase 1 merges:

1. Run `cargo audit` against the frozen `pyo3 0.23.x` advisory DB. **No HIGH/CRITICAL advisories accepted.**
2. Confirm the wheel builds on Windows (primary platform per `AGENTS.md`) AND Linux via `maturin build --release --find-interpreter --target …`.
3. `cargo test --quiet` (no feature) continues to PASS — the existing `_deep_rust_tests` in `_targeted_python_tests` is the canary.
4. **Workspace lint hygiene:** `cargo clippy --workspace --all-targets` and `cargo fmt --check --all` MUST both pass. The root `Cargo.toml` already sets `dead_code = "allow"`, `unused_variables = "allow"`, etc. on the workspace, but `#[cfg(feature = "pyo3")]` blocks must compile without triggering `unused_imports`/`unused_mut` warnings even when the no-feature path is taken.
5. Add an in-repo smoke test `01_KERNEL/reasoning/ouroboros_engine/tests/test_py_bindings.rs` gated `#[cfg(feature = "pyo3")]` that exercises a simple append + flush round-trip via a Python embedded interpreter (or via shelling out to `python -c "import ouroboros_engine; ouroboros_engine.log_execution(...)"`). Week-zero verification of the binding surface.

---

## 7. PQ-Crypto Audit Gate (extends §6) — Triage decision: option (b)+(c) hybrid

A consequence of the 2026-06-25 audit triage: the dependency family
`pqcrypto` / `pqcrypto-*` was unmaintained upstream (the PQClean project is
slated for archival) and triggered **9 RustSec `unmaintained` advisories**
against `kinetic_edge/pqcrypto` (the crate securing A2A channels between
Knights). The triage decision is documented in the Codex provenance ledger
under tag `[OUROBOROS_BINDING_PHASE1_AUDIT_PQCRYPTO_TRIAGE]`.

### Disposition (option b + option c hybrid)

The 9 advisories are INFO-category (`unmaintained`), not vulnerabilities; the
crate is **runtime-functional today**. Two paths were considered:

- **Option (a) — Replace with RustCrypto `ml-kem` + `ml-dsa`.** Attempted in
  this session; **rolled back** because crates.io reality (verified 2026-06-25)
  does not match what the docs-research pass assumed:
   - `ml-kem` latest publish is **0.3.2** (the audit pass assumed 0.2).
   - `ml-dsa` latest publish is **0.1.1** (the audit pass assumed 0.2).
  Both versions differ in trait surface (`Generate`, `Encapsulate`,
  `Decapsulate`, `Signer::try_sign` vs `sign`, `from_bytes` return shapes)
  from what the prior docs-research indicated. A clean migration requires
  a follow-up docs-research PR pass that pins the exact trait-import
  shapes per the *actual* 0.3.x and 0.1.x API. That pass is owned by
  SIR_CODEX and is now a tracked follow-up PR, not this gate.
- **Option (b)+(c) — Ignore list with rationale + expand audit gate.**
  Adopted in this PR.

### What is in place

1. **Code unchanged from baseline.** `kinetic_edge/pqcrypto/Cargo.toml`
   keeps `pqcrypto 0.17` + `pqcrypto-traits 0.3`. `lib.rs` keeps the
   original `pqcrypto::kem::kyber768` + `pqcrypto::sign::dilithium3`
   implementation. A header comment in both files documents the in-flight
   migration and the tag linking the rationale to the ledger.

2. **`.cargo/audit.toml` ignore list (workspace root).** The 9 RustSec IDs
   are listed in `[advisories].ignore` with a one-line rationale header
   explaining the INFO-category `unmaintained` status, the migration plan,
   the FIPS-stamped target family, and the ledger-tag reference.
   NOTE: cargo-audit v0.22.x rejects the `[warnings]` table; only
   `[advisories]` is recognised. The TOML conforms to that schema.

3. **`cargo audit --deny warnings` is now an establishing invariant.**
   Because the 9 INFO-category advisories are documented in
   `.cargo/audit.toml`, the gate `--deny warnings` PASSES for the
   current workspace. Any newly-introduced HIGH/CRITICAL advisory will
   fail the gate immediately.

4. **Release-cut criterion.** Any release tag touching `01_KERNEL/`
   or `kinetic_edge/` MUST invoke:

   ```bash
   cargo audit --deny warnings \
       --json | tee 03_VAULT/runtime_state/cargo_audit_release.json
   ```

   and the JSON must show zero advisories not in the ignore list.

5. **Forward migration — RustCrypto pure-Rust (deferred to follow-up PR).**
   The replacement target (when docs-research completes) is:

   | Family | Crate(s) | Status |
   |---|---|---|
   | Lightweight pure-Rust | `ml-kem 0.3.x` + `ml-dsa 0.1.x` | Future PR after trait-shape verification |
   | Formally verified | `libcrux` (Cryspen) | Future PR if a formal-verification mandate lands |
   | FIPS-backed binary | `aws-lc-rs` | Future PR if a downstream consumer requires the AWS-LC ABI |

   When that PR lands, the 9 entries in `.cargo/audit.toml`'s `[advisories]`
   list are removed (the dep is gone, so the ignore is moot), and the
   empty-list invariant from §6 (clippy/fmt/audit must remain warning-free)
   resumes being the gate without exemption.

### Re-introduction blind spot (known limitation)

Putting the 9 RUSTSEC IDs in `[advisories].ignore` masks any future
re-introduction of `pqcrypto-dilithium`, `pqcrypto-kyber`, etc. as
transitive deps — `cargo audit` will silently pass on a hypothetical new
`pqcrypto-dilithium 0.18.0` import because RUSTSEC-2024-0380 is already
in the ignore list. The header comment in `.cargo/audit.toml` flags this
as a regression-watch note, but **no enforcement is programmatic** in the
current setup. Future hardening (out of scope for this triage):

- Add a `[workspace.metadata.audit] ignore = []` plugin-style rule, or
- Replace `cargo-audit` with `cargo-deny`'s `bans = [{ name = "pqcrypto-*", ...}]`
  configuration (which CAN deny-by-crate-name), or
- Strip the 9 ignore entries at the moment a Codebuff daemon pans and the
  pqcrypto family re-emerges via a PR review check.

For now, the migration PR contract (described above) is the only enforced
mechanism: any PR that removes the 9 must, in the same commit, remove the
ignore-list entries.

---

## 8. Open questions (sovereign review)

- [ ] Does the Python SQLite layer stay canonical during Phase 1+2, with the Rust ring as a shadow buffer for memory events only? Or does the Rust ingestion become authoritative immediately on Phase 2? *Default: stays canonical — single source of truth for the audit trail.*
- [ ] Phase 3's WAL location `03_VAULT/memory/ouroboros/ouroboros.wal`: is that consistent with the King Arthur vault layout? Or should it be `03_VAULT/scratchpad/ouroboros/`?
- [ ] Should `ouroboros_loop_starter.py` directly call `ouroboros_engine.trigger_pending_compression()` after a threshold cross, or stay hands-off? The current Python emits an event and exits — adding a direct call would couple the daemon to the binding's install status.

---

## 9. Trace

- Authored by: SIR_CODEX (Codex / Antigravity)
- Source context: prior turn created `<repo>/ouroboros.py` top-level Python shim and resolved the orphan-imports problem for `from ouroboros import …`.
- Verification (planned, not yet executed): `cargo test --quiet`, `pytest 03_VAULT/training/configs/tests/test_ouroboros.py -q`, `camelot triage --deep --force-deep` (no FAILs introduced).
- Status: [OUROBOROS_BINDING_PLAN]
