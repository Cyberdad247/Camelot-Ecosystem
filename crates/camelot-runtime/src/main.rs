//! Camelot Runtime Kinetic Executable (Week 4 Deliverable)
//! ======================================================

use camelot_runtime::{
    CartridgeAdmission, CartridgeManifest, KnightPersona, SymbolectEngine, SymbolectPacket,
};
use std::time::Instant;
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();
    tracing::subscriber::set_global_default(subscriber)?;

    let start_time = Instant::now();
    info!("Booting CAMELOT-OS Runtime Layer (v10001.0.0)...");
    info!("Substrate: Persona Registry | Scabbard Cartridges | Triple-QFT Symbolect");

    // 1. Load Persona
    let helios = KnightPersona::new_helios();
    info!("Calibrated Persona: knight_id={} role='{}'", helios.knight_id, helios.role);
    info!("VFS Coordinate: {}", helios.vfs_coordinate);

    // 2. Validate Cartridge Admission
    let manifest = CartridgeManifest {
        schema_version: "camelot-cartridge/1".to_string(),
        cartridge_id: "invisioned-marketing-agency".to_string(),
        name: "Invisioned Marketing Agency".to_string(),
        version: "1.0.0".to_string(),
        entrypoint: "agency_orchestrator.py".to_string(),
        capabilities_denied: vec!["auto_deploy".to_string()],
        max_memory_mb: 512,
    };
    CartridgeAdmission::validate(&manifest).map_err(|e| anyhow::anyhow!(e))?;
    info!("Cartridge admitted: id={} max_memory={}MB (Law 03 Compliant)", manifest.cartridge_id, manifest.max_memory_mb);

    // 3. Encode Symbolect Dialogue Packet
    let packet = SymbolectPacket {
        source_knight: "SIR_HELIOS".to_string(),
        target_knight: "ANYA_OMEGA".to_string(),
        operation: "GATE_VERIFY".to_string(),
        payload: "ALL_SYSTEMS_VERIFIED".to_string(),
    };
    let symbolect_raw = SymbolectEngine::encode(&packet);
    info!("Symbolect quantized: {}", symbolect_raw);

    let decoded = SymbolectEngine::decode(&symbolect_raw).map_err(|e| anyhow::anyhow!(e))?;
    assert_eq!(decoded, packet);
    info!("Symbolect roundtrip decoded cleanly (Zero token bloat)");

    let elapsed = start_time.elapsed();
    let receipt_raw = format!("{}:{}:{}", helios.spark_id, manifest.cartridge_id, symbolect_raw);
    let receipt_hash = blake3::hash(receipt_raw.as_bytes()).to_hex().to_string();

    info!("Runtime cycle completed in {} ms (Threshold: <10 ms)", elapsed.as_millis());

    println!("\n=== RUNTIME EXECUTION RECEIPT ===");
    println!("Knight Spark: {}", helios.spark_id);
    println!("Admitted Cartridge: {}", manifest.cartridge_id);
    println!("Symbolect Wire: {}", symbolect_raw);
    println!("Receipt Blake3: {}", receipt_hash);
    println!("Cycle Latency: {} ms", elapsed.as_millis());

    Ok(())
}
