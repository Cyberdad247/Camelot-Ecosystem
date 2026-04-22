//! CAMELOT Post-Quantum Cryptography — A2A Channel Security
//! ML-KEM-768 (Kyber768, FIPS 203) + ML-DSA-65 (Dilithium3, FIPS 204)

use anyhow::{anyhow, Result};
use pqcrypto::kem::kyber768;
use pqcrypto::sign::dilithium3;
use pqcrypto_traits::kem::{Ciphertext as _, PublicKey as _, SecretKey as _, SharedSecret as _};
use pqcrypto_traits::sign::{PublicKey as _, SecretKey as _, SignedMessage as _};
use serde::{Deserialize, Serialize};

pub type SharedSecret = Vec<u8>;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct KemKeyPair {
    pub encap_key: String,
    pub decap_key: String,
    pub algorithm: String,
    pub key_size_bytes: usize,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DsaKeyPair {
    pub sign_key: String,
    pub verify_key: String,
    pub algorithm: String,
    pub key_size_bytes: usize,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct KemEncapResult {
    pub ciphertext: String,
    pub shared_secret: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SignedPayload {
    pub payload: String,
    pub signature: String,
    pub verify_key: String,
    pub knight_id: String,
}

// ── ML-KEM-768 ────────────────────────────────────────────────────────────────

pub fn kem_keygen() -> Result<KemKeyPair> {
    let (pk, sk) = kyber768::keypair();
    let ek = pk.as_bytes().to_vec();
    Ok(KemKeyPair {
        key_size_bytes: ek.len(),
        encap_key: hex::encode(&ek),
        decap_key: hex::encode(sk.as_bytes()),
        algorithm: "ML-KEM-768".to_string(),
    })
}

pub fn kem_encapsulate(peer_ek_hex: &str) -> Result<KemEncapResult> {
    let ek_bytes = hex::decode(peer_ek_hex)?;
    let pk = kyber768::PublicKey::from_bytes(&ek_bytes)
        .map_err(|e| anyhow!("ML-KEM-768: bad encap key: {:?}", e))?;
    let (ss, ct) = kyber768::encapsulate(&pk);
    Ok(KemEncapResult {
        ciphertext: hex::encode(ct.as_bytes()),
        shared_secret: hex::encode(ss.as_bytes()),
    })
}

pub fn kem_decapsulate(ciphertext_hex: &str, dk_hex: &str) -> Result<SharedSecret> {
    let ct_bytes = hex::decode(ciphertext_hex)?;
    let dk_bytes = hex::decode(dk_hex)?;
    let ct = kyber768::Ciphertext::from_bytes(&ct_bytes)
        .map_err(|e| anyhow!("ML-KEM-768: bad ciphertext: {:?}", e))?;
    let sk = kyber768::SecretKey::from_bytes(&dk_bytes)
        .map_err(|e| anyhow!("ML-KEM-768: bad decap key: {:?}", e))?;
    let ss = kyber768::decapsulate(&ct, &sk);
    Ok(ss.as_bytes().to_vec())
}

// ── ML-DSA-65 ─────────────────────────────────────────────────────────────────

pub fn dsa_keygen() -> Result<DsaKeyPair> {
    let (pk, sk) = dilithium3::keypair();
    let vk = pk.as_bytes().to_vec();
    Ok(DsaKeyPair {
        key_size_bytes: vk.len(),
        sign_key: hex::encode(sk.as_bytes()),
        verify_key: hex::encode(&vk),
        algorithm: "ML-DSA-65".to_string(),
    })
}

/// Sign message. Requires verify_key_hex alongside sign_key_hex (pqcrypto
/// does not derive pk from sk — caller always has both from dsa_keygen).
pub fn dsa_sign(
    message: &[u8],
    sign_key_hex: &str,
    verify_key_hex: &str,
    knight_id: &str,
) -> Result<SignedPayload> {
    let sk_bytes = hex::decode(sign_key_hex)?;
    let sk = dilithium3::SecretKey::from_bytes(&sk_bytes)
        .map_err(|e| anyhow!("ML-DSA-65: bad signing key: {:?}", e))?;
    let signed_msg = dilithium3::sign(message, &sk);
    // signed_msg bytes = signature || message; signature is the first sig_len bytes
    let sig_len = dilithium3::signature_bytes();
    let sig_hex = hex::encode(&signed_msg.as_bytes()[..sig_len]);
    Ok(SignedPayload {
        payload: hex::encode(message),
        signature: sig_hex,
        verify_key: verify_key_hex.to_string(),
        knight_id: knight_id.to_string(),
    })
}

pub fn dsa_verify(signed: &SignedPayload) -> Result<bool> {
    let vk_bytes = hex::decode(&signed.verify_key)?;
    let sig_bytes = hex::decode(&signed.signature)?;
    let msg_bytes = hex::decode(&signed.payload)?;
    let pk = dilithium3::PublicKey::from_bytes(&vk_bytes)
        .map_err(|e| anyhow!("ML-DSA-65: bad verify key: {:?}", e))?;
    // Reconstruct signed message as sig || msg (pqcrypto format)
    let mut sm_bytes = sig_bytes;
    sm_bytes.extend_from_slice(&msg_bytes);
    let sm = dilithium3::SignedMessage::from_bytes(&sm_bytes)
        .map_err(|e| anyhow!("ML-DSA-65: bad signed message: {:?}", e))?;
    Ok(dilithium3::open(&sm, &pk).is_ok())
}

// ── Key size constants ────────────────────────────────────────────────────────

pub const ML_KEM_768_EK_BYTES: usize = 1184;
pub const ML_KEM_768_DK_BYTES: usize = 2400;
pub const ML_KEM_768_CT_BYTES: usize = 1088;
pub const ML_KEM_768_SS_BYTES: usize = 32;
pub const ML_DSA_65_SK_BYTES: usize = 4000;
pub const ML_DSA_65_VK_BYTES: usize = 1952;
pub const ML_DSA_65_SIG_BYTES: usize = 3293;
