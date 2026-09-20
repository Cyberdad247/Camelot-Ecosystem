use std::path::Path;

use rusqlite::{params, Connection};

use crate::EdgeError;

#[derive(Clone, Copy, Debug)]
pub struct OutboxLimits {
    pub max_records: usize,
    pub max_bytes: usize,
}

impl OutboxLimits {
    pub fn test_defaults() -> Self {
        Self {
            max_records: 32,
            max_bytes: 16 * 1024,
        }
    }
}

#[derive(Clone, Debug)]
pub struct OutboxItem {
    pub nonce: String,
    pub kind: String,
    pub payload: Vec<u8>,
    pub expires_at: i64,
}

impl OutboxItem {
    pub fn telemetry(nonce: &str, payload: Vec<u8>, expires_at: i64) -> Self {
        Self {
            nonce: nonce.to_owned(),
            kind: "telemetry".to_owned(),
            payload,
            expires_at,
        }
    }
}

pub struct EdgeState {
    connection: Connection,
    limits: OutboxLimits,
}

impl EdgeState {
    pub fn open(path: impl AsRef<Path>, limits: OutboxLimits) -> Result<Self, EdgeError> {
        let connection = Connection::open(path).map_err(|_| EdgeError::Storage)?;
        connection
            .execute_batch(
                "CREATE TABLE IF NOT EXISTS outbox (
                    nonce TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    payload BLOB NOT NULL,
                    expires_at INTEGER NOT NULL,
                    created_at INTEGER NOT NULL
                );",
            )
            .map_err(|_| EdgeError::Storage)?;
        Ok(Self { connection, limits })
    }

    pub fn enqueue(&mut self, item: OutboxItem, now: i64) -> Result<(), EdgeError> {
        self.purge_expired(now)?;
        self.connection
            .execute(
                "INSERT INTO outbox (nonce, kind, payload, expires_at, created_at) VALUES (?1, ?2, ?3, ?4, ?5)",
                params![item.nonce, item.kind, item.payload, item.expires_at, now],
            )
            .map_err(|_| EdgeError::Storage)?;
        self.trim_telemetry_to_limits()
    }

    pub fn due_outbox(&mut self, now: i64) -> Result<Vec<OutboxItem>, EdgeError> {
        self.purge_expired(now)?;
        let mut statement = self
            .connection
            .prepare(
                "SELECT nonce, kind, payload, expires_at FROM outbox ORDER BY created_at, rowid",
            )
            .map_err(|_| EdgeError::Storage)?;
        let rows = statement
            .query_map([], |row| {
                Ok(OutboxItem {
                    nonce: row.get(0)?,
                    kind: row.get(1)?,
                    payload: row.get(2)?,
                    expires_at: row.get(3)?,
                })
            })
            .map_err(|_| EdgeError::Storage)?;
        rows.collect::<Result<Vec<_>, _>>()
            .map_err(|_| EdgeError::Storage)
    }

    pub fn purge_expired(&mut self, now: i64) -> Result<(), EdgeError> {
        self.connection
            .execute("DELETE FROM outbox WHERE expires_at <= ?1", [now])
            .map_err(|_| EdgeError::Storage)?;
        Ok(())
    }

    fn trim_telemetry_to_limits(&mut self) -> Result<(), EdgeError> {
        loop {
            let (count, bytes): (i64, i64) = self
                .connection
                .query_row(
                    "SELECT COUNT(*), COALESCE(SUM(length(payload)), 0) FROM outbox",
                    [],
                    |row| Ok((row.get(0)?, row.get(1)?)),
                )
                .map_err(|_| EdgeError::Storage)?;
            if count <= self.limits.max_records as i64 && bytes <= self.limits.max_bytes as i64 {
                return Ok(());
            }
            let deleted = self
                .connection
                .execute(
                    "DELETE FROM outbox WHERE rowid = (SELECT rowid FROM outbox WHERE kind = 'telemetry' ORDER BY created_at, rowid LIMIT 1)",
                    [],
                )
                .map_err(|_| EdgeError::Storage)?;
            if deleted == 0 {
                return Err(EdgeError::OutboxFull);
            }
        }
    }
}
