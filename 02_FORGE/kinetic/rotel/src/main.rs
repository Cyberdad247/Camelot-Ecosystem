// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
use clap::{Parser, Subcommand};
use serde::{Deserialize, Serialize};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use uuid::Uuid;
use chrono::{DateTime, Local, Utc};
use anyhow::{Context, Result};

#[derive(Parser)]
#[command(name = "rotel")]
#[command(about = "High-Performance Telemetry Collector (Kinetic Layer)", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Log a single span/event immediately
    Log {
        /// Name of the event/span
        #[arg(short, long)]
        name: String,

        /// Duration in milliseconds
        #[arg(short, long, default_value_t = 0.0)]
        duration: f64,

        /// Trace ID (optional, generates new if missing)
        #[arg(short, long)]
        trace_id: Option<String>,

        /// Span ID (optional, generates new if missing)
        #[arg(short, long)]
        span_id: Option<String>,

        /// Parent ID (optional)
        #[arg(short, long)]
        parent_id: Option<String>,

        /// JSON attributes (e.g. '{"key": "value"}')
        #[arg(short, long)]
        attrs: Option<String>,
    },
    /// Generate a new Trace ID
    Id,
}

#[derive(Serialize, Deserialize)]
struct RotelEntry {
    name: String,
    trace_id: String,
    span_id: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    parent_id: Option<String>,
    start_time: String,
    end_time: String,
    duration_ms: f64,
    attributes: serde_json::Value,
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Log { name, duration, trace_id, span_id, parent_id, attrs } => {
            let now = Utc::now();
            // Calculate start time based on duration (assuming 'now' is end)
            // In a real span system, we'd have explicit start/end, but for a simple logger, this works.
            let duration_ms = duration;
            let start_time_dt = now - chrono::Duration::milliseconds(duration as i64);
            
            let tid = trace_id.unwrap_or_else(|| Uuid::new_v4().to_string());
            let sid = span_id.unwrap_or_else(|| Uuid::new_v4().to_string());
            
            let attributes: serde_json::Value = if let Some(a_str) = attrs {
                serde_json::from_str(&a_str).unwrap_or(serde_json::json!({"error": "invalid_json_attrs"}))
            } else {
                serde_json::json!({})
            };

            let entry = RotelEntry {
                name,
                trace_id: tid,
                span_id: sid,
                parent_id,
                start_time: start_time_dt.to_rfc3339(),
                end_time: now.to_rfc3339(),
                duration_ms,
                attributes,
            };

            log_to_file(&entry)?;
            println!("✓ Logged: {} (Trace: {})", entry.name, entry.trace_id);
        }
        Commands::Id => {
            println!("{}", Uuid::new_v4());
        }
    }

    Ok(())
}

fn log_to_file(entry: &RotelEntry) -> Result<()> {
    let cos_root = std::env::var("CAMELOT_OS_HOME")
        .unwrap_or_else(|_| {
            let home = std::env::var("USERPROFILE")
                .or_else(|_| std::env::var("HOME"))
                .unwrap_or_else(|_| ".".to_string());
            format!("{}/CAMELOT_OS", home)
        });
    let base_path = PathBuf::from(cos_root).join("logs").join("rotel_traces");
    std::fs::create_dir_all(&base_path).context("Failed to create log dir")?;

    let date_str = Local::now().format("%Y%m%d").to_string();
    let file_name = format!("rotel_{}.jsonl", date_str);
    let file_path = base_path.join(file_name);

    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&file_path)
        .context("Failed to open log file")?;

    let json_line = serde_json::to_string(entry)?;
    writeln!(file, "{}", json_line)?;

    Ok(())
}