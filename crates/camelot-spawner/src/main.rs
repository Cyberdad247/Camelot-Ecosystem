//! Camelot MicroVM Spawner CLI & Daemon Binary
//! ============================================

mod apoptosis;
mod firecracker;
mod instance;
mod lease;
mod lifecycle;
mod output_trap;
mod pool;
mod sandlock;

use camelot_kernel::Ledger;
use lease::EphemeralVMLease;
use pool::VMPool;
use std::time::Instant;
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let boot_start = Instant::now();

    // Telemetry initialization
    let subscriber = FmtSubscriber::builder().with_max_level(Level::INFO).finish();
    let _ = tracing::subscriber::set_global_default(subscriber);

    info!("Initializing CAMELOT-OS MicroVM Spawner (v10001.0.0)...");
    info!("Hardware: Raspberry Pi 5 8GB | Runtime: Firecracker UDS | Protocol: 3.6GB Scarcity");

    // Initialize 5-Phial Pool (3.6GB Scarcity Protocol constraint)
    let mut pool = VMPool::new(5);
    let prewarmed = pool.prewarm_pool();
    info!("Pre-warmed {} Phial MicroVM slots in equilibrium pool", prewarmed);

    // Acquire Phial MicroVM from Pool
    let vm = pool.acquire_vm().expect("failed to acquire pre-warmed Phial");
    info!("Acquired Phial: {} (Socket: {})", vm.id, vm.socket_path);

    // Configure and issue instance start command
    let _boot = vm.configure_boot_source();
    let _machine = vm.configure_machine();
    let start_resp = vm.issue_start_command();
    info!("InstanceStart Response via UDS: {}", start_resp);

    // Bind Ephemeral Lease and execute MADV_DONTNEED cleanup
    let mut lease = EphemeralVMLease::new(&vm.id, "TASK_GENESIS_MICROVM", 80);
    let reclaim_token = lease.cleanup_and_reclaim();
    info!("Memory Reclaimed (Token: {})", reclaim_token);

    // Return Phial VM to equilibrium pool
    pool.release_vm(vm);
    info!("Returned Phial to pool. Pool available count: {}", pool.available_count());

    // Write Spawner Receipt to Kernel SQLite Ledger
    let db_path = "/var/lib/camelot/ledger.db";
    let mut ledger = Ledger::new(db_path).unwrap_or_else(|_| {
        info!("Falling back to local ledger_fallback.db for spawner receipts");
        Ledger::new("ledger_fallback.db").unwrap()
    });
    ledger.initialize()?;
    let receipt_hash = ledger.write_receipt("spawner_phial_cycle", "LUKAS_OMEGA", &reclaim_token)?;

    let duration_ms = boot_start.elapsed().as_millis() as u64;
    info!("MicroVM Spawner Cycle Completed in {}ms (Threshold: 80ms)", duration_ms);
    info!("Cryptographic Blake3 Spawner Receipt Hash: {}", receipt_hash);

    Ok(())
}
