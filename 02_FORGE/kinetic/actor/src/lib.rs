// =============================================================================
// 02_FORGE/kinetic/actor/src/lib.rs
// Camelot-OS WASM Actor Host — Wasmtime 30.x boundary.
//
// IRON-GATE-authorized Scope PR (see ../Cargo.toml header for full audit trail).
//
// Runtime role this is the *host* crate that loads and instantiates guest actor
// components compiled to `wasm32-wasip2`. It does NOT compile to wasm32 itself.
//
// Fix history (post-review):
//   - Policy C1: WASI 0.2 host-function registration is deferred to the
//     first-guest-actor follow-up PR. `wasmtime_wasi::add_to_linker` does
//     not type-check against a `wasmtime::component::Linker<T>` in Wasmtime
//     30.x canonical form; the registration belongs in a separate host
//     crate that owns the per-knight bindings.
//   - Policy M1 review: `Config::max_memory` was removed in Wasmtime 30.x.
//     The 64 MB cap from `02_FORGE/cartridge/digital_factory_v4000_ascended/Router.md`
//     item 2 is enforced per-Memory at instantiation
//     (`wasmtime::Memory::new_with_limits(...)`), not at the engine level.
//     The DEFAULT_LINEAR_MEMORY_BYTES constant below is the canonical plugin
//     point for downstream callers.
//   - Policy M2 review: removed the empty cfg-gated target block.
//
// Verified Wasmtime ≥30 APIs only (all still public in 30.0.2):
//   * wasmtime::Engine                       solo / multi-thread setups
//   * wasmtime::Config::new                  builder
//   * wasmtime::Store                        per-instance state
//   * wasmtime::component::Linker::<T>::new  component-model linker (no host fns yet)
//   * wasmtime::component::Component::deserialize(bytes) — RENAMED in 30.x
//   * wasmtime::component::bindgen!          typed guest bindings (planned)
// =============================================================================

use anyhow::Result;
use wasmtime::component::{Component, Linker};
use wasmtime::{Config, Engine};

/// Default 64 MB linear-memory cap. Canonized by `Router.md` item 2.
///
/// **ASPIRATIONAL enforcement** in this Iron-Gate stub. Wasmtime 30.x removed
/// `Config::max_memory`; the canonical enforcement point is per-Memory at
/// instance construction via `wasmtime::Memory::new_with_limits(64 MB, None)`
/// PLUS a `wasmtime::ResourceLimiter` attached to the Store. This crate
/// exposes the constant for downstream callers but does NOT enforce it here.
///
/// Tracking TODO: route cap enforcement into the first-guest-actor follow-up
/// PR alongside the `wasmtime_wasi::p2::add_to_linker_async` host registration.
pub const DEFAULT_LINEAR_MEMORY_BYTES: u64 = 64 * 1024 * 1024;

/// Errors specific to actor host wiring. Wraps wasmtime error messages so
/// callers can keep a stable error type without pinning the wasmtime version.
#[derive(thiserror::Error, Debug)]
pub enum ActorHostError {
    #[error("wasmtime configuration error: {0}")]
    WasmtimeConfig(String),

    #[error("component deserialize error: {0}")]
    Component(String),
}

/// Host-side wiring of a single Wasmtime engine + linker. One `ActorHost`
/// per process is the typical pattern; multiple stores derive cheaply from
/// the same `Engine` (for parallelism and DAG pre-warming).
pub struct ActorHost {
    engine: Engine,
}

impl ActorHost {
    /// Build a new host with default configuration for the WASI 0.2 /
    /// Component Model target family (`wasm32-wasip2`).
    ///
    /// Note: the 64 MB linear-memory cap from Router.md item 2 is *not* set
    /// here because Wasmtime 30.x removed `Config::max_memory`. Downstream
    /// callers enforce the cap per-Memory when building stores; see
    /// `Linker::instantiate_with_memories` or `Instance::new_with_limiter`.
    pub fn new() -> Result<Self, ActorHostError> {
        let mut config = Config::new();
        config.wasm_component_model(true).async_support(true);
        let engine =
            Engine::new(&config).map_err(|e| ActorHostError::WasmtimeConfig(e.to_string()))?;
        Ok(Self { engine })
    }

    /// Borrow the underlying engine. Stores derive cheaply from this reference.
    pub fn engine(&self) -> &Engine {
        &self.engine
    }

    /// Build a fresh linker bound to the host's engine.
    ///
    /// Currently does NOT register WASI 0.2 host functions: the camelot-side
    /// host-impl trait (filesystem, clock, random, etc.) lives in a
    /// downstream crate, registered there against this linker. Defer until
    /// first guest actor is wired.
    pub fn linker<U: 'static>(&self, _state: U) -> Result<Linker<U>, ActorHostError> {
        Ok(Linker::new(&self.engine))
    }

    /// Load (and validate) a guest component payload from raw wasm32-wasip2 bytes.
    /// Does NOT instantiate it — the caller wires a Store + Linker + instance.
    pub fn load_component(&self, bytes: &[u8]) -> Result<Component, ActorHostError> {
        // SAFETY: the caller MUST pass a valid wasm component-model module; the
        // Engine MUST have been created with `wasm_component_model(true)` (see
        // ActorHost::new). Wasmtime validates module soundness at instance
        // instantiation, NOT at deserialize — deserialization is unsafe because
        // byte-level structural validity is not enforced at this API boundary.
        unsafe { Component::deserialize(&self.engine, bytes) }
            .map_err(|e| ActorHostError::Component(e.to_string()))
    }
}

/// Loose convenience wrapper that loads a component without registering
/// host functions. Returns `(Component, Linker<()>)` ready for instantiation.
/// Pre-merge TODO: register WASI 0.2 host-fn impls via `wasmtime_wasi::p2::add_to_linker_async`
/// once the first guest actor lands.
pub fn prepare_component(engine: &Engine, wasm: &[u8]) -> Result<(Component, Linker<()>), ActorHostError> {
    // SAFETY: caller MUST pass a valid wasm component-model module; Engine is
    // host-trusted. Full contract documented on ActorHost::load_component above.
    let component = unsafe { Component::deserialize(engine, wasm) }
        .map_err(|e| ActorHostError::Component(e.to_string()))?;
    let linker = Linker::<()>::new(engine);
    Ok((component, linker))
}

// -----------------------------------------------------------------------------
// Self-test  host target only (Windows MSVC). The wasm32-wasip1/p2 component
// payloads are not loaded by this crate, so we only verify that Engine::new
// (with component-model enabled) and Linker::new succeed, and that garbage
// bytes are rejected at deserialize time.
// -----------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use anyhow::Context;

    #[test]
    fn host_engine_constructs_with_component_model_enabled() -> Result<()> {
        let host = ActorHost::new().context("actor host construction")?;
        let _ = host.engine();
        Ok(())
    }

    #[test]
    fn linker_constructs_bare_without_wasi_registration() -> Result<()> {
        let host = ActorHost::new().context("actor host construction")?;
        let _linker = host
            .linker(())
            .context("linker must construct with bare state")?;
        Ok(())
    }

    #[test]
    fn prepare_component_rejects_invalid_bytes() {
        let host = ActorHost::new().expect("host construction");
        let result = prepare_component(host.engine(), b"not-a-wasm-binary");
        assert!(result.is_err(), "garbage bytes must be rejected");
    }
}
