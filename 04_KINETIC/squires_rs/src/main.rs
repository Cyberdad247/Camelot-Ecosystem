use clap::{Parser, Subcommand};
use jwalk::WalkDir;
use serde::Serialize;
use sha2::{Digest, Sha256};
use std::fs::File;
use std::io::{self, BufReader, Read};
use std::path::{Path, PathBuf};
use std::time::Instant;

#[derive(Parser)]
#[command(name = "squires_rs")]
#[command(about = "CLARITY_CORE v1.0.0 — Squire Colony CLI (Rust Port)", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Scan {
        #[arg(default_value = ".")]
        path: PathBuf,
    },
}

#[derive(Serialize)]
struct FileRecord {
    rel_path: String,
    ext: String,
    lines: usize,
    size: u64,
    sha256: String,
}

fn hash_file(path: &Path) -> io::Result<String> {
    let mut file = File::open(path)?;
    let mut hasher = Sha256::new();
    io::copy(&mut file, &mut hasher)?;
    Ok(hex::encode(hasher.finalize()))
}

fn count_lines(path: &Path) -> io::Result<usize> {
    let file = File::open(path)?;
    let mut reader = BufReader::new(file);
    let mut buffer = [0; 8192];
    let mut count = 0;
    loop {
        let bytes_read = reader.read(&mut buffer)?;
        if bytes_read == 0 {
            break;
        }
        count += buffer[..bytes_read].iter().filter(|&&b| b == b'\n').count();
    }
    Ok(count)
}

fn scan_directory(root: &Path) {
    println!("🔍 Scanning: {}", root.display());
    let start = Instant::now();
    let mut records = Vec::new();

    for entry in WalkDir::new(root).into_iter().filter_map(|e| e.ok()) {
        if entry.file_type().is_file() {
            let path = entry.path();
            let size = entry.metadata().map(|m| m.len()).unwrap_or(0);
            
            let ext = path.extension()
                .and_then(|e| e.to_str())
                .unwrap_or("")
                .to_string();

            // Only analyze small text files for line count and hash to keep MVP fast
            let (lines, sha256) = if size < 10_000_000 {
                let l = count_lines(&path).unwrap_or(0);
                let s = hash_file(&path).unwrap_or_else(|_| String::new());
                (l, s)
            } else {
                (0, "too_large".to_string())
            };

            let rel_path = path.strip_prefix(root).unwrap_or(&path).display().to_string();

            records.push(FileRecord {
                rel_path,
                ext,
                lines,
                size,
                sha256,
            });
        }
    }
    let duration = start.elapsed();
    
    println!("{:<60} {:<8} {:>8} {:>10} {:<14}", "File", "Ext", "Lines", "Size", "SHA");
    for rec in records.iter().take(200) {
        println!("{:<60} {:<8} {:>8} {:>10} {:.14}...", rec.rel_path, rec.ext, rec.lines, rec.size, rec.sha256);
    }
    
    if records.len() > 200 {
        println!("... {} more files", records.len() - 200);
    }
    println!("\nTotal: {} files scanned in {:.2?}", records.len(), duration);
}

fn main() {
    let cli = Cli::parse();
    match &cli.command {
        Commands::Scan { path } => {
            scan_directory(path);
        }
    }
}
