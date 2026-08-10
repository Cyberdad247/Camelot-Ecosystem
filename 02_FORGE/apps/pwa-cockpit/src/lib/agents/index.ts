// src/lib/agents/index.ts
//
// Phase 3 Agent abstraction barrel + Phase 4 agent registry.
// getAgentById() resolves a short id (e.g. "routing", "voice",
// "cartridge") to a registered Agent so the /api/agent/run route
// can look agents up by name from incoming requests. The lookup is
// case-insensitive so clients sending "Routing" or "VOICE" still
// resolve correctly.

import type { Agent } from "./types";
import { routingAgent } from "./routing-agent";
import { voiceAgent } from "./voice-agent";
import { cartridgeAgent } from "./cartridge-agent";

export * from "./types";
export * from "./orchestrator";
export { routingAgent, voiceAgent, cartridgeAgent };

const AGENT_REGISTRY: Record<string, Agent> = {
  routing: routingAgent,
  voice: voiceAgent,
  cartridge: cartridgeAgent,
};

export function getAgentById(id: string): Agent | undefined {
  if (typeof id !== "string") return undefined;
  return AGENT_REGISTRY[id.toLowerCase()];
}
