//! Spawner Lifecycle Manager
//! =========================

use crate::instance::{CageState, KillReason, MicroVMInstance, SpawnConfig};
use crate::sandlock::SandlockCage;
use anyhow::{bail, Result};
use std::collections::HashMap;

pub struct SpawnerManager {
    cages: HashMap<String, Box<dyn MicroVMInstance>>,
    max_concurrent_cages: usize,
}

impl SpawnerManager {
    pub fn new(max_concurrent_cages: usize) -> Self {
        Self {
            cages: HashMap::new(),
            max_concurrent_cages,
        }
    }

    pub fn spawn(&mut self, config: SpawnConfig) -> Result<String> {
        if self.cages.len() >= self.max_concurrent_cages {
            bail!(
                "Cannot spawn cage '{}': reached concurrency limit of {}",
                config.cage_id,
                self.max_concurrent_cages
            );
        }

        let cage_id = config.cage_id.clone();
        let mut cage = SandlockCage::new(config);
        cage.start()?;
        self.cages.insert(cage_id.clone(), Box::new(cage));
        Ok(cage_id)
    }

    pub fn kill_cage(&mut self, cage_id: &str, reason: KillReason) -> Result<()> {
        if let Some(cage) = self.cages.get_mut(cage_id) {
            cage.kill(reason)?;
            Ok(())
        } else {
            bail!("Cage '{}' not found", cage_id);
        }
    }

    pub fn get_cage_state(&self, cage_id: &str) -> Option<CageState> {
        self.cages.get(cage_id).map(|c| c.state())
    }

    pub fn active_cage_count(&self) -> usize {
        self.cages
            .values()
            .filter(|c| matches!(c.state(), CageState::Running))
            .count()
    }

    pub fn total_memory_mb(&self) -> usize {
        self.cages.values().map(|c| c.memory_usage_mb()).sum()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Duration;

    #[test]
    fn spawner_manager_spawn_and_kill() {
        let mut manager = SpawnerManager::new(4);
        let config = SpawnConfig {
            cage_id: "cage_alpha".into(),
            command: "sleep".into(),
            args: vec!["10".into()],
            max_memory_mb: 512,
            timeout: Duration::from_secs(10),
            working_dir: ".".into(),
        };

        let id = manager.spawn(config).expect("spawn cage");
        assert_eq!(manager.active_cage_count(), 1);
        assert_eq!(manager.total_memory_mb(), 16);

        manager
            .kill_cage(&id, KillReason::HostDirective)
            .expect("kill cage");
        assert_eq!(manager.active_cage_count(), 0);
        assert_eq!(
            manager.get_cage_state(&id),
            Some(CageState::Killed {
                reason: KillReason::HostDirective
            })
        );
    }

    #[test]
    fn concurrency_limit_enforced() {
        let mut manager = SpawnerManager::new(1);
        let config1 = SpawnConfig {
            cage_id: "cage_1".into(),
            command: "cmd1".into(),
            args: vec![],
            max_memory_mb: 128,
            timeout: Duration::from_secs(5),
            working_dir: ".".into(),
        };
        let config2 = SpawnConfig {
            cage_id: "cage_2".into(),
            command: "cmd2".into(),
            args: vec![],
            max_memory_mb: 128,
            timeout: Duration::from_secs(5),
            working_dir: ".".into(),
        };

        assert!(manager.spawn(config1).is_ok());
        assert!(manager.spawn(config2).is_err());
    }
}
