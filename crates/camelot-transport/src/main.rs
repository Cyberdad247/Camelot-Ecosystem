//! Camelot Transport Kinetic Executable (Week 3 Deliverable)
//! ========================================================

use camelot_transport::{
    BifrostFrame, BifrostRouter, HateoasBuilder, KnightTelemetryView, MessageType, SseEvent,
    TransportReceipt,
};
use std::time::Instant;
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();
    tracing::subscriber::set_global_default(subscriber)?;

    let start_time = Instant::now();
    info!("Booting CAMELOT-OS Transport Layer (v10001.0.0)...");
    info!("Protocol: Bifrost Duplex UDS/WS | Framing: Pure HATEOAS & SSE Telemetry");

    // 1. Initialize Bifrost Router with canonical runic routes
    let mut router = BifrostRouter::new();

    router.register("//STATUS", Box::new(|frame| {
        Ok(BifrostFrame::new(
            MessageType::TelemetryStream,
            "BIFROST_GATEWAY",
            &frame.sender,
            "TELEMETRY: CPU=4.2% RAM=31.4MB/4096MB NODE=COMPLIANT MESH=ONLINE",
        ))
    }));

    router.register("//HELIOS", Box::new(|frame| {
        Ok(BifrostFrame::new(
            MessageType::RunicDispatch,
            "SIR_HELIOS",
            &frame.sender,
            "HELIOS_TRUTH_VERIFIED: High-altitude macroscopic audit clean. Zero drift.",
        ))
    }));

    router.register("//HATEOAS", Box::new(|frame| {
        let view = KnightTelemetryView {
            name: "SIR_HELIOS".to_string(),
            status: "ONLINE".to_string(),
            ram_mb: 32,
            role: "Sovereign Spire Sentinel".to_string(),
        };
        let card = HateoasBuilder::render_knight_card(&view);
        Ok(BifrostFrame::new(
            MessageType::HateoasFragment,
            "BIFROST_GATEWAY",
            &frame.sender,
            card,
        ))
    }));

    // 2. Dispatch Inbound Runic Frame
    let inbound_frame = BifrostFrame::new(
        MessageType::RunicDispatch,
        "OPERATOR_VIZION",
        "BIFROST_GATEWAY",
        "//HATEOAS",
    );
    info!("Dispatching inbound runic frame: id={}", inbound_frame.frame_id);

    let outbound_reply = router.dispatch(&inbound_frame)?;
    info!("Outbound reply received: msg_type={:?} recipient={}", outbound_reply.msg_type, outbound_reply.recipient);

    // 3. Cryptographic Transport Receipt
    let receipt = TransportReceipt::generate(&outbound_reply);
    info!("Transport receipt forged: receipt_id={} receipt_hash={}", receipt.receipt_id, receipt.receipt_hash);

    // 4. SSE Telemetry Stream Event
    let sse_event = SseEvent::new("knight_status", &outbound_reply.payload)
        .with_id(&receipt.receipt_id);
    let sse_wire = sse_event.format();
    info!("SSE Telemetry packet formatted ({} bytes)", sse_wire.len());

    let elapsed = start_time.elapsed();
    info!("Transport roundtrip completed in {} ms (Threshold: <10 ms)", elapsed.as_millis());

    println!("\n=== BIFROST TRANSPORT RECEIPT ===");
    println!("Receipt ID: {}", receipt.receipt_id);
    println!("Frame ID: {}", receipt.frame_id);
    println!("Payload Blake3: {}", receipt.payload_hash);
    println!("Receipt Blake3: {}", receipt.receipt_hash);
    println!("Roundtrip Latency: {} ms", elapsed.as_millis());
    println!("SSE Stream Wire:\n{}", sse_wire);

    Ok(())
}
