//! Sandlock Process Cage Backend (Landlock / Seccomp / Process Isolation)
//! ======================================================================

use crate::instance::{CageState, KillReason, MicroVMInstance, SpawnConfig};
use crate::output_trap::{OutputTrap, OutputTrapConfig, TruncatedStream};
use anyhow::Result;

pub struct SandlockCage {
    config: SpawnConfig,
    state: CageState,
    current_memory_mb: usize,
    output_trap: OutputTrap,
}

impl SandlockCage {
    pub fn new(config: SpawnConfig) -> Self {
        Self::with_trap_config(config, OutputTrapConfig::default())
    }

    pub fn with_trap_config(config: SpawnConfig, trap_config: OutputTrapConfig) -> Self {
        Self {
            config,
            state: CageState::Pending,
            current_memory_mb: 16,
            output_trap: OutputTrap::new(trap_config),
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

    pub fn append_stdout(&mut self, chunk: &[u8]) {
        if self.output_trap.append_stdout(chunk) {
            let _ = self.kill(KillReason::OutputLimitExceeded);
        }
    }

    #[allow(dead_code)]
    pub fn append_stderr(&mut self, chunk: &[u8]) {
        if self.output_trap.append_stderr(chunk) {
            let _ = self.kill(KillReason::OutputLimitExceeded);
        }
    }

    pub fn stdout(&self) -> TruncatedStream {
        self.output_trap.finish_stdout()
    }

    #[allow(dead_code)]
    pub fn stderr(&self) -> TruncatedStream {
        self.output_trap.finish_stderr()
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

    #[test]
    fn sandlock_cage_output_trap_truncation_and_kill() {
        let config = SpawnConfig {
            cage_id: "cage_compiler_explorer".into(),
            command: "rustc".into(),
            args: vec!["--emit=asm".into()],
            max_memory_mb: 256,
            timeout: Duration::from_secs(5),
            working_dir: ".".into(),
        };

        let trap_config = OutputTrapConfig {
            max_bytes: 50,
            max_lines: 10,
        };

        let mut cage = SandlockCage::with_trap_config(config, trap_config);
        cage.start().expect("start cage");
        assert_eq!(cage.state(), CageState::Running);

        // Append 30 bytes -> under limit
        cage.append_stdout(b"Section .text\nglobal _start\n");
        assert_eq!(cage.state(), CageState::Running);

        // Append 40 bytes -> total 70 > 50 -> exceeds limit, triggers OutputLimitExceeded kill
        cage.append_stdout(b"_start:\n  mov rax, 60\n  mov rdi, 0\n  syscall\n");
        match cage.state() {
            CageState::Killed { reason } => assert_eq!(reason, KillReason::OutputLimitExceeded),
            _ => panic!("Expected killed by OutputLimitExceeded"),
        }

        let out = cage.stdout();
        assert!(out.is_truncated);
        assert!(out.text.contains("[Compiler Explorer Trap]"));
    }
}

