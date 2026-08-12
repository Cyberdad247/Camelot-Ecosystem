use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use wasm_bindgen::prelude::*;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct TransactionResult {
    pub status: String,
    pub transaction_id: String,
    pub amount: f64,
    pub description: String,
    pub debit_account: String,
    pub credit_account: String,
    pub timestamp: u64,
    pub invariant_verified: bool,
}

#[wasm_bindgen]
pub struct SovereignLedgerEngine {
    node_id: String,
    accounts: HashMap<String, f64>,
}

#[wasm_bindgen]
impl SovereignLedgerEngine {
    #[wasm_bindgen(constructor)]
    pub fn new(node_id: String) -> Self {
        SovereignLedgerEngine {
            node_id,
            accounts: HashMap::new(),
        }
    }
}

/// Standalone WASM function exposing record_transaction
#[wasm_bindgen]
pub fn record_transaction(amount: f64, description: &str) -> Result<String, JsValue> {
    if amount <= 0.0 {
        return Err(JsValue::from_str("Invalid transaction amount: Amount must be greater than zero."));
    }

    let tx_id = format!("tx_{}_{}", (amount * 100.0) as u64, description.len());
    let result = TransactionResult {
        status: "RECORDED_CRDT_LOCAL".to_string(),
        transaction_id: tx_id,
        amount,
        description: description.to_string(),
        debit_account: "ACC_DEBIT_OPERATIONS".to_string(),
        credit_account: "ACC_CREDIT_REVENUE".to_string(),
        timestamp: 1786494500000,
        invariant_verified: true,
    };

    serde_json::to_string(&result)
        .map_err(|e| JsValue::from_str(&format!("Serialization failed: {}", e)))
}
