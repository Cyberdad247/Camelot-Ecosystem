//! Camelot Sovereign Persona & Cartridge Runtime (`camelot-runtime`)
//! ================================================================

pub mod cartridge;
pub mod persona;
pub mod symbolect;

pub use cartridge::{CartridgeAdmission, CartridgeManifest};
pub use persona::KnightPersona;
pub use symbolect::{SymbolectEngine, SymbolectPacket};
