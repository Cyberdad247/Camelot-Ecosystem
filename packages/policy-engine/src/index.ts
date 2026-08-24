// SPDX-License-Identifier: MIT

import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

export interface ApprovalStateGuard {
  name: string;
  condition?: string;
  failure_action?: string;
  rule?: string;
}

export interface StateConfig {
  description: string;
  timeout_seconds?: number;
  on_timeout?: string;
  required_roles?: string[];
  allowed_transitions?: string[];
  validation_guards?: ApprovalStateGuard[];
  is_terminal?: boolean;
}

export interface ApprovalStateMachineSchema {
  title: string;
  tenant_id: string;
  security_level: string;
  states: Record<string, StateConfig>;
}

export class KBAPolicyEngine {
  private schema: ApprovalStateMachineSchema;
  private currentState: string = 'IDLE';

  constructor(schemaPath?: string) {
    const defaultPath = schemaPath || path.join(__dirname, '../schemas/approval-states.yaml');
    const rawYaml = fs.readFileSync(defaultPath, 'utf8');
    this.schema = yaml.load(rawYaml) as ApprovalStateMachineSchema;
  }

  public getCurrentState(): string {
    return this.currentState;
  }

  public canTransition(targetState: string, userRoles: string[]): boolean {
    const config = this.schema.states[this.currentState];
    if (!config || !config.allowed_transitions) return false;

    if (!config.allowed_transitions.includes(targetState)) return false;

    if (config.required_roles && config.required_roles.length > 0) {
      const hasRole = config.required_roles.some((role) => userRoles.includes(role));
      if (!hasRole) return false;
    }

    return true;
  }

  public transition(targetState: string, userRoles: string[]): boolean {
    if (this.canTransition(targetState, userRoles)) {
      this.currentState = targetState;
      return true;
    }
    return false;
  }
}
