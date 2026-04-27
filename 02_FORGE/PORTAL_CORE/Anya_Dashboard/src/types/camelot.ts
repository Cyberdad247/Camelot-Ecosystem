import type { ElementType } from 'react';

export type CartridgeId =
  | 'COGNITIVE'
  | 'ENGINEER'
  | 'RESEARCH'
  | 'CREATIVE'
  | 'MARKETING'
  | 'LEGAL'
  | 'BRAINSTORM'
  | 'CRITICAL_THINKING';

export interface CartridgeMeta {
  id: CartridgeId;
  slug: string;
  label: string;
  knight: string;
  color: string;
  accentHex: string;
  borderClass: string;
  bgClass: string;
  textClass: string;
  icon: ElementType;
  description: string;
}

export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'failed';
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';

export interface CamelotTask {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  cartridge: CartridgeId;
  knight: string;
  created_at: number;
  updated_at: number;
  result?: string;
  dispatch_id?: string;
}

export interface DispatchRequest {
  intent: string;
  cartridge: CartridgeId;
  preferred_knight?: string;
  execution_target?: string;
  params?: Record<string, unknown>;
}

export interface DispatchResponse {
  status: string;
  dispatch_id: string;
  knight: string;
  cost: string;
  result?: string;
}

export interface ServiceHealth {
  name: string;
  label: string;
  port: number;
  healthUrl: string;
  status: 'live' | 'dark' | 'checking';
  latency_ms?: number;
  last_checked?: number;
}
