//! Anya Gate (L7 Zero-Bypass Modality Hypervisor)
//! ==============================================
//!
//! Enforces:
//!   - Anya First (Ingress sanitization & expansion)
//!   - Anya Last (Egress synthesis & token compression)
//!   - The Iron Gate: Code diffs > 10 lines require explicit operator approval

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum GateDecision {
    Permitted,
    RequiresHumanInTheLoop { reason: String, lines_changed: usize },
    Rejected { reason: String },
}

pub struct AnyaGate {
    max_unattended_lines: usize,
}

impl Default for AnyaGate {
    fn default() -> Self {
        Self {
            max_unattended_lines: 10,
        }
    }
}

impl AnyaGate {
    pub fn new(max_unattended_lines: usize) -> Self {
        Self {
            max_unattended_lines,
        }
    }

    /// Evaluates proposed code diff against the Iron Gate constraint.
    pub fn evaluate_diff(
        &self,
        lines_changed: usize,
        has_operator_token: bool,
    ) -> GateDecision {
        if lines_changed <= self.max_unattended_lines {
            GateDecision::Permitted
        } else if has_operator_token {
            GateDecision::Permitted
        } else {
            GateDecision::RequiresHumanInTheLoop {
                reason: format!(
                    "Proposed diff of {} lines exceeds {} line unattended ceiling without operator token",
                    lines_changed, self.max_unattended_lines
                ),
                lines_changed,
            }
        }
    }

    /// Sanitizes egress output: checks for suspicious secret/token leakage.
    pub fn sanitize_egress(&self, payload: &str) -> Result<String, String> {
        let suspicious_patterns = ["BEGIN PRIVATE KEY", "ghp_", "sk-proj-", "xoxb-"];
        for pattern in &suspicious_patterns {
            if payload.contains(pattern) {
                return Err(format!("Egress blocked by Anya Scythe: matched leak pattern '{}'", pattern));
            }
        }
        Ok(payload.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn small_diff_passes_unattended() {
        let gate = AnyaGate::default();
        let decision = gate.evaluate_diff(8, false);
        assert_eq!(decision, GateDecision::Permitted);
    }

    #[test]
    fn large_diff_requires_operator_token() {
        let gate = AnyaGate::default();
        let decision = gate.evaluate_diff(42, false);
        match decision {
            GateDecision::RequiresHumanInTheLoop { lines_changed, .. } => {
                assert_eq!(lines_changed, 42);
            }
            _ => panic!("Expected HITL requirement"),
        }

        let approved = gate.evaluate_diff(42, true);
        assert_eq!(approved, GateDecision::Permitted);
    }

    #[test]
    fn egress_scythe_blocks_secret_leak() {
        let gate = AnyaGate::default();
        let clean = "pub fn calculate() -> u32 { 42 }";
        assert!(gate.sanitize_egress(clean).is_ok());

        let leaked = "let key = \"ghp_abcdef1234567890\";";
        assert!(gate.sanitize_egress(leaked).is_err());
    }
}
