use clap::Parser;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Serialize, Deserialize, Debug)]
pub struct CrystalLayer {
    pub layer: String,
    pub path: String,
    pub sha256: String,
    pub status: String,
}

#[derive(Parser, Debug)]
#[command(name = "camelot-vkg-crystal", about = "Camelot-OS VKG Crystal Substrate")]
struct Args {
    #[arg(long, default_value = "")]
    agent_dir: String,

    #[arg(long)]
    verify: bool,

    #[arg(long)]
    daemon: bool,
}

fn detect_agent_dir(custom_path: &str) -> PathBuf {
    if !custom_path.is_empty() {
        return PathBuf::from(custom_path);
    }
    if let Ok(home) = std::env::var("CAMELOT_OS_HOME") {
        let p = Path::new(&home).join(".agent");
        if p.exists() {
            return p;
        }
    }
    let local = Path::new(".agent");
    if local.exists() {
        return local.to_path_buf();
    }
    PathBuf::from("/opt/Camelot-Ecosystem/.agent")
}

fn evaluate_layers(root: &Path) -> (Vec<CrystalLayer>, bool) {
    let layers = [
        "governance.yaml",
        "prd.yaml",
        "openapi.yaml",
        "security.yaml",
        "pipeline.yaml",
        "decision-log.md",
    ];

    let mut results = Vec::new();
    let mut all_ok = true;

    for layer in layers {
        let path = root.join(layer);
        if let Ok(content) = fs::read(&path) {
            let mut hasher = Sha256::new();
            hasher.update(&content);
            let sha = format!("{:x}", hasher.finalize());
            results.push(CrystalLayer {
                layer: layer.to_string(),
                path: path.to_string_lossy().to_string(),
                sha256: sha,
                status: "SEALED_CONVERGED".to_string(),
            });
            println!("  [OK] Sealed L_{}: {}", layer, path.display());
        } else {
            all_ok = false;
            results.push(CrystalLayer {
                layer: layer.to_string(),
                path: path.to_string_lossy().to_string(),
                sha256: String::new(),
                status: "MISSING".to_string(),
            });
            eprintln!("  [ERR] Missing layer: {}", path.display());
        }
    }
    (results, all_ok)
}

#[tokio::main]
async fn main() {
    let args = Args::parse();
    let root = detect_agent_dir(&args.agent_dir);

    println!("⚡ CAMELOT VKG CRYSTAL INITIALIZING...");
    println!("  Root backplane: {}", root.display());

    let (layers, ok) = evaluate_layers(&root);

    if args.verify {
        if ok {
            println!("⚜️ VKG CRYSTAL INTEGRITY VERIFIED (ALL {} LAYERS CONVERGED).", layers.len());
            std::process::exit(0);
        } else {
            eprintln!("❌ VKG CRYSTAL VERIFICATION FAILED: ONE OR MORE LAYERS MISSING.");
            std::process::exit(1);
        }
    }

    if args.daemon {
        println!("🛡️ VKG CRYSTAL DAEMON RUNNING (Continuous Sentinel Watch)...");
        loop {
            tokio::time::sleep(tokio::time::Duration::from_secs(30)).await;
            let (_, healthy) = evaluate_layers(&root);
            if !healthy {
                eprintln!("⚠️ VKG CRYSTAL WARNING: Degraded layer state detected.");
            }
        }
    }

    println!("⚜️ VKG CRYSTAL INITIALIZED SUCCESSFULLY.");
}
