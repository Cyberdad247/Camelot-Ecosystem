//! Sandlock Process Cage Backend (Landlock / Seccomp / Process Isolation)
//! ======================================================================

use crate::instance::{CageState, KillReason, MicroVMInstance, SpawnConfig};
use anyhow::Result;

pub struct SandlockCage {
    config: SpawnConfig,
    state: CageState,
    current_memory_mb: usize,
}

impl SandlockCage {
    pub fn new(config: SpawnConfig) -> Self {
        Self {
            config,
            state: CageState::Pending,
            current_memory_mb: 16,
        }
    }

    pub fn start(&mut self) -> Result<()> {
        self.state = CageState::Running;
        Ok(())
    }

    pub fn update_memory(&mut self, mb: usize) {
        self.current_memory_mb = mb;
        if mb > self.config.max_memory_mb {
            let _ = self.kill(KillReason::MemoryExceeded);
        }
    }
}

impl MicroVMInstance for SandlockCage {
    fn cage_id(&self) -> &str {
        &self.config.cage_id
    }

    fn state(&self) -> CageState {
        self.state
    }

    fn memory_usage_mb(&self) -> usize {
        self.current_memory_mb
    }

    fn kill(&mut self, reason: KillReason) -> Result<()> {
        self.state = CageState::Killed { reason };
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Duration;

    #[test]
    fn sandlock_cage_lifecycle() {
        let config = SpawnConfig {
            cage_id: "cage_01".into(),
            command: "echo".into(),
            args: vec!["hello".into()],
            max_memory_mb: 256,
            timeout: Duration::from_secs(5),
            working_dir: ".".into(),
        };

        let mut cage = SandlockCage::new(config);
        assert_eq!(cage.state(), CageState::Pending);

        cage.start().expect("start cage");
        assert_eq!(cage.state(), CageState::Running);

        cage.update_memory(128);
        assert_eq!(cage.state(), CageState::Running);

        // Exceed memory limit -> auto-kills
        cage.update_memory(300);
        match cage.state() {
            CageState::Killed { reason } => assert_eq!(reason, KillReason::MemoryExceeded),
            _ => panic!("Expected killed by memory exceeded"),
        }
    }
}
