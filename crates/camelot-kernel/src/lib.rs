//! Camelot Sovereign Authority Kernel (`camelot-kernel`)
//! ====================================================
//!
//! Ultra-compact authority core (<16 MB memory footprint).
//! Enforces:
//!   - Global Law 03 (RAM ceilings: Node 4096 MB / Server 8192 MB)
//!   - Invariants INV-001..INV-015
//!   - Anya First & Last verification gate
//!   - Zero-trust capability leases
//!   - Immutable Blake3 SQLite Ledger receipts

pub mod anya_gate;
pub mod authority;
pub mod epoch;
pub mod invariants;
pub mod lease;
pub mod ledger;
pub mod memory_governor;
pub mod policy;
pub mod signature;

pub use anya_gate::{AnyaGate, GateDecision};
pub use authority::{AuthorityLevel, Lease, SovereignAuthority};
pub use epoch::EpochTracker;
pub use invariants::{Invariant, InvariantChecker, InvariantReport};
pub use lease::ExecutionLease;
pub use ledger::Ledger;
pub use memory_governor::{MemoryGovernor, MemoryProfile, NodeRole};
pub use policy::KernelPolicy;
pub use signature::SignatureVerifier;
