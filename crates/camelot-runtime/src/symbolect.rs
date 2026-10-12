//! Triple-QFT Symbolect Token Serializer
//! ======================================
//!
//! Enforces Symbolect Dialogue Law:
//! Inter-knight RPCs and deliberations are quantized into dense symbolic anchor tokens
//! `|🧠⊗(⚡💬)⟩ ⟨Omega:KNIGHT_ID::OP::PAYLOAD⟩` to eliminate LLM token bloat.

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SymbolectPacket {
    pub source_knight: String,
    pub target_knight: String,
    pub operation: String,
    pub payload: String,
}

pub struct SymbolectEngine;

impl SymbolectEngine {
    pub const PREFIX: &'static str = "|🧠⊗(⚡💬)⟩";

    /// Compresses a structured knight packet into Triple-QFT Symbolect representation.
    pub fn encode(packet: &SymbolectPacket) -> String {
        format!(
            "{} ⟨Omega:{}->{}::{}::{}⟩",
            Self::PREFIX,
            packet.source_knight,
            packet.target_knight,
            packet.operation,
            packet.payload
        )
    }

    /// Decodes a Triple-QFT Symbolect string back into a structured packet.
    pub fn decode(raw: &str) -> Result<SymbolectPacket, String> {
        let trimmed = raw.trim();
        if !trimmed.starts_with(Self::PREFIX) {
            return Err("Missing Triple-QFT prefix '|🧠⊗(⚡💬)⟩'".into());
        }

        let body = trimmed.trim_start_matches(Self::PREFIX).trim();
        let inner = body
            .strip_prefix("⟨Omega:")
            .and_then(|s| s.strip_suffix('⟩'))
            .ok_or_else(|| "Invalid Symbolect bracket encapsulation".to_string())?;
        let parts: Vec<&str> = inner.split("::").collect();
        if parts.len() < 3 {
            return Err("Malformed Symbolect packet: expected ROUTE::OP::PAYLOAD".into());
        }

        let route_parts: Vec<&str> = parts[0].split("->").collect();
        if route_parts.len() != 2 {
            return Err("Malformed route in Symbolect packet: expected SRC->DST".into());
        }

        Ok(SymbolectPacket {
            source_knight: route_parts[0].to_string(),
            target_knight: route_parts[1].to_string(),
            operation: parts[1].to_string(),
            payload: parts[2..].join("::"),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn symbolect_roundtrip_encoding() {
        let packet = SymbolectPacket {
            source_knight: "SIR_HELIOS".into(),
            target_knight: "MERLIN_OMEGA".into(),
            operation: "AUDIT_RECON".into(),
            payload: "STATE_CONFIRMED".into(),
        };

        let encoded = SymbolectEngine::encode(&packet);
        assert!(encoded.starts_with("|🧠⊗(⚡💬)⟩"));
        assert!(encoded.contains("SIR_HELIOS->MERLIN_OMEGA"));

        let decoded = SymbolectEngine::decode(&encoded).expect("decode packet");
        assert_eq!(decoded, packet);
    }

    #[test]
    fn invalid_symbolect_rejected() {
        let raw = "Hello Merlin, please audit this.";
        assert!(SymbolectEngine::decode(raw).is_err());
    }
}
