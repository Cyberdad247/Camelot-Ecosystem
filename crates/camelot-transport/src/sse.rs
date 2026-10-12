//! Server-Sent Events (SSE) Telemetry Stream Formatter
//! ====================================================

use serde::Serialize;

#[derive(Debug, Clone, Serialize)]
pub struct SseEvent {
    pub event: String,
    pub data: String,
    pub id: Option<String>,
    pub retry: Option<u32>,
}

impl SseEvent {
    pub fn new(event: impl Into<String>, data: impl Into<String>) -> Self {
        Self {
            event: event.into(),
            data: data.into(),
            id: None,
            retry: None,
        }
    }

    pub fn with_id(mut self, id: impl Into<String>) -> Self {
        self.id = Some(id.into());
        self
    }

    pub fn format(&self) -> String {
        let mut out = String::new();
        if let Some(ref id) = self.id {
            out.push_str(&format!("id: {}\n", id));
        }
        out.push_str(&format!("event: {}\n", self.event));
        for line in self.data.lines() {
            out.push_str(&format!("data: {}\n", line));
        }
        if let Some(retry) = self.retry {
            out.push_str(&format!("retry: {}\n", retry));
        }
        out.push('\n');
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sse_event_format() {
        let event = SseEvent::new("telemetry", "{\"cpu\": 4.2, \"ram_mb\": 128}")
            .with_id("evt_001");
        let formatted = event.format();
        assert!(formatted.contains("id: evt_001\n"));
        assert!(formatted.contains("event: telemetry\n"));
        assert!(formatted.contains("data: {\"cpu\": 4.2, \"ram_mb\": 128}\n\n"));
    }
}
