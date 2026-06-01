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

const wss = new WebSocketServer({ port: PORT });
console.log(`[EDGE-ROUTER] Kinetic Edge :${PORT} ONLINE`);

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

  ws.on("message", (raw) => {
    let msg: EdgeMessage;
    try {
      msg = JSON.parse(raw.toString()) as EdgeMessage;
    } catch {
      ws.send(JSON.stringify({ status: "error", reason: "invalid JSON" }));
      return;
    }

    // Gate non-loopback on first message
    if (!meta.authenticated) {
      if (!verifyToken(msg.token ?? "")) {
        ws.send(JSON.stringify({ status: "denied", reason: "invalid bifrost token" }));
        ws.close(1008, "unauthorized");
        return;
      }
      meta.authenticated = true;
    }

    const msgId = msg.id ?? mkId();

    switch (msg.type) {
      case "ping":
        ws.send(JSON.stringify({ status: "pong", ts: Date.now() }));
        break;

      case "status":
        ws.send(JSON.stringify({
          status: "ok",
          clients: clients.size,
          uptime_s: Math.floor(process.uptime()),
          queue: QUEUE_PATH,
        }));
        break;

      case "forge":
        if (!msg.directive) {
          ws.send(JSON.stringify({ status: "error", reason: "missing directive" }));
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
        ws.send(JSON.stringify({ status: "queued", id: msgId }));
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
        ws.send(JSON.stringify({ status: "queued", id: msgId }));
        break;

      default:
        ws.send(JSON.stringify({ status: "error", reason: `unknown type: ${(msg as { type: string }).type}` }));
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
