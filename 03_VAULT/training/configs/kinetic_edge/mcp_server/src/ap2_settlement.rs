// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
//!
//! AP2 Cryptographic Settlement — Agent-to-Agent Compute Payment Protocol
//!
//! Uses ed25519-dalek for signing provenance attestations and compute rental
//! transactions between autonomous agents. Every SARDA cycle produces a signed
//! settlement record that cannot be repudiated.
//!
//! Titanium Law: This MUST be Rust (Kinetic Purity). No Python settlement layer.

use ed25519_dalek::{Signer, SigningKey, Verifier, VerifyingKey, Signature};
use rand::rngs::OsRng;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

/// A single compute rental transaction between two agents.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transaction {
    /// Unique transaction ID (hex-encoded)
    pub tx_id: String,
    /// Source agent (the one paying / requesting compute)
    pub source_agent: String,
    /// Target agent (the one providing compute)
    pub target_agent: String,
    /// Compute units consumed (abstract measurement)
    pub compute_units: u64,
    /// ISO 8601 timestamp
    pub timestamp: String,
    /// SHA-256 hash of the SARDA task output being attested
    pub artifact_hash: String,
    /// Human-readable description
    pub description: String,
}

/// A signed settlement record — the Transaction plus its cryptographic proof.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Settlement {
    pub transaction: Transaction,
    /// ed25519 signature over the canonical transaction bytes (hex-encoded)
    pub signature: String,
    /// Public key of the signer (hex-encoded)
    pub public_key: String,
}

/// Keypair holder for an agent's signing identity.
pub struct AgentIdentity {
    signing_key: SigningKey,
    verifying_key: VerifyingKey,
}

impl AgentIdentity {
    /// Generate a new random ed25519 keypair.
    pub fn generate() -> Self {
        let signing_key = SigningKey::generate(&mut OsRng);
        let verifying_key = signing_key.verifying_key();
        Self {
            signing_key,
            verifying_key,
        }
    }

    /// Load from existing secret key bytes (32 bytes).
    pub fn from_secret(secret: &[u8; 32]) -> Self {
        let signing_key = SigningKey::from_bytes(secret);
        let verifying_key = signing_key.verifying_key();
        Self {
            signing_key,
            verifying_key,
        }
    }

    /// Return the public key as hex string.
    pub fn public_key_hex(&self) -> String {
        hex::encode(self.verifying_key.as_bytes())
    }

    /// Sign a transaction, producing a Settlement.
    pub fn sign_transaction(&self, tx: Transaction) -> Settlement {
        let canonical = canonical_bytes(&tx);
        let signature = self.signing_key.sign(&canonical);

        Settlement {
            transaction: tx,
            signature: hex::encode(signature.to_bytes()),
            public_key: self.public_key_hex(),
        }
    }
}

/// Verify a settlement's signature against the embedded public key.
pub fn verify_settlement(settlement: &Settlement) -> Result<bool, String> {
    // Decode public key
    let pk_bytes = hex::decode(&settlement.public_key)
        .map_err(|e| format!("Invalid public key hex: {e}"))?;
    let pk_array: [u8; 32] = pk_bytes
        .try_into()
        .map_err(|_| "Public key must be 32 bytes".to_string())?;
    let verifying_key = VerifyingKey::from_bytes(&pk_array)
        .map_err(|e| format!("Invalid public key: {e}"))?;

    // Decode signature
    let sig_bytes = hex::decode(&settlement.signature)
        .map_err(|e| format!("Invalid signature hex: {e}"))?;
    let sig_array: [u8; 64] = sig_bytes
        .try_into()
        .map_err(|_| "Signature must be 64 bytes".to_string())?;
    let signature = Signature::from_bytes(&sig_array);

    // Recompute canonical bytes and verify
    let canonical = canonical_bytes(&settlement.transaction);
    match verifying_key.verify(&canonical, &signature) {
        Ok(()) => Ok(true),
        Err(_) => Ok(false),
    }
}

/// Load persistent agent identity from the vault key file.
/// Returns None if the key file doesn't exist or is invalid.
pub fn load_vault_identity() -> Option<AgentIdentity> {
    let home = std::env::var("CAMELOT_OS_HOME")
        .or_else(|_| std::env::var("USERPROFILE").map(|h| format!("{}/CAMELOT_OS", h)))
        .or_else(|_| std::env::var("HOME").map(|h| format!("{}/CAMELOT_OS", h)))
        .ok()?;
    let key_path = std::path::Path::new(&home)
        .join(".camelot")
        .join("ap2_signing_key.bin");
    let bytes = std::fs::read(&key_path).ok()?;
    let secret: [u8; 32] = bytes.try_into().ok()?;
    Some(AgentIdentity::from_secret(&secret))
}

/// Compute SHA-256 hash of arbitrary data (for artifact_hash field).
pub fn sha256_hex(data: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data);
    hex::encode(hasher.finalize())
}

/// Produce deterministic canonical bytes for signing.
/// Format: "{tx_id}|{source}|{target}|{units}|{timestamp}|{artifact_hash}"
fn canonical_bytes(tx: &Transaction) -> Vec<u8> {
    format!(
        "{}|{}|{}|{}|{}|{}",
        tx.tx_id,
        tx.source_agent,
        tx.target_agent,
        tx.compute_units,
        tx.timestamp,
        tx.artifact_hash,
    )
    .into_bytes()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sign_and_verify() {
        let identity = AgentIdentity::generate();
        let tx = Transaction {
            tx_id: "test_001".into(),
            source_agent: "sir_boris".into(),
            target_agent: "modal_brain".into(),
            compute_units: 100,
            timestamp: "2026-04-02T23:00:00Z".into(),
            artifact_hash: sha256_hex(b"test artifact"),
            description: "SARDA cycle settlement".into(),
        };

        let settlement = identity.sign_transaction(tx);

        // Signature should be 64 bytes hex = 128 chars
        assert_eq!(settlement.signature.len(), 128);

        // Verify should pass
        assert!(verify_settlement(&settlement).unwrap());
    }

    #[test]
    fn test_tampered_transaction_fails() {
        let identity = AgentIdentity::generate();
        let tx = Transaction {
            tx_id: "test_002".into(),
            source_agent: "sir_boris".into(),
            target_agent: "modal_brain".into(),
            compute_units: 50,
            timestamp: "2026-04-02T23:00:00Z".into(),
            artifact_hash: sha256_hex(b"original data"),
            description: "Original settlement".into(),
        };

        let mut settlement = identity.sign_transaction(tx);

        // Tamper with the transaction
        settlement.transaction.compute_units = 9999;

        // Verify should fail
        assert!(!verify_settlement(&settlement).unwrap());
    }

    #[test]
    fn test_deterministic_hashing() {
        let hash1 = sha256_hex(b"hello world");
        let hash2 = sha256_hex(b"hello world");
        assert_eq!(hash1, hash2);
        assert_eq!(hash1.len(), 64); // 32 bytes = 64 hex chars
    }
}
