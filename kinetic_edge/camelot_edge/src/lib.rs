//! Core contracts for the native Camelot Android edge supervisor.

mod client;
mod protocol;
mod state;

pub use client::TailnetClient;
pub use protocol::{signing_key_from_pkcs8_pem, Action, PolicySnapshot, SignedEnvelope, SignedPolicySnapshot};
pub use state::{EdgeState, OutboxItem, OutboxLimits};

#[derive(Debug)]
pub enum EdgeError {
    RejectedSnapshot,
    ForbiddenAction,
    InvalidSignatureEncoding,
    InvalidPublicKeyEncoding,
    InvalidPrivateKeyEncoding,
    InvalidSignature,
    CanonicalSerialization,
    Storage,
    OutboxFull,
    InvalidTailnetEndpoint,
    Transport,
}
