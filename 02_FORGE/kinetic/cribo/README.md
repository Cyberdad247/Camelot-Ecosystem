# 🗜️ Cribo — Dead-Code Analyzer & Tree-Shaker

> **STATUS:** Active · `v0.1.0` · Rust

Cribo is a command-line utility for analyzing file dependency graphs and performing simulated tree-shaking. It walks directory trees, resolves imports, identifies unused ("dead") code paths, and reports the "shaken size" after removing unreachable modules.

## Stack

| Layer | Technology |
|-------|-----------|
| Language | Rust (edition 2021) |
| CLI | Clap 4 (derive) |
| Serialization | Serde + serde_json |
| File Walking | walkdir |

## Install

```bash
cargo build -p cribo --release
```

## Usage

```bash
cribo --path ./src --entry main.ts
```

Outputs a dependency graph and estimated size reduction from tree-shaking.
