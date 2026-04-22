//! CAMELOT Post-Quantum Cryptography — A2A Channel Security
//! ===========================================================
//! Implements NIST PQC standards for CAMELOT knight-to-knight (A2A) communication.
//!
//! Algorithms:
//!   ML-KEM-768 (FIPS 203) — Key Encapsulation Mechanism (replaces X25519/ECDH)
//!   ML-DSA-65  (FIPS 204) — Digital Signature (replaces Ed25519)
//!
//! Security levels:
//!   ML-KEM-768: NIST Level 3 (≈ AES-192 classical / quantum-resistant)
//!   ML-DSA-65:  NIST Level 3 (≈ SHA3-256 collision resistance)
//!
//! Usage in A2A:
//!   1. Each knight generates (ek, dk) = kem_keygen() on startup
//!   2. Sender calls (shared_secret, ciphertext) = kem_encapsulate(peer_ek)
//!   3. Receiver calls shared_secret = kem_decapsulate(ciphertext, dk)
//!   4. Knight signs payloads: sig = dsa_sign(msg, signing_key)
//!   5. Receiver verifies:    ok  = dsa_verify(msg, sig, verifying_key)

use anyhow::Result;
use serde::{Deserialize, Serialize};
use zeroize::Zeroize;

// ── Type aliases for clarity ──────────────────────────────────────────────────

pub type KemEncapKey   = Vec<u8>;   // ML-KEM-768 encapsulation key (1184 bytes)
pub type KemDecapKey   = Vec<u8>;   // ML-KEM-768 decapsulation key (2400 bytes)
pub type KemCiphertext = Vec<u8>;   // ML-KEM-768 ciphertext (1088 bytes)
pub type SharedSecret  = Vec<u8>;   // 32-byte shared secret (zeroize on drop)
pub type DsaSignKey    = Vec<u8>;   // ML-DSA-65 signing key (4032 bytes)
pub type DsaVerifyKey  = Vec<u8>;   // ML-DSA-65 verifying key (1952 bytes)
pub type Signature     = Vec<u8>;   // ML-DSA-65 signature (3309 bytes)

// ── Serializable key bundle ───────────────────────────────────────────────────

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct KemKeyPair {
    pub encap_key:  String,  // hex-encoded — share with peers
    pub decap_key:  String,  // hex-encoded — NEVER share, zeroize on drop
    pub algorithm:  String,
    pub key_size_bytes: usize,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DsaKeyPair {
    pub sign_key:    String,  // hex-encoded — keep secret
    pub verify_key:  String,  // hex-encoded — share with peers
    pub algorithm:   String,
    pub key_size_bytes: usize,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct KemEncapResult {
    pub ciphertext:    String,  // hex — send to decapsulator
    pub shared_secret: String,  // hex — use as symmetric key (AES-256-GCM)
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SignedPayload {
    pub payload:   String,   // hex-encoded message bytes
    pub signature: String,   // hex-encoded ML-DSA-65 signature
    pub verify_key: String,  // hex-encoded verifying key for verification
    pub knight_id: String,
}

// ── ML-KEM-768 operations ─────────────────────────────────────────────────────

/// Generate an ML-KEM-768 key pair.
/// ek (encapsulation key) is public — share with peers.
/// dk (decapsulation key) is secret — store securely, zeroize after use.
pub fn kem_keygen() -> Result<KemKeyPair> {
    use ml_kem::MlKem768;
    use ml_kem::kem::{Kem, Decapsulate, Encapsulate};
    use rand::rngs::OsRng;

    let (dk, ek) = MlKem768::generate(&mut OsRng);
    let ek_bytes = ek.as_bytes();
    let dk_bytes = dk.as_bytes();

    Ok(KemKeyPair {
        encap_key:      hex::encode(ek_bytes),
        decap_key:      hex::encode(dk_bytes),
        algorithm:      "ML-KEM-768".to_string(),
        key_size_bytes: ek_bytes.len(),
    })
}

/// Encapsulate: sender generates shared_secret + ciphertext from peer's encap_key.
pub fn kem_encapsulate(peer_ek_hex: &str) -> Result<KemEncapResult> {
    use ml_kem::MlKem768;
    use ml_kem::kem::{Encapsulate};
    use ml_kem::EncodedSizeUser;
    use rand::rngs::OsRng;

    let ek_bytes = hex::decode(peer_ek_hex)?;
    let ek = ml_kem::kem::EncapsulationKey::<MlKem768>::from_bytes(
        ek_bytes.as_slice().try_into()
            .map_err(|_| anyhow::anyhow!("ML-KEM-768: invalid encapsulation key length"))?
    );
    let (ct, ss) = ek.encapsulate(&mut OsRng)
        .map_err(|e| anyhow::anyhow!("ML-KEM-768 encapsulate error: {:?}", e))?;

    Ok(KemEncapResult {
        ciphertext:    hex::encode(ct.as_bytes()),
        shared_secret: hex::encode(ss.as_bytes()),
    })
}

/// Decapsulate: receiver recovers shared_secret from ciphertext using their decap_key.
pub fn kem_decapsulate(ciphertext_hex: &str, dk_hex: &str) -> Result<SharedSecret> {
    use ml_kem::MlKem768;
    use ml_kem::kem::Decapsulate;
    use ml_kem::EncodedSizeUser;

    let ct_bytes = hex::decode(ciphertext_hex)?;
    let dk_bytes = hex::decode(dk_hex)?;

    let dk = ml_kem::kem::DecapsulationKey::<MlKem768>::from_bytes(
        dk_bytes.as_slice().try_into()
            .map_err(|_| anyhow::anyhow!("ML-KEM-768: invalid decapsulation key length"))?
    );
    let ct = ml_kem::kem::Ciphertext::<MlKem768>::from_bytes(
        ct_bytes.as_slice().try_into()
            .map_err(|_| anyhow::anyhow!("ML-KEM-768: invalid ciphertext length"))?
    );
    let ss = dk.decapsulate(&ct)
        .map_err(|e| anyhow::anyhow!("ML-KEM-768 decapsulate error: {:?}", e))?;

    Ok(ss.as_bytes().to_vec())
}

// ── ML-DSA-65 operations ─────────────────────────────────────────────────────

/// Generate an ML-DSA-65 signing key pair.
/// verify_key is public — register in RBAC access_matrix.
/// sign_key is secret — per-knight identity credential.
pub fn dsa_keygen() -> Result<DsaKeyPair> {
    use ml_dsa::MlDsa65;
    use ml_dsa::KeyGen;
    use rand::rngs::OsRng;

    let (sk, vk) = MlDsa65::try_keygen_with_rng(&mut OsRng)
        .map_err(|e| anyhow::anyhow!("ML-DSA-65 keygen error: {:?}", e))?;

    Ok(DsaKeyPair {
        sign_key:       hex::encode(sk.encode()),
        verify_key:     hex::encode(vk.encode()),
        algorithm:      "ML-DSA-65".to_string(),
        key_size_bytes: vk.encode().len(),
    })
}

/// Sign a message with ML-DSA-65 signing key. Returns hex-encoded signature.
pub fn dsa_sign(message: &[u8], sign_key_hex: &str, knight_id: &str) -> Result<SignedPayload> {
    use ml_dsa::MlDsa65;
    use ml_dsa::{KeyGen, Sign};
    use rand::rngs::OsRng;

    let sk_bytes = hex::decode(sign_key_hex)?;
    let sk = ml_dsa::SigningKey::<MlDsa65>::decode(
        sk_bytes.as_slice().try_into()
            .map_err(|_| anyhow::anyhow!("ML-DSA-65: invalid signing key"))?
    );
    let vk = sk.verifying_key();
    let sig = sk.try_sign_with_rng(&mut OsRng, message, b"")
        .map_err(|e| anyhow::anyhow!("ML-DSA-65 sign error: {:?}", e))?;

    Ok(SignedPayload {
        payload:    hex::encode(message),
        signature:  hex::encode(sig.encode()),
        verify_key: hex::encode(vk.encode()),
        knight_id:  knight_id.to_string(),
    })
}

/// Verify an ML-DSA-65 signature. Returns Ok(true) if valid, Ok(false) if invalid.
pub fn dsa_verify(signed: &SignedPayload) -> Result<bool> {
    use ml_dsa::MlDsa65;
    use ml_dsa::Verify;

    let vk_bytes = hex::decode(&signed.verify_key)?;
    let sig_bytes = hex::decode(&signed.signature)?;
    let msg_bytes = hex::decode(&signed.payload)?;

    let vk = ml_dsa::VerifyingKey::<MlDsa65>::decode(
        vk_bytes.as_slice().try_into()
            .map_err(|_| anyhow::anyhow!("ML-DSA-65: invalid verifying key"))?
    );
    let sig = ml_dsa::Signature::<MlDsa65>::decode(
        sig_bytes.as_slice().try_into()
            .map_err(|_| anyhow::anyhow!("ML-DSA-65: invalid signature"))?
    );

    Ok(vk.verify(&msg_bytes, &sig, b"").is_ok())
}

// ── Key sizes (for validation) ────────────────────────────────────────────────

pub const ML_KEM_768_EK_BYTES:  usize = 1184;
pub const ML_KEM_768_DK_BYTES:  usize = 2400;
pub const ML_KEM_768_CT_BYTES:  usize = 1088;
pub const ML_KEM_768_SS_BYTES:  usize = 32;
pub const ML_DSA_65_SK_BYTES:   usize = 4032;
pub const ML_DSA_65_VK_BYTES:   usize = 1952;
pub const ML_DSA_65_SIG_BYTES:  usize = 3309;
