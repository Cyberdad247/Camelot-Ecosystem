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

import { WebSocketServer, WebSocket } from 'ws';
import * as crypto from 'crypto';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import * as http from 'http';

const PORT = 3002;
const HOME = process.env.CAMELOT_OS_HOME ?? path.join(os.homedir(), 'CAMELOT_OS');
const QUEUE_PATH = path.join(HOME, 'logs', 'harness_queue.jsonl');

const VAD_RMS_THRESHOLD = 0.01;
const VAD_SPEECH_MIN_MS = 200;
const VAD_SILENCE_GAP_MS = 800;
const PCM_FRAME_BYTES = 3200;
const HTTP_SESSION_TTL_MS = 60_000;
const MAX_HTTP_SESSIONS = 16;
const AUDIO_RETENTION_MS = 5 * 60_000;

interface PeerState {
  id: string;
  remoteAddr: string;
  speaking: boolean;
  speechStartMs: number | null;
  silenceStartMs: number | null;
  utteranceBuffer: number[];
  knight_id?: string;
}

interface OmniMessage {
  type: 'offer' | 'answer' | 'candidate' | 'data_frame' | 'transcript' | 'ping' | 'set_knight';
  sdp?: string;
  candidate?: unknown;
  samples?: number[];
  text?: string;
  knight_id?: string;
}

const peers = new Map<WebSocket, PeerState>();

interface HttpPeerState {
  peer: PeerState;
  lastSeenMs: number;
  lastSequence: number;
}

const httpPeers = new Map<string, HttpPeerState>();

function enqueue(task: object): void {
  try {
    fs.appendFileSync(QUEUE_PATH, JSON.stringify(task) + '\n', 'utf8');
  } catch (e) {
    console.error(`[OMNIVOICE] QUEUE ERROR: ${e}`);
  }
}

function mkId(prefix: string): string {
  return `${prefix}-${Date.now()}-${crypto.randomBytes(2).toString('hex')}`;
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

  buffer.write('RIFF', 0);
  buffer.writeUInt32LE(36 + dataSize, 4);
  buffer.write('WAVE', 8);
  buffer.write('fmt ', 12);
  buffer.writeUInt32LE(16, 16); // Subchunk1Size
  buffer.writeUInt16LE(1, 20); // AudioFormat (PCM)
  buffer.writeUInt16LE(numChannels, 22);
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(byteRate, 28);
  buffer.writeUInt16LE(blockAlign, 32);
  buffer.writeUInt16LE(bytesPerSample * 8, 34);
  buffer.write('data', 36);
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

function purgeExpiredAudio(audioDir: string, now: number): void {
  try {
    for (const entry of fs.readdirSync(audioDir, { withFileTypes: true })) {
      if (!entry.isFile() || !entry.name.endsWith('.wav')) continue;
      const candidate = path.join(audioDir, entry.name);
      if (now - fs.statSync(candidate).mtimeMs > AUDIO_RETENTION_MS) fs.unlinkSync(candidate);
    }
  } catch (error) {
    console.error(`[OMNIVOICE] Audio retention sweep failed: ${error}`);
  }
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

      console.log(`[OMNIVOICE] VAD Speech Started for ${state.id} — dispatching interruption`);

      // 1. Send socket clear-signal to clients to immediately halt local audio playback
      for (const [ws, peer] of peers) {
        if (ws.readyState === ws.OPEN) {
          ws.send(JSON.stringify({ type: 'clear' }));
          console.log(`[OMNIVOICE] Broadcast clear-signal to ${peer.id}`);
        }
      }

      // 2. Flush current outgoing audio streams in kitten_service.py
      const req = http.request(
        {
          hostname: '127.0.0.1',
          port: 8300,
          path: '/flush',
          method: 'POST',
          headers: {
            'Content-Length': 0,
          },
        },
        (res) => {
          console.log(`[OMNIVOICE] Kitten flush response status: ${res.statusCode}`);
        },
      );
      req.on('error', (err) => {
        console.error(`[OMNIVOICE] Kitten flush HTTP request error: ${err.message}`);
      });
      req.end();

      // 3. Cancel current LLM completion run on the control plane
      enqueue({
        id: mkId('interrupt'),
        type: 'interrupt',
        source: 'omnivoice-router',
        queued_at: new Date().toISOString(),
        priority: 1,
      });
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
      const audioDir = path.join(HOME, '03_VAULT', 'runtime_state', 'audio');
      if (!fs.existsSync(audioDir)) {
        fs.mkdirSync(audioDir, { recursive: true });
      }
      purgeExpiredAudio(audioDir, now);
      const audioPath = path.join(audioDir, `${state.id}-${now}.wav`);
      writeWavFile(audioPath, state.utteranceBuffer, 16000);

      enqueue({
        id: mkId('vad'),
        type: 'vad_utterance',
        source: 'omnivoice-router',
        peer_id: state.id,
        samples_count: state.utteranceBuffer.length,
        duration_ms: speechDuration,
        file_path: audioPath,
        expires_at: new Date(now + AUDIO_RETENTION_MS).toISOString(),
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

function isLoopback(address: string | undefined): boolean {
  return address === '127.0.0.1' || address === '::1' || address === '::ffff:127.0.0.1';
}

function header(req: http.IncomingMessage, name: string): string {
  const value = req.headers[name];
  return Array.isArray(value) ? (value[0] ?? '') : (value ?? '');
}

function respondJson(res: http.ServerResponse, status: number, body: object): void {
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
  });
  res.end(JSON.stringify(body));
}

function resetPeerSpeech(peer: PeerState): void {
  peer.speaking = false;
  peer.speechStartMs = null;
  peer.silenceStartMs = null;
  peer.utteranceBuffer = [];
}

function getHttpPeer(sessionId: string, remoteAddr: string): HttpPeerState | null {
  const now = Date.now();
  for (const [id, state] of httpPeers) {
    if (now - state.lastSeenMs > HTTP_SESSION_TTL_MS) httpPeers.delete(id);
  }

  const existing = httpPeers.get(sessionId);
  if (existing) {
    existing.lastSeenMs = now;
    return existing;
  }
  if (httpPeers.size >= MAX_HTTP_SESSIONS) return null;

  const created: HttpPeerState = {
    peer: {
      id: sessionId,
      remoteAddr,
      speaking: false,
      speechStartMs: null,
      silenceStartMs: null,
      utteranceBuffer: [],
    },
    lastSeenMs: now,
    lastSequence: -1,
  };
  httpPeers.set(sessionId, created);
  return created;
}

// ── Server ────────────────────────────────────────────────────────────────────

const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/ingest_pcm') {
    const remoteAddr = req.socket.remoteAddress ?? '';
    if (!isLoopback(remoteAddr)) {
      respondJson(res, 403, { error: 'loopback_only' });
      req.resume();
      return;
    }

    if (!header(req, 'content-type').toLowerCase().startsWith('application/octet-stream')) {
      respondJson(res, 415, { error: 'unsupported_media_type' });
      req.resume();
      return;
    }

    const sessionId = header(req, 'x-voice-session');
    const sequenceText = header(req, 'x-voice-sequence');
    const sampleRateText = header(req, 'x-voice-sample-rate');
    const discontinuity = header(req, 'x-voice-discontinuity') === '1';
    const sequence = Number(sequenceText);
    if (
      !/^vfc-[a-f0-9]{24}$/.test(sessionId) ||
      !Number.isSafeInteger(sequence) ||
      sequence < 0 ||
      sampleRateText !== '16000'
    ) {
      respondJson(res, 400, { error: 'invalid_frame_metadata' });
      req.resume();
      return;
    }

    const contentLength = Number(header(req, 'content-length'));
    if (
      !Number.isSafeInteger(contentLength) ||
      contentLength <= 0 ||
      contentLength > PCM_FRAME_BYTES ||
      contentLength % 2 !== 0
    ) {
      respondJson(res, 413, { error: 'invalid_frame_size' });
      req.resume();
      return;
    }

    const state = getHttpPeer(sessionId, remoteAddr);
    if (!state) {
      respondJson(res, 503, { error: 'session_capacity_reached' });
      req.resume();
      return;
    }
    if (sequence <= state.lastSequence) {
      respondJson(res, 409, { error: 'stale_sequence' });
      req.resume();
      return;
    }

    const chunks: Buffer[] = [];
    let received = 0;
    req.on('data', (chunk: Buffer) => {
      received += chunk.length;
      if (received <= PCM_FRAME_BYTES) chunks.push(chunk);
    });
    req.on('end', () => {
      if (received !== contentLength || received > PCM_FRAME_BYTES || received % 2 !== 0) {
        respondJson(res, 400, { error: 'frame_length_mismatch' });
        return;
      }

      if (discontinuity || (state.lastSequence >= 0 && sequence !== state.lastSequence + 1)) {
        resetPeerSpeech(state.peer);
      }
      state.lastSequence = sequence;
      state.lastSeenMs = Date.now();

      const pcm = Buffer.concat(chunks, received);
      const samples = new Array<number>(received / 2);
      for (let offset = 0; offset < received; offset += 2) {
        samples[offset / 2] = pcm.readInt16LE(offset) / 32768;
      }
      processFrame(state.peer, samples);
      respondJson(res, 202, { accepted: true, sequence });
    });
    return;
  }

  if (req.method === 'POST' && req.url === '/broadcast_audio') {
    const chunks: Buffer[] = [];
    req.on('data', (chunk) => chunks.push(chunk));
    req.on('end', () => {
      const pcmData = Buffer.concat(chunks);
      const base64Data = pcmData.toString('base64');
      const payload = JSON.stringify({
        type: 'audio_playback',
        audio_b64: base64Data,
      });
      for (const [ws, state] of peers) {
        if (ws.readyState === ws.OPEN) {
          ws.send(payload);
          console.log(`[OMNIVOICE] Broadcast audio to ${state.id}`);
        }
      }
      res.writeHead(200);
      res.end('OK');
    });
    return;
  }
  res.writeHead(404);
  res.end('Not found');
});

const wss = new WebSocketServer({ server });

server.listen(PORT, '127.0.0.1', () => {
  console.log(`[OMNIVOICE] OmniVoice Router 127.0.0.1:${PORT} ONLINE`);
});

wss.on('connection', (ws: WebSocket, req) => {
  const remoteAddr = req.socket.remoteAddress ?? '';
  const state: PeerState = {
    id: mkId('peer'),
    remoteAddr,
    speaking: false,
    speechStartMs: null,
    silenceStartMs: null,
    utteranceBuffer: [],
  };
  peers.set(ws, state);
  console.log(`[OMNIVOICE] CONNECT ${state.id} ${remoteAddr}`);
  ws.send(JSON.stringify({ type: 'welcome', peer_id: state.id }));

  ws.on('message', (raw) => {
    let msg: OmniMessage;
    try {
      msg = JSON.parse(raw.toString()) as OmniMessage;
    } catch {
      ws.send(JSON.stringify({ type: 'error', reason: 'invalid JSON' }));
      return;
    }

    switch (msg.type) {
      case 'ping':
        ws.send(JSON.stringify({ type: 'pong', ts: Date.now() }));
        break;

      case 'offer':
        // Relay SDP offer — future: forward to target peer; for now ack
        ws.send(JSON.stringify({ type: 'offer_ack', peer_id: state.id }));
        break;

      case 'answer':
        ws.send(JSON.stringify({ type: 'answer_ack' }));
        break;

      case 'candidate':
        // ICE candidate relay — future: trickle to target peer
        ws.send(JSON.stringify({ type: 'candidate_ack' }));
        break;

      case 'data_frame': {
        const samples = Array.isArray(msg.samples) ? msg.samples : [];
        processFrame(state, samples);
        break;
      }

      case 'transcript': {
        const text = (msg.text ?? '').trim();
        if (text) {
          const tId = mkId('transcript');
          const targetKnight = msg.knight_id ?? state.knight_id;
          enqueue({
            id: tId,
            type: 'forge',
            directive: text,
            source: 'omnivoice-router',
            queued_at: new Date().toISOString(),
            priority: 1,
            knight_id: targetKnight ?? null,
          });
          console.log(
            `[OMNIVOICE] TRANSCRIPT queued ${tId} (knight_id: ${targetKnight ?? 'default'}): ${text.slice(0, 60)}`,
          );
          ws.send(JSON.stringify({ type: 'transcript_queued', id: tId, knight_id: targetKnight }));
        }
        break;
      }

      case 'set_knight': {
        if (msg.knight_id) {
          state.knight_id = msg.knight_id;
          console.log(`[OMNIVOICE] Set active knight for ${state.id} to ${msg.knight_id}`);
          ws.send(JSON.stringify({ type: 'knight_updated', knight_id: msg.knight_id }));
        }
        break;
      }

      default:
        ws.send(
          JSON.stringify({ type: 'error', reason: `unknown: ${(msg as { type: string }).type}` }),
        );
    }
  });

  ws.on('close', () => {
    console.log(`[OMNIVOICE] DISCONNECT ${state.id}`);
    peers.delete(ws);
  });

  ws.on('error', (err: Error) => {
    console.error(`[OMNIVOICE] ERROR ${state.id}: ${err.message}`);
  });
});

function shutdown(): void {
  console.log('[OMNIVOICE] Shutdown signal — closing connections');
  for (const [ws] of peers) {
    ws.close(1001, 'server shutdown');
  }
  wss.close(() => {
    console.log('[OMNIVOICE] OFFLINE');
    process.exit(0);
  });
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
