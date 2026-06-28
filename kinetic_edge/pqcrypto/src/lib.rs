//! CAMELOT Post-Quantum Cryptography — A2A Channel Security
//! ML-KEM-768 (Kyber768, FIPS 203) + ML-DSA-65 (Dilithium3, FIPS 204)
//!
//! Runtime-functional via the pqcrypto family. Migration to actively-maintained
//! RustCrypto `ml-kem` 0.3.x + `ml-dsa` 0.1.x is tracked under tag
//! `[OUROBOROS_BINDING_PHASE1_AUDIT_PQCRYPTO_MIGRATION_DEFERRED]` in the
//! Codex provenance ledger. The follow-up PR will swap the inner `use`
//! statements + call sites once trait surfaces are verified against docs.rs
//! in a dedicated docs-research-and-test cycle with Windows CI.

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

// ── Tests (P4-T02): ML-KEM-768 handshake round-trip + ML-DSA-65 sign/verify ──
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ml_kem_768_handshake_round_trips() {
        // Bob generates a keypair; Alice encapsulates to Bob's encap key.
        let bob = kem_keygen().expect("keygen");
        assert_eq!(bob.algorithm, "ML-KEM-768");
        assert_eq!(bob.key_size_bytes, ML_KEM_768_EK_BYTES);

        let enc = kem_encapsulate(&bob.encap_key).expect("encapsulate");
        // Bob decapsulates with his decap key and recovers the same shared secret.
        let ss_bob = kem_decapsulate(&enc.ciphertext, &bob.decap_key).expect("decapsulate");

        let ss_alice = hex::decode(&enc.shared_secret).expect("hex");
        assert_eq!(ss_alice, ss_bob, "ML-KEM-768 shared secrets must match");
        assert_eq!(ss_bob.len(), ML_KEM_768_SS_BYTES);
    }

    #[test]
    fn ml_kem_768_wrong_key_yields_different_secret() {
        let bob = kem_keygen().unwrap();
        let mallory = kem_keygen().unwrap();
        let enc = kem_encapsulate(&bob.encap_key).unwrap();
        // Decapsulating with the wrong decap key must NOT recover Alice's secret.
        let ss_wrong = kem_decapsulate(&enc.ciphertext, &mallory.decap_key).unwrap();
        let ss_alice = hex::decode(&enc.shared_secret).unwrap();
        assert_ne!(ss_alice, ss_wrong, "wrong decap key must not recover the secret");
    }

    #[test]
    fn ml_dsa_65_sign_verify_round_trips() {
        let kp = dsa_keygen().unwrap();
        assert_eq!(kp.algorithm, "ML-DSA-65");
        let msg = b"CAMELOT-OS v9000.14 A2A channel attest";
        let signed = dsa_sign(msg, &kp.sign_key, &kp.verify_key, "sir_sentinel").unwrap();
        assert!(dsa_verify(&signed).unwrap(), "valid signature must verify");

        // Tamper the payload -> verification fails.
        let mut tampered = signed;
        tampered.payload = hex::encode(b"tampered message");
        assert!(!dsa_verify(&tampered).unwrap(), "tampered payload must not verify");
    }
}
