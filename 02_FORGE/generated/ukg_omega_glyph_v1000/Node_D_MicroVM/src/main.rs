use camelot_node_d_microvm::execute_soul_algorithm;
use std::env;
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};

fn write_health_response(mut stream: TcpStream) -> std::io::Result<()> {
    let mut buffer = [0; 1024];
    let _ = stream.read(&mut buffer);
    let sample = execute_soul_algorithm("camelot");
    let body = format!(
        r#"{{"status":"ok","node":"Node_D_MicroVM","sample":"{}"}}"#,
        sample
    );
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

fn main() -> Result<(), Box<dyn std::error::Error>> {
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
            .unwrap_or(4179);
        serve_health(host, port)?;
        return Ok(());
    }

    println!("{}", execute_soul_algorithm("camelot"));
    Ok(())
}
