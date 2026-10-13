//! Immutable SQLite Ledger with Blake3 Cryptographic Hashes
//! ========================================================

use blake3::Hasher;
use rusqlite::{params, Connection, Result};
use std::time::{SystemTime, UNIX_EPOCH};

pub struct Ledger {
    conn: Connection,
}

impl Ledger {
    pub fn new(path: &str) -> Result<Self> {
        let conn = Connection::open(path)?;
        Ok(Self { conn })
    }

    pub fn in_memory() -> Result<Self> {
        let conn = Connection::open_in_memory()?;
        Ok(Self { conn })
    }

    pub fn initialize(&self) -> Result<()> {
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                action TEXT NOT NULL,
                actor TEXT NOT NULL,
                status TEXT NOT NULL,
                hash TEXT NOT NULL
            )",
            [],
        )?;
        Ok(())
    }

    pub fn write_receipt(&mut self, action: &str, actor: &str, status: &str) -> Result<String> {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        // Cryptographic Hash Generation via Blake3
        let mut hasher = Hasher::new();
        hasher.update(action.as_bytes());
        hasher.update(actor.as_bytes());
        hasher.update(status.as_bytes());
        hasher.update(timestamp.to_string().as_bytes());
        let hash = hasher.finalize().to_hex().to_string();

        self.conn.execute(
            "INSERT INTO receipts (timestamp, action, actor, status, hash) VALUES (?1, ?2, ?3, ?4, ?5)",
            params![timestamp as i64, action, actor, status, hash],
        )?;

        Ok(hash)
    }

    pub fn write_explicit_receipt(
        &mut self,
        action: &str,
        actor: &str,
        status: &str,
        hash: &str,
    ) -> Result<()> {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        self.conn.execute(
            "INSERT INTO receipts (timestamp, action, actor, status, hash) VALUES (?1, ?2, ?3, ?4, ?5)",
            params![timestamp as i64, action, actor, status, hash],
        )?;

        Ok(())
    }

    pub fn count_receipts(&self) -> Result<usize> {
        let mut stmt = self.conn.prepare("SELECT COUNT(*) FROM receipts")?;
        let count: usize = stmt.query_row([], |row| row.get(0))?;
        Ok(count)
    }

    pub fn get_latest_receipt_hash(&self) -> Result<Option<String>> {
        let mut stmt = self
            .conn
            .prepare("SELECT hash FROM receipts ORDER BY id DESC LIMIT 1")?;
        let mut rows = stmt.query([])?;
        if let Some(row) = rows.next()? {
            Ok(Some(row.get(0)?))
        } else {
            Ok(None)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ledger_initialization_and_receipt_write() {
        let mut ledger = Ledger::in_memory().expect("in-memory db");
        ledger.initialize().expect("initialize table");

        let hash = ledger
            .write_receipt("system_boot", "MERLIN_OMEGA", "SUCCESS")
            .expect("write receipt");

        assert_eq!(hash.len(), 64);
        assert_eq!(ledger.count_receipts().unwrap(), 1);
        assert_eq!(ledger.get_latest_receipt_hash().unwrap(), Some(hash));
    }
}
