import "server-only";

import { execFile } from "node:child_process";
import path from "node:path";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
const CAMELOT_ROOT = process.env.CAMELOT_OS_HOME
  ? path.resolve(/* turbopackIgnore: true */ process.env.CAMELOT_OS_HOME)
  : path.resolve(/* turbopackIgnore: true */ process.cwd(), "../../..");
const CAMELOT_BINARY = path.join(/* turbopackIgnore: true */ CAMELOT_ROOT, ".venv", "Scripts", "camelot.exe");

export type RunicExecution = {
  executed: boolean;
  status: "disabled" | "blocked" | "complete" | "failed";
  result?: Record<string, unknown>;
  error?: string;
};

export function runicExecutionEnabled() {
  return process.env.CAMELOT_COCKPIT_EXEC_ENABLED === "true" && allowedRunes().size > 0;
}

function normalizeDirective(value: string) {
  if (value.startsWith("//")) return value.toUpperCase();
  if (value.toLowerCase().startsWith("omega_")) return `Omega_${value.slice(6).toUpperCase()}`;
  return value;
}

export function allowedRunes() {
  return new Set(
    (process.env.CAMELOT_COCKPIT_ALLOWED_RUNES ?? "")
      .split(",")
      .map((value) => normalizeDirective(value.trim()))
      .filter((value) => value.startsWith("//") || value.startsWith("Omega_")),
  );
}

function parseJsonEnvelope(stdout: string) {
  const cleaned = stdout.replace(/\u001b\[[0-9;]*m/g, "");
  const start = cleaned.indexOf("{");
  const end = cleaned.lastIndexOf("}");
  if (start < 0 || end <= start) throw new Error("Camelot CLI returned no JSON envelope");
  const value: unknown = JSON.parse(cleaned.slice(start, end + 1));
  if (typeof value !== "object" || value === null || Array.isArray(value)) throw new Error("Camelot CLI JSON was not an object");
  return value as Record<string, unknown>;
}

export async function executeRunic(command: string, approvalGrant: string): Promise<RunicExecution> {
  if (process.env.CAMELOT_COCKPIT_EXEC_ENABLED !== "true") {
    return { executed: false, status: "disabled" };
  }

  const directive = normalizeDirective(command.trim().split(/\s+/)[0] ?? "");
  if (!allowedRunes().has(directive)) {
    return { executed: false, status: "blocked", error: `${directive || "Command"} is not in CAMELOT_COCKPIT_ALLOWED_RUNES.` };
  }

  try {
    const { stdout } = await execFileAsync(CAMELOT_BINARY, ["--json", "cockpit", "exec", command], {
      cwd: CAMELOT_ROOT,
      encoding: "utf8",
      env: {
        ...process.env,
        CAMELOT_COCKPIT_APPROVAL_GRANT: approvalGrant,
        CAMELOT_COCKPIT_REQUIRE_APPROVAL_GRANT: "true",
      },
      timeout: 30_000,
      windowsHide: true,
      maxBuffer: 1024 * 1024,
    });
    const result = parseJsonEnvelope(stdout);
    if (result.status !== "ROUTED" || result.routed !== true || result.queued !== true) {
      return {
        executed: true,
        status: "failed",
        result,
        error: `Camelot rejected or failed to queue ${directive}.`,
      };
    }
    return { executed: true, status: "complete", result };
  } catch (error) {
    return {
      executed: true,
      status: "failed",
      error: error instanceof Error ? error.message : String(error),
    };
  }
}
