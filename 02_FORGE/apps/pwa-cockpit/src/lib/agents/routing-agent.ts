// src/lib/agents/routing-agent.ts
//
// Phase 3 RoutingAgent — edge-safe agent that wraps middleware routing
// decisions (auth + path validation). Used by the middleware to make
// agentic control decisions before the request hits the page handler.

import type { Agent, Tool } from "./types";
import { isValidBearerToken, isValidCartridgeId } from "@/lib/security/gate";

const checkAuth: Tool = {
  name: "checkAuth",
  description:
    "Validate a Bearer token format (32+ base64url chars). Returns 'authorized' or 'unauthorized'.",
  execute: async (args) => {
    const header = (args.header as string) ?? "";
    return isValidBearerToken(header) ? "authorized" : "unauthorized";
  },
};

const validatePath: Tool = {
  name: "validatePath",
  description:
    "Validate a cartridge path segment (alphanumeric + dash/underscore, 1-64 chars). Returns 'valid' or 'invalid'.",
  execute: async (args) => {
    const id = (args.id as string) ?? "";
    return isValidCartridgeId(id) ? "valid" : "invalid";
  },
};

export const routingAgent: Agent = {
  name: "RoutingAgent",
  goal:
    "Decide if a request is authorized and well-formed for the cockpit's agentic control surface.",
  tools: { checkAuth, validatePath },
};
