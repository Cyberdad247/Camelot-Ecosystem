/**
 * [EDGE-ROUTER] Kinetic Edge — WebSocket persistent connection server
 * Port :3001 — replaces HTTP POST on hot path for CAMELOT-OS forge directives
 *
 * Auth rules (mirrors bifrost.py):
 *   Rule A: loopback — always trusted
 *   Rule B: non-loopback — must present valid bifrost token in first message
 */
var __createBinding =
  (this && this.__createBinding) ||
  (Object.create
    ? (o, m, k, k2) => {
        if (k2 === undefined) k2 = k;
        var desc = Object.getOwnPropertyDescriptor(m, k);
        if (!desc || ('get' in desc ? !m.__esModule : desc.writable || desc.configurable)) {
          desc = { enumerable: true, get: () => m[k] };
        }
        Object.defineProperty(o, k2, desc);
      }
    : (o, m, k, k2) => {
        if (k2 === undefined) k2 = k;
        o[k2] = m[k];
      });
var __setModuleDefault =
  (this && this.__setModuleDefault) ||
  (Object.create
    ? (o, v) => {
        Object.defineProperty(o, 'default', { enumerable: true, value: v });
      }
    : (o, v) => {
        o['default'] = v;
      });
var __importStar =
  (this && this.__importStar) ||
  (() => {
    var ownKeys = (o) => {
      ownKeys =
        Object.getOwnPropertyNames ||
        ((o) => {
          var ar = [];
          for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
          return ar;
        });
      return ownKeys(o);
    };
    return (mod) => {
      if (mod && mod.__esModule) return mod;
      var result = {};
      if (mod != null)
        for (var k = ownKeys(mod), i = 0; i < k.length; i++)
          if (k[i] !== 'default') __createBinding(result, mod, k[i]);
      __setModuleDefault(result, mod);
      return result;
    };
  })();
Object.defineProperty(exports, '__esModule', { value: true });
const ws_1 = require('ws');
const crypto = __importStar(require('crypto'));
const fs = __importStar(require('fs'));
const os = __importStar(require('os'));
const path = __importStar(require('path'));
const zlib = __importStar(require('zlib'));
const PORT = 3001;
const HOME = process.env.CAMELOT_OS_HOME ?? path.join(os.homedir(), 'CAMELOT_OS');
const QUEUE_PATH = path.join(HOME, 'logs', 'harness_queue.jsonl');
const TOKEN_PATH = path.join(os.homedir(), '.camelot', 'bifrost.token');
const clients = new Map();
function readToken() {
  try {
    return fs.readFileSync(TOKEN_PATH, 'ascii').trim();
  } catch {
    return null;
  }
}
function verifyToken(presented) {
  const local = readToken();
  if (!local || !presented) return false;
  // constant-time comparison to resist timing attacks
  try {
    return crypto.timingSafeEqual(Buffer.from(local, 'utf8'), Buffer.from(presented, 'utf8'));
  } catch {
    return false;
  }
}
function isLoopback(addr) {
  return addr === '127.0.0.1' || addr === '::1' || addr === '::ffff:127.0.0.1';
}
function enqueue(task) {
  try {
    fs.appendFileSync(QUEUE_PATH, JSON.stringify(task) + '\n', 'utf8');
  } catch (e) {
    console.error(`[EDGE-ROUTER] QUEUE ERROR: ${e}`);
  }
}
function mkId() {
  return `ws-${Date.now()}-${crypto.randomBytes(3).toString('hex')}`;
}
// ── Server ────────────────────────────────────────────────────────────────────
const wss = new ws_1.WebSocketServer({
  port: PORT,
  perMessageDeflate: {
    zlibDeflateOptions: {
      chunkSize: 1024,
      memLevel: 7,
      level: 3,
    },
    zlibInflateOptions: {
      chunkSize: 10 * 1024,
    },
    clientNoContextTakeover: true,
    serverNoContextTakeover: true,
    concurrencyLimit: 10,
    threshold: 1024,
  },
});
console.log(`[EDGE-ROUTER] Kinetic Edge :${PORT} ONLINE (gzip compression enabled)`);
wss.on('connection', (ws, req) => {
  const remoteAddr = req.socket.remoteAddress ?? '';
  const meta = {
    id: mkId(),
    remoteAddr,
    connectedAt: Date.now(),
    authenticated: isLoopback(remoteAddr),
  };
  clients.set(ws, meta);
  console.log(`[EDGE-ROUTER] CONNECT ${meta.id} ${remoteAddr}`);
  function sendResponse(obj, compress = false) {
    const payloadStr = JSON.stringify(obj);
    if (compress) {
      zlib.gzip(Buffer.from(payloadStr, 'utf8'), (err, compressed) => {
        if (err) {
          ws.send(payloadStr);
        } else {
          ws.send(compressed, { binary: true });
        }
      });
    } else {
      ws.send(payloadStr);
    }
  }
  ws.on('message', (raw) => {
    let data;
    if (Buffer.isBuffer(raw)) {
      data = raw;
    } else if (Array.isArray(raw)) {
      data = Buffer.concat(raw);
    } else if (raw instanceof ArrayBuffer) {
      data = Buffer.from(raw);
    } else {
      data = Buffer.from(raw);
    }
    // Check for gzip signature (0x1f 0x8b)
    if (data.length > 2 && data[0] === 0x1f && data[1] === 0x8b) {
      try {
        data = zlib.gunzipSync(data);
      } catch (e) {
        sendResponse({ status: 'error', reason: `gunzip failed: ${e}` });
        return;
      }
    }
    let msg;
    try {
      msg = JSON.parse(data.toString('utf8'));
    } catch {
      sendResponse({ status: 'error', reason: 'invalid JSON' });
      return;
    }
    // Gate non-loopback on first message
    if (!meta.authenticated) {
      if (!verifyToken(msg.token ?? '')) {
        sendResponse({ status: 'denied', reason: 'invalid bifrost token' });
        ws.close(1008, 'unauthorized');
        return;
      }
      meta.authenticated = true;
    }
    const msgId = msg.id ?? mkId();
    const shouldCompress = !!msg.compress;
    switch (msg.type) {
      case 'ping':
        sendResponse({ status: 'pong', ts: Date.now() }, shouldCompress);
        break;
      case 'status':
        sendResponse(
          {
            status: 'ok',
            clients: clients.size,
            uptime_s: Math.floor(process.uptime()),
            queue: QUEUE_PATH,
          },
          shouldCompress,
        );
        break;
      case 'forge':
        if (!msg.directive) {
          sendResponse({ status: 'error', reason: 'missing directive' }, shouldCompress);
          break;
        }
        enqueue({
          id: msgId,
          type: 'forge',
          directive: msg.directive,
          payload: msg.payload ?? null,
          source: 'edge-router',
          queued_at: new Date().toISOString(),
          priority: 2,
        });
        console.log(`[EDGE-ROUTER] FORGE queued ${msgId}`);
        sendResponse({ status: 'queued', id: msgId }, shouldCompress);
        break;
      case 'query':
        enqueue({
          id: msgId,
          type: 'query',
          payload: msg.payload ?? null,
          source: 'edge-router',
          queued_at: new Date().toISOString(),
          priority: 3,
        });
        sendResponse({ status: 'queued', id: msgId }, shouldCompress);
        break;
      default:
        sendResponse({ status: 'error', reason: `unknown type: ${msg.type}` }, shouldCompress);
    }
  });
  ws.on('close', () => {
    console.log(`[EDGE-ROUTER] DISCONNECT ${meta.id}`);
    clients.delete(ws);
  });
  ws.on('error', (err) => {
    console.error(`[EDGE-ROUTER] ERROR ${meta.id}: ${err.message}`);
  });
});
function shutdown() {
  console.log('[EDGE-ROUTER] Shutdown signal — closing connections');
  for (const [ws] of clients) {
    ws.close(1001, 'server shutdown');
  }
  wss.close(() => {
    console.log('[EDGE-ROUTER] OFFLINE');
    process.exit(0);
  });
}
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
