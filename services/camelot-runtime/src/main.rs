mod persona_loader;

use persona_loader::PersonaLoader;
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize High-Performance Telemetry
    let subscriber = FmtSubscriber::builder().with_max_level(Level::INFO).finish();
    tracing::subscriber::set_global_default(subscriber)?;

    info!("Booting Camelot-OS Cognitive Runtime Daemon (v10001.0.0)...");

    // Define the expected path for the sovereign cartridges
    let persona_path = "/opt/camelot-os/.agent/cartridges/merlin_omega.json";

    // Week 4 Execution: Load Persona from VFS
    let active_persona = PersonaLoader::load_from_disk(persona_path)?;

    // Simulate VM ID acquired from camelot-spawner (Week 2)
    let target_vm = "core-001";

    // Execute the cognitive injection across the hypervisor boundary
    PersonaLoader::inject_to_vm(&active_persona, target_vm);

    info!("Runtime daemon holding state. Ready to process execution telemetry.");

    Ok(())
}
