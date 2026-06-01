"use strict";
/**
 * [OMNIVOICE] OmniVoice Router — WebRTC signaling + energy VAD server
 * Port :3002 — handles WebRTC offer/candidate relay and PCM frame VAD
 *
 * Energy VAD params:
 *   RMS threshold : 0.01  (float32 PCM)
 *   speech_min_ms : 200   — minimum voiced segment before it's an utterance
 *   silence_gap_ms: 800   — trailing silence to close utterance
 *
 * On utterance boundary: enqueues vad_utterance directive to harness_queue.jsonl (priority=1)
 * On transcript message: enqueues forge directive to harness_queue.jsonl (priority=1)
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const ws_1 = require("ws");
const crypto = __importStar(require("crypto"));
const fs = __importStar(require("fs"));
const os = __importStar(require("os"));
const path = __importStar(require("path"));
const PORT = 3002;
const HOME = process.env.CAMELOT_OS_HOME ?? path.join(os.homedir(), "CAMELOT_OS");
const QUEUE_PATH = path.join(HOME, "logs", "harness_queue.jsonl");
const VAD_RMS_THRESHOLD = 0.01;
const VAD_SPEECH_MIN_MS = 200;
const VAD_SILENCE_GAP_MS = 800;
const peers = new Map();
function enqueue(task) {
    try {
        fs.appendFileSync(QUEUE_PATH, JSON.stringify(task) + "\n", "utf8");
    }
    catch (e) {
        console.error(`[OMNIVOICE] QUEUE ERROR: ${e}`);
    }
}
function mkId(prefix) {
    return `${prefix}-${Date.now()}-${crypto.randomBytes(2).toString("hex")}`;
}
function rms(samples) {
    if (!samples.length)
        return 0;
    const sum = samples.reduce((s, v) => s + v * v, 0);
    return Math.sqrt(sum / samples.length);
}
// ── Energy VAD state machine ──────────────────────────────────────────────────
function processFrame(state, samples) {
    const energy = rms(samples);
    const isSpeech = energy > VAD_RMS_THRESHOLD;
    const now = Date.now();
    if (isSpeech) {
        state.utteranceBuffer.push(...samples);
        if (!state.speaking) {
            state.speaking = true;
            state.speechStartMs = now;
            state.silenceStartMs = null;
        }
        else {
            state.silenceStartMs = null; // reset silence timer on new energy
        }
    }
    else if (state.speaking) {
        state.utteranceBuffer.push(...samples);
        if (state.silenceStartMs === null) {
            state.silenceStartMs = now;
        }
        const silenceDuration = now - state.silenceStartMs;
        const speechDuration = now - (state.speechStartMs ?? now);
        if (silenceDuration >= VAD_SILENCE_GAP_MS && speechDuration >= VAD_SPEECH_MIN_MS) {
            enqueue({
                id: mkId("vad"),
                type: "vad_utterance",
                source: "omnivoice-router",
                peer_id: state.id,
                samples_count: state.utteranceBuffer.length,
                duration_ms: speechDuration,
                queued_at: new Date().toISOString(),
                priority: 1,
            });
            console.log(`[OMNIVOICE] VAD utterance ${state.id} ${speechDuration}ms`);
            // reset state
            state.speaking = false;
            state.speechStartMs = null;
            state.silenceStartMs = null;
            state.utteranceBuffer = [];
        }
    }
}
// ── Server ────────────────────────────────────────────────────────────────────
const wss = new ws_1.WebSocketServer({ port: PORT });
console.log(`[OMNIVOICE] OmniVoice Router :${PORT} ONLINE`);
wss.on("connection", (ws, req) => {
    const remoteAddr = req.socket.remoteAddress ?? "";
    const state = {
        id: mkId("peer"),
        remoteAddr,
        speaking: false,
        speechStartMs: null,
        silenceStartMs: null,
        utteranceBuffer: [],
    };
    peers.set(ws, state);
    console.log(`[OMNIVOICE] CONNECT ${state.id} ${remoteAddr}`);
    ws.send(JSON.stringify({ type: "welcome", peer_id: state.id }));
    ws.on("message", (raw) => {
        let msg;
        try {
            msg = JSON.parse(raw.toString());
        }
        catch {
            ws.send(JSON.stringify({ type: "error", reason: "invalid JSON" }));
            return;
        }
        switch (msg.type) {
            case "ping":
                ws.send(JSON.stringify({ type: "pong", ts: Date.now() }));
                break;
            case "offer":
                // Relay SDP offer — future: forward to target peer; for now ack
                ws.send(JSON.stringify({ type: "offer_ack", peer_id: state.id }));
                break;
            case "answer":
                ws.send(JSON.stringify({ type: "answer_ack" }));
                break;
            case "candidate":
                // ICE candidate relay — future: trickle to target peer
                ws.send(JSON.stringify({ type: "candidate_ack" }));
                break;
            case "data_frame": {
                const samples = Array.isArray(msg.samples) ? msg.samples : [];
                processFrame(state, samples);
                break;
            }
            case "transcript": {
                const text = (msg.text ?? "").trim();
                if (text) {
                    const tId = mkId("transcript");
                    enqueue({
                        id: tId,
                        type: "forge",
                        directive: text,
                        source: "omnivoice-router",
                        queued_at: new Date().toISOString(),
                        priority: 1,
                    });
                    console.log(`[OMNIVOICE] TRANSCRIPT queued ${tId}: ${text.slice(0, 60)}`);
                    ws.send(JSON.stringify({ type: "transcript_queued", id: tId }));
                }
                break;
            }
            default:
                ws.send(JSON.stringify({ type: "error", reason: `unknown: ${msg.type}` }));
        }
    });
    ws.on("close", () => {
        console.log(`[OMNIVOICE] DISCONNECT ${state.id}`);
        peers.delete(ws);
    });
    ws.on("error", (err) => {
        console.error(`[OMNIVOICE] ERROR ${state.id}: ${err.message}`);
    });
});
function shutdown() {
    console.log("[OMNIVOICE] Shutdown signal — closing connections");
    for (const [ws] of peers) {
        ws.close(1001, "server shutdown");
    }
    wss.close(() => {
        console.log("[OMNIVOICE] OFFLINE");
        process.exit(0);
    });
}
process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);
