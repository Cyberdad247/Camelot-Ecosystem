//! Camelot Kinetic Spawner & MicroVM Gateway (`camelot-spawner`)
//! ==========================================================

pub mod apoptosis;
pub mod firecracker;
pub mod instance;
pub mod lease;
pub mod lifecycle;
pub mod pool;
pub mod sandlock;

pub use apoptosis::{ApoptosisMonitor, ApoptosisPolicy};
pub use firecracker::{BootSource, FirecrackerVMM, MachineConfig};
pub use instance::{CageState, KillReason, MicroVMInstance, SpawnConfig};
pub use lease::EphemeralVMLease;
pub use lifecycle::SpawnerManager;
pub use pool::{VMPool, DEFAULT_POOL_CAPACITY};
pub use sandlock::SandlockCage;
