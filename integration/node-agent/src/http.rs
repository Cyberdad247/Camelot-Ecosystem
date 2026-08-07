//! Minimal HTTP/1.1 server over std::net — no async runtime, no deps.
//! Two routes: GET /healthz and POST /v1/compute. One thread per connection
//! is plenty for a local compute node scaffold.

use crate::backend::ComputeBackend;
use crate::compute::{run_job, ComputeJob};
use crate::validate::{JobValidator, LeaseValidator, StrictValidator};
use std::io::{BufRead, BufReader, Read, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::Arc;
use std::time::{Duration, Instant};

const MAX_BODY: usize = 8 * 1024 * 1024;
const DRAIN_TIMEOUT: Duration = Duration::from_secs(3);

/// Set by the SIGINT/SIGTERM handlers (main.rs). The accept loop polls it and
/// drains in-flight connections before returning — graceful shutdown without
/// an async runtime.
pub static SHUTDOWN: AtomicBool = AtomicBool::new(false);
static ACTIVE_CONNECTIONS: AtomicUsize = AtomicUsize::new(0);

pub struct Agent {
    pub backend: Box<dyn ComputeBackend>,
    pub validator: StrictValidator,
}

pub fn serve(addr: &str, agent: Agent) -> std::io::Result<()> {
    let listener = TcpListener::bind(addr)?;
    listener.set_nonblocking(true)?;
    eprintln!(
        "camelot-node-agent 0.1.0 listening on {addr} (backend: {}, lease_key: {})",
        agent.backend.name(),
        if agent.validator.lease_key.is_some() { "set" } else { "unset" },
    );
    let agent = Arc::new(agent);
    while !SHUTDOWN.load(Ordering::SeqCst) {
        match listener.accept() {
            Ok((stream, _)) => {
                let _ = stream.set_nonblocking(false);
                let agent = Arc::clone(&agent);
                ACTIVE_CONNECTIONS.fetch_add(1, Ordering::SeqCst);
                std::thread::spawn(move || {
                    let _ = handle(stream, &agent);
                    ACTIVE_CONNECTIONS.fetch_sub(1, Ordering::SeqCst);
                });
            }
            Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => {
                std::thread::sleep(Duration::from_millis(50));
            }
            Err(_) => continue,
        }
    }
    // Drain: let in-flight requests finish, bounded.
    let deadline = Instant::now() + DRAIN_TIMEOUT;
    while ACTIVE_CONNECTIONS.load(Ordering::SeqCst) > 0 && Instant::now() < deadline {
        std::thread::sleep(Duration::from_millis(25));
    }
    eprintln!("camelot-node-agent: graceful shutdown complete");
    Ok(())
}

fn handle(mut stream: TcpStream, agent: &Agent) -> std::io::Result<()> {
    let mut reader = BufReader::new(stream.try_clone()?);
    let mut request_line = String::new();
    reader.read_line(&mut request_line)?;
    let mut parts = request_line.split_whitespace();
    let method = parts.next().unwrap_or("").to_string();
    let path = parts.next().unwrap_or("").to_string();

    let mut content_length = 0usize;
    loop {
        let mut line = String::new();
        reader.read_line(&mut line)?;
        let trimmed = line.trim();
        if trimmed.is_empty() {
            break;
        }
        if let Some(value) = trimmed
            .to_ascii_lowercase()
            .strip_prefix("content-length:")
            .map(str::trim)
            .map(String::from)
        {
            content_length = value.parse().unwrap_or(0);
        }
    }

    match (method.as_str(), path.as_str()) {
        ("GET", "/healthz") => {
            let body = format!(
                "{{\"status\":\"ok\",\"service\":\"camelot-node-agent\",\"version\":\"0.1.0\",\"backend\":\"{}\",\"leaseKey\":\"{}\"}}",
                agent.backend.name(),
                if agent.validator.lease_key.is_some() { "set" } else { "unset" },
            );
            respond(&mut stream, 200, "OK", &body)
        }
        ("POST", "/v1/compute") => {
            if content_length == 0 || content_length > MAX_BODY {
                return respond_error(&mut stream, 400, "missing or oversized body");
            }
            let mut body = vec![0u8; content_length];
            reader.read_exact(&mut body)?;
            let job: ComputeJob = match serde_json::from_slice(&body) {
                Ok(j) => j,
                Err(e) => return respond_error(&mut stream, 400, &format!("invalid ComputeJob: {e}")),
            };
            if let Err(e) = agent.validator.validate_job(&job) {
                return respond_error(&mut stream, 400, &e.to_string());
            }
            if let Err(e) = agent.validator.validate_lease(&job) {
                return respond_error(&mut stream, 403, &e.to_string());
            }
            let result = run_job(&job, agent.backend.as_ref());
            let body = serde_json::to_string(&result).unwrap_or_else(|_| "{}".into());
            respond(&mut stream, 200, "OK", &body)
        }
        _ => respond_error(&mut stream, 404, "not found"),
    }
}

fn respond(stream: &mut TcpStream, status: u16, reason: &str, body: &str) -> std::io::Result<()> {
    write!(
        stream,
        "HTTP/1.1 {status} {reason}\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}",
        body.len(),
    )
}

fn respond_error(stream: &mut TcpStream, status: u16, message: &str) -> std::io::Result<()> {
    let body = serde_json::json!({ "error": message }).to_string();
    let reason = match status {
        400 => "Bad Request",
        403 => "Forbidden",
        404 => "Not Found",
        _ => "Error",
    };
    respond(stream, status, reason, &body)
}
