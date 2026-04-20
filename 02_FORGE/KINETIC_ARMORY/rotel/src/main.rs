// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
use warp::Filter;
use serde::{Deserialize, Serialize};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use chrono::Local;
use tokio::sync::broadcast;
use tokio_stream::wrappers::BroadcastStream;
use tokio_stream::StreamExt;
use warp::sse::Event;
use std::convert::Infallible;

const KINETIC_TOKEN: &str = "camelot-kinetic-v300-auth-token";

// ROTEL: The Kinetic Telemetry Collector
// "Logging at the speed of Rust."

#[derive(Deserialize, Serialize, Debug, Clone)]
struct LogEntry {
    level: String,
    message: String,
    component: String,
    timestamp: Option<String>,
    metadata: Option<serde_json::Value>,
}

#[derive(Serialize)]
struct Stats {
    total_logs: usize,
    status: String,
}

fn with_auth() -> impl Filter<Extract = ((),), Error = warp::Rejection> + Clone {
    warp::header::optional::<String>("x-api-key")
        .and(warp::header::optional::<String>("authorization"))
        .and(warp::query::<std::collections::HashMap<String, String>>())
        .and_then(|key: Option<String>, auth: Option<String>, query: std::collections::HashMap<String, String>| async move {
            let authorized = key.map(|k| k == KINETIC_TOKEN).unwrap_or(false)
                || auth.map(|a| a == format!("Bearer {}", KINETIC_TOKEN)).unwrap_or(false)
                || query.get("token").map(|t| t == KINETIC_TOKEN).unwrap_or(false);

            if authorized {
                Ok(())
            } else {
                Err(warp::reject::custom(Unauthorized))
            }
        })
}
#[derive(Debug)]
struct Unauthorized;
impl warp::reject::Reject for Unauthorized {}

#[tokio::main]
async fn main() {
    let log_counter = Arc::new(AtomicUsize::new(0));
    let (tx, _rx) = broadcast::channel::<LogEntry>(100);

    let tx_filter = warp::any().map(move || tx.clone());
    let counter_filter = warp::any().map(move || log_counter.clone());

    println!("🦀 ROTEL v0.3.0 [KINETIC_GATE] Initialized on :4317");

    // Route: POST /v1/logs
    let logs_route = warp::post()
        .and(warp::path("v1"))
        .and(warp::path("logs"))
        .and(with_auth())
        .and(warp::body::json())
        .and(counter_filter.clone())
        .and(tx_filter.clone())
        .map(|_, entry: LogEntry, counter: Arc<AtomicUsize>, tx: broadcast::Sender<LogEntry>| {
            let count = counter.fetch_add(1, Ordering::SeqCst);
            let ts = entry.timestamp.clone().unwrap_or_else(|| Local::now().to_rfc3339());

            println!("[RATEL::{}] {} | {} | {}", count, ts, entry.component, entry.message);

            let _ = tx.send(entry);
            warp::reply::json(&"ACK")
        });

    // Route: GET /v1/stream (SSE)
    let stream_route = warp::get()
        .and(warp::path("v1"))
        .and(warp::path("stream"))
        .and(with_auth())
        .and(tx_filter)
        .map(|_, tx: broadcast::Sender<LogEntry>| {
            let stream = BroadcastStream::new(tx.subscribe())
                .map(|msg| {
                    match msg {
                        Ok(log) => Event::default().json_data(log),
                        Err(_) => Ok(Event::default().data("ping")),
                    }
                });
            warp::sse::reply(stream)
        });

    // Route: GET /status
    let status_route = warp::get()
        .and(warp::path("status"))
        .and(counter_filter)
        .map(|counter: Arc<AtomicUsize>| {
            let count = counter.load(Ordering::SeqCst);
            warp::reply::json(&Stats {
                total_logs: count,
                status: "RADIANT".to_string(),
            })
        });

    let routes = logs_route
        .or(stream_route)
        .or(status_route)
        .with(warp::cors().allow_any_origin())
        .recover(|err: warp::Rejection| async move {
            if err.find::<Unauthorized>().is_some() {
                Ok(warp::reply::with_status(
                    warp::reply::json(&"Unauthorized: Kinetic Token Required"),
                    warp::http::StatusCode::UNAUTHORIZED,
                ))
            } else {
                Err(err)
            }
        });

    warp::serve(routes).run(([0, 0, 0, 0], 4317)).await;
}