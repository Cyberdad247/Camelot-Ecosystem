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
    lock_owner_required?: boolean;
    lock_timeout_seconds?: number;
    execution_timeout_seconds?: number;
    required_roles?: string[];
    requires_override_token?: string;
    allowed_transitions?: string[];
    validation_guards?: ApprovalStateGuard[];
    hooks?: {
        on_enter?: string;
        on_exit?: string;
    };
    is_terminal?: boolean;
}

export interface TransitionMatrixRule {
    from: string;
    to: string;
    trigger: string;
    rbac?: string[];
    requires_2fa?: boolean;
    guard?: string;
}

export interface AuditLoggingConfig {
    destination: string;
    include_fields: string[];
}

export interface ApprovalStateMachineSchema {
    title: string;
    tenant_id: string;
    security_level: string;
    states: Record<string, StateConfig>;
    transitions_matrix?: TransitionMatrixRule[];
    audit_logging?: AuditLoggingConfig;
}

export interface TransitionContext {
    userRoles: string[];
    trigger?: string;
    twoFactorVerified?: boolean;
    riskEntropy?: number;
    nodeRamUsageMb?: number;
    proposedDiff?: string;
    overrideTokenProvided?: boolean;
    elapsedSeconds?: number;
    operatorId?: string;
    transactionId?: string;
    signature?: string;
    astValidator?: (diff: string) => boolean;
}

export interface HitlAuditRecord {
    tenant_id: string;
    transaction_id: string;
    from_state: string;
    to_state: string;
    operator_id: string;
    timestamp: string;
    signature: string;
}

export interface TransitionResult {
    allowed: boolean;
    fromState: string;
    toState: string;
    reason: string;
    requiredAction?: string;
    failedGuard?: string;
    auditRecord?: HitlAuditRecord;
}

const SAFETY_BYPASS_TARGETS = new Set([
    'REJECTED',
    'CANCELLED',
    'SUSPENDED',
    'ROLLBACK_IN_PROGRESS',
    'ROLLED_BACK',
    'CRITICAL_HALT',
]);

const SECRET_PATTERNS: RegExp[] = [
    /-----BEGIN\s+[A-Z0-9 ]*PRIVATE KEY-----/,
    /\bsk-[A-Za-z0-9_-]{16,}\b/,
    /\bghp_[A-Za-z0-9]{20,}\b/,
    /\bAKIA[0-9A-Z]{16}\b/,
    /\bBearer\s+[A-Za-z0-9._-]{20,}\b/i,
    /\b(?:api[_-]?key|secret[_-]?key|password|token)\s*[:=]\s*['"]?[A-Za-z0-9._-]{12,}['"]?/i,
];

function containsRawSecret(diff: string): boolean {
    return SECRET_PATTERNS.some((pattern) => pattern.test(diff));
}

function defaultAstSyntaxValidator(diff: string): boolean {
    const trimmed = diff.trim();
    if (trimmed.length === 0) {
        return false;
    }
    const pairs: Record<string, string> = { '{': '}', '[': ']', '(': ')' };
    const closers = new Set(Object.values(pairs));
    const stack: string[] = [];
    for (const ch of trimmed) {
        if (pairs[ch]) {
            stack.push(pairs[ch]);
        } else if (closers.has(ch)) {
            if (stack.pop() !== ch) {
                return false;
            }
        }
    }
    return stack.length === 0;
}

export class KBAPolicyEngine {
    private schema: ApprovalStateMachineSchema;
    private currentState: string = 'IDLE';

    constructor(schemaPath?: string) {
        const defaultPath = schemaPath || path.join(__dirname, '../schemas/approval-states.yaml');
        const rawYaml = fs.readFileSync(defaultPath, 'utf8');
        this.schema = yaml.load(rawYaml) as ApprovalStateMachineSchema;
    }

    public getSchema(): ApprovalStateMachineSchema {
        return this.schema;
    }

    public getCurrentState(): string {
        return this.currentState;
    }

    private findMatrixRule(from: string, to: string, trigger?: string): TransitionMatrixRule | undefined {
        const rules = this.schema.transitions_matrix || [];
        if (trigger) {
            const exact = rules.find((r) => r.from === from && r.to === to && r.trigger === trigger);
            if (exact) return exact;
        }
        return rules.find((r) => r.from === from && r.to === to);
    }

    private evaluateGuard(
        guard: ApprovalStateGuard,
        context: TransitionContext,
    ): { ok: boolean; reason: string; requiredAction?: string } {
        switch (guard.name) {
            case 'RiskScoreCheck': {
                if (typeof context.riskEntropy !== 'number' || Number.isNaN(context.riskEntropy)) {
                    return {
                        ok: false,
                        reason: 'RiskScoreCheck failed: riskEntropy is required (fail-closed).',
                        requiredAction: guard.failure_action || 'REQUIRE_MULTI_SIG',
                    };
                }
                if (context.riskEntropy >= 75) {
                    return {
                        ok: false,
                        reason: `RiskScoreCheck failed: riskEntropy ${context.riskEntropy} >= 75.`,
                        requiredAction: guard.failure_action || 'REQUIRE_MULTI_SIG',
                    };
                }
                return { ok: true, reason: 'RiskScoreCheck passed.' };
            }

            case 'MemoryCeilingCheck': {
                if (typeof context.nodeRamUsageMb !== 'number' || Number.isNaN(context.nodeRamUsageMb)) {
                    return {
                        ok: false,
                        reason: 'MemoryCeilingCheck failed: nodeRamUsageMb is required (fail-closed).',
                        requiredAction: 'TRIM_MEMORY_BELOW_7168MB',
                    };
                }
                if (context.nodeRamUsageMb >= 7168) {
                    return {
                        ok: false,
                        reason: `MemoryCeilingCheck failed: RAM usage ${context.nodeRamUsageMb} MB >= 7168 MB ceiling.`,
                        requiredAction: 'TRIM_MEMORY_BELOW_7168MB',
                    };
                }
                return { ok: true, reason: 'MemoryCeilingCheck passed.' };
            }

            case 'NoSecretExposure': {
                if (typeof context.proposedDiff !== 'string') {
                    return {
                        ok: false,
                        reason: 'NoSecretExposure failed: proposedDiff is required (fail-closed).',
                        requiredAction: 'PROVIDE_SANITIZED_DIFF',
                    };
                }
                if (containsRawSecret(context.proposedDiff)) {
                    return {
                        ok: false,
                        reason: 'NoSecretExposure failed: raw secret material detected in proposedDiff.',
                        requiredAction: 'REDACT_SECRETS',
                    };
                }
                return { ok: true, reason: 'NoSecretExposure passed.' };
            }

            case 'ASTSyntaxValidator': {
                if (typeof context.proposedDiff !== 'string') {
                    return {
                        ok: false,
                        reason: 'ASTSyntaxValidator failed: proposedDiff is required (fail-closed).',
                        requiredAction: 'FIX_DIFF_SYNTAX',
                    };
                }
                const validator = context.astValidator || defaultAstSyntaxValidator;
                if (!validator(context.proposedDiff)) {
                    return {
                        ok: false,
                        reason: 'ASTSyntaxValidator failed: proposedDiff failed syntax validation.',
                        requiredAction: 'FIX_DIFF_SYNTAX',
                    };
                }
                return { ok: true, reason: 'ASTSyntaxValidator passed.' };
            }

            default:
                return {
                    ok: false,
                    reason: `Unknown guard '${guard.name}' rejected (fail-closed).`,
                    requiredAction: guard.failure_action || 'MANUAL_REVIEW',
                };
        }
    }

    private buildAuditRecord(fromState: string, toState: string, context: TransitionContext): HitlAuditRecord {
        return {
            tenant_id: this.schema.tenant_id,
            transaction_id: context.transactionId || 'UNASSIGNED_TX',
            from_state: fromState,
            to_state: toState,
            operator_id: context.operatorId || 'UNKNOWN_OPERATOR',
            timestamp: new Date().toISOString(),
            signature: context.signature || 'UNSIGNED',
        };
    }

    public evaluateTransition(targetState: string, context: TransitionContext): TransitionResult {
        const fromState = this.currentState;
        const config = this.schema.states[fromState];

        if (!config) {
            return {
                allowed: false,
                fromState,
                toState: targetState,
                reason: `Current state '${fromState}' is not defined in schema.`,
            };
        }

        if (config.is_terminal) {
            return {
                allowed: false,
                fromState,
                toState: targetState,
                reason: `State '${fromState}' is terminal and cannot transition.`,
            };
        }

        if (!config.allowed_transitions || !config.allowed_transitions.includes(targetState)) {
            return {
                allowed: false,
                fromState,
                toState: targetState,
                reason: `Transition '${fromState}' -> '${targetState}' is not permitted.`,
            };
        }

        const isSafetyBypass = SAFETY_BYPASS_TARGETS.has(targetState);

        // Enforce timeout on active states for forward transitions
        if (
            !isSafetyBypass &&
            typeof context.elapsedSeconds === 'number' &&
            typeof config.timeout_seconds === 'number' &&
            context.elapsedSeconds > config.timeout_seconds
        ) {
            return {
                allowed: false,
                fromState,
                toState: targetState,
                reason: `State '${fromState}' exceeded timeout (${context.elapsedSeconds}s > ${config.timeout_seconds}s).`,
                requiredAction: config.on_timeout || 'TIMEOUT_EXCEEDED',
            };
        }

        // Enforce state-level required roles
        if (config.required_roles && config.required_roles.length > 0) {
            const hasRole = config.required_roles.some((role) => context.userRoles.includes(role));
            if (!hasRole) {
                return {
                    allowed: false,
                    fromState,
                    toState: targetState,
                    reason: `RBAC denied: requires one of [${config.required_roles.join(', ')}].`,
                };
            }
        }

        // Enforce override token attestation when resuming out of SUSPENDED
        if (config.requires_override_token && !isSafetyBypass && !context.overrideTokenProvided) {
            return {
                allowed: false,
                fromState,
                toState: targetState,
                reason: `Override token attestation (${config.requires_override_token}) required to resume from '${fromState}'.`,
                requiredAction: 'PROVIDE_OPERATOR_OVERRIDE_TOKEN',
            };
        }

        // Enforce transitions_matrix edge rules (RBAC, 2FA, edge guard)
        const matrixRule = this.findMatrixRule(fromState, targetState, context.trigger);
        if (matrixRule) {
            if (matrixRule.rbac && matrixRule.rbac.length > 0) {
                const hasMatrixRole = matrixRule.rbac.some((role) => context.userRoles.includes(role));
                if (!hasMatrixRole) {
                    return {
                        allowed: false,
                        fromState,
                        toState: targetState,
                        reason: `Transition '${matrixRule.trigger}' requires role in [${matrixRule.rbac.join(', ')}].`,
                    };
                }
            }

            if (matrixRule.requires_2fa && !context.twoFactorVerified) {
                return {
                    allowed: false,
                    fromState,
                    toState: targetState,
                    reason: `Transition '${matrixRule.trigger}' requires 2FA verification.`,
                    requiredAction: 'REQUIRE_2FA',
                };
            }
        }

        // Enforce validation_guards on forward transitions (e.g., to EXECUTING or saving human edits)
        if (!isSafetyBypass && config.validation_guards && config.validation_guards.length > 0) {
            const shouldEvaluateStateGuards =
                targetState === 'EXECUTING' || fromState === 'EDITING_BY_HUMAN';

            if (shouldEvaluateStateGuards) {
                for (const guard of config.validation_guards) {
                    const check = this.evaluateGuard(guard, context);
                    if (!check.ok) {
                        return {
                            allowed: false,
                            fromState,
                            toState: targetState,
                            reason: check.reason,
                            requiredAction: check.requiredAction,
                            failedGuard: guard.name,
                        };
                    }
                }
            }
        }

        // Enforce explicit edge guard from transitions_matrix if not already covered above
        if (!isSafetyBypass && matrixRule?.guard) {
            const matchingGuard =
                config.validation_guards?.find((g) => g.name === matrixRule.guard) || {
                    name: matrixRule.guard,
                };
            const check = this.evaluateGuard(matchingGuard, context);
            if (!check.ok) {
                return {
                    allowed: false,
                    fromState,
                    toState: targetState,
                    reason: check.reason,
                    requiredAction: check.requiredAction,
                    failedGuard: matchingGuard.name,
                };
            }
        }

        return {
            allowed: true,
            fromState,
            toState: targetState,
            reason: `Transition '${fromState}' -> '${targetState}' approved.`,
            auditRecord: this.buildAuditRecord(fromState, targetState, context),
        };
    }

    public canTransition(
        targetState: string,
        userRoles: string[],
        context?: Omit<TransitionContext, 'userRoles'>,
    ): boolean {
        return this.evaluateTransition(targetState, { ...context, userRoles }).allowed;
    }

    public transition(
        targetState: string,
        userRoles: string[],
        context?: Omit<TransitionContext, 'userRoles'>,
    ): boolean {
        const result = this.evaluateTransition(targetState, { ...context, userRoles });
        if (result.allowed) {
            this.currentState = targetState;
            return true;
        }
        return false;
    }

    public executeTransition(targetState: string, context: TransitionContext): TransitionResult {
        const result = this.evaluateTransition(targetState, context);
        if (result.allowed) {
            this.currentState = targetState;
        }
        return result;
    }

    public appendAuditRecord(record: HitlAuditRecord, auditPath?: string): string {
        const targetPath =
            auditPath ||
            this.schema.audit_logging?.destination ||
            '03_VAULT/runtime_state/hitl_audit_ledger.jsonl';
        fs.mkdirSync(path.dirname(targetPath), { recursive: true });
        fs.appendFileSync(targetPath, `${JSON.stringify(record)}\n`, 'utf8');
        return targetPath;
    }
}
