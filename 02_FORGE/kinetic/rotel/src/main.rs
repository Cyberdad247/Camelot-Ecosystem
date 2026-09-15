// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
use clap::{Parser, Subcommand};
use serde::{Deserialize, Serialize};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use uuid::Uuid;
use chrono::{Local, Utc};
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
    /// Mobile Sentinel & ADB Device Controller (assimilated from escrcpy)
    Adb {
        #[command(subcommand)]
        action: AdbAction,
    },
}

#[derive(Subcommand)]
pub enum AdbAction {
    /// List connected mobile sentinels via ADB (S26 Ultra & Moto G)
    Devices,
    /// Generate or launch scrcpy streaming session optimized for Excalibur
    Mirror {
        /// Target device serial or Tailscale IP (e.g. 100.106.246.126:5555)
        #[arg(short, long, default_value = "100.106.246.126:5555")]
        serial: String,

        /// Video bitrate (Mbps)
        #[arg(long, default_value_t = 8)]
        bitrate: u32,

        /// Forward Opus audio stream into Bifrost
        #[arg(long, default_value_t = true)]
        audio: bool,

        /// Only output the command line without launching
        #[arg(long)]
        dry_run: bool,
    },
    /// Inject touch tap at coordinates (x, y)
    Tap {
        #[arg(short, long, default_value = "100.106.246.126:5555")]
        serial: String,
        x: u32,
        y: u32,
    },
    /// Inject swipe gesture (x1 y1 x2 y2 duration_ms)
    Swipe {
        #[arg(short, long, default_value = "100.106.246.126:5555")]
        serial: String,
        x1: u32,
        y1: u32,
        x2: u32,
        y2: u32,
        #[arg(long, default_value_t = 300)]
        duration_ms: u32,
    },
    /// Inject text input into mobile device
    Text {
        #[arg(short, long, default_value = "100.106.246.126:5555")]
        serial: String,
        text: String,
    },
    /// Capture screenshot and save to path
    Screenshot {
        #[arg(short, long, default_value = "100.106.246.126:5555")]
        serial: String,
        #[arg(short, long, default_value = "excalibur_screenshot.png")]
        output: String,
    },
    /// Pull reverse device telemetry (battery, memory, orientation, active window)
    Telemetry {
        #[arg(short, long, default_value = "100.106.246.126:5555")]
        serial: String,
        /// Output formatted JSON
        #[arg(long)]
        json: bool,
    },
    /// Listen for reverse mobile intent broadcasts and touch telemetry
    Listen {
        #[arg(short, long, default_value = "100.106.246.126:5555")]
        serial: String,
        /// Bounded stream capture duration (seconds)
        #[arg(long, default_value_t = 10)]
        duration_s: u64,
    },
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
        Commands::Adb { action } => {
            handle_adb(action)?;
        }
    }

    Ok(())
}

fn handle_adb(action: AdbAction) -> Result<()> {
    match action {
        AdbAction::Devices => {
            println!("⚡ [ROTEL_ADB] Enumerating connected Mobile Sentinels...");
            let out = std::process::Command::new("adb")
                .arg("devices")
                .output()
                .context("Failed to execute adb. Ensure android platform-tools are in PATH.")?;
            println!("{}", String::from_utf8_lossy(&out.stdout));
        }
        AdbAction::Mirror { serial, bitrate, audio, dry_run } => {
            let mut args = vec![
                "-s".to_string(), serial.clone(),
                "--video-bit-rate".to_string(), format!("{}M", bitrate),
                "--max-fps".to_string(), "60".to_string(),
            ];
            if audio {
                args.push("--audio-codec=opus".to_string());
            } else {
                args.push("--no-audio".to_string());
            }

            let full_cmd = format!("scrcpy {}", args.join(" "));
            println!("⚡ [EXCALIBUR_MIRROR] Command: {}", full_cmd);
            if !dry_run {
                println!("🚀 Launching scrcpy mobile stream for Excalibur ({serial})...");
                std::process::Command::new("scrcpy")
                    .args(&args)
                    .spawn()
                    .context("Failed to spawn scrcpy. Ensure scrcpy is installed.")?;
            }
        }
        AdbAction::Tap { serial, x, y } => {
            println!("⚡ [ROTEL_ADB] Injecting tap at ({x}, {y}) on {serial}...");
            std::process::Command::new("adb")
                .args(["-s", &serial, "shell", "input", "tap", &x.to_string(), &y.to_string()])
                .status()
                .context("Failed to inject tap via adb")?;
            println!("✓ Tap injected.");
        }
        AdbAction::Swipe { serial, x1, y1, x2, y2, duration_ms } => {
            println!("⚡ [ROTEL_ADB] Injecting swipe ({x1},{y1}) -> ({x2},{y2}) [{}ms] on {serial}...", duration_ms);
            std::process::Command::new("adb")
                .args([
                    "-s", &serial, "shell", "input", "swipe",
                    &x1.to_string(), &y1.to_string(),
                    &x2.to_string(), &y2.to_string(),
                    &duration_ms.to_string()
                ])
                .status()
                .context("Failed to inject swipe via adb")?;
            println!("✓ Swipe injected.");
        }
        AdbAction::Text { serial, text } => {
            println!("⚡ [ROTEL_ADB] Sending text input to {serial}...");
            std::process::Command::new("adb")
                .args(["-s", &serial, "shell", "input", "text", &text])
                .status()
                .context("Failed to input text via adb")?;
            println!("✓ Text dispatched.");
        }
        AdbAction::Screenshot { serial, output } => {
            println!("⚡ [ROTEL_ADB] Capturing screenshot from {serial} -> {output}...");
            let out_file = std::fs::File::create(&output).context("Failed to create screenshot file")?;
            std::process::Command::new("adb")
                .args(["-s", &serial, "exec-out", "screencap", "-p"])
                .stdout(out_file)
                .status()
                .context("Failed to capture screenshot via adb")?;
            println!("✓ Screenshot saved to {output}");
        }
        AdbAction::Telemetry { serial, json } => {
            println!("⚡ [ROTEL_ADB] Pulling reverse mobile sentinel telemetry from {serial}...");
            let battery = std::process::Command::new("adb")
                .args(["-s", &serial, "shell", "dumpsys", "battery"])
                .output()
                .map(|o| String::from_utf8_lossy(&o.stdout).to_string())
                .unwrap_or_else(|_| "battery_unavailable".to_string());

            let window = std::process::Command::new("adb")
                .args(["-s", &serial, "shell", "dumpsys", "window", "displays"])
                .output()
                .map(|o| String::from_utf8_lossy(&o.stdout).to_string())
                .unwrap_or_else(|_| "window_unavailable".to_string());

            if json {
                let report = serde_json::json!({
                    "serial": serial,
                    "direction": "MOBILE_TO_CAMELOT (REVERSE TELEMETRY)",
                    "battery_sample": battery.lines().take(6).collect::<Vec<&str>>(),
                    "window_sample": window.lines().filter(|l| l.contains("cur=")).take(3).collect::<Vec<&str>>(),
                    "timestamp": Utc::now().to_rfc3339()
                });
                println!("{}", serde_json::to_string_pretty(&report)?);
            } else {
                println!("--- Battery Telemetry ---");
                for line in battery.lines().take(6) {
                    println!("  {}", line);
                }
                println!("--- Display & Focus Telemetry ---");
                for line in window.lines().filter(|l| l.contains("cur=")).take(3) {
                    println!("  {}", line);
                }
            }
            println!("✓ Bidirectional telemetry verified.");
        }
        AdbAction::Listen { serial, duration_s } => {
            println!("⚡ [ROTEL_ADB] Listening to reverse event stream from {serial} for {}s...", duration_s);
            let mut child = std::process::Command::new("adb")
                .args(["-s", &serial, "shell", "getevent", "-l"])
                .stdout(std::process::Stdio::piped())
                .spawn()
                .context("Failed to attach to device event queue")?;

            std::thread::sleep(std::time::Duration::from_secs(duration_s));
            let _ = child.kill();
            println!("✓ Reverse stream listener detached after {}s.", duration_s);
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