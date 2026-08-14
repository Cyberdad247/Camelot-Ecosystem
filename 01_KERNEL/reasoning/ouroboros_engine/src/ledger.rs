// SPDX-License-Identifier: MIT

// Phase 3: Rust in-memory ring of executions + WAL persistence.
// Path: 03_VAULT/memory/ouroboros/ouroboros.wal

use std::fs::{create_dir_all, File, OpenOptions};
use std::io::{BufRead, BufReader, Write};
use std::path::PathBuf;
use std::sync::Mutex;
use std::sync::LazyLock;
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Clone)]
pub struct Entry {
    pub id: u64,
    pub timestamp: String,
    pub directive: String,
    pub intent: Option<String>,
    pub domain: Option<String>,
    pub complexity: i64,
    pub knight: String,
    pub status: String,
    pub result: Option<String>,
    pub duration_ms: i64,
    pub files_created: Vec<String>,
}

#[derive(Serialize, Deserialize, Clone, Default)]
pub struct KnightStats {
    pub knight: String,
    pub total_runs: i64,
    pub successes: i64,
    pub failures: i64,
    pub blocked: i64,
    pub avg_duration_ms: f64,
}

pub struct Ledger {
    pub entries: Vec<Entry>,
    pub next_id: u64,
    pub wal_file: Option<File>,
}

static LEDGER_STATE: LazyLock<Mutex<Ledger>> = LazyLock::new(|| {
    Mutex::new(Ledger::new())
});

impl Ledger {
    fn new() -> Self {
        let mut entries = Vec::new();
        let mut next_id = 1;

        // Resolve WAL path relative to CAMELOT_OS_HOME or current directory
        let base = std::env::var("CAMELOT_OS_HOME")
            .map(PathBuf::from)
            .unwrap_or_else(|_| {
                std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."))
            });
        let wal_dir = base.join("03_VAULT/memory/ouroboros");
        let wal_path = wal_dir.join("ouroboros.wal");

        // Try loading historical WAL
        if wal_path.exists() {
            if let Ok(file) = File::open(&wal_path) {
                let reader = BufReader::new(file);
                for line in reader.lines().map_while(Result::ok) {
                    if let Ok(entry) = serde_json::from_str::<Entry>(&line) {
                        if entry.id >= next_id {
                            next_id = entry.id + 1;
                        }
                        entries.push(entry);
                    }
                }
            }
        } else {
            // Ensure directory exists
            let _ = create_dir_all(&wal_dir);
        }

        // Open WAL file for appending
        let wal_file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&wal_path)
            .ok();

        Ledger {
            entries,
            next_id,
            wal_file,
        }
    }
}

#[allow(clippy::too_many_arguments)]
pub fn append(
    directive: String,
    intent: Option<String>,
    domain: Option<String>,
    complexity: i64,
    knight: String,
    status: String,
    result: Option<String>,
    duration_ms: i64,
    files_created: Option<String>,
) -> Result<(), String> {
    let mut state = LEDGER_STATE.lock().map_err(|e| e.to_string())?;
    
    // Parse files_created JSON list from Python side if present
    let files = if let Some(ref s) = files_created {
        serde_json::from_str::<Vec<String>>(s).unwrap_or_default()
    } else {
        Vec::new()
    };

    let id = state.next_id;
    state.next_id += 1;

    let timestamp = chrono::Local::now().to_rfc3339();

    let entry = Entry {
        id,
        timestamp,
        directive,
        intent,
        domain,
        complexity,
        knight,
        status,
        result,
        duration_ms,
        files_created: files,
    };

    // Write to WAL file first (Write-Ahead Log)
    if let Some(ref mut file) = state.wal_file {
        if let Ok(serialized) = serde_json::to_string(&entry) {
            if let Err(e) = writeln!(file, "{}", serialized) {
                return Err(format!("Failed to write to WAL: {}", e));
            }
            if let Err(e) = file.flush() {
                return Err(format!("Failed to flush WAL: {}", e));
            }
        }
    }

    // Append to memory ring
    state.entries.push(entry);

    Ok(())
}

pub fn get_history(limit: Option<usize>) -> Result<Vec<Entry>, String> {
    let state = LEDGER_STATE.lock().map_err(|e| e.to_string())?;
    let len = state.entries.len();
    let take_count = limit.unwrap_or(20).min(len);
    let mut history: Vec<Entry> = state.entries[len - take_count..].to_vec();
    history.reverse(); // newest first
    Ok(history)
}

pub fn get_stats() -> Result<Vec<KnightStats>, String> {
    let state = LEDGER_STATE.lock().map_err(|e| e.to_string())?;
    let mut stats_map = std::collections::HashMap::new();

    for entry in &state.entries {
        let stats = stats_map.entry(entry.knight.clone()).or_insert_with(|| KnightStats {
            knight: entry.knight.clone(),
            ..Default::default()
        });

        stats.total_runs += 1;
        match entry.status.as_str() {
            "success" => stats.successes += 1,
            "error" => stats.failures += 1,
            "blocked" => stats.blocked += 1,
            _ => {}
        }
        stats.avg_duration_ms += entry.duration_ms as f64;
    }

    let mut result: Vec<KnightStats> = stats_map.into_values().collect();
    for stats in &mut result {
        if stats.total_runs > 0 {
            stats.avg_duration_ms /= stats.total_runs as f64;
        }
    }

    // Sort by total runs descending
    result.sort_by_key(|b| std::cmp::Reverse(b.total_runs));
    Ok(result)
}

pub fn flush_pending() -> Result<u64, String> {
    let state = LEDGER_STATE.lock().map_err(|e| e.to_string())?;
    Ok(state.entries.len() as u64)
}

pub fn clear() -> Result<(), String> {
    let mut state = LEDGER_STATE.lock().map_err(|e| e.to_string())?;
    state.entries.clear();
    state.next_id = 1;
    
    // Reset/truncate the WAL file under the current CAMELOT_OS_HOME
    let base = std::env::var("CAMELOT_OS_HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|_| {
            std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."))
        });
    let wal_dir = base.join("03_VAULT/memory/ouroboros");
    let wal_path = wal_dir.join("ouroboros.wal");
    let _ = create_dir_all(&wal_dir);
    state.wal_file = OpenOptions::new()
        .create(true)
        .write(true)
        .truncate(true)
        .open(&wal_path)
        .ok();
    Ok(())
}
