//! Bifrost Router (Runic Command & Message Dispatch)
//! =================================================

use crate::frame::{BifrostFrame, MessageType};
use anyhow::{bail, Result};
use std::collections::HashMap;

pub type HandlerFn = Box<dyn Fn(&BifrostFrame) -> Result<BifrostFrame> + Send + Sync>;

pub struct BifrostRouter {
    handlers: HashMap<String, HandlerFn>,
}

impl Default for BifrostRouter {
    fn default() -> Self {
        Self::new()
    }
}

impl BifrostRouter {
    pub fn new() -> Self {
        let mut router = Self {
            handlers: HashMap::new(),
        };

        // Default ping handler
        router.register("//PING", Box::new(|frame| {
            Ok(BifrostFrame::new(
                MessageType::Pong,
                "BIFROST_GATEWAY",
                &frame.sender,
                "PONG",
            ))
        }));

        router
    }

    pub fn register(&mut self, rune: impl Into<String>, handler: HandlerFn) {
        self.handlers.insert(rune.into(), handler);
    }

    pub fn dispatch(&self, frame: &BifrostFrame) -> Result<BifrostFrame> {
        let command = frame.payload.trim().split_whitespace().next().unwrap_or("");
        if let Some(handler) = self.handlers.get(command) {
            handler(frame)
        } else {
            bail!("Unrecognized runic command or route: '{}'", command);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ping_handler_dispatches_pong() {
        let router = BifrostRouter::new();
        let frame = BifrostFrame::new(
            MessageType::RunicDispatch,
            "TEST_SQUIRE",
            "BIFROST_GATEWAY",
            "//PING",
        );

        let reply = router.dispatch(&frame).expect("dispatch frame");
        assert_eq!(reply.msg_type, MessageType::Pong);
        assert_eq!(reply.payload, "PONG");
        assert_eq!(reply.recipient, "TEST_SQUIRE");
    }

    #[test]
    fn custom_runic_route() {
        let mut router = BifrostRouter::new();
        router.register("//STATUS", Box::new(|frame| {
            Ok(BifrostFrame::new(
                MessageType::TelemetryStream,
                "ORCHESTRATOR",
                &frame.sender,
                "ALL_SYSTEMS_NOMINAL",
            ))
        }));

        let frame = BifrostFrame::new(
            MessageType::RunicDispatch,
            "OPERATOR",
            "ORCHESTRATOR",
            "//STATUS --json",
        );

        let reply = router.dispatch(&frame).expect("dispatch status");
        assert_eq!(reply.payload, "ALL_SYSTEMS_NOMINAL");
    }
}
