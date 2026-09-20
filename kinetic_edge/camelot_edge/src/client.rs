//! Deliberately small, Tailnet-only HTTP transport for the Termux edge supervisor.

use std::{
    io::{Read, Write},
    net::TcpStream,
    time::Duration,
};

use base64::{engine::general_purpose::STANDARD, Engine as _};

use crate::{EdgeError, SignedEnvelope, SignedPolicySnapshot};

const MAX_RESPONSE_BYTES: u64 = 64 * 1024;

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct TailnetClient {
    base_url: String,
    authority: String,
}

impl TailnetClient {
    pub fn new(base_url: &str) -> Result<Self, EdgeError> {
        let authority = base_url
            .strip_prefix("http://")
            .and_then(|value| value.split('/').next())
            .filter(|value| !value.is_empty())
            .ok_or(EdgeError::InvalidTailnetEndpoint)?;
        let host = authority.split(':').next().unwrap_or_default();
        let is_tailnet_ip = host
            .split('.')
            .next()
            .is_some_and(|first_octet| first_octet == "100");
        if !is_tailnet_ip && !host.ends_with(".ts.net") {
            return Err(EdgeError::InvalidTailnetEndpoint);
        }
        Ok(Self {
            base_url: base_url.trim_end_matches('/').to_owned(),
            authority: authority.to_owned(),
        })
    }

    pub fn endpoint(&self, path: &str) -> Result<String, EdgeError> {
        if !path.starts_with("/v1/edge/") || path.contains("..") {
            return Err(EdgeError::InvalidTailnetEndpoint);
        }
        Ok(format!("{}{}", self.base_url, path))
    }

    pub fn snapshot_request_bytes(&self, envelope: &SignedEnvelope) -> Result<Vec<u8>, EdgeError> {
        let header = STANDARD.encode(
            serde_json::to_vec(envelope).map_err(|_| EdgeError::CanonicalSerialization)?,
        );
        Ok(format!(
            "GET /v1/edge/snapshot HTTP/1.1\r\nHost: {}\r\nX-Camelot-Edge-Envelope: {}\r\nConnection: close\r\n\r\n",
            self.authority, header
        )
        .into_bytes())
    }

    pub fn fetch_snapshot(&self, envelope: &SignedEnvelope) -> Result<SignedPolicySnapshot, EdgeError> {
        let mut stream = TcpStream::connect(&self.authority).map_err(|_| EdgeError::Transport)?;
        stream
            .set_read_timeout(Some(Duration::from_secs(10)))
            .map_err(|_| EdgeError::Transport)?;
        stream
            .set_write_timeout(Some(Duration::from_secs(10)))
            .map_err(|_| EdgeError::Transport)?;
        stream
            .write_all(&self.snapshot_request_bytes(envelope)?)
            .map_err(|_| EdgeError::Transport)?;

        let mut response = Vec::new();
        stream
            .take(MAX_RESPONSE_BYTES)
            .read_to_end(&mut response)
            .map_err(|_| EdgeError::Transport)?;
        let (status, body) = split_http_response(&response)?;
        if status != 200 {
            return Err(EdgeError::Transport);
        }
        serde_json::from_slice(body).map_err(|_| EdgeError::Transport)
    }
}

fn split_http_response(response: &[u8]) -> Result<(u16, &[u8]), EdgeError> {
    let separator = response
        .windows(4)
        .position(|window| window == b"\r\n\r\n")
        .ok_or(EdgeError::Transport)?;
    let head = std::str::from_utf8(&response[..separator]).map_err(|_| EdgeError::Transport)?;
    let status = head
        .split_whitespace()
        .nth(1)
        .ok_or(EdgeError::Transport)?
        .parse::<u16>()
        .map_err(|_| EdgeError::Transport)?;
    Ok((status, &response[separator + 4..]))
}
