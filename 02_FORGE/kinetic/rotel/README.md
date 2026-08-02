# 📡 Rotel — High-Performance Telemetry Collector

> **STATUS:** Active · `v0.1.0` · Rust

Rotel is a high-performance telemetry and tracing collector for CAMELOT-OS. It logs structured events with distributed trace IDs, span IDs, and attributes to daily-rotated JSONL files — compatible with OpenTelemetry pipelines.

## Stack

| Layer | Technology |
|-------|-----------|
| Language | Rust (edition 2021) |
| CLI | Clap 4 (derive) |
| Serialization | Serde + serde_json |
| Time | Chrono (with serde) |
| IDs | UUID v4 (fast-rng) |
| Errors | anyhow |

## Install

```bash
cargo build -p rotel --release
```

## Usage

```bash
rotel --service my-agent --output ./logs/
```

Traces are written to `logs/rotel_traces/YYYY-MM-DD.jsonl`.
