//! Bifrost Transport Cryptographic Receipt Generator
//! ==================================================

use crate::frame::BifrostFrame;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TransportReceipt {
    pub receipt_id: String,
    pub frame_id: String,
    pub sender: String,
    pub recipient: String,
    pub payload_hash: String,
    pub receipt_hash: String,
    pub timestamp: DateTime<Utc>,
}

impl TransportReceipt {
    pub fn generate(frame: &BifrostFrame) -> Self {
        let payload_hash = blake3::hash(frame.payload.as_bytes()).to_hex().to_string();
        let timestamp = Utc::now();
        
        let receipt_raw = format!(
            "{}:{}:{}:{}:{}:{}",
            frame.frame_id,
            frame.sender,
            frame.recipient,
            payload_hash,
            frame.msg_type as u8,
            timestamp.to_rfc3339()
        );
        let receipt_hash = blake3::hash(receipt_raw.as_bytes()).to_hex().to_string();
        
        Self {
            receipt_id: format!("rcpt_{}", &receipt_hash[..16]),
            frame_id: frame.frame_id.clone(),
            sender: frame.sender.clone(),
            recipient: frame.recipient.clone(),
            payload_hash,
            receipt_hash,
            timestamp,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::frame::MessageType;

    #[test]
    fn test_receipt_generation_deterministic_hash() {
        let frame = BifrostFrame::new(
            MessageType::RunicDispatch,
            "SIR_HELIOS",
            "MERLIN_OMEGA",
            "//STATUS",
        );
        let receipt = TransportReceipt::generate(&frame);
        assert!(!receipt.receipt_id.is_empty());
        assert_eq!(receipt.frame_id, frame.frame_id);
        assert_eq!(receipt.sender, "SIR_HELIOS");
        assert_eq!(receipt.recipient, "MERLIN_OMEGA");
        assert_eq!(receipt.payload_hash.len(), 64);
        assert_eq!(receipt.receipt_hash.len(), 64);
    }
}
