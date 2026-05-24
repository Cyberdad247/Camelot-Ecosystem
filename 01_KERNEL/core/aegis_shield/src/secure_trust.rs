use rand::{rngs::StdRng, Rng, SeedableRng};
use sha2::{Digest, Sha256};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TrustAgent {
    pub spiffe_id: String,
    pub tenant_id: String,
    token_hash: String,
}

impl TrustAgent {
    pub fn new(spiffe_id: impl Into<String>, tenant_id: impl Into<String>, token: &str) -> Self {
        Self {
            spiffe_id: spiffe_id.into(),
            tenant_id: tenant_id.into(),
            token_hash: hash_token(token),
        }
    }
}

pub fn verify_agent_token(agent: &TrustAgent, token: &str, expected_tenant: &str) -> bool {
    agent.tenant_id == expected_tenant
        && agent.spiffe_id.starts_with("spiffe://")
        && agent.token_hash == hash_token(token)
}

pub fn qjl_project(vector: &[f32], output_dims: usize, seed: u64) -> Vec<f32> {
    if output_dims == 0 || vector.is_empty() {
        return Vec::new();
    }

    let mut rng = StdRng::seed_from_u64(seed);
    let scale = (output_dims as f32).sqrt();
    (0..output_dims)
        .map(|_| {
            let mut sum = 0.0;
            for value in vector {
                let sign = if rng.gen_bool(0.5) { 1.0 } else { -1.0 };
                sum += value * sign;
            }
            sum / scale
        })
        .collect()
}

fn hash_token(token: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(token.as_bytes());
    hex::encode(hasher.finalize())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn verifies_spiffe_agent_and_projects_deterministically() {
        let agent = TrustAgent::new("spiffe://camelot/ns/core/sa/aegis", "tenant-a", "token");
        assert!(verify_agent_token(&agent, "token", "tenant-a"));
        assert!(!verify_agent_token(&agent, "wrong", "tenant-a"));

        let lhs = qjl_project(&[1.0, 2.0, 3.0], 2, 42);
        let rhs = qjl_project(&[1.0, 2.0, 3.0], 2, 42);
        assert_eq!(lhs, rhs);
    }
}

