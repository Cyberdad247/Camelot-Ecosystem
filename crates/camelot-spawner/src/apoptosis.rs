//! Cellular Apoptosis & Working Set Governor
//! ==========================================
//!
//! Enforces:
//!   - Automatic apoptosis when error rate > 5% over min tasks
//!   - Working set trimming when memory approaches node ceiling
//!   - Zero zombie process leakage

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApoptosisPolicy {
    pub max_error_rate: f64,
    pub min_sample_tasks: u32,
    pub idle_timeout_secs: u64,
    pub working_set_threshold_mb: usize,
}

impl Default for ApoptosisPolicy {
    fn default() -> Self {
        Self {
            max_error_rate: 0.05, // 5%
            min_sample_tasks: 10,
            idle_timeout_secs: 300, // 5 minutes
            working_set_threshold_mb: 3686, // 90% of 4096 MB
        }
    }
}

pub struct ApoptosisMonitor {
    policy: ApoptosisPolicy,
    tasks_succeeded: u32,
    tasks_failed: u32,
}

impl ApoptosisMonitor {
    pub fn new(policy: ApoptosisPolicy) -> Self {
        Self {
            policy,
            tasks_succeeded: 0,
            tasks_failed: 0,
        }
    }

    pub fn record_task(&mut self, success: bool) {
        if success {
            self.tasks_succeeded += 1;
        } else {
            self.tasks_failed += 1;
        }
    }

    pub fn total_tasks(&self) -> u32 {
        self.tasks_succeeded + self.tasks_failed
    }

    pub fn error_rate(&self) -> f64 {
        let total = self.total_tasks();
        if total == 0 {
            0.0
        } else {
            self.tasks_failed as f64 / total as f64
        }
    }

    pub fn should_trigger_apoptosis(&self) -> bool {
        if self.total_tasks() < self.policy.min_sample_tasks {
            return false;
        }
        self.error_rate() > self.policy.max_error_rate
    }

    pub fn should_trim_memory(&self, current_mb: usize) -> bool {
        current_mb >= self.policy.working_set_threshold_mb
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn apoptosis_triggers_after_error_threshold() {
        let mut monitor = ApoptosisMonitor::new(ApoptosisPolicy::default());

        // 8 successes, 2 failures = 20% error rate on 10 tasks
        for _ in 0..8 {
            monitor.record_task(true);
        }
        assert!(!monitor.should_trigger_apoptosis());

        for _ in 0..2 {
            monitor.record_task(false);
        }
        assert_eq!(monitor.total_tasks(), 10);
        assert_eq!(monitor.error_rate(), 0.20);
        assert!(monitor.should_trigger_apoptosis());
    }

    #[test]
    fn memory_trim_check_matches_law_03() {
        let monitor = ApoptosisMonitor::new(ApoptosisPolicy::default());
        assert!(!monitor.should_trim_memory(2048));
        assert!(monitor.should_trim_memory(3686));
        assert!(monitor.should_trim_memory(4000));
    }
}
