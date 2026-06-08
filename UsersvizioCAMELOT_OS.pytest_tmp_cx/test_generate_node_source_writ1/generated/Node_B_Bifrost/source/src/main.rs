use serde::{Deserialize, Serialize};

use std::env;
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct BridgeEnvelope {
    pub target: String,
    pub payload: String,
}

pub fn encode_length_prefixed(payload: &[u8]) -> Vec<u8> {
    let len = payload.len() as u32;
    let mut frame = len.to_be_bytes().to_vec();
    frame.extend_from_slice(payload);
    frame
}

pub fn decode_length_prefixed(frame: &[u8]) -> Result<&[u8], String> {
    if frame.len() < 4 {
        return Err("frame missing 4-byte length prefix".to_string());
    }
    let len = u32::from_be_bytes([frame[0], frame[1], frame[2], frame[3]]) as usize;
    let body = &frame[4..];
    if body.len() != len {
        return Err(format!("frame length mismatch: expected {len}, got {}", body.len()));
    }
    Ok(body)
}

fn write_health_response(mut stream: TcpStream) -> std::io::Result<()> {
    let mut buffer = [0; 1024];
    let _ = stream.read(&mut buffer);
    let body = r#"{"status":"ok","node":"Node_B_Bifrost","bridge":"length-prefixed-native-messaging"}"#;
    let response = format!(
        "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
        body.len(),
        body
    );
    stream.write_all(response.as_bytes())
}

pub fn serve_health(host: &str, port: u16) -> std::io::Result<()> {
    let listener = TcpListener::bind(format!("{host}:{port}"))?;
    for stream in listener.incoming() {
        write_health_response(stream?)?;
    }
    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();
    if args.iter().any(|arg| arg == "--serve") {
        let host = args
            .windows(2)
            .find(|window| window[0] == "--host")
            .map(|window| window[1].as_str())
            .unwrap_or("127.0.0.1");
        let port = args
            .windows(2)
            .find(|window| window[0] == "--port")
            .and_then(|window| window[1].parse::<u16>().ok())
            .unwrap_or(4178);
        serve_health(host, port)?;
        return Ok(());
    }

    let envelope = BridgeEnvelope {
        target: "tailscale-tcp-forward".to_string(),
        payload: "//STATUS".to_string(),
    };
    println!("{}", serde_json::to_string(&envelope)?);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn round_trips_length_prefixed_payload() {
        let frame = encode_length_prefixed(b"camelot");
        assert_eq!(decode_length_prefixed(&frame).unwrap(), b"camelot");
    }
}
