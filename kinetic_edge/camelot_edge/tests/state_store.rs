use camelot_edge::{EdgeState, OutboxItem, OutboxLimits};

const NOW: i64 = 1_700_000_000;

fn test_db() -> std::path::PathBuf {
    let nonce = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    std::env::temp_dir().join(format!(
        "camelot-edge-state-{}-{nonce}.db",
        std::process::id()
    ))
}

fn telemetry(nonce: &str) -> OutboxItem {
    OutboxItem::telemetry(
        nonce,
        format!("{{\"event\":\"{nonce}\"}}").into_bytes(),
        NOW + 600,
    )
}

#[test]
fn retains_only_the_newest_two_telemetry_records_at_cap() {
    let mut state = EdgeState::open(
        test_db(),
        OutboxLimits {
            max_records: 2,
            max_bytes: 512,
        },
    )
    .unwrap();
    state.enqueue(telemetry("one"), NOW).unwrap();
    state.enqueue(telemetry("two"), NOW).unwrap();
    state.enqueue(telemetry("three"), NOW).unwrap();

    let records = state.due_outbox(NOW).unwrap();
    assert_eq!(records.len(), 2);
    assert_eq!(records[0].nonce, "two");
    assert_eq!(records[1].nonce, "three");
}

#[test]
fn rejects_duplicate_nonce_without_overwriting_the_original() {
    let mut state = EdgeState::open(test_db(), OutboxLimits::test_defaults()).unwrap();
    state.enqueue(telemetry("same-nonce"), NOW).unwrap();
    assert!(state.enqueue(telemetry("same-nonce"), NOW).is_err());
    assert_eq!(state.due_outbox(NOW).unwrap().len(), 1);
}

#[test]
fn removes_expired_records_before_returning_the_outbox() {
    let mut state = EdgeState::open(test_db(), OutboxLimits::test_defaults()).unwrap();
    state
        .enqueue(
            OutboxItem::telemetry("expired", b"{}".to_vec(), NOW - 1),
            NOW,
        )
        .unwrap();
    assert!(state.due_outbox(NOW).unwrap().is_empty());
}
