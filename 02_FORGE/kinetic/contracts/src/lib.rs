// 02_FORGE/kinetic/contracts/src/lib.rs
// MsgPack wire-format boundary structs for the WASM actor <-> ouroboros_engine <-> control_plane path.
// Iron-Gate scope PR member: minimal — serde derives + rmp-serde pack/unpack helpers. No ouroboros_engine dep.

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, Clone)] pub struct TriageRequestV1 { pub intent: String }
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct TriageScoreWireV1 {
    pub hitl_tier: String,
    pub risk_entropy: f32,
    pub cartridge_hint: String,
    pub assigned_knight: String,
    pub needs_human: bool,
}
#[derive(Serialize, Deserialize, Debug, Clone)] pub struct CartridgeSwitchRequestV1 { pub name: String }
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct CartridgeSwitchAckV1 {
    pub name: String,
    pub title: String,
    pub lead_knight: String,
    pub activated_at: f64,
}

pub fn pack<T: Serialize>(v: &T) -> Result<Vec<u8>, String> {
    rmp_serde::to_vec(v).map_err(|e| e.to_string())
}
pub fn unpack<'a, T: Deserialize<'a>>(b: &'a [u8]) -> Result<T, String> {
    rmp_serde::from_slice(b).map_err(|e| e.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn triage_request_roundtrip() {
        let r = TriageRequestV1 { intent: "build a foo".into() };
        let b = pack(&r).unwrap();
        let d: TriageRequestV1 = unpack(&b).unwrap();
        assert_eq!(d.intent, "build a foo");
    }
    #[test]
    fn switch_request_roundtrip() {
        let r = CartridgeSwitchRequestV1 { name: "ANT".into() };
        let b = pack(&r).unwrap();
        let d: CartridgeSwitchRequestV1 = unpack(&b).unwrap();
        assert_eq!(d.name, "ANT");
    }
}
