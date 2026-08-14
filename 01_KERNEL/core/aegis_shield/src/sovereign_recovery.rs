// SPDX-License-Identifier: MIT

use sha2::{Digest, Sha256};
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum RecoveryAction {
    Verified,
    Repaired,
    MissingMirror,
}

#[derive(Debug, Clone)]
pub struct SovereignRecovery {
    mirror: HashMap<String, Vec<u8>>,
    checksums: HashMap<String, String>,
}

impl SovereignRecovery {
    pub fn new() -> Self {
        Self {
            mirror: HashMap::new(),
            checksums: HashMap::new(),
        }
    }

    pub fn seed_mirror(&mut self, key: impl Into<String>, bytes: impl Into<Vec<u8>>) {
        let key = key.into();
        let bytes = bytes.into();
        self.checksums.insert(key.clone(), checksum(&bytes));
        self.mirror.insert(key, bytes);
    }

    pub fn verify_and_repair(
        &self,
        key: &str,
        live_bytes: &[u8],
    ) -> (RecoveryAction, Option<Vec<u8>>) {
        let Some(mirror_bytes) = self.mirror.get(key) else {
            return (RecoveryAction::MissingMirror, None);
        };

        let Some(expected) = self.checksums.get(key) else {
            return (RecoveryAction::MissingMirror, None);
        };

        if &checksum(live_bytes) == expected {
            (RecoveryAction::Verified, None)
        } else {
            (RecoveryAction::Repaired, Some(mirror_bytes.clone()))
        }
    }
}

impl Default for SovereignRecovery {
    fn default() -> Self {
        Self::new()
    }
}

pub fn verify_and_repair(
    recovery: &SovereignRecovery,
    key: &str,
    live_bytes: &[u8],
) -> (RecoveryAction, Option<Vec<u8>>) {
    recovery.verify_and_repair(key, live_bytes)
}

pub fn inject_activation_noise(values: &mut [f32], amplitude: f32, seed: u64) {
    if amplitude == 0.0 {
        return;
    }
    let mut state = seed ^ 0xA5A5_5A5A_D3C3_B4B4;
    for value in values {
        state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
        let unit = ((state >> 32) as f32) / (u32::MAX as f32);
        *value += ((unit * 2.0) - 1.0) * amplitude;
    }
}

fn checksum(bytes: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(bytes);
    hex::encode(hasher.finalize())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn repairs_corrupt_live_bytes_from_mirror() {
        let mut recovery = SovereignRecovery::new();
        recovery.seed_mirror("kernel", b"trusted".to_vec());

        let (action, repair) = recovery.verify_and_repair("kernel", b"tampered");
        assert_eq!(action, RecoveryAction::Repaired);
        assert_eq!(repair, Some(b"trusted".to_vec()));
    }
}

