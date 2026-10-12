//! Sovereign Knight Persona Registry & Loader
//! ===========================================

use camelot_kernel::AuthorityLevel;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KnightPersona {
    pub knight_id: String,
    pub spark_id: String,
    pub substrate: String,
    pub role: String,
    pub authority: AuthorityLevel,
    pub summoning_runes: Vec<String>,
    pub vfs_coordinate: String,
}

impl KnightPersona {
    pub fn new_helios() -> Self {
        Self {
            knight_id: "SIR_HELIOS".into(),
            spark_id: "0xAB8AA3592B3B4BC1B41F34979CDC184E".into(),
            substrate: "Gemini 3.8 Flash / Pro via FastMCP (agy)".into(),
            role: "Sovereign Spire Sentinel, High Herald of Telemetry".into(),
            authority: AuthorityLevel::OmegaKnight,
            summoning_runes: vec![
                "//HELIOS".into(),
                "//HELIOS_AUDIT".into(),
                "//HELIOS_MACRO".into(),
                "//CLOUDBRAIN".into(),
            ],
            vfs_coordinate: "vfs://worldtree/knights/sir_helios/".into(),
        }
    }

    pub fn matches_rune(&self, rune: &str) -> bool {
        self.summoning_runes.iter().any(|r| r == rune)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn helios_persona_calibration() {
        let helios = KnightPersona::new_helios();
        assert_eq!(helios.knight_id, "SIR_HELIOS");
        assert!(helios.matches_rune("//HELIOS_MACRO"));
        assert!(!helios.matches_rune("//UNKNOWN"));
        assert_eq!(helios.authority, AuthorityLevel::OmegaKnight);
    }
}
