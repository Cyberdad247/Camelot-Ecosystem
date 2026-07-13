import type { CockpitStatus } from "./cockpit-types";

export type KnightRecommendation = {
  id: string;
  name: string;
  role: string;
  score: number;
  reason: string;
  recommendation: string;
  severity: "normal" | "attention" | "critical";
};

type Candidate = Omit<KnightRecommendation, "score" | "reason" | "recommendation" | "severity"> & {
  score: number;
  reasons: string[];
  actions: string[];
  severity: KnightRecommendation["severity"];
};

const KNIGHTS = [
  { id: "lady-mnemosyne", name: "Lady Mnemosyne", role: "Cloud Brain and memory integrity" },
  { id: "sir-link", name: "Sir Link", role: "Transport and service topology" },
  { id: "sir-helio", name: "Sir Helio", role: "Voice and audio pipeline" },
  { id: "sir-debug", name: "Sir Debug", role: "Runtime healing and resource triage" },
  { id: "sir-sentinel", name: "Sir Sentinel", role: "Security and Iron Gate policy" },
  { id: "sir-alex", name: "Sir Alex", role: "Task DAG and cognitive planning" },
  { id: "sir-forge", name: "Sir Forge", role: "Kinetic implementation" },
  { id: "sir-codex", name: "Sir Codex", role: "Full-stack architecture and verification" },
  { id: "sir-boris", name: "Sir Boris", role: "Council and swarm orchestration" },
] as const;

function candidates() {
  const roster = new Map<string, Candidate>();
  KNIGHTS.forEach((knight) => {
    roster.set(knight.id, {
      ...knight,
      score: 0,
      reasons: [],
      actions: [],
      severity: "normal",
    });
  });
  return roster;
}

function add(
  roster: ReturnType<typeof candidates>,
  id: string,
  score: number,
  reason: string,
  action: string,
  severity: KnightRecommendation["severity"] = "attention",
) {
  const knight = roster.get(id);
  if (!knight) return;
  knight.score += score;
  knight.reasons.push(reason);
  knight.actions.push(action);
  if (severity === "critical" || (severity === "attention" && knight.severity === "normal")) knight.severity = severity;
}

export function recommendKnights(status: CockpitStatus | null): KnightRecommendation[] {
  const roster = candidates();
  if (!status) {
    add(roster, "sir-alex", 80, "Runtime evidence is still loading.", "Establish a fact-bound task DAG before execution.");
    add(roster, "sir-link", 70, "No service topology is available yet.", "Verify the Cockpit transport and runtime bridge.");
  } else {
    const offline = status.services.filter((service) => service.status === "offline");
    const degraded = status.services.filter((service) => service.status === "degraded");
    const memory = status.telemetry.memoryPercent ?? 0;

    if (status.capabilities.cloudbrain !== "live") {
      add(roster, "lady-mnemosyne", 100, `Cloud Brain is ${status.capabilities.cloudbrain}.`, "Drain queued sync events and reconcile memory provenance.", "critical");
      add(roster, "sir-link", 45, "Cloud Brain transport is not fully healthy.", "Trace the NotebookLM and local-memory bridge.");
    }
    if (memory >= 85) {
      add(roster, "sir-debug", 95, `Host memory pressure is ${memory}%.`, "Identify the largest resident processes and preserve the resource guard.", "critical");
      add(roster, "sir-boris", 35, "Swarm concurrency should remain constrained.", "Limit active cells until memory pressure recovers.");
    }
    if (offline.length > 0 || degraded.length > 0) {
      add(roster, "sir-link", 85, `${offline.length} services are offline and ${degraded.length} are degraded.`, "Repair transport dependencies in blast-radius order.", offline.length >= 3 ? "critical" : "attention");
      add(roster, "sir-debug", 45, "Runtime services need failure isolation.", "Correlate service probes with recent event evidence.");
    }
    if (status.stale) {
      add(roster, "sir-alex", 75, `Cockpit evidence is stale by ${status.ageSeconds ?? "unknown"} seconds.`, "Separate live probes from cached claims before planning.");
      add(roster, "sir-sentinel", 35, "Stale evidence weakens execution confidence.", "Keep mutating runes disabled until freshness is restored.");
    }
    if (status.capabilities.commandExecution === "record-only") {
      add(roster, "sir-sentinel", 70, "Command execution is intentionally record-only.", "Audit exact rune scopes before enabling execution.");
      add(roster, "sir-forge", 30, "Implementation can proceed in a non-executing lane.", "Prepare patches and tests without widening runtime authority.", "normal");
    }
    if (status.capabilities.voiceInput !== "browser") {
      add(roster, "sir-helio", 90, "Voice input is unavailable.", "Restore microphone capability and prioritize a local ASR fallback.", "critical");
    } else {
      add(roster, "sir-helio", 40, "Voice currently depends on the browser path.", "Add measured VAD and sovereign local ASR fallback.", "normal");
    }
    if (status.telemetry.swarmCells > 0) {
      add(roster, "sir-boris", 45, `${status.telemetry.swarmCells} Bio-Kinetic cells are active.`, "Coordinate cell limits and release evidence.", "normal");
    }
    add(roster, "sir-codex", 42, "The Cockpit is in an active production-hardening cycle.", "Keep implementation, browser evidence, and architecture contracts aligned.", "normal");
    add(roster, "sir-forge", 32, "Verified recommendations need kinetic follow-through.", "Implement only council-approved changes with focused tests.", "normal");
  }

  return Array.from(roster.values())
    .filter((candidate) => candidate.score > 0)
    .sort((left, right) => right.score - left.score || left.name.localeCompare(right.name))
    .slice(0, 5)
    .map((candidate) => ({
      id: candidate.id,
      name: candidate.name,
      role: candidate.role,
      score: Math.min(100, candidate.score),
      reason: candidate.reasons.join(" "),
      recommendation: candidate.actions.join(" "),
      severity: candidate.severity,
    }));
}

export function councilPlan(recommendations: KnightRecommendation[]) {
  const council = recommendations.slice(0, 4);
  const names = council.map((knight) => knight.name).join(", ");
  const actions = council.map((knight) => knight.recommendation).join(" ");
  return `//PLAN Anya council [${names}]: ${actions}`.slice(0, 1200);
}
