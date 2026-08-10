use std::env;
use std::fs;
use std::path::Path;
use std::thread;
use std::time::{Duration, Instant};
use rusqlite::{params, Connection, Result};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct SearchResult {
    id: String,
    score: f32,
    payload: serde_json::Value,
}

fn cosine_similarity(a: &[f32], b: &[f32]) -> f32 {
    let dot: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
    let norm_a: f32 = a.iter().map(|x| x * x).sum::<f32>().sqrt();
    let norm_b: f32 = b.iter().map(|x| x * x).sum::<f32>().sqrt();
    if norm_a > 0.0 && norm_b > 0.0 {
        dot / (norm_a * norm_b)
    } else {
        0.0
    }
}

fn get_db_connection() -> Connection {
    let db_path = Path::new("data/memory_store.sqlite3");
    if let Some(parent) = db_path.parent() {
        let _ = fs::create_dir_all(parent);
    }
    let conn = Connection::open(db_path).expect("failed to open sqlite database");
    
    // Create tables if they do not exist
    conn.execute(
        "CREATE TABLE IF NOT EXISTS vectors (
            collection TEXT,
            id TEXT,
            vector TEXT,
            payload TEXT,
            PRIMARY KEY (collection, id)
        )",
        [],
    ).expect("failed to create vectors table");

    conn.execute(
        "CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel TEXT,
            message TEXT,
            consumed INTEGER DEFAULT 0
        )",
        [],
    ).expect("failed to create messages table");

    conn
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage:");
        eprintln!("  memory_palace upsert <collection> <id> <vector_json> <payload_json>");
        eprintln!("  memory_palace search <collection> <vector_json> <limit>");
        eprintln!("  memory_palace delete <collection> <id>");
        eprintln!("  memory_palace publish <channel> <message>");
        eprintln!("  memory_palace subscribe_one <channel> <timeout_secs>");
        eprintln!("  memory_palace stats");
        std::process::exit(1);
    }

    let cmd = &args[1];
    let conn = get_db_connection();

    match cmd.as_str() {
        "upsert" => {
            if args.len() < 6 {
                eprintln!("Error: upsert requires: <collection> <id> <vector_json> <payload_json>");
                std::process::exit(1);
            }
            let collection = &args[2];
            let id = &args[3];
            let vector_json = &args[4];
            let payload_json = &args[5];

            // Verify valid JSON
            let _: Vec<f32> = serde_json::from_str(vector_json).expect("invalid vector json");
            let _: serde_json::Value = serde_json::from_str(payload_json).expect("invalid payload json");

            conn.execute(
                "INSERT INTO vectors (collection, id, vector, payload)
                 VALUES (?1, ?2, ?3, ?4)
                 ON CONFLICT(collection, id) DO UPDATE SET
                    vector=excluded.vector,
                    payload=excluded.payload",
                params![collection, id, vector_json, payload_json],
            ).expect("failed to execute upsert");

            println!("{{\"status\":\"ok\",\"action\":\"upsert\",\"id\":\"{}\"}}", id);
        }
        "search" => {
            if args.len() < 5 {
                eprintln!("Error: search requires: <collection> <vector_json> <limit>");
                std::process::exit(1);
            }
            let collection = &args[2];
            let vector_json = &args[3];
            let limit: usize = args[4].parse().unwrap_or(5);

            let query_vector: Vec<f32> = serde_json::from_str(vector_json).expect("invalid query vector json");

            let mut stmt = conn.prepare(
                "SELECT id, vector, payload FROM vectors WHERE collection = ?1"
            ).expect("failed to prepare select statement");

            let rows = stmt.query_map(params![collection], |row| {
                let id: String = row.get(0)?;
                let v_str: String = row.get(1)?;
                let p_str: String = row.get(2)?;
                Ok((id, v_str, p_str))
            }).expect("failed to execute select query");

            let mut results = Vec::new();
            for row in rows {
                if let Ok((id, v_str, p_str)) = row {
                    if let Ok(v) = serde_json::from_str::<Vec<f32>>(&v_str) {
                        let score = cosine_similarity(&query_vector, &v);
                        let payload: serde_json::Value = serde_json::from_str(&p_str).unwrap_or(serde_json::Value::Null);
                        results.push(SearchResult { id, score, payload });
                    }
                }
            }

            // Sort descending by score
            results.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap_or(std::cmp::Ordering::Equal));
            results.truncate(limit);

            let out_json = serde_json::to_string(&results).unwrap();
            println!("{}", out_json);
        }
        "delete" => {
            if args.len() < 4 {
                eprintln!("Error: delete requires: <collection> <id>");
                std::process::exit(1);
            }
            let collection = &args[2];
            let id = &args[3];

            conn.execute(
                "DELETE FROM vectors WHERE collection = ?1 AND id = ?2",
                params![collection, id],
            ).expect("failed to delete");

            println!("{{\"status\":\"ok\",\"action\":\"delete\",\"id\":\"{}\"}}", id);
        }
        "publish" => {
            if args.len() < 4 {
                eprintln!("Error: publish requires: <channel> <message>");
                std::process::exit(1);
            }
            let channel = &args[2];
            let message = &args[3];

            conn.execute(
                "INSERT INTO messages (channel, message, consumed) VALUES (?1, ?2, 0)",
                params![channel, message],
            ).expect("failed to publish message");

            println!("{{\"status\":\"ok\",\"action\":\"publish\",\"channel\":\"{}\"}}", channel);
        }
        "subscribe_one" => {
            if args.len() < 3 {
                eprintln!("Error: subscribe_one requires: <channel> [timeout_secs]");
                std::process::exit(1);
            }
            let channel = &args[2];
            let timeout_secs: u64 = if args.len() > 3 { args[3].parse().unwrap_or(30) } else { 30 };

            let start = Instant::now();
            let poll_interval = Duration::from_millis(200);
            let timeout = Duration::from_secs(timeout_secs);

            let mut message_found: Option<String> = None;

            while start.elapsed() < timeout {
                // Perform thread-safe SQLite transaction block
                let tx = conn.unchecked_transaction().expect("failed to begin transaction");
                let res: Result<(i64, String)> = tx.query_row(
                    "SELECT id, message FROM messages WHERE channel = ?1 AND consumed = 0 ORDER BY id ASC LIMIT 1",
                    params![channel],
                    |row| Ok((row.get(0)?, row.get(1)?))
                );

                if let Ok((id, msg)) = res {
                    let _ = tx.execute(
                        "UPDATE messages SET consumed = 1 WHERE id = ?1",
                        params![id]
                    );
                    let _ = tx.commit();
                    message_found = Some(msg);
                    break;
                } else {
                    let _ = tx.rollback();
                }
                thread::sleep(poll_interval);
            }

            match message_found {
                Some(msg) => println!("{}", msg),
                None => {
                    println!("{{\"status\":\"timeout\",\"channel\":\"{}\"}}", channel);
                    std::process::exit(1);
                }
            }
        }
        "stats" => {
            let mut stmt = conn.prepare(
                "SELECT collection, COUNT(*) FROM vectors GROUP BY collection"
            ).expect("failed to prepare stats query");

            let rows = stmt.query_map([], |row| {
                let col: String = row.get(0)?;
                let count: i64 = row.get(1)?;
                Ok((col, count))
            }).expect("failed to execute stats query");

            let mut stats_map = std::collections::HashMap::new();
            for row in rows {
                if let Ok((col, count)) = row {
                    stats_map.insert(col, count);
                }
            }

            let out_json = serde_json::to_string(&stats_map).unwrap();
            println!("{}", out_json);
        }
        _ => {
            eprintln!("Unknown command: {}", cmd);
            std::process::exit(1);
        }
    }
}
