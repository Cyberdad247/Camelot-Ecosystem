//! Camelot Sovereign Persona & Cartridge Runtime (`camelot-runtime`)
//! ================================================================

pub mod cartridge;
pub mod concretizer;
pub mod persona;
pub mod persona_loader;
pub mod symbolect;

pub use cartridge::{CartridgeAdmission, CartridgeManifest};
pub use concretizer::{
    AbstractCartridgeSpec, CartridgeConcretizer, ConcreteCartridgeDAG, HostContext,
};
pub use persona::KnightPersona;
pub use persona_loader::{Persona, PersonaLoader};
pub use symbolect::{SymbolectEngine, SymbolectPacket};
