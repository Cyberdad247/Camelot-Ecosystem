use base64::{engine::general_purpose::STANDARD, Engine as _};
use ed25519_dalek::{Signature, SigningKey, VerifyingKey};
use serde::{Deserialize, Serialize};
use serde_json::Value;

use crate::EdgeError;

#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum Action {
    HealthProbe,
    TailscaleRouteCheck,
    CollectTelemetry,
    Notify,
    RefreshSnapshot,
    FlushOutbox,
}

impl Action {
    pub fn parse_allowlisted(value: &str) -> Result<Self, EdgeError> {
        match value {
            "health_probe" => Ok(Self::HealthProbe),
            "tailscale_route_check" => Ok(Self::TailscaleRouteCheck),
            "collect_telemetry" => Ok(Self::CollectTelemetry),
            "notify" => Ok(Self::Notify),
            "refresh_snapshot" => Ok(Self::RefreshSnapshot),
            "flush_outbox" => Ok(Self::FlushOutbox),
            _ => Err(EdgeError::ForbiddenAction),
        }
    }
}

/// Extract the 32-byte Ed25519 seed from the locally provisioned PKCS#8 PEM.
///
/// The device private key never crosses the Tailnet; this accepts only the
/// private PEM format produced by the Termux OpenSSL enrollment step.
pub fn signing_key_from_pkcs8_pem(pem: &[u8]) -> Result<SigningKey, EdgeError> {
    let pem = std::str::from_utf8(pem).map_err(|_| EdgeError::InvalidPrivateKeyEncoding)?;
    if !pem.contains("-----BEGIN PRIVATE KEY-----") || !pem.contains("-----END PRIVATE KEY-----") {
        return Err(EdgeError::InvalidPrivateKeyEncoding);
    }
    let encoded = pem
        .lines()
        .filter(|line| !line.starts_with("-----"))
        .collect::<String>();
    let der = STANDARD
        .decode(encoded)
        .map_err(|_| EdgeError::InvalidPrivateKeyEncoding)?;
    let seed = der
        .get(der.len().saturating_sub(32)..)
        .ok_or(EdgeError::InvalidPrivateKeyEncoding)?;
    let seed: [u8; 32] = seed
        .try_into()
        .map_err(|_| EdgeError::InvalidPrivateKeyEncoding)?;
    Ok(SigningKey::from_bytes(&seed))
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct PolicySnapshot {
    pub version: u8,
    pub device_id: String,
    pub issued_at: i64,
    pub expires_at: i64,
    pub allowed_actions: Vec<Action>,
    pub route: String,
}

#[derive(Serialize)]
struct UnsignedPolicySnapshot<'a> {
    version: u8,
    device_id: &'a str,
    issued_at: i64,
    expires_at: i64,
    allowed_actions: &'a [Action],
    route: &'a str,
}

impl PolicySnapshot {
    pub fn canonical_bytes(&self) -> Result<Vec<u8>, EdgeError> {
        serde_json::to_vec(&UnsignedPolicySnapshot {
            version: self.version,
            device_id: &self.device_id,
            issued_at: self.issued_at,
            expires_at: self.expires_at,
            allowed_actions: &self.allowed_actions,
            route: &self.route,
        })
        .map_err(|_| EdgeError::CanonicalSerialization)
    }
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct SignedEnvelope {
    pub device_id: String,
    pub action: Action,
    pub payload: Value,
    pub issued_at: i64,
    pub expires_at: i64,
    pub nonce: String,
    pub signature: String,
}

#[derive(Serialize)]
struct UnsignedEnvelope<'a> {
    device_id: &'a str,
    action: &'a Action,
    payload: &'a Value,
    issued_at: i64,
    expires_at: i64,
    nonce: &'a str,
}

impl SignedEnvelope {
    pub fn sign(
        device_id: &str,
        action: Action,
        payload: Value,
        issued_at: i64,
        expires_at: i64,
        nonce: &str,
        signing_key: &SigningKey,
    ) -> Self {
        use ed25519_dalek::Signer as _;

        let mut envelope = Self {
            device_id: device_id.to_owned(),
            action,
            payload,
            issued_at,
            expires_at,
            nonce: nonce.to_owned(),
            signature: String::new(),
        };
        let signature = signing_key.sign(&envelope.canonical_bytes().expect("serializable envelope"));
        envelope.signature = STANDARD.encode(signature.to_bytes());
        envelope
    }

    pub fn canonical_bytes(&self) -> Result<Vec<u8>, EdgeError> {
        serde_json::to_vec(&UnsignedEnvelope {
            device_id: &self.device_id,
            action: &self.action,
            payload: &self.payload,
            issued_at: self.issued_at,
            expires_at: self.expires_at,
            nonce: &self.nonce,
        })
        .map_err(|_| EdgeError::CanonicalSerialization)
    }

    pub fn verify_with(&self, trusted_key: &[u8; 32]) -> Result<(), EdgeError> {
        let verifying_key = VerifyingKey::from_bytes(trusted_key)
            .map_err(|_| EdgeError::InvalidPublicKeyEncoding)?;
        let signature = Signature::from_slice(
            &STANDARD
                .decode(&self.signature)
                .map_err(|_| EdgeError::InvalidSignatureEncoding)?,
        )
        .map_err(|_| EdgeError::InvalidSignatureEncoding)?;
        verifying_key
            .verify_strict(&self.canonical_bytes()?, &signature)
            .map_err(|_| EdgeError::InvalidSignature)
    }
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct SignedPolicySnapshot {
    pub snapshot: PolicySnapshot,
    pub signature: String,
    pub public_key: String,
}

impl SignedPolicySnapshot {
    pub fn sign(snapshot: PolicySnapshot, signing_key: &SigningKey) -> Self {
        use ed25519_dalek::Signer as _;

        let bytes = snapshot.canonical_bytes().expect("serializable snapshot");
        let signature = signing_key.sign(&bytes);
        Self {
            snapshot,
            signature: STANDARD.encode(signature.to_bytes()),
            public_key: STANDARD.encode(signing_key.verifying_key().to_bytes()),
        }
    }

    pub fn verify_for(&self, device_id: &str, now_unix: i64) -> Result<(), EdgeError> {
        if self.snapshot.device_id != device_id || self.snapshot.expires_at <= now_unix {
            return Err(EdgeError::RejectedSnapshot);
        }
        let public_key = STANDARD
            .decode(&self.public_key)
            .map_err(|_| EdgeError::InvalidPublicKeyEncoding)?;
        let public_key: [u8; 32] = public_key
            .try_into()
            .map_err(|_| EdgeError::InvalidPublicKeyEncoding)?;
        let verifying_key = VerifyingKey::from_bytes(&public_key)
            .map_err(|_| EdgeError::InvalidPublicKeyEncoding)?;
        let signature = Signature::from_slice(
            &STANDARD
                .decode(&self.signature)
                .map_err(|_| EdgeError::InvalidSignatureEncoding)?,
        )
        .map_err(|_| EdgeError::InvalidSignatureEncoding)?;
        verifying_key
            .verify_strict(&self.snapshot.canonical_bytes()?, &signature)
            .map_err(|_| EdgeError::InvalidSignature)
    }

    /// Verifies both the signature and the enrolled VPS signer key.
    ///
    /// A key carried by a received snapshot is informational only; it must
    /// match the public key provisioned during the human-controlled enrollment.
    pub fn verify_for_with_trusted_key(
        &self,
        device_id: &str,
        now_unix: i64,
        trusted_key: &[u8; 32],
    ) -> Result<(), EdgeError> {
        let advertised_key = STANDARD
            .decode(&self.public_key)
            .map_err(|_| EdgeError::InvalidPublicKeyEncoding)?;
        let advertised_key: [u8; 32] = advertised_key
            .try_into()
            .map_err(|_| EdgeError::InvalidPublicKeyEncoding)?;
        if &advertised_key != trusted_key {
            return Err(EdgeError::RejectedSnapshot);
        }
        self.verify_for(device_id, now_unix)
    }
}
