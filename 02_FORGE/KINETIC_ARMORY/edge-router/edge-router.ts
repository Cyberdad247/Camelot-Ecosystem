/**
 * [EDGE-ROUTER] Kinetic Edge — WebSocket persistent connection server
 * Port :3001 — replaces HTTP POST on hot path for CAMELOT-OS forge directives
 *
 * Auth rules (mirrors bifrost.py):
 *   Rule A: loopback — always trusted
 *   Rule B: non-loopback — must present valid bifrost token in first message
 */

import { WebSocketServer, WebSocket } from "ws";
import * as crypto from "crypto";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import * as zlib from "zlib";

const PORT = 3001;
const HOME = process.env.CAMELOT_OS_HOME ?? path.join(os.homedir(), "CAMELOT_OS");
const QUEUE_PATH = path.join(HOME, "logs", "harness_queue.jsonl");
const TOKEN_PATH = path.join(os.homedir(), ".camelot", "bifrost.token");

interface ClientMeta {
  id: string;
  remoteAddr: string;
  connectedAt: number;
  authenticated: boolean;
}

interface EdgeMessage {
  type: "forge" | "query" | "ping" | "status";
  token?: string;
  id?: string;
  directive?: string;
  payload?: unknown;
  compress?: boolean;
}

const clients = new Map<WebSocket, ClientMeta>();

function readToken(): string | null {
  try {
    return fs.readFileSync(TOKEN_PATH, "ascii").trim();
  } catch {
    return null;
  }
}

function verifyToken(presented: string): boolean {
  const local = readToken();
  if (!local || !presented) return false;
  // constant-time comparison to resist timing attacks
  try {
    return crypto.timingSafeEqual(
      Buffer.from(local, "utf8"),
      Buffer.from(presented, "utf8"),
    );
  } catch {
    return false;
  }
}

function isLoopback(addr: string): boolean {
  return addr === "127.0.0.1" || addr === "::1" || addr === "::ffff:127.0.0.1";
}

function enqueue(task: object): void {
  try {
    fs.appendFileSync(QUEUE_PATH, JSON.stringify(task) + "\n", "utf8");
  } catch (e) {
    console.error(`[EDGE-ROUTER] QUEUE ERROR: ${e}`);
  }
}

function mkId(): string {
  return `ws-${Date.now()}-${crypto.randomBytes(3).toString("hex")}`;
}

// ── Server ────────────────────────────────────────────────────────────────────

const wss = new WebSocketServer({
  port: PORT,
  perMessageDeflate: {
    zlibDeflateOptions: {
      chunkSize: 1024,
      memLevel: 7,
      level: 3
    },
    zlibInflateOptions: {
      chunkSize: 10 * 1024
    },
    clientNoContextTakeover: true,
    serverNoContextTakeover: true,
    concurrencyLimit: 10,
    threshold: 1024
  }
});
console.log(`[EDGE-ROUTER] Kinetic Edge :${PORT} ONLINE (gzip compression enabled)`);

wss.on("connection", (ws: WebSocket, req) => {
  const remoteAddr = req.socket.remoteAddress ?? "";
  const meta: ClientMeta = {
    id: mkId(),
    remoteAddr,
    connectedAt: Date.now(),
    authenticated: isLoopback(remoteAddr),
  };
  clients.set(ws, meta);
  console.log(`[EDGE-ROUTER] CONNECT ${meta.id} ${remoteAddr}`);

  function sendResponse(obj: object, compress: boolean = false): void {
    const payloadStr = JSON.stringify(obj);
    if (compress) {
      zlib.gzip(Buffer.from(payloadStr, "utf8"), (err, compressed) => {
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

  ws.on("message", (raw) => {
    let data: Buffer;
    if (Buffer.isBuffer(raw)) {
      data = raw;
    } else if (Array.isArray(raw)) {
      data = Buffer.concat(raw);
    } else if (raw instanceof ArrayBuffer) {
      data = Buffer.from(raw);
    } else {
      data = Buffer.from(raw as any);
    }

    // Check for gzip signature (0x1f 0x8b)
    if (data.length > 2 && data[0] === 0x1f && data[1] === 0x8b) {
      try {
        data = zlib.gunzipSync(data);
      } catch (e) {
        sendResponse({ status: "error", reason: `gunzip failed: ${e}` });
        return;
      }
    }

    let msg: EdgeMessage;
    try {
      msg = JSON.parse(data.toString("utf8")) as EdgeMessage;
    } catch {
      sendResponse({ status: "error", reason: "invalid JSON" });
      return;
    }

    // Gate non-loopback on first message
    if (!meta.authenticated) {
      if (!verifyToken(msg.token ?? "")) {
        sendResponse({ status: "denied", reason: "invalid bifrost token" });
        ws.close(1008, "unauthorized");
        return;
      }
      meta.authenticated = true;
    }

    const msgId = msg.id ?? mkId();
    const shouldCompress = !!msg.compress;

    switch (msg.type) {
      case "ping":
        sendResponse({ status: "pong", ts: Date.now() }, shouldCompress);
        break;

      case "status":
        sendResponse({
          status: "ok",
          clients: clients.size,
          uptime_s: Math.floor(process.uptime()),
          queue: QUEUE_PATH,
        }, shouldCompress);
        break;

      case "forge":
        if (!msg.directive) {
          sendResponse({ status: "error", reason: "missing directive" }, shouldCompress);
          break;
        }
        enqueue({
          id: msgId,
          type: "forge",
          directive: msg.directive,
          payload: msg.payload ?? null,
          source: "edge-router",
          queued_at: new Date().toISOString(),
          priority: 2,
        });
        console.log(`[EDGE-ROUTER] FORGE queued ${msgId}`);
        sendResponse({ status: "queued", id: msgId }, shouldCompress);
        break;

      case "query":
        enqueue({
          id: msgId,
          type: "query",
          payload: msg.payload ?? null,
          source: "edge-router",
          queued_at: new Date().toISOString(),
          priority: 3,
        });
        sendResponse({ status: "queued", id: msgId }, shouldCompress);
        break;

      default:
        sendResponse({ status: "error", reason: `unknown type: ${(msg as { type: string }).type}` }, shouldCompress);
    }
  });

  ws.on("close", () => {
    console.log(`[EDGE-ROUTER] DISCONNECT ${meta.id}`);
    clients.delete(ws);
  });

  ws.on("error", (err: Error) => {
    console.error(`[EDGE-ROUTER] ERROR ${meta.id}: ${err.message}`);
  });
});

function shutdown(): void {
  console.log("[EDGE-ROUTER] Shutdown signal — closing connections");
  for (const [ws] of clients) {
    ws.close(1001, "server shutdown");
  }
  wss.close(() => {
    console.log("[EDGE-ROUTER] OFFLINE");
    process.exit(0);
  });
}

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);
