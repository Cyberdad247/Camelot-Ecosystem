// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
//! Autonomous Rust background daemon for memory governance and working set trimming.
//! Operates in the background with <2MB resident working set, fulfilling Rule 7 (0% Python hotpath).

use crate::pagekeeper::{self, MemoryAudit, SystemMemory};
use serde::{Deserialize, Serialize};
use std::fs::{self, File};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone)]
pub struct DaemonConfig {
    pub interval_secs: u64,
    pub threshold_pct: f64,
    pub heartbeat_path: Option<PathBuf>,
    pub max_cycles: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HeartbeatReport {
    pub daemon: String,
    pub pid: u32,
    pub cycle: u64,
    pub timestamp: String,
    pub interval_secs: u64,
    pub threshold_pct: f64,
    pub memory: SystemMemory,
    pub last_audit: MemoryAudit,
    pub cumulative_trims: usize,
    pub cumulative_reclaimed_mb: f64,
    pub status: String,
}

fn iso_timestamp() -> String {
    let now = SystemTime::now();
    let duration = now.duration_since(UNIX_EPOCH).unwrap_or_default();
    format!("{}.{:03}Z", duration.as_secs(), duration.subsec_millis())
}

fn write_atomic_heartbeat(path: &Path, report: &HeartbeatReport) -> std::io::Result<()> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    let tmp_path = path.with_extension("tmp");
    let json_bytes = serde_json::to_vec_pretty(report)?;
    {
        let mut file = File::create(&tmp_path)?;
        file.write_all(&json_bytes)?;
        file.flush()?;
    }
    fs::rename(&tmp_path, path)?;
    Ok(())
}

fn get_pid() -> u32 {
    #[cfg(target_os = "windows")]
    unsafe {
        #[link(name = "kernel32")]
        extern "system" {
            fn GetCurrentProcessId() -> u32;
        }
        GetCurrentProcessId()
    }
    #[cfg(not(target_os = "windows"))]
    {
        std::process::id()
    }
}

pub fn run_daemon(config: DaemonConfig) {
    let pid = get_pid();
    println!("[PAGEKEEPER_RS] CAMELOT-OS Rust Memory Governor Daemon");
    println!("   PID:             {}", pid);
    println!("   Cycle Interval:  {}s", config.interval_secs);
    println!("   Threshold:       {}%", config.threshold_pct);
    println!("   Max Cycles:      {}", if config.max_cycles == 0 { "Infinite".to_string() } else { config.max_cycles.to_string() });
    if let Some(ref hb) = config.heartbeat_path {
        println!("   Heartbeat Sink:  {}", hb.display());
    }
    println!("------------------------------------------------------------");

    let mut cycle: u64 = 0;
    let mut cumulative_trims: usize = 0;
    let mut cumulative_reclaimed_mb: f64 = 0.0;

    loop {
        cycle += 1;
        let audit = pagekeeper::govern(config.threshold_pct, false);
        let mem = pagekeeper::get_system_memory();

        if audit.reclaimed_mb > 0.0 {
            cumulative_trims += 1;
            cumulative_reclaimed_mb += audit.reclaimed_mb;
            println!(
                "[{}] Cycle #{}: Action: {} | Reclaimed: {:.1} MB | Total: {:.1} MB",
                iso_timestamp(),
                cycle,
                audit.action_taken,
                audit.reclaimed_mb,
                cumulative_reclaimed_mb
            );
        } else {
            println!(
                "[{}] Cycle #{}: Util: {:.1}% ({:.1}/{:.1} MB) | Pressure: {} | Status: OK",
                iso_timestamp(),
                cycle,
                mem.utilization_pct,
                mem.used_phys_mb,
                mem.total_phys_mb,
                audit.pressure_detected
            );
        }

        if let Some(ref hb_path) = config.heartbeat_path {
            let status = if audit.pressure_detected {
                "HIGH_PRESSURE"
            } else {
                "HEALTHY"
            };
            let report = HeartbeatReport {
                daemon: "PAGEKEEPER_RS".to_string(),
                pid,
                cycle,
                timestamp: iso_timestamp(),
                interval_secs: config.interval_secs,
                threshold_pct: config.threshold_pct,
                memory: mem,
                last_audit: audit,
                cumulative_trims,
                cumulative_reclaimed_mb: (cumulative_reclaimed_mb * 10.0).round() / 10.0,
                status: status.to_string(),
            };

            if let Err(e) = write_atomic_heartbeat(hb_path, &report) {
                eprintln!("[WARN] Failed writing heartbeat to {}: {}", hb_path.display(), e);
            }
        }

        if config.max_cycles > 0 && cycle >= config.max_cycles {
            println!("[OK] Completed configured max cycles ({}). Daemon exiting gracefully.", config.max_cycles);
            break;
        }

        thread::sleep(Duration::from_secs(config.interval_secs));
    }
}
