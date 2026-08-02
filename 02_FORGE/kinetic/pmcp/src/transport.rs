use crate::{PmcpError, Result};
use tokio::io::{AsyncReadExt, AsyncWriteExt};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TransportKind {
    Stdio,
    Tcp,
    Unix,
}

#[derive(Debug, Clone)]
pub struct TransportConfig {
    pub kind: TransportKind,
    pub bind: Option<String>,
    pub port: Option<u16>,
}

impl Default for TransportConfig {
    fn default() -> Self {
        Self {
            kind: TransportKind::Stdio,
            bind: Some("127.0.0.1".into()),
            port: Some(3002),
        }
    }
}

/// Anything that carries framed JSON-RPC bytes between MCP peers.
#[async_trait::async_trait]
pub trait Transport: Send + Sync {
    async fn recv(&mut self) -> Result<Vec<u8>>;
    async fn send(&mut self, payload: &[u8]) -> Result<()>;
    fn kind(&self) -> TransportKind;
}

/// Bind a transport according to config. Stdio works today; TCP/Unix are placeholders
/// for the Phase 1 cut window.
pub async fn bind(cfg: TransportConfig) -> Result<Box<dyn Transport>> {
    match cfg.kind {
        TransportKind::Stdio => Ok(Box::new(StdioTransport::new())),
        TransportKind::Tcp => Err(PmcpError::Transport(
            "tcp transport not yet wired — planned for Phase 1 cut window".into(),
        )),
        TransportKind::Unix => Err(PmcpError::Transport(
            "unix transport not yet wired — planned for Phase 1 cut window".into(),
        )),
    }
}

pub struct StdioTransport {
    // Kept as a unit struct for now; future phases will own a framed newline-delimited
    // reader here. Stdio works as a sanity scaffold immediately.
}

impl StdioTransport {
    pub fn new() -> Self {
        Self {}
    }
}

#[async_trait::async_trait]
impl Transport for StdioTransport {
    async fn recv(&mut self) -> Result<Vec<u8>> {
        let mut buf = Vec::with_capacity(4096);
        let n = AsyncReadExt::read(&mut tokio::io::stdin(), &mut buf).await?;
        buf.truncate(n);
        Ok(buf)
    }

    async fn send(&mut self, payload: &[u8]) -> Result<()> {
        let mut out = tokio::io::stdout();
        AsyncWriteExt::write_all(&mut out, payload).await?;
        AsyncWriteExt::flush(&mut out).await?;
        Ok(())
    }

    fn kind(&self) -> TransportKind {
        TransportKind::Stdio
    }
}
