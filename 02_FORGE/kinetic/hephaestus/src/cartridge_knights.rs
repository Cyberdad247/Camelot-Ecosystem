// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
// SEPTEM REGNA Layer: L2_KINETIC

use serde::{Deserialize, Serialize};

/// The core trait all CAMELOT-OS cognitive cartridges must implement.
/// Every cartridge is a deterministic, sandboxed execution unit — not a chat wrapper.
pub trait CognitiveCartridge: Send + Sync {
    fn identifier(&self) -> &'static str;
    fn execute(&self, payload: &[u8]) -> Result<Vec<u8>, &'static str>;
    fn memory_footprint_mb(&self) -> f32;
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum CartridgeStatus {
    Forging,
    Active,
    Rejected,
    TddFailed,
    AstFractured,
    Crystallized,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CartridgeResult {
    pub status: CartridgeStatus,
    pub artifact_hash: String,
    pub memory_mb: f32,
    pub error: Option<String>,
}
