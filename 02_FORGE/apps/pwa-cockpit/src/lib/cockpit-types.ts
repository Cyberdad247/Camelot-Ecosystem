export type CockpitMode = "live" | "degraded" | "offline";
export type ServiceStatus = "online" | "degraded" | "offline";
export type ApprovalStatus = "pending" | "approved" | "rejected";

export type CockpitService = {
  id: string;
  label: string;
  status: ServiceStatus;
  detail: string;
  latencyMs?: number | null;
};

export type CockpitEvent = {
  id: string;
  ts: string;
  level: "info" | "warn" | "error";
  source: string;
  message: string;
};

export type CockpitStatus = {
  mode: CockpitMode;
  source: string;
  updatedAt: string;
  stale: boolean;
  ageSeconds: number | null;
  telemetry: {
    cpuPercent: number | null;
    memoryPercent: number | null;
    memoryUsedGb: number | null;
    memoryTotalGb: number | null;
    queuePending: number;
    eventLagMs: number;
    swarmCells: number;
  };
  services: CockpitService[];
  lastCommand: {
    input?: string | null;
    rune?: string | null;
    knight?: string | null;
    status?: string | null;
    timestamp?: string | null;
  };
  capabilities: {
    commandExecution: "record-only" | "safe-runes" | "enabled";
    voiceInput: "browser" | "unavailable";
    cloudbrain: "live" | "degraded" | "offline";
    offlineShell: boolean;
  };
  warnings: string[];
};

export type Approval = {
  id: string;
  command: string;
  reason: string;
  status: ApprovalStatus;
  createdAt: string;
  resolvedAt?: string;
};

export type CommandReceipt = {
  id: string;
  command: string;
  status: "accepted" | "requires_approval" | "approved" | "rejected" | "execution_blocked" | "executed" | "failed";
  createdAt: string;
};

export type CommandResponse = {
  accepted: boolean;
  message: string;
  receiptId?: string;
  approvalId?: string;
};
