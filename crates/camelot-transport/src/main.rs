//! Camelot-OS Bifrost Gateway Transport Daemon
//! ============================================

mod bifrost;
mod memfd;

use axum::{
    routing::{get, post},
    Router,
};
use bifrost::BifrostRouter;
use memfd::SharedMemBuffer;
use std::net::SocketAddr;
use tracing::{info, warn, Level};
use tracing_subscriber::FmtSubscriber;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();
    let _ = tracing::subscriber::set_global_default(subscriber);

    info!("Initializing Camelot-OS Bifrost Gateway (v10001.0.0)...");

    // Initialize 64KB static shared memory ring buffer for zero-copy IPC
    let _ipc_buffer = SharedMemBuffer::create("bifrost_shared_ring", 65536)?;

    // Configure Axum router endpoints
    let app = Router::new()
        .route("/health", get(|| async { "OK" }))
        .route("/execute", post(BifrostRouter::handle_execute));

    let port: u16 = std::env::var("PORT")
        .or_else(|_| std::env::var("BIFROST_PORT"))
        .ok()
        .and_then(|p| p.parse().ok())
        .unwrap_or(8080);

    let addr = SocketAddr::from(([127, 0, 0, 1], port));

    let listener = match tokio::net::TcpListener::bind(addr).await {
        Ok(l) => {
            info!("Bifrost Transport Gateway listening on http://{}", addr);
            l
        }
        Err(e) if e.kind() == std::io::ErrorKind::AddrInUse && port == 8080 => {
            let alt_port = 8088;
            let alt_addr = SocketAddr::from(([127, 0, 0, 1], alt_port));
            warn!(
                "Port 8080 in use by host proxy; falling back to http://{}",
                alt_addr
            );
            let l = tokio::net::TcpListener::bind(alt_addr).await?;
            info!("Bifrost Transport Gateway listening on http://{}", alt_addr);
            l
        }
        Err(e) => return Err(e.into()),
    };

    axum::serve(listener, app).await?;

    Ok(())
}
