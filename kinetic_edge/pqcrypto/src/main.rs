//! camelot-pqcrypto CLI — Post-Quantum Crypto Operations
//! ========================================================
//! Used by control_plane/pqcrypto_bridge.py via subprocess.
//!
//! Commands:
//!   kem-keygen                  → KemKeyPair JSON
//!   kem-encapsulate <ek_hex>    → KemEncapResult JSON
//!   kem-decapsulate <ct> <dk>   → {"shared_secret": "<hex>"}
//!   dsa-keygen                  → DsaKeyPair JSON
//!   dsa-sign <msg_hex> <sk_hex> <knight_id> → SignedPayload JSON
//!   dsa-verify <signed_json>    → {"valid": true/false}
//!   self-test                   → {"status": "PASS", "kem_ok": true, "dsa_ok": true}

use anyhow::Result;
use camelot_pqcrypto::*;

fn main() -> Result<()> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: camelot-pqcrypto <command> [args...]");
        eprintln!("Commands: kem-keygen | kem-encapsulate | kem-decapsulate | dsa-keygen | dsa-sign | dsa-verify | self-test");
        std::process::exit(1);
    }

    match args[1].as_str() {
        "kem-keygen" => {
            let kp = kem_keygen()?;
            println!("{}", serde_json::to_string(&kp)?);
        }

        "kem-encapsulate" => {
            if args.len() < 3 { anyhow::bail!("kem-encapsulate <ek_hex>"); }
            let result = kem_encapsulate(&args[2])?;
            println!("{}", serde_json::to_string(&result)?);
        }

        "kem-decapsulate" => {
            if args.len() < 4 { anyhow::bail!("kem-decapsulate <ct_hex> <dk_hex>"); }
            let ss = kem_decapsulate(&args[2], &args[3])?;
            println!("{}", serde_json::json!({"shared_secret": hex::encode(&ss)}));
        }

        "dsa-keygen" => {
            let kp = dsa_keygen()?;
            println!("{}", serde_json::to_string(&kp)?);
        }

        "dsa-sign" => {
            if args.len() < 6 { anyhow::bail!("dsa-sign <msg_hex> <sk_hex> <vk_hex> <knight_id>"); }
            let msg = hex::decode(&args[2])?;
            let signed = dsa_sign(&msg, &args[3], &args[4], &args[5])?;
            println!("{}", serde_json::to_string(&signed)?);
        }

        "dsa-verify" => {
            if args.len() < 3 { anyhow::bail!("dsa-verify <signed_payload_json>"); }
            let signed: SignedPayload = serde_json::from_str(&args[2])?;
            let valid = dsa_verify(&signed)?;
            println!("{}", serde_json::json!({"valid": valid, "knight_id": signed.knight_id}));
        }

        "self-test" => {
            // KEM round-trip
            let kp = kem_keygen()?;
            let enc = kem_encapsulate(&kp.encap_key)?;
            let ss_dec = kem_decapsulate(&enc.ciphertext, &kp.decap_key)?;
            let kem_ok = hex::encode(&ss_dec) == enc.shared_secret;

            // DSA round-trip
            let dsa_kp = dsa_keygen()?;
            let msg = b"CAMELOT PQ self-test 2026-04-21";
            let signed = dsa_sign(msg, &dsa_kp.sign_key, &dsa_kp.verify_key, "self-test")?;
            let dsa_ok = dsa_verify(&signed)?;

            println!("{}", serde_json::json!({
                "status": if kem_ok && dsa_ok { "PASS" } else { "FAIL" },
                "kem_ok": kem_ok,
                "dsa_ok": dsa_ok,
                "kem_algorithm": "ML-KEM-768 (FIPS 203 NIST Level 3)",
                "dsa_algorithm": "ML-DSA-65 (FIPS 204 NIST Level 3)",
                "kem_ek_bytes": ML_KEM_768_EK_BYTES,
                "kem_ct_bytes": ML_KEM_768_CT_BYTES,
                "kem_ss_bytes": ML_KEM_768_SS_BYTES,
                "dsa_sig_bytes": ML_DSA_65_SIG_BYTES,
            }));
        }

        cmd => {
            anyhow::bail!("Unknown command: {}", cmd);
        }
    }
    Ok(())
}
