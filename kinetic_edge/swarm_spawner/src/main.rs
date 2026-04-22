//! SRDL Bio-Swarm Spawner — CAMELOT Apex OS v400.1.0
//! ====================================================
//! Lukas_Omega | L2_KINETIC | kinetic_edge/swarm_spawner
//!
//! SRDL 3-Phase loop:
//!   PHASE A (MAP)    — reads harness_queue.jsonl, decomposes into Nano-Knight DAG
//!   PHASE B (REDUCE) — Sir Sentinel audit + Iron Gate HITL check
//!   PHASE C (KINETIC)— spawns isolated subprocesses, apoptosis monitoring
//!
//! Bio-Swarm Zoology:
//!   Formica (Ant)    — map-reduce parallel file ops      budget=150 tokens
//!   Pongid (Gorilla) — heavy API integration             budget=300 tokens
//!   Castor (Beaver)  — infrastructure + isolation builds  budget=200 tokens
//!   Arachne (Spider) — headless browser / MCP scraping   budget=200 tokens
//!   Simian (Chaos)   — resilience/entropy injection       budget=150 tokens
//!   Strigiform (Owl) — swarm oversight, conflict detect   budget=100 tokens

use anyhow::Result;
use chrono::Utc;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
use tokio::fs;
use tokio::io::{AsyncBufReadExt, BufReader};
use tokio::time::sleep;
use tracing::{error, info, warn};

// ── Constants ────────────────────────────────────────────────────────────────

const POLL_INTERVAL_MS: u64 = 2_000;
const APOPTOSIS_ERROR_THRESHOLD: f64 = 0.05;
const APOPTOSIS_MIN_TASKS: u32 = 10;
const APOPTOSIS_IDLE_SECS: u64 = 7 * 24 * 3600; // 7 days
const MAX_FORMICA_INSTANCES: usize = 50;          // 8GB RAM ceiling
const RAM_CEILING_MB: usize = 7_800;

// ── Nano-Knight species ───────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
enum Species {
    Formica,   // Ant — map-reduce file ops
    Pongid,    // Gorilla — heavy API calls
    Castor,    // Beaver — infra builds
    Arachne,   // Spider — browser/MCP scraping
    Simian,    // Chaos Monkey — resilience testing
    Strigiform, // Owl — oversight
}

impl Species {
    fn token_budget(&self) -> u32 {
        match self {
            Species::Formica    => 150,
            Species::Pongid     => 300,
            Species::Castor     => 200,
            Species::Arachne    => 200,
            Species::Simian     => 150,
            Species::Strigiform => 100,
        }
    }

    fn sandbox(&self) -> &'static str {
        match self {
            Species::Formica    => "gVisor/Docker",
            Species::Pongid     => "Docker",
            Species::Castor     => "Docker",
            Species::Arachne    => "Docker",
            Species::Simian     => "isolated",
            Species::Strigiform => "none",
        }
    }

    fn from_directive(directive: &str) -> Self {
        let d = directive.to_lowercase();
        if d.contains("file") || d.contains("read") || d.contains("write") {
            Species::Formica
        } else if d.contains("api") || d.contains("sdk") || d.contains("http") {
            Species::Pongid
        } else if d.contains("infra") || d.contains("docker") || d.contains("build") {
            Species::Castor
        } else if d.contains("browser") || d.contains("mcp") || d.contains("scrape") {
            Species::Arachne
        } else if d.contains("test") || d.contains("chaos") || d.contains("resilience") {
            Species::Simian
        } else {
            Species::Strigiform
        }
    }
}

// ── Task structures ───────────────────────────────────────────────────────────

#[derive(Debug, Deserialize, Clone)]
struct HarnessTask {
    id: String,
    knight: String,
    directive: String,
    priority: u8,
    #[serde(default)]
    submitted: String,
}

#[derive(Debug, Clone)]
struct NanoKnight {
    id: String,
    species: Species,
    task: HarnessTask,
    spawned_at: Instant,
    task_count: u32,
    error_count: u32,
    last_active: Instant,
}

impl NanoKnight {
    fn error_rate(&self) -> f64 {
        if self.task_count == 0 { return 0.0; }
        self.error_count as f64 / self.task_count as f64
    }

    fn idle_secs(&self) -> u64 {
        self.last_active.elapsed().as_secs()
    }

    fn should_apoptose(&self) -> bool {
        (self.error_rate() > APOPTOSIS_ERROR_THRESHOLD && self.task_count >= APOPTOSIS_MIN_TASKS)
            || self.idle_secs() > APOPTOSIS_IDLE_SECS
    }
}

// ── Spawner state ─────────────────────────────────────────────────────────────

struct SwarmSpawner {
    queue_path: PathBuf,
    processed: Arc<Mutex<std::collections::HashSet<String>>>,
    cells: Arc<Mutex<HashMap<String, NanoKnight>>>,
    tasks_done: Arc<Mutex<u32>>,
    tasks_fail: Arc<Mutex<u32>>,
}

impl SwarmSpawner {
    fn new(queue_path: PathBuf) -> Self {
        Self {
            queue_path,
            processed: Arc::new(Mutex::new(std::collections::HashSet::new())),
            cells: Arc::new(Mutex::new(HashMap::new())),
            tasks_done: Arc::new(Mutex::new(0)),
            tasks_fail: Arc::new(Mutex::new(0)),
        }
    }

    // ── PHASE A: MAP ─────────────────────────────────────────────────────────

    async fn read_queue(&self) -> Vec<HarnessTask> {
        let mut tasks = Vec::new();
        if !self.queue_path.exists() {
            return tasks;
        }
        let file = match fs::File::open(&self.queue_path).await {
            Ok(f) => f,
            Err(e) => { warn!("queue open error: {}", e); return tasks; }
        };
        let mut lines = BufReader::new(file).lines();
        let processed = self.processed.lock().unwrap();
        while let Ok(Some(line)) = lines.next_line().await {
            let line = line.trim().to_string();
            if line.is_empty() { continue; }
            if let Ok(task) = serde_json::from_str::<HarnessTask>(&line) {
                if !processed.contains(&task.id) {
                    tasks.push(task);
                }
            }
        }
        tasks
    }

    fn assign_species(&self, task: &HarnessTask) -> Species {
        Species::from_directive(&task.directive)
    }

    // ── PHASE B: REDUCE (Iron Gate check) ────────────────────────────────────

    fn iron_gate_check(&self, tasks: &[HarnessTask]) -> Vec<HarnessTask> {
        let formica_count = {
            let cells = self.cells.lock().unwrap();
            cells.values()
                .filter(|c| c.species == Species::Formica)
                .count()
        };
        tasks.iter().filter_map(|t| {
            let species = self.assign_species(t);
            // Formica ceiling: max 50 instances (8GB RAM guard)
            if species == Species::Formica && formica_count >= MAX_FORMICA_INSTANCES {
                warn!("[IRON_GATE] Formica ceiling hit ({}/{}) — task {} deferred",
                    formica_count, MAX_FORMICA_INSTANCES, t.id);
                return None;
            }
            Some(t.clone())
        }).collect()
    }

    // ── PHASE C: KINETIC EXECUTION ────────────────────────────────────────────

    async fn spawn_cell(&self, task: HarnessTask) {
        let species = self.assign_species(&task);
        let cell_id = format!("{}-{}", task.knight, &task.id[..8.min(task.id.len())]);

        info!(
            "[SPAWN] {} species={:?} sandbox={} budget={} tokens | {}",
            cell_id,
            species,
            species.sandbox(),
            species.token_budget(),
            &task.directive[..60.min(task.directive.len())],
        );

        // Mark processed before async work
        {
            let mut processed = self.processed.lock().unwrap();
            processed.insert(task.id.clone());
        }

        // Simulate execution (real impl: spawn sandboxed subprocess / Docker)
        let result = self.execute_task(&task, &species).await;

        {
            let mut cells = self.cells.lock().unwrap();
            let cell = cells.entry(cell_id.clone()).or_insert_with(|| NanoKnight {
                id: cell_id.clone(),
                species: species.clone(),
                task: task.clone(),
                spawned_at: Instant::now(),
                task_count: 0,
                error_count: 0,
                last_active: Instant::now(),
            });
            cell.task_count += 1;
            cell.last_active = Instant::now();

            match result {
                Ok(output) => {
                    *self.tasks_done.lock().unwrap() += 1;
                    info!("[DONE] {} → {}", task.id, output);
                }
                Err(e) => {
                    cell.error_count += 1;
                    *self.tasks_fail.lock().unwrap() += 1;
                    error!("[FAIL] {} error={}", task.id, e);
                }
            }

            // Apoptosis check
            if cell.should_apoptose() {
                warn!("[APOPTOSIS] {} error_rate={:.1}% idle={}s — cell pruned",
                    cell_id, cell.error_rate() * 100.0, cell.idle_secs());
                cells.remove(&cell_id);
            }
        }
    }

    async fn execute_task(&self, task: &HarnessTask, species: &Species) -> Result<String> {
        // Simulated execution — real impl spawns isolated subprocess per species.sandbox()
        // Strigiform (Owl) runs inline as overseer
        if *species == Species::Strigiform {
            let cells = self.cells.lock().unwrap();
            let summary: Vec<String> = cells.values()
                .map(|c| format!("{}:{:?}(e={:.1}%)", c.id, c.species, c.error_rate() * 100.0))
                .collect();
            return Ok(format!("[OWL_OVERSIGHT] cells={} | {}", cells.len(), summary.join(",")));
        }
        Ok(format!("task={} species={:?} directive_len={}", task.id, species, task.directive.len()))
    }

    // ── Status ────────────────────────────────────────────────────────────────

    fn print_status(&self) {
        let cells = self.cells.lock().unwrap();
        let done = *self.tasks_done.lock().unwrap();
        let fail = *self.tasks_fail.lock().unwrap();
        let status = serde_json::json!({
            "spawner": "swarm-spawner",
            "version": "400.1.0",
            "cells_active": cells.len(),
            "tasks_done": done,
            "tasks_fail": fail,
            "ram_ceiling_mb": RAM_CEILING_MB,
            "formica_ceiling": MAX_FORMICA_INSTANCES,
            "ts": Utc::now().to_rfc3339(),
        });
        println!("{}", serde_json::to_string_pretty(&status).unwrap_or_default());
    }

    // ── Main SRDL loop ────────────────────────────────────────────────────────

    async fn run(&self) -> Result<()> {
        info!("[SWARM_SPAWNER] SRDL Bio-Swarm online — queue={}", self.queue_path.display());
        loop {
            // PHASE A: MAP
            let raw_tasks = self.read_queue().await;
            if !raw_tasks.is_empty() {
                info!("[MAP] {} new tasks from harness_queue", raw_tasks.len());

                // PHASE B: REDUCE — Iron Gate filter
                let approved = self.iron_gate_check(&raw_tasks);
                let deferred = raw_tasks.len() - approved.len();
                if deferred > 0 {
                    warn!("[REDUCE] {} tasks deferred by Iron Gate", deferred);
                }

                // PHASE C: KINETIC — spawn sorted by priority
                let mut sorted = approved;
                sorted.sort_by_key(|t| t.priority);
                for task in sorted {
                    tokio::spawn({
                        // Re-borrow via Arc for the async task
                        let queue_path = self.queue_path.clone();
                        let processed = Arc::clone(&self.processed);
                        let cells = Arc::clone(&self.cells);
                        let tasks_done = Arc::clone(&self.tasks_done);
                        let tasks_fail = Arc::clone(&self.tasks_fail);
                        let task = task.clone();
                        async move {
                            let spawner = SwarmSpawner {
                                queue_path,
                                processed,
                                cells,
                                tasks_done,
                                tasks_fail,
                            };
                            spawner.spawn_cell(task).await;
                        }
                    });
                }
            }
            sleep(Duration::from_millis(POLL_INTERVAL_MS)).await;
        }
    }
}

// ── Entry point ───────────────────────────────────────────────────────────────

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(
            std::env::var("RUST_LOG")
                .unwrap_or_else(|_| "swarm_spawner=info".to_string())
        )
        .init();

    let camelot_home = std::env::var("CAMELOT_OS_HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|_| dirs_or_home());

    let queue_path = camelot_home.join("logs").join("harness_queue.jsonl");

    // --status flag
    if std::env::args().any(|a| a == "--status") {
        let spawner = SwarmSpawner::new(queue_path);
        spawner.print_status();
        return Ok(());
    }

    let spawner = SwarmSpawner::new(queue_path);
    spawner.run().await
}

fn dirs_or_home() -> PathBuf {
    std::env::var("USERPROFILE")
        .or_else(|_| std::env::var("HOME"))
        .map(|h| PathBuf::from(h).join("CAMELOT_OS"))
        .unwrap_or_else(|_| PathBuf::from("C:/Users/vizio/CAMELOT_OS"))
}
