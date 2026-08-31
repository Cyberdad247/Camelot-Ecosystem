/**
 * Sovereign Camelot-OS Hub Types
 * Specification for Camelot-OS vMAX OMEGA TITAN Baremetal Hub on 8GB InterServer VPS
 */

export type ServiceCategory = 
  | 'core_orchestration' 
  | 'data_memory' 
  | 'runtimes_routing' 
  | 'intelligence_tools' 
  | 'security_mesh'
  | 'cognitive_intelligence';

export type ServiceStatus = 'active' | 'booting' | 'stopped' | 'failed' | 'converged';

export interface CamelotService {
  id: string;
  name: string;
  unitName: string;
  language: 'Rust' | 'Go' | 'Java' | 'C/C++' | 'Native Bin' | 'Python' | 'TypeScript';
  category: ServiceCategory;
  allocatedRamMB: number;
  cgroupLimitMB: number;
  currentRamMB: number;
  port?: number;
  status: ServiceStatus;
  description: string;
  zeroTrustRole: string;
  systemdExec: string;
  z3Verified: boolean;
  repoUrl?: string;
}

export interface BootstrapPhase {
  id: number;
  title: string;
  subtitle: string;
  commands: string[];
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  estimatedSeconds: number;
  logs: string[];
}

export interface SovereignLaw {
  id: number;
  title: string;
  description: string;
  enforcement: string;
  status: 'ENFORCED' | 'VERIFYING' | 'BREACH';
  axiom: string;
}

export interface TerminalLog {
  id: string;
  timestamp: string;
  level: 'info' | 'warn' | 'error' | 'success' | 'sovereign' | 'command' | 'z3';
  phase?: number;
  message: string;
}

export interface AgentMission {
  id: string;
  agentId: 'sir_codex' | 'sir_galahad' | 'sir_lancelot' | 'lady_guinevere' | 'merlin' | 'sir_percival';
  agentName: string;
  agentTitle: string;
  prompt: string;
  leaseId?: string;
  leaseGranted: boolean;
  status: 'idle' | 'authorizing' | 'executing' | 'receipted' | 'rejected';
  wal2ReceiptHash?: string;
  executionMs?: number;
  resultOutput?: string;
  z3ProofStatus?: 'PROVED' | 'UNSAT' | 'TIMEOUT';
}

export interface LedgerReceipt {
  receiptId: string;
  timestamp: string;
  actor: string;
  action: string;
  hash: string;
  signature: string;
  blockHeight: number;
  r5_r6_seal: boolean;
}

export interface SystemVitals {
  targetHost: string;
  hostAlias: string;
  os: string;
  kernel: string;
  cgroups: string;
  totalRamMB: number;
  scarcityCapMB: number;
  kernelReserveMB: number;
  usedRamMB: number;
  tailscaleStatus: 'CONNECTED' | 'DISCONNECTED' | 'AUTHENTICATING';
  tailscaleIp: string;
  tailscaleTag: string;
  gideonConvergence: 'CONVERGED' | 'CHECKING' | 'DIVERGENT';
  caddyStatus: 'ONLINE' | 'RESTARTING' | 'OFFLINE';
  caddyDomain: string;
  sentinelLeaseCount: number;
  wal2LedgerTxCount: number;
  uptimeSeconds: number;
}
