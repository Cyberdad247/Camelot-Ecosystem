import type { CockpitEvent, CockpitStatus } from "@/lib/cockpit-types";

export type CartridgeId = "command" | "factory" | "forge-law" | "intelligence" | "interphase" | "device-hall" | "mesh";

export type CartridgeManifest = {
  id: CartridgeId;
  label: string;
  shortLabel: string;
  description: string;
  lead: string;
  phaseGlyph: "[PLAN]" | "[EXECUTE]" | "[VALIDATE]" | "[COLONY]" | "[LIVE]";
  accent: "teal" | "amber" | "blue" | "coral";
  capabilities: string[];
};

export type CartridgeProps = {
  status: CockpitStatus | null;
  events: CockpitEvent[];
  onCommand: (command: string) => Promise<void>;
  onInterrupt: () => void;
  busy: boolean;
  transport: {
    state: "offline" | "connecting" | "live" | "reconnecting";
    attempt: number;
    nextRetryMs: number | null;
  };
};
