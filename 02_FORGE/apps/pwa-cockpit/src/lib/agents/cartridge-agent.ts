// src/lib/agents/cartridge-agent.ts
//
// Phase 3 CartridgeAgent — metadata-only agent. The V2 verify path
// (verifyV2Archive, Ed25519) is nodejs-only because
// @/cartridges/registry transitively imports React. This agent exposes
// the V1 cartridge list edge-safely (hardcoded to match trustedLoaders
// keys; kept in sync via the cartridge-list test in v2.test.mjs) and
// documents the nodejs-only verify constraint.

import type { Agent, Tool } from "./types";

// Hardcoded V1 cartridge ids. MUST match the keys of `trustedLoaders` in
// src/cartridges/registry.tsx. The v2.test.mjs cartridge-list test
// fails if these drift.
const V1_CARTRIDGE_IDS: readonly string[] = [
  "command",
  "factory",
  "forge-law",
  "intelligence",
  "interphase",
  "device-hall",
  "mesh",
];

const listCartridges: Tool = {
  name: "listCartridges",
  description: "List the registered V1 cartridge ids. Returns a JSON array of strings.",
  execute: async () => JSON.stringify(V1_CARTRIDGE_IDS),
};

const getCartridgeVerifyHint: Tool = {
  name: "getCartridgeVerifyHint",
  description:
    "Return a hint that V2 archive verification requires the nodejs runtime. Always returns the same JSON.",
  execute: async () =>
    JSON.stringify({
      runtime: "nodejs",
      endpoint: "/api/agent/verify",
      reason:
        "V2 platform transitively imports React via @/cartridges/registry; edge runtime cannot load it",
    }),
};

export const cartridgeAgent: Agent = {
  name: "CartridgeAgent",
  goal:
    "List registered V1 cartridges and route V2 archive verification to the nodejs runtime.",
  tools: { listCartridges, getCartridgeVerifyHint },
};
