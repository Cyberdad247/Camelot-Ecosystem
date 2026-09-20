//! Native, no-listener command surface for the Android edge supervisor.

use std::{
    env, fs,
    path::PathBuf,
    process::ExitCode,
    time::{SystemTime, UNIX_EPOCH},
};

use camelot_edge::{
    signing_key_from_pkcs8_pem, Action, EdgeState, OutboxLimits, SignedEnvelope, TailnetClient,
};
use serde_json::json;

fn state_dir(args: &[String]) -> Result<PathBuf, &'static str> {
    args.windows(2)
        .find(|pair| pair[0] == "--state-dir")
        .map(|pair| PathBuf::from(&pair[1]))
        .or_else(|| env::var_os("CAMELOT_EDGE_STATE_DIR").map(PathBuf::from))
        .ok_or("--state-dir or CAMELOT_EDGE_STATE_DIR is required")
}

fn required_path(args: &[String], flag: &str, environment: &str) -> Result<PathBuf, String> {
    args.windows(2)
        .find(|pair| pair[0] == flag)
        .map(|pair| PathBuf::from(&pair[1]))
        .or_else(|| env::var_os(environment).map(PathBuf::from))
        .ok_or_else(|| format!("{flag} or {environment} is required"))
}

fn required_env(name: &str) -> Result<String, String> {
    env::var(name).map_err(|_| format!("{name} is required"))
}

fn enrolled_hub_key(path: PathBuf) -> Result<[u8; 32], String> {
    let bytes = fs::read(path).map_err(|_| "cannot read enrolled hub key".to_owned())?;
    bytes
        .as_slice()
        .try_into()
        .map_err(|_| "enrolled hub key must be exactly 32 bytes".to_owned())
}

fn request_nonce() -> String {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0, |value| value.as_nanos());
    format!("{}-{nanos}", std::process::id())
}

fn now_unix() -> i64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0, |value| value.as_secs() as i64)
}

fn run() -> Result<(), String> {
    let args = env::args().skip(1).collect::<Vec<_>>();
    match args.first().map(String::as_str) {
        Some("status") => {
            println!("camelot-edge status listener=disabled transport=tailnet-only actions=6");
            Ok(())
        }
        Some("refresh") => {
            let directory = state_dir(&args).map_err(str::to_owned)?;
            let hub = required_env("CAMELOT_EDGE_HUB_URL")?;
            let device_id = required_env("CAMELOT_EDGE_DEVICE_ID")?;
            let device_key_path = required_path(&args, "--device-key", "CAMELOT_EDGE_DEVICE_KEY")?;
            let hub_key_path = required_path(&args, "--hub-key", "CAMELOT_EDGE_HUB_KEY")?;
            let client = TailnetClient::new(&hub)
                .map_err(|_| "CAMELOT_EDGE_HUB_URL must use a Tailnet address".to_owned())?;
            let device_key = signing_key_from_pkcs8_pem(
                &fs::read(device_key_path).map_err(|_| "cannot read device key".to_owned())?,
            )
            .map_err(|_| "device key is not a valid Ed25519 private PEM".to_owned())?;
            let hub_key = enrolled_hub_key(hub_key_path)?;
            let now = now_unix();
            let envelope = SignedEnvelope::sign(
                &device_id,
                Action::RefreshSnapshot,
                json!({}),
                now,
                now + 60,
                &request_nonce(),
                &device_key,
            );
            let snapshot = client
                .fetch_snapshot(&envelope)
                .map_err(|_| "snapshot request was rejected or unavailable".to_owned())?;
            snapshot
                .verify_for_with_trusted_key(&device_id, now, &hub_key)
                .map_err(|_| "snapshot failed pinned-signer verification".to_owned())?;
            fs::create_dir_all(&directory)
                .map_err(|_| "cannot create edge state directory".to_owned())?;
            let mut state = EdgeState::open(
                directory.join("edge.sqlite3"),
                OutboxLimits::test_defaults(),
            )
            .map_err(|_| "cannot open edge state".to_owned())?;
            let pending = state
                .due_outbox(now)
                .map_err(|_| "cannot read edge outbox".to_owned())?
                .len();
            println!("refresh=verified listener=disabled pending_outbox={pending}");
            Ok(())
        }
        Some("flush-outbox") => {
            let directory = state_dir(&args).map_err(str::to_owned)?;
            let mut state = EdgeState::open(
                directory.join("edge.sqlite3"),
                OutboxLimits::test_defaults(),
            )
            .map_err(|_| "cannot open edge state".to_owned())?;
            let pending = state
                .due_outbox(now_unix())
                .map_err(|_| "cannot read edge outbox".to_owned())?
                .len();
            println!("flush-outbox=staged listener=disabled pending={pending}");
            Ok(())
        }
        _ => Err("usage: camelot-edge <status|refresh|flush-outbox> [--state-dir PATH] [--device-key PATH] [--hub-key PATH]".to_owned()),
    }
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("camelot-edge: {error}");
            ExitCode::FAILURE
        }
    }
}
