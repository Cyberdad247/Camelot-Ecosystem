//! Sovereign Invariants Checker (INV-001..INV-015)
//! ==============================================

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Invariant {
    pub id: &'static str,
    pub title: &'static str,
    pub description: &'static str,
}

pub const KNOWN_INVARIANTS: &[Invariant] = &[
    Invariant {
        id: "INV-001",
        title: "Zero-Trust Unprivileged Execution",
        description: "All drone processes execute without root or ambient host privileges.",
    },
    Invariant {
        id: "INV-003",
        title: "Process-Level Isolation & Apoptosis",
        description: "Sub-processes operate inside bounded cages; failing cells self-terminate cleanly.",
    },
    Invariant {
        id: "INV-006",
        title: "Cryptographic Provenance Attestation",
        description: "All crystals and release artifacts possess deterministic SHA-256 and Ed25519 signatures.",
    },
    Invariant {
        id: "INV-014",
        title: "Global Memory Governance (Law 03)",
        description: "Nodes strictly constrained to 4096 MB RAM; Server constrained to 8192 MB RAM.",
    },
    Invariant {
        id: "INV-015",
        title: "Sub-50ms Process Lifecycle Turnaround",
        description: "MicroVM / process sandbox startup and tear-down latency must not exceed 50ms.",
    },
];

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InvariantReport {
    pub invariant_id: String,
    pub passed: bool,
    pub evidence: String,
}

pub struct InvariantChecker;

impl InvariantChecker {
    pub fn verify_all<F>(check_fn: F) -> Vec<InvariantReport>
    where
        F: Fn(&Invariant) -> (bool, String),
    {
        KNOWN_INVARIANTS
            .iter()
            .map(|inv| {
                let (passed, evidence) = check_fn(inv);
                InvariantReport {
                    invariant_id: inv.id.to_string(),
                    passed,
                    evidence,
                }
            })
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn known_invariants_enumerate_canonical_rules() {
        assert_eq!(KNOWN_INVARIANTS.len(), 5);
        assert!(KNOWN_INVARIANTS.iter().any(|i| i.id == "INV-014"));
    }

    #[test]
    fn verify_all_evaluates_suite() {
        let reports = InvariantChecker::verify_all(|inv| match inv.id {
            "INV-014" => (true, "4096 MB node ceiling active".into()),
            _ => (true, "Verified by test harness".into()),
        });
        assert_eq!(reports.len(), 5);
        assert!(reports.iter().all(|r| r.passed));
    }
}
