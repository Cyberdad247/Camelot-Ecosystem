//! Sovereign Ed25519 Signature Verification
//! ========================================

use ed25519_dalek::{Signature, VerifyingKey};

pub struct SignatureVerifier;

impl SignatureVerifier {
    pub fn verify(public_key_bytes: &[u8; 32], message: &[u8], signature_bytes: &[u8; 64]) -> bool {
        let verifying_key = match VerifyingKey::from_bytes(public_key_bytes) {
            Ok(key) => key,
            Err(_) => return false,
        };

        let signature = Signature::from_bytes(signature_bytes);
        verifying_key.verify_strict(message, &signature).is_ok()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ed25519_dalek::Signer;
    use ed25519_dalek::SigningKey;

    #[test]
    fn ed25519_signature_verification() {
        let signing_key = SigningKey::from_bytes(&[7u8; 32]);
        let verifying_key = signing_key.verifying_key();

        let message = b"CAMELOT_OS_GENESIS_BOOT_PAYLOAD";
        let signature = signing_key.sign(message);

        let valid = SignatureVerifier::verify(
            verifying_key.as_bytes(),
            message,
            &signature.to_bytes(),
        );

        assert!(valid);
    }
}
