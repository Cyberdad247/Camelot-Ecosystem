//! Memory Governor (Global Law 03 Implementation)
//! ==============================================
//!
//! Strict enforcement of memory boundaries:
//!   - Node ceiling:   4096 MB (Proactive eviction trigger: 3686 MB = 90%)
//!   - Server ceiling: 8192 MB (Proactive eviction trigger: 7372 MB = 90%)

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum NodeRole {
    DistributedNode,
    SovereignServer,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryProfile {
    pub role: NodeRole,
    pub max_ram_mb: usize,
    pub trim_threshold_mb: usize,
    pub current_working_set_mb: usize,
}

pub struct MemoryGovernor {
    role: NodeRole,
    max_ram_mb: usize,
    trim_threshold_mb: usize,
}

impl MemoryGovernor {
    pub fn new(role: NodeRole) -> Self {
        let (max_ram_mb, trim_threshold_mb) = match role {
            NodeRole::DistributedNode => (4096, 3686),
            NodeRole::SovereignServer => (8192, 7372),
        };
        Self {
            role,
            max_ram_mb,
            trim_threshold_mb,
        }
    }

    pub fn inspect(&self, current_mb: usize) -> MemoryVerdict {
        if current_mb > self.max_ram_mb {
            MemoryVerdict::CeilingBreach {
                current_mb,
                max_mb: self.max_ram_mb,
                excess_mb: current_mb - self.max_ram_mb,
            }
        } else if current_mb >= self.trim_threshold_mb {
            MemoryVerdict::RequiresTrim {
                current_mb,
                threshold_mb: self.trim_threshold_mb,
            }
        } else {
            MemoryVerdict::Compliant {
                current_mb,
                headroom_mb: self.max_ram_mb - current_mb,
            }
        }
    }

    pub fn role(&self) -> NodeRole {
        self.role
    }

    pub fn max_ram_mb(&self) -> usize {
        self.max_ram_mb
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum MemoryVerdict {
    Compliant { current_mb: usize, headroom_mb: usize },
    RequiresTrim { current_mb: usize, threshold_mb: usize },
    CeilingBreach { current_mb: usize, max_mb: usize, excess_mb: usize },
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn distributed_node_enforces_4gb_ceiling() {
        let gov = MemoryGovernor::new(NodeRole::DistributedNode);
        assert_eq!(gov.max_ram_mb(), 4096);

        // Under threshold: compliant
        match gov.inspect(2048) {
            MemoryVerdict::Compliant { headroom_mb, .. } => assert_eq!(headroom_mb, 2048),
            _ => panic!("Expected compliant"),
        }

        // Above 90% threshold: requires trim
        match gov.inspect(3700) {
            MemoryVerdict::RequiresTrim { threshold_mb, .. } => assert_eq!(threshold_mb, 3686),
            _ => panic!("Expected requires trim"),
        }

        // Above 4096 MB: ceiling breach
        match gov.inspect(4200) {
            MemoryVerdict::CeilingBreach { excess_mb, .. } => assert_eq!(excess_mb, 104),
            _ => panic!("Expected ceiling breach"),
        }
    }

    #[test]
    fn sovereign_server_allows_8gb() {
        let gov = MemoryGovernor::new(NodeRole::SovereignServer);
        assert_eq!(gov.max_ram_mb(), 8192);

        match gov.inspect(6000) {
            MemoryVerdict::Compliant { headroom_mb, .. } => assert_eq!(headroom_mb, 2192),
            _ => panic!("Expected compliant"),
        }
    }
}
