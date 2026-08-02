use tokio::process::Command;
use tokio::time::{sleep, Duration};
use anyhow::{Result};
use serde::{Deserialize, Serialize};
use std::net::TcpStream;

#[derive(Debug, Serialize, Deserialize, Clone)]
enum BootTier {
    Core,
    Senses,
    Cloud,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct ServiceConfig {
    name: String,
    tier: BootTier,
    command: String,
    args: Vec<String>,
    required: bool,
    max_retries: u8,
    port: Option<u16>,
}

struct ServiceManager {
    services: Vec<ServiceConfig>,
}

impl ServiceManager {
    fn new() -> Self {
        let home = std::env::var("USERPROFILE").unwrap_or_else(|_| "C:\\Users\\vizio".to_string());
        let camelot_home = format!("{}\\CAMELOT_OS", home);
        Self {
            services: vec![
                ServiceConfig {
                    name: "CLIProxyAPI".to_string(),
                    tier: BootTier::Core,
                    command: format!("{}\\CLIProxyAPI\\cli-proxy-api.exe", home),
                    args: vec![],
                    required: true,
                    max_retries: 3,
                    port: Some(8080),
                },
                ServiceConfig {
                    name: "Kinetic Edge".to_string(),
                    tier: BootTier::Core,
                    command: format!("{}\\bin\\camelot-mcp-edge.exe", camelot_home),
                    args: vec![],
                    required: true,
                    max_retries: 3,
                    port: Some(3001),
                },
                ServiceConfig {
                    name: "Defense Grid".to_string(),
                    tier: BootTier::Core,
                    command: "go".to_string(),
                    args: vec!["run".to_string(), format!("{}\\cmd\\pulse\\heartbeat.go", home)],
                    required: true,
                    max_retries: 3,
                    port: None,
                },
                ServiceConfig {
                    name: "Morgana Bridge".to_string(),
                    tier: BootTier::Senses,
                    command: format!("{}\\01_KERNEL\\senses\\morgana_bridge\\target\\debug\\morgana_bridge.exe", camelot_home),
                    args: vec![],
                    required: true,
                    max_retries: 2,
                    port: Some(8001),
                },
            ],
        }
    }

    fn check_port(port: u16) -> bool {
        TcpStream::connect_timeout(&format!("127.0.0.1:{}", port).parse().unwrap(), Duration::from_millis(50)).is_ok()
    }

    async fn spawn_with_healing(svc: ServiceConfig) -> Result<bool> {
        if let Some(port) = svc.port {
            if Self::check_port(port) {
                println!("  \x1b[92m[OK]\x1b[0m {} already active on :{}", svc.name, port);
                return Ok(true);
            }
        }

        let mut retries = 0;
        while retries <= svc.max_retries {
            let mut cmd = Command::new(&svc.command);
            cmd.args(&svc.args);
            
            match cmd.spawn() {
                Ok(mut child) => {
                    sleep(Duration::from_millis(800)).await;
                    if let Some(port) = svc.port {
                        if Self::check_port(port) {
                            println!("  \x1b[92m[OK]\x1b[0m {} active", svc.name);
                            return Ok(true);
                        }
                    } else if child.try_wait()?.is_none() {
                        println!("  \x1b[92m[OK]\x1b[0m {} active", svc.name);
                        return Ok(true);
                    }
                }
                Err(e) => {
                    if retries == svc.max_retries {
                        println!("  \x1b[91m[FAIL]\x1b[0m {}: {}", svc.name, e);
                    }
                }
            }
            retries += 1;
            sleep(Duration::from_secs(1)).await;
        }
        Ok(false)
    }

    async fn boot_tier(&self, tier: BootTier) -> Result<()> {
        let mut handles = vec![];
        let target_discriminant = std::mem::discriminant(&tier);
        for svc in self.services.iter() {
            if std::mem::discriminant(&svc.tier) == target_discriminant {
                handles.push(tokio::spawn(Self::spawn_with_healing(svc.clone())));
            }
        }
        for h in handles {
            h.await??;
        }
        Ok(())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    println!("\x1b[95m\x1b[1m[RUSTCLAW] Initializing High-Velocity Self-Healing Boot...\x1b[0m");
    let manager = ServiceManager::new();
    
    println!("\x1b[1mPhase I: Core Awakening\x1b[0m");
    manager.boot_tier(BootTier::Core).await?;
    
    println!("\x1b[1mPhase II: Sensory Synthesis\x1b[0m");
    manager.boot_tier(BootTier::Senses).await?;
    
    println!("\n\x1b[92m[RUSTCLAW] Boot Sequence Completed.\x1b[0m");
    Ok(())
}
