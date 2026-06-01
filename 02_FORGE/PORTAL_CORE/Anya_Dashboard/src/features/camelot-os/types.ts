export interface ArchitectureLayer {
  layer: string;
  owner: string;
  purpose: string;
  source: string;
}

export interface SchematicEdge {
  from: string;
  to: string;
  contract: string;
}

export interface MemoryTier {
  id: 'flash' | 'short' | 'long';
  label: string;
  owner: string;
  status: string;
  purpose: string;
  source: string;
  action: string;
  notebook_url?: string;
  queue_pending?: number;
  local_db?: FileState;
}

export interface FileState {
  exists: boolean;
  path: string;
  bytes?: number;
  updated?: number;
}

export interface CamelotOsState {
  status: string;
  generated_utc?: string;
  repo_root: string;
  version: string;
  summary: {
    architecture_layers: number;
    schematic_edges: number;
    active_cartridges: number;
    knights: number;
    codex_surfaces_online: number;
    cloudbrain_queue_pending: number;
  };
  orchestration: {
    layers: ArchitectureLayer[];
    edges: SchematicEdge[];
    codex_surfaces: Record<string, boolean>;
    switchboard_terminals: Array<Record<string, unknown>>;
    cartridges: {
      active_count?: number;
      names?: string[];
      source?: string;
    };
    roster: {
      count?: number;
      agents?: string[];
      source?: string;
    };
  };
  memory_tiers: MemoryTier[];
  ledgers: {
    root: FileState;
    verification: FileState;
    cloudbrain_manifest: FileState;
    codex_integration: FileState;
    knight_configuration: FileState;
    latest_root_excerpt: string;
  };
  outputs: Record<string, string>;
  frontier: FrontierState;
}

export interface FrontierNode {
  node_id: string;
  provider: string;
  surface: string;
  role: string;
  permissions: string[];
  memory_tiers: string[];
  status: string;
  last_seen_utc?: string;
}

export interface SupportSession {
  session_id: string;
  status: string;
  created_utc?: string;
  expires_utc?: string;
  duration_minutes?: number;
  reason?: string;
  portal_path?: string;
  permissions?: string[];
  revoked_utc?: string;
}

export interface FrontierState {
  schema: string;
  generated_utc: string;
  artifact_path: string;
  nodes: FrontierNode[];
  support: {
    status: string;
    active_session?: SupportSession | null;
    sessions: SupportSession[];
  };
  events: Array<Record<string, string>>;
  one_time_token?: string;
  support_url?: string;
}
