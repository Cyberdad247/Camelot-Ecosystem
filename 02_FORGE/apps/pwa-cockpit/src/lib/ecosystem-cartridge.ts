export type CartridgeState = "implemented" | "degraded" | "planned" | "offline";

export type EcosystemComponent = {
  id: string;
  name: string;
  role: string;
  state: CartridgeState;
  detail: string;
};

export type EcosystemLaw = {
  id: string;
  name: string;
  rule: string;
};

export type EcosystemWorkflow = {
  id: string;
  name: string;
  chain: string[];
  state: CartridgeState;
};

export type KnightAssignment = {
  knight: string;
  task: string;
};

export const ecosystemCartridge = {
  id: "PWA_ECOSYSTEM_CARTRIDGE_vMAX",
  title: "PWA Ecosystem Cartridge vMAX",
  source: "03_VAULT/UKG/PWA_ECOSYSTEM_CARTRIDGE_vMAX.toon",
  visualLanguage: {
    base: "Obsidian shell",
    panels: "Smoke glass operational panels",
    accentPrimary: "Kickbox gold active indicators",
    accentSecondary: "Violet agent and Bifrost accents",
    tone: "Sovereign executive intelligence",
  },
  components: [
    {
      id: "pwa-cockpit",
      name: "PWA Cockpit",
      role: "Installable agentic OS shell",
      state: "implemented",
      detail: "Next.js 16 shell with status, events, commands, approvals, and PWA metadata.",
    },
    {
      id: "control-plane-api",
      name: "Control Plane API",
      role: "Server-backed command surface",
      state: "implemented",
      detail: "/api/status, /api/events, /api/commands, and /api/approvals are present.",
    },
    {
      id: "titanlink",
      name: "TitanLink Adapter",
      role: "Future Bifrost WebSocket transport",
      state: "planned",
      detail: "The shell uses authenticated same-origin SSE today; a typed WebSocket client exists but is not mounted.",
    },
    {
      id: "kickbox-audio",
      name: "Kickbox Audio Adapter",
      role: "Future voice/audio service adapter",
      state: "planned",
      detail: "Anya currently uses browser speech recognition and synthesis; no Kickbox service binding is claimed.",
    },
    {
      id: "cloudbrain",
      name: "Cloud Brain Status Adapter",
      role: "NotebookLM and sync health observation",
      state: "implemented",
      detail: "Reads Camelot's Cloud Brain audit state and exposes truthful live, degraded, or offline status.",
    },
    {
      id: "uiux-swarm",
      name: "UI/UX Swarm",
      role: "Bio-Kinetic verification and design provenance",
      state: "implemented",
      detail: "The interface uses the approved UI/UX guidance and observes verified Bio-Swarm release state.",
    },
  ] satisfies EcosystemComponent[],
  laws: [
    {
      id: "truth-labeling",
      name: "Truth Labeling",
      rule: "Never claim live state without API, event, file, or route evidence.",
    },
    {
      id: "approval-gate",
      name: "Approval Gate",
      rule: "Dangerous commands must route through /api/approvals before execution.",
    },
    {
      id: "cloudbrain-sync",
      name: "Cloudbrain Sync",
      rule: "Sync only after local verification; show queue fallback as degraded.",
    },
    {
      id: "kickbox-boundary",
      name: "Kickbox Boundary",
      rule: "Extract vibe and service contracts first; do not copy the full app into Cockpit.",
    },
  ] satisfies EcosystemLaw[],
  workflows: [
    {
      id: "swarm-optimize",
      name: "Swarm Optimize",
      chain: ["Anya compresses", "Knights critique", "Cloudbrain recalls", "Cockpit renders"],
      state: "implemented",
    },
    {
      id: "command-execute",
      name: "Command Execute",
      chain: ["/api/commands", "classify danger", "/api/approvals", "receipt in event log"],
      state: "implemented",
    },
    {
      id: "bifrost-orchestration",
      name: "Bifrost Orchestration",
      chain: ["TitanLink connect", "validate events", "render status", "HITL before mutation"],
      state: "planned",
    },
    {
      id: "kickbox-audio",
      name: "Kickbox Audio",
      chain: ["Bifrost health", "voice/audio status", "command adapter", "HITL-gated actions"],
      state: "planned",
    },
    {
      id: "uiux-release",
      name: "UIUX Release",
      chain: ["Build [Test]", "Visual Check [Responsive A11y]", "Cloudbrain Sync [Approved]"],
      state: "implemented",
    },
  ] satisfies EcosystemWorkflow[],
};

export const anyaSwarmPrompt = {
  objective:
    "Optimize PWA Cockpit into the structural agentic OS shell for Camelot-OS using Cloudbrain, Mastering Professional UI/UX, and the knight roster.",
  sourceMaterial: [
    "03_VAULT/training/configs/cartridges/uiux-cloudbrain-sync.yaml",
    "UI_UX_ARCHITECTURE.md",
    "engineering-uiux-pro-max skill",
    "PWA Cockpit APIs",
    "Digital Factory router policy",
    "Kickbox-audio local checkout",
  ],
  assignments: [
    { knight: "Anya", task: "Compress objective and route the swarm." },
    { knight: "Sir Visage", task: "Critique visual direction and Kickbox vibe alignment." },
    { knight: "Sir Stitch", task: "Check responsive layout, accessibility, and assembly." },
    { knight: "Sir Syntax", task: "Enforce TypeScript, Next.js, and schema discipline." },
    { knight: "Sir ForgeMaster", task: "Shape workflow DAGs and orchestration." },
    { knight: "Sir Alchemist", task: "Simplify, optimize, and remove excess surface area." },
    { knight: "Baron Vaelen", task: "Harden delivery, verification, and CI gates." },
    { knight: "Sir Link", task: "Validate bridge and adapter handoff boundaries." },
    { knight: "Sir Codex", task: "Review implementation safety and regression risk." },
  ] satisfies KnightAssignment[],
  hitlRequired: [
    "Executing generated code",
    "Deploying or publishing",
    "Mutating ledgers",
    "Running Cloudbrain sync",
    "Binding live Kickbox or Bifrost commands",
  ],
};

export function stateLabel(state: CartridgeState) {
  return state.toUpperCase();
}
