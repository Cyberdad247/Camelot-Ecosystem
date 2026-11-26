// SPDX-License-Identifier: MIT

import fs from 'fs';
import os from 'os';
import path from 'path';
import { describe, expect, it } from 'vitest';
import { KBAPolicyEngine } from './index.js';

describe('KBAPolicyEngine (KBA Tenant 001 HITL State Machine)', () => {
    it('loads the canonical approval-states.yaml schema at IDLE', () => {
        const engine = new KBAPolicyEngine();
        expect(engine.getCurrentState()).toBe('IDLE');
        expect(engine.getSchema().tenant_id).toBe('KBA-TENANT-001');
        expect(engine.getSchema().security_level).toBe('ZERO_TRUST_HITL_IRON_GATE');
    });

    it('completes the full human-edited HITL lifecycle with 2FA and valid diff', () => {
        const engine = new KBAPolicyEngine();

        expect(engine.transition('AWAITING_APPROVAL', ['Audit_Knight'])).toBe(true);
        expect(engine.getCurrentState()).toBe('AWAITING_APPROVAL');

        const acquireLock = engine.executeTransition('EDITING_BY_HUMAN', {
            userRoles: ['Audit_Knight'],
            trigger: 'HUMAN_ACQUIRE_LOCK',
            operatorId: 'op-audit-1',
            transactionId: 'tx-001',
            signature: 'sig-abc',
        });
        expect(acquireLock.allowed).toBe(true);
        expect(engine.getCurrentState()).toBe('EDITING_BY_HUMAN');

        const approveExec = engine.executeTransition('EXECUTING', {
            userRoles: ['Sovereign_Executive'],
            trigger: 'HUMAN_APPROVE_AND_EXECUTE',
            twoFactorVerified: true,
            proposedDiff: '{ "action": "deploy", "target": "edge" }',
            operatorId: 'op-exec-1',
            transactionId: 'tx-001',
            signature: 'sig-def',
        });
        expect(approveExec.allowed).toBe(true);
        expect(approveExec.auditRecord).toMatchObject({
            tenant_id: 'KBA-TENANT-001',
            transaction_id: 'tx-001',
            from_state: 'EDITING_BY_HUMAN',
            to_state: 'EXECUTING',
            operator_id: 'op-exec-1',
            signature: 'sig-def',
        });
        expect(engine.getCurrentState()).toBe('EXECUTING');

        expect(engine.transition('COMPLETED', ['Sovereign_Executive'])).toBe(true);
        expect(engine.getCurrentState()).toBe('COMPLETED');
    });

    it('enforces RiskScoreCheck and MemoryCeilingCheck (fail-closed) on DIRECT_SOVEREIGN_APPROVE', () => {
        const engine = new KBAPolicyEngine();
        expect(engine.transition('AWAITING_APPROVAL', ['Sovereign_Executive'])).toBe(true);

        // Missing telemetry fails closed
        const missingRisk = engine.evaluateTransition('EXECUTING', {
            userRoles: ['Sovereign_Executive'],
            trigger: 'DIRECT_SOVEREIGN_APPROVE',
        });
        expect(missingRisk.allowed).toBe(false);
        expect(missingRisk.failedGuard).toBe('RiskScoreCheck');
        expect(missingRisk.requiredAction).toBe('REQUIRE_MULTI_SIG');

        // High risk entropy fails with REQUIRE_MULTI_SIG
        const highRisk = engine.evaluateTransition('EXECUTING', {
            userRoles: ['Sovereign_Executive'],
            trigger: 'DIRECT_SOVEREIGN_APPROVE',
            riskEntropy: 82,
            nodeRamUsageMb: 4096,
        });
        expect(highRisk.allowed).toBe(false);
        expect(highRisk.failedGuard).toBe('RiskScoreCheck');
        expect(highRisk.requiredAction).toBe('REQUIRE_MULTI_SIG');

        // Exceeding 7168 MB RAM ceiling blocks execution
        const highRam = engine.evaluateTransition('EXECUTING', {
            userRoles: ['Sovereign_Executive'],
            trigger: 'DIRECT_SOVEREIGN_APPROVE',
            riskEntropy: 20,
            nodeRamUsageMb: 7400,
        });
        expect(highRam.allowed).toBe(false);
        expect(highRam.failedGuard).toBe('MemoryCeilingCheck');

        // Safe risk + safe RAM succeeds
        const safeExec = engine.executeTransition('EXECUTING', {
            userRoles: ['Sovereign_Executive'],
            trigger: 'DIRECT_SOVEREIGN_APPROVE',
            riskEntropy: 20,
            nodeRamUsageMb: 5120,
        });
        expect(safeExec.allowed).toBe(true);
        expect(engine.getCurrentState()).toBe('EXECUTING');
    });

    it('enforces RBAC and 2FA on EDITING_BY_HUMAN -> EXECUTING', () => {
        const engine = new KBAPolicyEngine();
        engine.transition('AWAITING_APPROVAL', ['Audit_Knight']);
        engine.transition('EDITING_BY_HUMAN', ['Audit_Knight']);

        // Audit_Knight cannot execute directly
        const wrongRole = engine.evaluateTransition('EXECUTING', {
            userRoles: ['Audit_Knight'],
            trigger: 'HUMAN_APPROVE_AND_EXECUTE',
            twoFactorVerified: true,
            proposedDiff: '{ "ok": true }',
        });
        expect(wrongRole.allowed).toBe(false);

        // Sovereign_Executive without 2FA is denied
        const no2fa = engine.evaluateTransition('EXECUTING', {
            userRoles: ['Sovereign_Executive'],
            trigger: 'HUMAN_APPROVE_AND_EXECUTE',
            twoFactorVerified: false,
            proposedDiff: '{ "ok": true }',
        });
        expect(no2fa.allowed).toBe(false);
        expect(no2fa.requiredAction).toBe('REQUIRE_2FA');
    });

    it('rejects raw secret exposure and malformed syntax in proposedDiff', () => {
        const engine = new KBAPolicyEngine();
        engine.transition('AWAITING_APPROVAL', ['Sovereign_Executive']);
        engine.transition('EDITING_BY_HUMAN', ['Sovereign_Executive']);

        const secretLeak = engine.evaluateTransition('AWAITING_APPROVAL', {
            userRoles: ['Sovereign_Executive'],
            trigger: 'HUMAN_SAVE_DRAFT',
            proposedDiff: 'const key = "sk-live-1234567890abcdef123456";',
        });
        expect(secretLeak.allowed).toBe(false);
        expect(secretLeak.failedGuard).toBe('NoSecretExposure');

        const badSyntax = engine.evaluateTransition('AWAITING_APPROVAL', {
            userRoles: ['Sovereign_Executive'],
            trigger: 'HUMAN_SAVE_DRAFT',
            proposedDiff: '{ "unclosed": [1, 2, 3 }',
        });
        expect(badSyntax.allowed).toBe(false);
        expect(badSyntax.failedGuard).toBe('ASTSyntaxValidator');
    });

    it('always permits safety exits (REJECTED / SUSPENDED) and requires override token to resume from SUSPENDED', () => {
        const engine = new KBAPolicyEngine();
        engine.transition('AWAITING_APPROVAL', ['Audit_Knight']);

        // Safety exit to SUSPENDED allowed even without risk/RAM telemetry
        expect(engine.transition('SUSPENDED', ['Audit_Knight'])).toBe(true);

        // Resuming to AWAITING_APPROVAL blocked without override token attestation
        const blockedResume = engine.evaluateTransition('AWAITING_APPROVAL', {
            userRoles: ['Sovereign_Executive'],
            overrideTokenProvided: false,
        });
        expect(blockedResume.allowed).toBe(false);
        expect(blockedResume.requiredAction).toBe('PROVIDE_OPERATOR_OVERRIDE_TOKEN');

        // Resuming with override token succeeds
        const allowedResume = engine.executeTransition('AWAITING_APPROVAL', {
            userRoles: ['Sovereign_Executive'],
            overrideTokenProvided: true,
        });
        expect(allowedResume.allowed).toBe(true);
        expect(engine.getCurrentState()).toBe('AWAITING_APPROVAL');
    });

    it('enforces state timeout escalation and terminal state immutability', () => {
        const engine = new KBAPolicyEngine();
        engine.transition('AWAITING_APPROVAL', ['Sovereign_Executive']);

        const timedOut = engine.evaluateTransition('EXECUTING', {
            userRoles: ['Sovereign_Executive'],
            elapsedSeconds: 1801,
            riskEntropy: 10,
            nodeRamUsageMb: 4000,
        });
        expect(timedOut.allowed).toBe(false);
        expect(timedOut.requiredAction).toBe('ESCALATE_TO_SOVEREIGN');

        // Reject moves into terminal state REJECTED
        expect(engine.transition('REJECTED', ['Sovereign_Executive'])).toBe(true);
        const fromTerminal = engine.evaluateTransition('AWAITING_APPROVAL', {
            userRoles: ['Sovereign_Executive'],
        });
        expect(fromTerminal.allowed).toBe(false);
    });

    it('appends structured JSONL audit records to disk', () => {
        const engine = new KBAPolicyEngine();
        const result = engine.executeTransition('AWAITING_APPROVAL', {
            userRoles: ['Sovereign_Executive'],
            operatorId: 'king-arthur',
            transactionId: 'tx-audit-99',
            signature: 'sig-999',
        });
        expect(result.allowed).toBe(true);
        expect(result.auditRecord).toBeDefined();

        const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'camelot-policy-audit-'));
        const auditFile = path.join(tmpDir, 'hitl_audit_ledger.jsonl');
        try {
            engine.appendAuditRecord(result.auditRecord!, auditFile);
            const lines = fs.readFileSync(auditFile, 'utf8').trim().split('\n');
            expect(lines).toHaveLength(1);
            const parsed = JSON.parse(lines[0]);
            expect(parsed).toMatchObject({
                tenant_id: 'KBA-TENANT-001',
                transaction_id: 'tx-audit-99',
                from_state: 'IDLE',
                to_state: 'AWAITING_APPROVAL',
                operator_id: 'king-arthur',
                signature: 'sig-999',
            });
            expect(typeof parsed.timestamp).toBe('string');
        } finally {
            fs.rmSync(tmpDir, { recursive: true, force: true });
        }
    });
});
