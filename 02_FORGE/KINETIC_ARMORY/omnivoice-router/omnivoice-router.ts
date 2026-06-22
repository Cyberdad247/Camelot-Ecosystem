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

import { WebSocketServer, WebSocket } from "ws";
import * as crypto from "crypto";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";

const PORT = 3002;
const HOME = process.env.CAMELOT_OS_HOME ?? path.join(os.homedir(), "CAMELOT_OS");
const QUEUE_PATH = path.join(HOME, "logs", "harness_queue.jsonl");

const VAD_RMS_THRESHOLD = 0.01;
const VAD_SPEECH_MIN_MS = 200;
const VAD_SILENCE_GAP_MS = 800;

interface PeerState {
  id: string;
  remoteAddr: string;
  speaking: boolean;
  speechStartMs: number | null;
  silenceStartMs: number | null;
  utteranceBuffer: number[];
}

interface OmniMessage {
  type: "offer" | "answer" | "candidate" | "data_frame" | "transcript" | "ping";
  sdp?: string;
  candidate?: unknown;
  samples?: number[];
  text?: string;
}

const peers = new Map<WebSocket, PeerState>();

function enqueue(task: object): void {
  try {
    fs.appendFileSync(QUEUE_PATH, JSON.stringify(task) + "\n", "utf8");
  } catch (e) {
    console.error(`[OMNIVOICE] QUEUE ERROR: ${e}`);
  }
}

function mkId(prefix: string): string {
  return `${prefix}-${Date.now()}-${crypto.randomBytes(2).toString("hex")}`;
}

function rms(samples: number[]): number {
  if (!samples.length) return 0;
  const sum = samples.reduce((s, v) => s + v * v, 0);
  return Math.sqrt(sum / samples.length);
}

function writeWavFile(filePath: string, samples: number[], sampleRate: number = 16000): void {
  const numChannels = 1;
  const bytesPerSample = 2; // Int16
  const blockAlign = numChannels * bytesPerSample;
  const byteRate = sampleRate * blockAlign;
  const dataSize = samples.length * bytesPerSample;

  const buffer = Buffer.alloc(44 + dataSize);

  buffer.write("RIFF", 0);
  buffer.writeUInt32LE(36 + dataSize, 4);
  buffer.write("WAVE", 8);
  buffer.write("fmt ", 12);
  buffer.writeUInt32LE(16, 16); // Subchunk1Size
  buffer.writeUInt16LE(1, 20);  // AudioFormat (PCM)
  buffer.writeUInt16LE(numChannels, 22);
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(byteRate, 28);
  buffer.writeUInt16LE(blockAlign, 32);
  buffer.writeUInt16LE(bytesPerSample * 8, 34);
  buffer.write("data", 36);
  buffer.writeUInt32LE(dataSize, 40);

  let offset = 44;
  for (const sample of samples) {
    const s = Math.max(-1, Math.min(1, sample));
    const val = s < 0 ? s * 32768 : s * 32767;
    buffer.writeInt16LE(Math.floor(val), offset);
    offset += 2;
  }

  fs.writeFileSync(filePath, buffer);
}

// ── Energy VAD state machine ──────────────────────────────────────────────────

function processFrame(state: PeerState, samples: number[]): void {
  const energy = rms(samples);
  const isSpeech = energy > VAD_RMS_THRESHOLD;
  const now = Date.now();

  if (isSpeech) {
    state.utteranceBuffer.push(...samples);
    if (!state.speaking) {
      state.speaking = true;
      state.speechStartMs = now;
      state.silenceStartMs = null;
    } else {
      state.silenceStartMs = null; // reset silence timer on new energy
    }
  } else if (state.speaking) {
    state.utteranceBuffer.push(...samples);
    if (state.silenceStartMs === null) {
      state.silenceStartMs = now;
    }
    const silenceDuration = now - state.silenceStartMs;
    const speechDuration = now - (state.speechStartMs ?? now);

    if (silenceDuration >= VAD_SILENCE_GAP_MS && speechDuration >= VAD_SPEECH_MIN_MS) {
      const audioDir = path.join(HOME, "03_VAULT", "runtime_state", "audio");
      if (!fs.existsSync(audioDir)) {
        fs.mkdirSync(audioDir, { recursive: true });
      }
      const audioPath = path.join(audioDir, `${state.id}-${now}.wav`);
      writeWavFile(audioPath, state.utteranceBuffer, 16000);

      enqueue({
        id: mkId("vad"),
        type: "vad_utterance",
        source: "omnivoice-router",
        peer_id: state.id,
        samples_count: state.utteranceBuffer.length,
        duration_ms: speechDuration,
        file_path: audioPath,
        queued_at: new Date().toISOString(),
        priority: 1,
      });
      console.log(`[OMNIVOICE] VAD utterance ${state.id} ${speechDuration}ms -> ${audioPath}`);
      // reset state
      state.speaking = false;
      state.speechStartMs = null;
      state.silenceStartMs = null;
      state.utteranceBuffer = [];
    }
  }
}

// ── Server ────────────────────────────────────────────────────────────────────
import * as http from "http";

const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/broadcast_audio') {
    const chunks: Buffer[] = [];
    req.on('data', chunk => chunks.push(chunk));
    req.on('end', () => {
      const pcmData = Buffer.concat(chunks);
      const base64Data = pcmData.toString('base64');
      const payload = JSON.stringify({
        type: "audio_playback",
        audio_b64: base64Data
      });
      for (const [ws, state] of peers) {
        if (ws.readyState === ws.OPEN) {
          ws.send(payload);
          console.log(`[OMNIVOICE] Broadcast audio to ${state.id}`);
        }
      }
      res.writeHead(200);
      res.end("OK");
    });
    return;
  }
  res.writeHead(404);
  res.end("Not found");
});

const wss = new WebSocketServer({ server });

server.listen(PORT, () => {
  console.log(`[OMNIVOICE] OmniVoice Router :${PORT} ONLINE`);
});

wss.on("connection", (ws: WebSocket, req) => {
  const remoteAddr = req.socket.remoteAddress ?? "";
  const state: PeerState = {
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
    let msg: OmniMessage;
    try {
      msg = JSON.parse(raw.toString()) as OmniMessage;
    } catch {
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
        ws.send(JSON.stringify({ type: "error", reason: `unknown: ${(msg as { type: string }).type}` }));
    }
  });

  ws.on("close", () => {
    console.log(`[OMNIVOICE] DISCONNECT ${state.id}`);
    peers.delete(ws);
  });

  ws.on("error", (err: Error) => {
    console.error(`[OMNIVOICE] ERROR ${state.id}: ${err.message}`);
  });
});

function shutdown(): void {
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
