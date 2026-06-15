// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
// Cartridge_Hephaestus — CLI entrypoint

use hephaestus::cartridge_knights::CognitiveCartridge;
use hephaestus::EngineeringCartridge;
use std::io::{self, Read};

fn main() {
    println!("[HEPHAESTUS] Cartridge_Hephaestus v1.0 — TDD_OR_DEATH active");

    let cartridge = EngineeringCartridge::forge();
    println!("[HEPHAESTUS] Identifier: {}", cartridge.identifier());
    println!("[HEPHAESTUS] Memory footprint: {}MB", cartridge.memory_footprint_mb());

    // Read source from stdin for pipeline use
    let mut payload = Vec::new();
    if io::stdin().read_to_end(&mut payload).is_ok() && !payload.is_empty() {
        match cartridge.execute(&payload) {
            Ok(_)  => println!("[HEPHAESTUS] ✅ Artifact crystallized."),
            Err(e) => eprintln!("[HEPHAESTUS] ❌ Gate failed: {}", e),
        }
    } else {
        println!("[HEPHAESTUS] No payload on stdin. Cartridge standing by.");
    }
}
