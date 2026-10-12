//! Monotonic Epoch Tracker for Kernel State Transitions
//! ====================================================

use serde::{Deserialize, Serialize};
use std::sync::atomic::{AtomicU64, Ordering};

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct EpochTracker {
    #[serde(skip)]
    current_epoch: AtomicU64,
}

impl EpochTracker {
    pub fn new(initial: u64) -> Self {
        Self {
            current_epoch: AtomicU64::new(initial),
        }
    }

    pub fn current(&self) -> u64 {
        self.current_epoch.load(Ordering::SeqCst)
    }

    pub fn advance(&self) -> u64 {
        self.current_epoch.fetch_add(1, Ordering::SeqCst) + 1
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn epoch_monotonic_advancement() {
        let tracker = EpochTracker::new(100);
        assert_eq!(tracker.current(), 100);
        assert_eq!(tracker.advance(), 101);
        assert_eq!(tracker.advance(), 102);
        assert_eq!(tracker.current(), 102);
    }
}
