//! Scabbard Cartridge Admission & Manifest Verification
//! =====================================================

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CartridgeManifest {
    pub schema_version: String,
    pub cartridge_id: String,
    pub name: String,
    pub version: String,
    pub entrypoint: String,
    pub capabilities_denied: Vec<String>,
    pub max_memory_mb: usize,
}

pub struct CartridgeAdmission;

impl CartridgeAdmission {
    pub fn validate(manifest: &CartridgeManifest) -> Result<(), String> {
        if manifest.schema_version != "camelot-cartridge/1" {
            return Err(format!(
                "Invalid schema version: expected 'camelot-cartridge/1', got '{}'",
                manifest.schema_version
            ));
        }

        // Global Law 03 check: single cartridge must not exceed 4096 MB node ceiling
        if manifest.max_memory_mb > 4096 {
            return Err(format!(
                "Cartridge '{}' requested {} MB RAM, violating Global Law 03 (4096 MB max)",
                manifest.cartridge_id, manifest.max_memory_mb
            ));
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn valid_cartridge_admission() {
        let manifest = CartridgeManifest {
            schema_version: "camelot-cartridge/1".into(),
            cartridge_id: "invisioned-marketing-agency".into(),
            name: "Invisioned Marketing Agency".into(),
            version: "1.0.0".into(),
            entrypoint: "agency_orchestrator.py".into(),
            capabilities_denied: vec!["auto_deploy".into()],
            max_memory_mb: 512,
        };

        assert!(CartridgeAdmission::validate(&manifest).is_ok());
    }

    #[test]
    fn invalid_ram_ceiling_rejected() {
        let manifest = CartridgeManifest {
            schema_version: "camelot-cartridge/1".into(),
            cartridge_id: "bloated-cartridge".into(),
            name: "Bloated Cartridge".into(),
            version: "1.0.0".into(),
            entrypoint: "run.py".into(),
            capabilities_denied: vec![],
            max_memory_mb: 8192,
        };

        let err = CartridgeAdmission::validate(&manifest).unwrap_err();
        assert!(err.contains("violating Global Law 03"));
    }
}
