//! Bifrost Binary/Text Frame Protocol
//! ====================================

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum MessageType {
    Ping,
    Pong,
    RunicDispatch,
    TelemetryStream,
    AnyaGateReview,
    HateoasFragment,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BifrostFrame {
    pub frame_id: String,
    pub msg_type: MessageType,
    pub sender: String,
    pub recipient: String,
    pub timestamp: DateTime<Utc>,
    pub payload: String,
}

impl BifrostFrame {
    pub fn new(
        msg_type: MessageType,
        sender: impl Into<String>,
        recipient: impl Into<String>,
        payload: impl Into<String>,
    ) -> Self {
        Self {
            frame_id: format!("frame_{}", Uuid::new_v4()),
            msg_type,
            sender: sender.into(),
            recipient: recipient.into(),
            timestamp: Utc::now(),
            payload: payload.into(),
        }
    }

    pub fn serialize(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string(self)
    }

    pub fn deserialize(raw: &str) -> Result<Self, serde_json::Error> {
        serde_json::from_str(raw)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn frame_roundtrip_serialization() {
        let frame = BifrostFrame::new(
            MessageType::RunicDispatch,
            "SIR_HELIOS",
            "MERLIN_OMEGA",
            "//HELIOS_MACRO audit",
        );
        let encoded = frame.serialize().expect("serialize frame");
        let decoded = BifrostFrame::deserialize(&encoded).expect("deserialize frame");

        assert_eq!(frame.frame_id, decoded.frame_id);
        assert_eq!(frame.msg_type, decoded.msg_type);
        assert_eq!(frame.sender, decoded.sender);
        assert_eq!(frame.payload, decoded.payload);
    }
}
