import "server-only";

import { readFile } from "node:fs/promises";
import net from "node:net";
import os from "node:os";
import path from "node:path";
import type { CockpitService, CockpitStatus, ServiceStatus } from "./cockpit-types";
import { runicExecutionEnabled } from "./runic-adapter";

type JsonRecord = Record<string, unknown>;

const CAMELOT_ROOT = process.env.CAMELOT_OS_HOME
  ? path.resolve(/* turbopackIgnore: true */ process.env.CAMELOT_OS_HOME)
  : path.resolve(/* turbopackIgnore: true */ process.cwd(), "../../..");
const RUNTIME_ROOT = path.join(/* turbopackIgnore: true */ CAMELOT_ROOT, "03_VAULT", "runtime_state");

const probes = [
  ["cliproxy", "CLIProxy", 8080],
  ["kinetic-edge", "Kinetic Edge", 3001],
  ["omni-voice", "OmniVoice", 3002],
  ["holotable", "Holotable", 3000],
  ["kitten-tts", "Kitten TTS", 8300],
  ["sir-octavian", "Sir Octavian", 8400],
] as const;

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

async function readJson(fileName: string): Promise<JsonRecord | null> {
  try {
    const raw = await readFile(/* turbopackIgnore: true */ path.join(RUNTIME_ROOT, fileName), "utf8");
    const value: unknown = JSON.parse(raw);
    return isRecord(value) ? value : null;
  } catch {
    return null;
  }
}

function numberValue(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function stringValue(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}

function child(record: JsonRecord | null, key: string): JsonRecord {
  const value = record?.[key];
  return isRecord(value) ? value : {};
}

function probePort(port: number): Promise<{ online: boolean; latencyMs: number | null }> {
  return new Promise((resolve) => {
    const started = performance.now();
    const socket = net.createConnection({ host: "127.0.0.1", port });
    let settled = false;

    const finish = (online: boolean) => {
      if (settled) return;
      settled = true;
      socket.destroy();
      resolve({
        online,
        latencyMs: online ? Math.max(1, Math.round(performance.now() - started)) : null,
      });
    };

    socket.setTimeout(180);
    socket.once("connect", () => finish(true));
    socket.once("timeout", () => finish(false));
    socket.once("error", () => finish(false));
  });
}

function fileStatus(value: string | null, onlineValues: string[]): ServiceStatus {
  if (!value) return "offline";
  if (onlineValues.includes(value.toUpperCase())) return "online";
  return "degraded";
}

export async function getRuntimeStatus(): Promise<CockpitStatus> {
  const [snapshot, bioSwarm, cloudAudit, ...probeResults] = await Promise.all([
    readJson("cockpit_prompt_latest.json"),
    readJson("pwa_cockpit_swarm_latest.json"),
    readJson("lady_mnemosyne_cloudbrain_audit_latest.json"),
    ...probes.map(([, , port]) => probePort(port)),
  ]);

  const now = Date.now();
  const generated = stringValue(snapshot?.generated_utc);
  const generatedMs = generated ? Date.parse(generated) : Number.NaN;
  const ageSeconds = Number.isFinite(generatedMs) ? Math.max(0, (now - generatedMs) / 1000) : null;
  const ttl = numberValue(snapshot?.ttl_seconds) ?? 8;
  const stale = ageSeconds === null || ageSeconds > ttl;
  const system = child(snapshot, "system");
  const queue = child(snapshot, "queue");
  const lastCommand = child(snapshot, "last_command");
  const bioStatus = stringValue(bioSwarm?.status);
  const cloudAuth = child(cloudAudit, "auth");
  const cloudQueue = child(cloudAudit, "queue");
  const cloudPending = numberValue(cloudQueue.pending) ?? 0;
  const cloudAuthReady = stringValue(cloudAuth.status)?.toUpperCase() === "READY";

  const totalMemory = os.totalmem();
  const freeMemory = os.freemem();
  const memoryUsedGb = Number(((totalMemory - freeMemory) / 1024 ** 3).toFixed(2));
  const memoryTotalGb = Number((totalMemory / 1024 ** 3).toFixed(2));
  const memoryPercent = Number((((totalMemory - freeMemory) / totalMemory) * 100).toFixed(1));

  const services: CockpitService[] = probes.map(([id, label, port], index) => {
    const result = probeResults[index] as { online: boolean; latencyMs: number | null };
    return {
      id,
      label,
      status: result.online ? "online" : "offline",
      detail: result.online ? `127.0.0.1:${port} responding` : `127.0.0.1:${port} unavailable`,
      latencyMs: result.latencyMs,
    };
  });

  services.push(
    {
      id: "bio-swarm",
      label: "Bio-Kinetic Swarm",
      status: fileStatus(bioStatus, ["PASS", "READY"]),
      detail: bioStatus
        ? `${bioStatus} - ${numberValue(bioSwarm?.tasks_done) ?? 0} task(s) verified`
        : "No Bio-Swarm runtime evidence",
    },
    {
      id: "cloudbrain",
      label: "Cloud Brain",
      status: cloudAuthReady ? (cloudPending > 0 ? "degraded" : "online") : "offline",
      detail: cloudAuthReady
        ? `${cloudPending} queued sync event(s); NotebookLM auth ready`
        : "Cloud Brain audit or authentication unavailable",
    },
  );

  const onlineCount = services.filter((service) => service.status === "online").length;
  const warnings: string[] = [];
  if (stale) warnings.push("Cockpit snapshot is stale; TCP probes are live but cached queue and command data may be old.");
  if (memoryPercent >= 85) warnings.push(`Memory pressure is ${memoryPercent.toFixed(1)}%.`);
  if (cloudPending > 0) warnings.push(`${cloudPending} Cloud Brain sync event(s) require Mnemosyne triage.`);

  const mode = onlineCount === 0 ? "offline" : stale || warnings.length > 0 ? "degraded" : "live";

  return {
    mode,
    source: "camelot-runtime-state+tcp-probes",
    updatedAt: new Date().toISOString(),
    stale,
    ageSeconds: ageSeconds === null ? null : Number(ageSeconds.toFixed(1)),
    telemetry: {
      cpuPercent: numberValue(system.cpu_percent),
      memoryPercent,
      memoryUsedGb,
      memoryTotalGb,
      queuePending: numberValue(queue.pending) ?? 0,
      eventLagMs: ageSeconds === null ? 0 : Math.round(ageSeconds * 1000),
      swarmCells: numberValue(bioSwarm?.cells_active) ?? 0,
    },
    services,
    lastCommand: {
      input: stringValue(lastCommand.input),
      rune: stringValue(lastCommand.rune),
      knight: stringValue(lastCommand.knight),
      status: stringValue(lastCommand.status),
      timestamp: stringValue(lastCommand.timestamp_utc),
    },
    capabilities: {
      commandExecution: runicExecutionEnabled() ? "safe-runes" : "record-only",
      voiceInput: "browser",
      cloudbrain: cloudAuthReady ? (cloudPending > 0 ? "degraded" : "live") : "offline",
      offlineShell: true,
    },
    warnings,
  };
}
