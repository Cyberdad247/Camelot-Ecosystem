//! MicroVM Instance Trait & Status Definitions
//! ============================================

use serde::{Deserialize, Serialize};
use std::time::Duration;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum CageState {
    Pending,
    Booting,
    Running,
    Terminated { exit_code: i32 },
    Killed { reason: KillReason },
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum KillReason {
    Timeout,
    MemoryExceeded,
    ApoptosisFailure,
    HostDirective,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpawnConfig {
    pub cage_id: String,
    pub command: String,
    pub args: Vec<String>,
    pub max_memory_mb: usize,
    pub timeout: Duration,
    pub working_dir: String,
}

pub trait MicroVMInstance: Send + Sync {
    #[allow(dead_code)]
    fn cage_id(&self) -> &str;
    fn state(&self) -> CageState;
    #[allow(dead_code)]
    fn memory_usage_mb(&self) -> usize;
    fn kill(&mut self, reason: KillReason) -> anyhow::Result<()>;
}
