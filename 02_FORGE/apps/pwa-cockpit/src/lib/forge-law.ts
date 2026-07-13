import "server-only";

import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";

import type { ApprovalGrantBinding } from "./approval-grant";

const CAMELOT_ROOT = process.env.CAMELOT_OS_HOME
  ? path.resolve(/* turbopackIgnore: true */ process.env.CAMELOT_OS_HOME)
  : path.resolve(/* turbopackIgnore: true */ process.cwd(), "../../..");
const FORGE_ROOT = path.join(/* turbopackIgnore: true */ CAMELOT_ROOT, "03_VAULT", "runtime_state", "forge_law");

export type ForgeOperation = {
  id: string;
  type: "write_file" | "run_check" | "build" | "service_restart";
  dependsOn: string[];
  path?: string;
  argv?: string[];
};

export type ForgeCartridge = {
  id: string;
  title: string;
  digest: string;
  protocolVersion: string;
  sourceDir: string;
  createdAt: string;
  targetRoot: string;
  operations: ForgeOperation[];
  verification: string[];
  risk: { level: string; requiresOperatorApproval: boolean; serviceRestartApproval: string };
  state: string;
  stateUpdatedAt?: string;
  history: Array<{ state: string; timestampUtc: string; error?: string }>;
};

function readObject(file: string): Record<string, unknown> {
  const value: unknown = JSON.parse(readFileSync(/* turbopackIgnore: true */ file, "utf8"));
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("Forge artifact is not an object.");
  return value as Record<string, unknown>;
}

function validId(value: string) {
  return /^forge-[0-9a-f]{16}$/.test(value);
}

export function readForgeCartridge(id: string): ForgeCartridge {
  if (!validId(id)) throw new Error("Invalid Forge cartridge id.");
  const cartridge = readObject(path.join(/* turbopackIgnore: true */ FORGE_ROOT, "cartridges", `${id}.json`));
  const state = readObject(path.join(/* turbopackIgnore: true */ FORGE_ROOT, "state", `${id}.json`));
  return {
    ...(cartridge as unknown as Omit<ForgeCartridge, "state" | "history">),
    state: typeof state.state === "string" ? state.state : "drafted",
    stateUpdatedAt: typeof state.updatedAt === "string" ? state.updatedAt : undefined,
    history: Array.isArray(state.history) ? state.history as ForgeCartridge["history"] : [],
  };
}

export function listForgeCartridges() {
  const directory = path.join(/* turbopackIgnore: true */ FORGE_ROOT, "cartridges");
  try {
    return readdirSync(/* turbopackIgnore: true */ directory)
      .filter((name) => /^forge-[0-9a-f]{16}\.json$/.test(name))
      .map((name) => readForgeCartridge(name.replace(/\.json$/, "")))
      .sort((left, right) => right.createdAt.localeCompare(left.createdAt));
  } catch {
    return [];
  }
}

// Phase 1 hardening: widen the return type to ApprovalGrantBinding | null so
// downstream code (approvals/[id]/route.ts) can pass the binding straight into
// issueApprovalGrant without an `as` cast.
export function forgeApprovalBinding(command: string): ApprovalGrantBinding | null {
  const match = /^\/\/EXECUTE_PROMPT\s+(forge-[0-9a-f]{16})$/i.exec(command.trim());
  if (!match) return null;
  const cartridge = readForgeCartridge(match[1].toLowerCase());
  return { cartridgeDigest: cartridge.digest, targetRoot: cartridge.targetRoot };
}


