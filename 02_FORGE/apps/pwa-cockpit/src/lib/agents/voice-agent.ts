// src/lib/agents/voice-agent.ts
//
// Phase 3 VoiceAgent — stub for Phase 5 (Kickbox-audio BifrostContext
// integration). The pwa-cockpit does not have actual voice code; this
// stub documents the intended goal and tools so the orchestrator can
// be exercised end-to-end with a mock LLM.

import type { Agent } from "./types";

export const voiceAgent: Agent = {
  name: "VoiceAgent",
  goal:
    "Transcribe speech and dispatch a command. (Phase 5 — Kickbox-audio BifrostContext integration not yet wired.)",
  tools: {},
};
