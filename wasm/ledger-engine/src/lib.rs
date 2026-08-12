use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use wasm_bindgen::prelude::*;

/// EntryType represents double-entry book-keeping sides
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq, Eq)]
pub enum EntryType {
    Debit,
    Credit,
}

/// LedgerEntry represents a single debit/credit line in a double-entry transaction
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct LedgerEntry {
    pub account_id: String,
    pub entry_type: EntryType,
    pub amount_cents: u64,
}

/// LamportTimestamp tracking causality across distributed edge nodes
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub struct LamportTimestamp {
    pub counter: u64,
    pub node_id: String,
}

/// TransactionCRDT represents a state-based CRDT transaction record
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct TransactionCRDT {
    pub transaction_id: String,
    pub tenant_id: String,
    pub timestamp: LamportTimestamp,
    pub entries: Vec<LedgerEntry>,
    pub metadata_hash: String,
    pub synced_to_memcastle: bool,
}

/// SovereignLedgerEngine state held inside WebAssembly memory instance
#[wasm_bindgen]
pub struct SovereignLedgerEngine {
    node_id: String,
    current_lamport: u64,
    accounts: HashMap<String, i64>,
    transaction_log: Vec<TransactionCRDT>,
}

#[wasm_bindgen]
impl SovereignLedgerEngine {
    /// Instantiate a new Ledger Engine for an Edge Node
    #[wasm_bindgen(constructor)]
    pub fn new(node_id: String) -> Self {
        SovereignLedgerEngine {
            node_id,
            current_lamport: 0,
            accounts: HashMap::new(),
            transaction_log: Vec::new(),
        }
    }

    /// Advance local Lamport clock
    fn tick(&mut self) -> LamportTimestamp {
        self.current_lamport += 1;
        LamportTimestamp {
            counter: self.current_lamport,
            node_id: self.node_id.clone(),
        }
    }

    /// Create and validate a double-entry transaction locally before queuing to IndexedDB/MemCastle
    pub fn create_transaction(
        &mut self,
        transaction_id: String,
        tenant_id: String,
        entries_json: String,
        metadata_hash: String,
    ) -> Result<JsValue, JsValue> {
        let entries: Vec<LedgerEntry> = serde_json::from_str(&entries_json)
            .map_err(|e| JsValue::from_str(&format!("Invalid entry JSON: {}", e)))?;

        // Enforce double-entry invariant: Sum(Debits) MUST EQUAL Sum(Credits)
        let mut total_debits: u64 = 0;
        let mut total_credits: u64 = 0;

        for entry in &entries {
            match entry.entry_type {
                EntryType::Debit => total_debits += entry.amount_cents,
                EntryType::Credit => total_credits += entry.amount_cents,
            }
        }

        if total_debits != total_credits {
            return Err(JsValue::from_str(&format!(
                "Double-entry violation: Debits ({} cents) != Credits ({} cents)",
                total_debits, total_credits
            )));
        }

        let timestamp = self.tick();

        let tx = TransactionCRDT {
            transaction_id: transaction_id.clone(),
            tenant_id,
            timestamp,
            entries: entries.clone(),
            metadata_hash,
            synced_to_memcastle: false,
        };

        // Apply to local in-memory state balances
        for entry in entries {
            let balance = self.accounts.entry(entry.account_id).or_insert(0);
            match entry.entry_type {
                EntryType::Debit => *balance += entry.amount_cents as i64,
                EntryType::Credit => *balance -= entry.amount_cents as i64,
            }
        }

        self.transaction_log.push(tx.clone());

        serde_wasm_bindgen::to_value(&tx)
            .map_err(|e| JsValue::from_str(&format!("Serialization error: {}", e)))
    }

    /// Merge incoming CRDT deltas from external nodes or offline sync replay
    pub fn merge_crdt_delta(&mut self, remote_tx_json: String) -> Result<bool, JsValue> {
        let remote_tx: TransactionCRDT = serde_json::from_str(&remote_tx_json)
            .map_err(|e| JsValue::from_str(&format!("Invalid remote transaction: {}", e)))?;

        // Update local Lamport clock if remote is higher
        if remote_tx.timestamp.counter > self.current_lamport {
            self.current_lamport = remote_tx.timestamp.counter;
        }

        // Idempotency check: if transaction already exists, skip
        if self.transaction_log.iter().any(|tx| tx.transaction_id == remote_tx.transaction_id) {
            return Ok(false);
        }

        // Apply balances
        for entry in &remote_tx.entries {
            let balance = self.accounts.entry(entry.account_id.clone()).or_insert(0);
            match entry.entry_type {
                EntryType::Debit => *balance += entry.amount_cents as i64,
                EntryType::Credit => *balance -= entry.amount_cents as i64,
            }
        }

        self.transaction_log.push(remote_tx);
        // Sort log deterministically by Lamport timestamp
        self.transaction_log.sort_by(|a, b| a.timestamp.cmp(&b.timestamp));

        Ok(true)
    }

    /// Export un-synced Lamport timestamped queue for pushing to MemCastle over Bifrost Bridge
    pub fn export_lamport_queue(&mut self) -> Result<String, JsValue> {
        let pending: Vec<&TransactionCRDT> = self
            .transaction_log
            .iter()
            .filter(|tx| !tx.synced_to_memcastle)
            .collect();

        serde_json::to_string(&pending)
            .map_err(|e| JsValue::from_str(&format!("Failed to serialize queue: {}", e)))
    }

    /// Mark exported transactions as synced after MemCastle confirmation
    pub fn ack_memcastle_sync(&mut self, transaction_ids_json: String) -> Result<u32, JsValue> {
        let ids: Vec<String> = serde_json::from_str(&transaction_ids_json)
            .map_err(|e| JsValue::from_str(&format!("Invalid IDs JSON: {}", e)))?;

        let mut acked_count = 0;
        for tx in self.transaction_log.iter_mut() {
            if ids.contains(&tx.transaction_id) {
                tx.synced_to_memcastle = true;
                acked_count += 1;
            }
        }

        Ok(acked_count)
    }

    /// Return current account balance in cents
    pub fn get_account_balance(&self, account_id: String) -> i64 {
        *self.accounts.get(&account_id).unwrap_or(&0)
    }

    /// Verify full ledger integrity across all recorded transactions
    pub fn verify_ledger_integrity(&self) -> bool {
        let mut computed_balances: HashMap<String, i64> = HashMap::new();

        for tx in &self.transaction_log {
            for entry in &tx.entries {
                let bal = computed_balances.entry(entry.account_id.clone()).or_insert(0);
                match entry.entry_type {
                    EntryType::Debit => *bal += entry.amount_cents as i64,
                    EntryType::Credit => *bal -= entry.amount_cents as i64,
                }
            }
        }

        computed_balances == self.accounts
    }
}
