use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine};
use ed25519_dalek::{pkcs8::{spki::der::pem::LineEnding, EncodePublicKey}, Signer, SigningKey};
use keyring::{Entry, Error as KeyringError};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::time::{SystemTime, UNIX_EPOCH};
use tauri::{AppHandle, Manager};
use tauri_plugin_notification::NotificationExt;
use url::Url;

const KEYRING_SERVICE: &str = "Camelot-OS Device Bridge";
const KEYRING_USER: &str = "desktop-ed25519";

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct DeviceIdentity {
    public_key: String,
    fingerprint: String,
    capabilities: Vec<&'static str>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
struct DeviceAction {
    id: String,
    device_id: String,
    capability: String,
    arguments: Value,
}

#[derive(Deserialize)]
struct PollResponse {
    action: Option<DeviceAction>,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct BridgeTick {
    connected: bool,
    action_id: Option<String>,
    result: String,
}

fn signing_key() -> Result<SigningKey, String> {
    let entry = Entry::new(KEYRING_SERVICE, KEYRING_USER).map_err(|error| error.to_string())?;
    match entry.get_secret() {
        Ok(secret) => {
            let bytes: [u8; 32] = secret.try_into().map_err(|_| "Stored device key has an invalid length.".to_string())?;
            Ok(SigningKey::from_bytes(&bytes))
        }
        Err(KeyringError::NoEntry) => {
            let mut secret = [0_u8; 32];
            getrandom::fill(&mut secret).map_err(|error| error.to_string())?;
            entry.set_secret(&secret).map_err(|error| error.to_string())?;
            Ok(SigningKey::from_bytes(&secret))
        }
        Err(error) => Err(format!("Credential store unavailable: {error}")),
    }
}

fn identity_for(key: &SigningKey) -> Result<DeviceIdentity, String> {
    let verifying = key.verifying_key();
    let public_key = verifying.to_public_key_pem(LineEnding::LF).map_err(|error| error.to_string())?;
    let fingerprint = hex::encode(Sha256::digest(verifying.as_bytes()));
    Ok(DeviceIdentity {
        public_key,
        fingerprint: fingerprint[..24].to_string(),
        capabilities: vec!["system.status", "desktop.notification", "desktop.window.focus"],
    })
}

#[tauri::command]
fn device_identity() -> Result<DeviceIdentity, String> {
    identity_for(&signing_key()?)
}

fn checked_endpoint(endpoint: &str) -> Result<Url, String> {
    let url = Url::parse(endpoint).map_err(|_| "Cockpit endpoint is not a valid URL.".to_string())?;
    let loopback = matches!(url.host_str(), Some("127.0.0.1" | "localhost" | "::1"));
    if url.scheme() != "https" && !(url.scheme() == "http" && loopback) {
        return Err("Device bridge requires HTTPS; HTTP is permitted only on loopback.".to_string());
    }
    Ok(url)
}

fn request_headers(method: &str, path: &str, body: &str, device_id: &str, key: &SigningKey) -> Result<Vec<(&'static str, String)>, String> {
    let timestamp = SystemTime::now().duration_since(UNIX_EPOCH).map_err(|error| error.to_string())?.as_millis().to_string();
    let mut nonce_bytes = [0_u8; 18];
    getrandom::fill(&mut nonce_bytes).map_err(|error| error.to_string())?;
    let nonce = URL_SAFE_NO_PAD.encode(nonce_bytes);
    let body_digest = hex::encode(Sha256::digest(body.as_bytes()));
    let canonical = [method, path, &timestamp, &nonce, &body_digest].join("\n");
    let signature = URL_SAFE_NO_PAD.encode(key.sign(canonical.as_bytes()).to_bytes());
    Ok(vec![
        ("x-camelot-device-id", device_id.to_string()),
        ("x-camelot-timestamp", timestamp),
        ("x-camelot-nonce", nonce),
        ("x-camelot-signature", signature),
    ])
}

fn execute_action(app: &AppHandle, action: &DeviceAction) -> Result<String, String> {
    match action.capability.as_str() {
        "system.status" => Ok(format!("{} {}", std::env::consts::OS, std::env::consts::ARCH)),
        "desktop.notification" => {
            let message = action.arguments.get("message").and_then(Value::as_str).unwrap_or("Anya device action received.");
            let bounded_message = message.chars().take(200).collect::<String>();
            app.notification().builder().title("Camelot-OS - Anya").body(&bounded_message).show().map_err(|error| error.to_string())?;
            Ok("Desktop notification displayed.".to_string())
        }
        "desktop.window.focus" => {
            let window = app.get_webview_window("main").ok_or_else(|| "Main bridge window is unavailable.".to_string())?;
            window.show().map_err(|error| error.to_string())?;
            window.set_focus().map_err(|error| error.to_string())?;
            Ok("Device bridge window focused.".to_string())
        }
        _ => Err("Capability is not implemented by the desktop allowlist.".to_string()),
    }
}

#[tauri::command]
async fn bridge_tick(app: AppHandle, endpoint: String, device_id: String) -> Result<BridgeTick, String> {
    if !device_id.starts_with("dev-") { return Err("A valid enrolled device ID is required.".to_string()); }
    let base = checked_endpoint(&endpoint)?;
    let key = signing_key()?;
    let client = reqwest::Client::builder().timeout(std::time::Duration::from_secs(15)).build().map_err(|error| error.to_string())?;
    let poll_path = "/api/device-bridge/poll";
    let poll_url = base.join(poll_path).map_err(|error| error.to_string())?;
    let mut poll = client.get(poll_url);
    for (name, value) in request_headers("GET", poll_path, "", &device_id, &key)? { poll = poll.header(name, value); }
    let response = poll.send().await.map_err(|error| error.to_string())?;
    if !response.status().is_success() { return Err(format!("Cockpit rejected device poll with HTTP {}.", response.status())); }
    let action = response.json::<PollResponse>().await.map_err(|error| error.to_string())?.action;
    let Some(action) = action else { return Ok(BridgeTick { connected: true, action_id: None, result: "No approved action is queued.".to_string() }); };
    let execution = execute_action(&app, &action);
    let receipt_body = json!({ "actionId": action.id, "success": execution.is_ok(), "result": execution.as_deref().unwrap_or_else(|error| error) }).to_string();
    let receipt_path = "/api/device-bridge/receipt";
    let receipt_url = base.join(receipt_path).map_err(|error| error.to_string())?;
    let mut receipt = client.post(receipt_url).header("content-type", "application/json").body(receipt_body.clone());
    for (name, value) in request_headers("POST", receipt_path, &receipt_body, &device_id, &key)? { receipt = receipt.header(name, value); }
    let receipt_response = receipt.send().await.map_err(|error| error.to_string())?;
    if !receipt_response.status().is_success() { return Err(format!("Cockpit rejected action receipt with HTTP {}.", receipt_response.status())); }
    Ok(BridgeTick { connected: true, action_id: Some(action.id), result: execution.unwrap_or_else(|error| error) })
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_notification::init())
        .invoke_handler(tauri::generate_handler![device_identity, bridge_tick])
        .run(tauri::generate_context!())
        .expect("error while running Camelot device bridge");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn endpoint_policy_allows_https_and_loopback_only() {
        assert!(checked_endpoint("https://camelot.example").is_ok());
        assert!(checked_endpoint("http://127.0.0.1:3006").is_ok());
        assert!(checked_endpoint("http://camelot.example").is_err());
    }
}
