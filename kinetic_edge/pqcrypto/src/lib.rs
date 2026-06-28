//! CAMELOT Post-Quantum Cryptography — A2A Channel Security
//! ML-KEM-768 (Kyber768, FIPS 203) + ML-DSA-65 (Dilithium3, FIPS 204)
//!
//! P4-T04 (2026-06-28): migrated from the unmaintained `pqcrypto`/PQClean family
//! to the maintained RustCrypto `ml-kem` 0.3.x + `ml-dsa` 0.1.x. Keys/ciphertexts
//! serialize via the crypto-common `KeyExport`/`KeyInit`/`TryKeyInit` byte forms;
//! the public hex-string API and on-the-wire shapes are unchanged.

use anyhow::{anyhow, Result};
use serde::{Deserialize, Serialize};

use crypto_common::{Key, KeyExport, KeyInit};
use ml_kem::{Ciphertext, Decapsulate, Encapsulate, EncapsulationKey, DecapsulationKey, Kem, MlKem768};
use ml_dsa::{
    EncodedSignature, Generate, Keypair, MlDsa65, Signature, SigningKey, Signer, VerifyingKey,
    Verifier,
};

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
    let (dk, ek) = MlKem768::generate_keypair();
    let ek_bytes = ek.to_bytes();
    let dk_bytes = dk.to_bytes();
    Ok(KemKeyPair {
        key_size_bytes: ek_bytes.len(),
        encap_key: hex::encode(ek_bytes.as_slice()),
        decap_key: hex::encode(dk_bytes.as_slice()),
        algorithm: "ML-KEM-768".to_string(),
    })
}

pub fn kem_encapsulate(peer_ek_hex: &str) -> Result<KemEncapResult> {
    let ek_bytes = hex::decode(peer_ek_hex)?;
    let key = Key::<EncapsulationKey<MlKem768>>::try_from(ek_bytes.as_slice())
        .map_err(|_| anyhow!("ML-KEM-768: bad encap key length"))?;
    let ek = EncapsulationKey::<MlKem768>::new(&key)
        .map_err(|_| anyhow!("ML-KEM-768: invalid encap key"))?;
    let (ct, ss) = ek.encapsulate();
    Ok(KemEncapResult {
        ciphertext: hex::encode(ct.as_slice()),
        shared_secret: hex::encode(ss.as_slice()),
    })
}

pub fn kem_decapsulate(ciphertext_hex: &str, dk_hex: &str) -> Result<SharedSecret> {
    let ct_bytes = hex::decode(ciphertext_hex)?;
    let dk_bytes = hex::decode(dk_hex)?;
    let dk_key = Key::<DecapsulationKey<MlKem768>>::try_from(dk_bytes.as_slice())
        .map_err(|_| anyhow!("ML-KEM-768: bad decap key length"))?;
    let dk = DecapsulationKey::<MlKem768>::new(&dk_key);
    let ct = Ciphertext::<MlKem768>::try_from(ct_bytes.as_slice())
        .map_err(|_| anyhow!("ML-KEM-768: bad ciphertext length"))?;
    let ss = dk.decapsulate(&ct);
    Ok(ss.as_slice().to_vec())
}

// ── ML-DSA-65 ─────────────────────────────────────────────────────────────────

pub fn dsa_keygen() -> Result<DsaKeyPair> {
    let sk = SigningKey::<MlDsa65>::generate();
    let vk = sk.verifying_key();
    let sk_bytes = sk.to_bytes();
    let vk_bytes = vk.to_bytes();
    Ok(DsaKeyPair {
        key_size_bytes: vk_bytes.len(),
        sign_key: hex::encode(sk_bytes.as_slice()),
        verify_key: hex::encode(vk_bytes.as_slice()),
        algorithm: "ML-DSA-65".to_string(),
    })
}

/// Sign a message. verify_key_hex is carried into the SignedPayload so the
/// verifier has the public key (ML-DSA does not derive pk from sk).
pub fn dsa_sign(
    message: &[u8],
    sign_key_hex: &str,
    verify_key_hex: &str,
    knight_id: &str,
) -> Result<SignedPayload> {
    let sk_bytes = hex::decode(sign_key_hex)?;
    let key = Key::<SigningKey<MlDsa65>>::try_from(sk_bytes.as_slice())
        .map_err(|_| anyhow!("ML-DSA-65: bad signing key length"))?;
    let sk = SigningKey::<MlDsa65>::new(&key);
    let sig: Signature<MlDsa65> = sk.sign(message);
    let sig_enc = sig.encode();
    Ok(SignedPayload {
        payload: hex::encode(message),
        signature: hex::encode(sig_enc.as_slice()),
        verify_key: verify_key_hex.to_string(),
        knight_id: knight_id.to_string(),
    })
}

pub fn dsa_verify(signed: &SignedPayload) -> Result<bool> {
    let vk_bytes = hex::decode(&signed.verify_key)?;
    let sig_bytes = hex::decode(&signed.signature)?;
    let msg_bytes = hex::decode(&signed.payload)?;
    let vk_key = Key::<VerifyingKey<MlDsa65>>::try_from(vk_bytes.as_slice())
        .map_err(|_| anyhow!("ML-DSA-65: bad verify key length"))?;
    let vk = VerifyingKey::<MlDsa65>::new(&vk_key);
    let sig_enc = EncodedSignature::<MlDsa65>::try_from(sig_bytes.as_slice())
        .map_err(|_| anyhow!("ML-DSA-65: bad signature length"))?;
    let sig = Signature::<MlDsa65>::decode(&sig_enc)
        .ok_or_else(|| anyhow!("ML-DSA-65: invalid signature encoding"))?;
    Ok(vk.verify(&msg_bytes, &sig).is_ok())
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
