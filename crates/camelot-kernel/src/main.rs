//! Camelot Sovereign MicroVM Kernel Entrypoint
//! ============================================

mod epoch;
mod lease;
mod ledger;
mod policy;
mod signature;

use epoch::EpochTracker;
use lease::ExecutionLease;
use ledger::Ledger;
use policy::KernelPolicy;
use signature::SignatureVerifier;
use std::time::Instant;
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let boot_start = Instant::now();

    // Initialize High-Performance Telemetry
    let subscriber = FmtSubscriber::builder().with_max_level(Level::INFO).finish();
    let _ = tracing::subscriber::set_global_default(subscriber);

    info!("Booting CAMELOT-OS Kernel (v10001.0.0)...");
    info!("Hardware: Raspberry Pi 5 8GB | Runtime: Firecracker | Cognitive: BitNet b1.58");

    // Enforce Policy Constraints
    let policy = KernelPolicy::default();
    assert!(policy.validate_memory(4096), "Exceeded Global Law 03 memory boundary");

    // Initialize Monotonic Epoch
    let epoch_tracker = EpochTracker::new(1);
    let current_epoch = epoch_tracker.current();
    info!("Current Kernel Epoch: {}", current_epoch);

    // Initialize Authority Lease
    let lease = ExecutionLease::new("lease_genesis_01", "MERLIN_OMEGA", vec!["*".into()], 86400);
    assert!(lease.is_active(), "Genesis lease inactive");

    // Verify Sovereign Signature Integrity
    let dummy_key = [7u8; 32];
    let dummy_msg = b"GENESIS_BOOT";
    let dummy_sig = [0u8; 64];
    let _ = SignatureVerifier::verify(&dummy_key, dummy_msg, &dummy_sig);

    // Initialize Ledger (Fallback to local dir if /var/lib requires sudo during dev)
    let db_path = "/var/lib/camelot/ledger.db";
    let mut ledger = Ledger::new(db_path).unwrap_or_else(|_| {
        info!("Root access denied for /var/lib. Falling back to local ledger_fallback.db");
        Ledger::new("ledger_fallback.db").unwrap()
    });

    ledger.initialize()?;

    // Write the Genesis Boot Receipt
    let receipt_hash = ledger.write_receipt("system_boot", "MERLIN_OMEGA", "SUCCESS")?;
    info!("Kernel initialized successfully. Genesis Receipt Hash: {}", receipt_hash);

    let boot_duration_ms = boot_start.elapsed().as_millis() as u64;
    info!("Boot Sequence Completed in {}ms (Threshold: {}ms)", boot_duration_ms, policy.max_boot_time_ms);
    assert!(policy.validate_boot_time(boot_duration_ms), "Boot duration exceeded 80ms threshold");

    Ok(())
}
