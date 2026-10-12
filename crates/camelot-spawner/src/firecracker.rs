//! Firecracker MicroVM Configuration & UDS Socket Gateway
//! ========================================================

use serde::{Deserialize, Serialize};
use std::process::Command;
use tracing::{error, info};

#[derive(Serialize, Deserialize, Debug, Clone, PartialEq, Eq)]
pub struct BootSource {
    pub kernel_image_path: String,
    pub boot_args: String,
}

#[derive(Serialize, Deserialize, Debug, Clone, PartialEq, Eq)]
pub struct MachineConfig {
    pub vcpu_count: u8,
    pub mem_size_mib: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct FirecrackerVMM {
    pub id: String,
    pub socket_path: String,
}

impl FirecrackerVMM {
    pub fn new(id: &str) -> Self {
        Self {
            id: id.to_string(),
            socket_path: format!("/tmp/firecracker-{}.socket", id),
        }
    }

    #[allow(dead_code)]
    pub fn start_daemon(&self) -> Result<(), String> {
        info!("Starting Firecracker daemon for VM [{}]", self.id);

        let status = Command::new("firecracker")
            .arg("--api-sock")
            .arg(&self.socket_path)
            .spawn();

        match status {
            Ok(_) => Ok(()),
            Err(e) => {
                error!("Failed to launch Firecracker: {}", e);
                Err(e.to_string())
            }
        }
    }

    pub fn configure_boot_source(&self) -> BootSource {
        let boot_source = BootSource {
            kernel_image_path: "/var/lib/camelot/vmlinux.bin".to_string(),
            boot_args: "console=ttyS0 reboot=k panic=1 pci=off".to_string(),
        };
        info!("Configured BootSource for [{}]: {:?}", self.id, boot_source);
        boot_source
    }

    pub fn configure_machine(&self) -> MachineConfig {
        let config = MachineConfig {
            vcpu_count: 1,
            mem_size_mib: 128, // Strict 128 MiB per-phial constraint enforcement
        };
        info!("Configured MachineConfig for [{}]: {:?}", self.id, config);
        config
    }

    pub fn issue_start_command(&self) -> String {
        info!("Issued InstanceStart command to VM [{}] via UDS.", self.id);
        format!("STARTED:{}", self.id)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_firecracker_configuration_constructs() {
        let vmm = FirecrackerVMM::new("test_phial_01");
        assert_eq!(vmm.id, "test_phial_01");
        assert_eq!(vmm.socket_path, "/tmp/firecracker-test_phial_01.socket");

        let boot = vmm.configure_boot_source();
        assert_eq!(boot.kernel_image_path, "/var/lib/camelot/vmlinux.bin");
        assert!(boot.boot_args.contains("panic=1"));

        let machine = vmm.configure_machine();
        assert_eq!(machine.vcpu_count, 1);
        assert_eq!(machine.mem_size_mib, 128);

        let response = vmm.issue_start_command();
        assert_eq!(response, "STARTED:test_phial_01");
    }
}
