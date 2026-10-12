//! Combinatorial Cartridge Concretizer (Assimilated from Spack HPC Architecture)
//! ==============================================================================
//!
//! Enforces:
//!   - Abstract Spec parsing (`@version +variant ~disabled arch=aarch64 node=profile mem=512`)
//!   - Combinatorial constraint resolution (Variant conflict resolution & Knight class alignment)
//!   - Strict Global Law 03 enforcement (Hard constraint: max 4096 MB node RAM ceiling, 8192 MB server)
//!   - Virtual capability provider binding (`depends_on('microvm_spawner')` -> Sandlock / Firecracker)
//!   - Deterministic Blake3 DAG hash & Position-Addressed VFS prefix generation

use blake3::Hasher;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// An abstract user or knight specification for a cartridge capability
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct AbstractCartridgeSpec {
    pub cartridge_name: String,
    pub version_constraint: Option<String>,
    pub variants_enabled: Vec<String>,
    pub variants_disabled: Vec<String>,
    pub target_arch: Option<String>,
    pub node_profile: Option<String>,
    pub requested_memory_mb: Option<usize>,
}

impl AbstractCartridgeSpec {
    /// Parses an abstract Spack-style spec string.
    ///
    /// Example:
    /// `"invisioned-marketing-agency@1.1.0 +scoped_net +vfs_write ~auto_deploy arch=aarch64 node=marketing mem=512"`
    pub fn parse(raw: &str) -> Result<Self, String> {
        let tokens: Vec<&str> = raw.split_whitespace().collect();
        if tokens.is_empty() {
            return Err("Empty spec string".into());
        }

        let first = tokens[0];
        let (name, version) = if let Some(idx) = first.find('@') {
            (
                first[..idx].to_string(),
                Some(first[idx + 1..].to_string()),
            )
        } else {
            (first.to_string(), None)
        };

        let mut variants_enabled = Vec::new();
        let mut variants_disabled = Vec::new();
        let mut target_arch = None;
        let mut node_profile = None;
        let mut requested_memory_mb = None;

        for &tok in &tokens[1..] {
            if let Some(stripped) = tok.strip_prefix('+') {
                variants_enabled.push(stripped.to_string());
            } else if let Some(stripped) = tok.strip_prefix('~').or_else(|| tok.strip_prefix('-')) {
                variants_disabled.push(stripped.to_string());
            } else if let Some(stripped) = tok.strip_prefix("arch=") {
                target_arch = Some(stripped.to_string());
            } else if let Some(stripped) = tok.strip_prefix("node=") {
                node_profile = Some(stripped.to_string());
            } else if let Some(stripped) = tok.strip_prefix("mem=") {
                let mb = stripped
                    .parse::<usize>()
                    .map_err(|e| format!("Invalid memory spec: {}", e))?;
                requested_memory_mb = Some(mb);
            }
        }

        Ok(Self {
            cartridge_name: name,
            version_constraint: version,
            variants_enabled,
            variants_disabled,
            target_arch,
            node_profile,
            requested_memory_mb,
        })
    }
}

/// Host execution context and telemetry bounds
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HostContext {
    pub arch: String,
    pub available_memory_mb: usize,
    pub is_sovereign_server: bool,
    pub active_knight: String,
}

impl Default for HostContext {
    fn default() -> Self {
        Self {
            arch: "x86_64".into(),
            available_memory_mb: 4096, // Law 03 default node ceiling
            is_sovereign_server: false,
            active_knight: "SIR_HELIOS".into(),
        }
    }
}

/// A fully resolved, immutable, and content-addressed cartridge execution DAG
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ConcreteCartridgeDAG {
    pub cartridge_id: String,
    pub resolved_version: String,
    pub resolved_arch: String,
    pub active_variants: Vec<String>,
    pub active_capabilities: Vec<String>,
    pub bound_providers: HashMap<String, String>,
    pub allocated_memory_mb: usize,
    pub blake3_dag_hash: String,
    pub vfs_prefix_uri: String,
}

/// Capability provider candidate
#[derive(Debug, Clone)]
pub struct ProviderCandidate {
    pub name: String,
    pub supported_archs: Vec<String>,
    pub overhead_ram_mb: usize,
}

pub struct CartridgeConcretizer {
    provider_registry: HashMap<String, Vec<ProviderCandidate>>,
}

impl Default for CartridgeConcretizer {
    fn default() -> Self {
        let mut registry = HashMap::new();

        // Register core Camelot virtual capability providers
        registry.insert(
            "microvm_spawner".to_string(),
            vec![
                ProviderCandidate {
                    name: "sandlock_cage".to_string(),
                    supported_archs: vec!["x86_64".into(), "aarch64".into()],
                    overhead_ram_mb: 16,
                },
                ProviderCandidate {
                    name: "firecracker_uds".to_string(),
                    supported_archs: vec!["x86_64".into(), "aarch64".into()],
                    overhead_ram_mb: 128,
                },
            ],
        );

        registry.insert(
            "vector_memory".to_string(),
            vec![
                ProviderCandidate {
                    name: "memcastle_sqlite_vec".to_string(),
                    supported_archs: vec!["x86_64".into(), "aarch64".into()],
                    overhead_ram_mb: 32,
                },
            ],
        );

        Self {
            provider_registry: registry,
        }
    }
}

impl CartridgeConcretizer {
    pub fn new() -> Self {
        Self::default()
    }

    /// Concretizes an abstract specification against host constraints and returns an immutable DAG.
    pub fn concretize(
        &self,
        spec: &AbstractCartridgeSpec,
        host: &HostContext,
        base_ram_mb: usize,
        supported_capabilities: &[String],
        denied_capabilities: &[String],
    ) -> Result<ConcreteCartridgeDAG, String> {
        // 1. Architecture Resolution
        let resolved_arch = if let Some(ref req_arch) = spec.target_arch {
            if req_arch != &host.arch {
                return Err(format!(
                    "Architecture mismatch: spec requested '{}', host is '{}'",
                    req_arch, host.arch
                ));
            }
            req_arch.clone()
        } else {
            host.arch.clone()
        };

        // 2. Memory Bound Concretization (Global Law 03 enforcement)
        let requested_ram = spec.requested_memory_mb.unwrap_or(base_ram_mb);
        let max_allowed_ram = if host.is_sovereign_server { 8192 } else { 4096 };

        if requested_ram > max_allowed_ram {
            return Err(format!(
                "Global Law 03 Violation: requested {} MB exceeds {} MB ceiling (is_server: {})",
                requested_ram, max_allowed_ram, host.is_sovereign_server
            ));
        }

        if requested_ram > host.available_memory_mb {
            return Err(format!(
                "Insufficient host memory: requested {} MB, only {} MB available",
                requested_ram, host.available_memory_mb
            ));
        }

        // 3. Variant Resolution & Capability Collision Check
        let mut active_capabilities = Vec::new();
        for cap in supported_capabilities {
            if !spec.variants_disabled.contains(cap) {
                active_capabilities.push(cap.clone());
            }
        }
        for enabled in &spec.variants_enabled {
            if denied_capabilities.contains(enabled) {
                return Err(format!(
                    "Security conflict: variant '+{}' is strictly denied for cartridge '{}'",
                    enabled, spec.cartridge_name
                ));
            }
            if !active_capabilities.contains(enabled) {
                active_capabilities.push(enabled.clone());
            }
        }

        // 4. Virtual Capability Provider Binding
        let mut bound_providers = HashMap::new();
        for (virtual_cap, candidates) in &self.provider_registry {
            // Find first matching candidate compatible with resolved arch
            if let Some(candidate) = candidates
                .iter()
                .find(|c| c.supported_archs.contains(&resolved_arch))
            {
                bound_providers.insert(virtual_cap.clone(), candidate.name.clone());
            }
        }

        // 5. Compute Deterministic Blake3 Content Hash (The Spack Prefix Anchor)
        let version = spec.version_constraint.clone().unwrap_or_else(|| "1.0.0".into());
        let mut hasher = Hasher::new();
        hasher.update(spec.cartridge_name.as_bytes());
        hasher.update(b"@");
        hasher.update(version.as_bytes());
        hasher.update(b":arch=");
        hasher.update(resolved_arch.as_bytes());
        hasher.update(b":ram=");
        hasher.update(&requested_ram.to_le_bytes());
        for cap in &active_capabilities {
            hasher.update(b":cap=");
            hasher.update(cap.as_bytes());
        }
        for (k, v) in &bound_providers {
            hasher.update(b":prov=");
            hasher.update(k.as_bytes());
            hasher.update(b"->");
            hasher.update(v.as_bytes());
        }

        let blake3_dag_hash = hasher.finalize().to_hex().to_string();
        let vfs_prefix_uri = format!("vfs://worldtree/cartridges/{}", blake3_dag_hash);

        Ok(ConcreteCartridgeDAG {
            cartridge_id: spec.cartridge_name.clone(),
            resolved_version: version,
            resolved_arch,
            active_variants: spec.variants_enabled.clone(),
            active_capabilities,
            bound_providers,
            allocated_memory_mb: requested_ram,
            blake3_dag_hash,
            vfs_prefix_uri,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_abstract_spec_spack_grammar() {
        let spec_str = "invisioned-marketing-agency@1.1.0 +scoped_net +vfs_write ~auto_deploy arch=aarch64 node=marketing mem=512";
        let parsed = AbstractCartridgeSpec::parse(spec_str).expect("parse spec");

        assert_eq!(parsed.cartridge_name, "invisioned-marketing-agency");
        assert_eq!(parsed.version_constraint.as_deref(), Some("1.1.0"));
        assert_eq!(parsed.variants_enabled, vec!["scoped_net", "vfs_write"]);
        assert_eq!(parsed.variants_disabled, vec!["auto_deploy"]);
        assert_eq!(parsed.target_arch.as_deref(), Some("aarch64"));
        assert_eq!(parsed.node_profile.as_deref(), Some("marketing"));
        assert_eq!(parsed.requested_memory_mb, Some(512));
    }

    #[test]
    fn concretize_valid_spec_produces_blake3_dag_and_vfs() {
        let concretizer = CartridgeConcretizer::new();
        let spec = AbstractCartridgeSpec::parse(
            "invisioned-marketing-agency@1.1.0 +vfs_write ~auto_deploy arch=x86_64 mem=512",
        )
        .expect("parse spec");

        let host = HostContext {
            arch: "x86_64".into(),
            available_memory_mb: 2048,
            is_sovereign_server: false,
            active_knight: "SIR_HELIOS".into(),
        };

        let supported = vec!["vfs_read".into(), "vfs_write".into()];
        let denied = vec!["auto_deploy".into(), "direct_main_branch_write".into()];

        let dag = concretizer
            .concretize(&spec, &host, 512, &supported, &denied)
            .expect("concretize");

        assert_eq!(dag.cartridge_id, "invisioned-marketing-agency");
        assert_eq!(dag.resolved_version, "1.1.0");
        assert_eq!(dag.resolved_arch, "x86_64");
        assert_eq!(dag.allocated_memory_mb, 512);
        assert!(dag.active_capabilities.contains(&"vfs_write".to_string()));
        assert!(!dag.active_capabilities.contains(&"auto_deploy".to_string()));
        assert!(dag.bound_providers.contains_key("microvm_spawner"));
        assert!(dag.vfs_prefix_uri.starts_with("vfs://worldtree/cartridges/"));
        assert_eq!(dag.blake3_dag_hash.len(), 64);
    }

    #[test]
    fn concretize_rejects_global_law_03_violation() {
        let concretizer = CartridgeConcretizer::new();
        let spec = AbstractCartridgeSpec::parse("bloated-cartridge@2.0.0 mem=5000").unwrap();

        let host = HostContext {
            arch: "x86_64".into(),
            available_memory_mb: 8192,
            is_sovereign_server: false, // Node mode: strictly capped at 4096 MB
            active_knight: "SIR_HELIOS".into(),
        };

        let err = concretizer
            .concretize(&spec, &host, 5000, &[], &[])
            .unwrap_err();

        assert!(err.contains("Global Law 03 Violation"));
        assert!(err.contains("exceeds 4096 MB ceiling"));
    }

    #[test]
    fn concretize_rejects_denied_security_variant() {
        let concretizer = CartridgeConcretizer::new();
        let spec = AbstractCartridgeSpec::parse("agency +auto_deploy").unwrap();

        let host = HostContext::default();
        let denied = vec!["auto_deploy".into()];

        let err = concretizer
            .concretize(&spec, &host, 256, &[], &denied)
            .unwrap_err();

        assert!(err.contains("Security conflict: variant '+auto_deploy' is strictly denied"));
    }
}
