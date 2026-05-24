use crate::kv_event_gate::KVEvent;
use std::collections::VecDeque;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PublishError {
    BufferFull,
}

#[derive(Debug, Clone)]
pub struct BoundedEventPublisher {
    high_priority: VecDeque<KVEvent>,
    normal_priority: VecDeque<KVEvent>,
    capacity: usize,
    high_watermark: usize,
}

impl BoundedEventPublisher {
    pub fn new(capacity: usize, high_watermark: usize) -> Self {
        let capacity = capacity.max(1);
        Self {
            high_priority: VecDeque::with_capacity(capacity),
            normal_priority: VecDeque::with_capacity(capacity),
            capacity,
            high_watermark: high_watermark.min(capacity),
        }
    }

    pub fn push_event(&mut self, event: KVEvent, high_priority: bool) -> Result<(), PublishError> {
        if high_priority {
            if self.high_priority.len() >= self.capacity {
                return Err(PublishError::BufferFull);
            }
            self.high_priority.push_back(event);
            return Ok(());
        }

        if self.pending_len() >= self.high_watermark {
            return Err(PublishError::BufferFull);
        }
        self.normal_priority.push_back(event);
        Ok(())
    }

    pub fn flush_buffer(&mut self, max_events: usize) -> Vec<KVEvent> {
        let mut flushed = Vec::with_capacity(max_events);
        while flushed.len() < max_events {
            if let Some(event) = self.high_priority.pop_front() {
                flushed.push(event);
                continue;
            }
            if let Some(event) = self.normal_priority.pop_front() {
                flushed.push(event);
                continue;
            }
            break;
        }
        flushed
    }

    pub fn pending_len(&self) -> usize {
        self.high_priority.len() + self.normal_priority.len()
    }
}

pub fn push_event(
    publisher: &mut BoundedEventPublisher,
    event: KVEvent,
    high_priority: bool,
) -> Result<(), PublishError> {
    publisher.push_event(event, high_priority)
}

pub fn flush_buffer(publisher: &mut BoundedEventPublisher, max_events: usize) -> Vec<KVEvent> {
    publisher.flush_buffer(max_events)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::kv_event_gate::{KVEventType, KVEvent};

    fn event(sequence: u64) -> KVEvent {
        KVEvent {
            sequence,
            tenant_id: "tenant-a".to_string(),
            event_type: KVEventType::Put,
            key: format!("key-{sequence}"),
            value_hash: "hash".to_string(),
            previous_hash: "genesis".to_string(),
        }
    }

    #[test]
    fn flushes_high_priority_first() {
        let mut publisher = BoundedEventPublisher::new(4, 4);
        publisher.push_event(event(1), false).unwrap();
        publisher.push_event(event(2), true).unwrap();

        let flushed = publisher.flush_buffer(2);
        assert_eq!(flushed[0].sequence, 2);
        assert_eq!(flushed[1].sequence, 1);
    }
}

