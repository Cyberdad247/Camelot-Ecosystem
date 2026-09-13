// SPDX-License-Identifier: MIT

'use client';

import { useState } from 'react';
import { submitDecision, type DecisionResponse } from '../../lib/operator_console/operator-api';
import type { EffectManifest } from '../../lib/operator_console/schemas';
import { EffectManifestDialog } from './EffectManifestDialog';
import { ApprovalConfirmationDialog } from './ApprovalConfirmationDialog';

export function ApprovalPanel({ approval, taskId, forceDisabled = false }: {
  approval: Record<string, unknown>;
  taskId: string;
  forceDisabled?: boolean;
}) {
  const [pendingDecision, setPendingDecision] = useState<'approve' | 'deny' | null>(null);
  const [outcome, setOutcome] = useState<DecisionResponse | null>(null);

  const state = String(approval.state ?? 'APPROVAL_REQUIRED');
  const suspended = state === 'APPROVAL_SUSPENDED' || state === 'AUDIT_SUSPENDED';
  const policyBlocked = state === 'POLICY_BLOCKED';
  const disabled = suspended || policyBlocked || forceDisabled;

  // Dynamic manifest surfaced by the BFF/snapshot, falling back to the default fixture manifest.
  const rawManifest = (approval.manifest ?? {}) as Partial<EffectManifest>;
  const manifest: EffectManifest = {
    schemaVersion: 'effect-manifest/1',
    manifestId: rawManifest.manifestId ?? 'eff_01J',
    taskId,
    correlationId: rawManifest.correlationId ?? `cor_${taskId}`,
    kind: rawManifest.kind ?? 'worktree.patch.promote',
    baseRevision: rawManifest.baseRevision ?? 'base',
    candidateRevision: rawManifest.candidateRevision ?? 'cand',
    diffSha256: rawManifest.diffSha256 ?? 'sha256:abc',
    allowedPaths: rawManifest.allowedPaths ?? ['apps/pwa/src/components/operator_console/**'],
    requiredEvidence: rawManifest.requiredEvidence ?? ['receipt://vfs/no-escape/1'],
    policyClass: rawManifest.policyClass ?? 'engineering.write',
    expiresAt: rawManifest.expiresAt ?? new Date(Date.now() + 60_000).toISOString(),
    oneTimeNonce: rawManifest.oneTimeNonce ?? 'nonce_fixture',
    effectClass: rawManifest.effectClass ?? 'workspace.patch',
    declaredRiskTier: rawManifest.declaredRiskTier ?? 'T1',
    declarationHash: rawManifest.declarationHash ?? 'sha256:fixture_decl_hash',
  };

  const runDecision = async (decision: 'approve' | 'deny', reason?: string) => {
    try {
      const res = await submitDecision(manifest.manifestId, decision, reason);
      setOutcome(res);
    } catch (err) {
      setOutcome({ status: 'BLOCKED', manifestId: manifest.manifestId, reasons: [String(err)] });
    }
    setPendingDecision(null);
  };

  if (suspended) {
    return (
      <div className="border border-amber-300/40 p-3" role="alert">
        <p className="font-mono text-[11px] uppercase tracking-widest text-amber-200">
          {state === 'APPROVAL_SUSPENDED' ? 'Approval suspended — Sentinel unavailable' : 'Audit suspended — Gideon unavailable'}
        </p>
        <p className="mt-1 text-[11px] text-white/50">Existing manifests remain readable. Approve/deny is disabled.</p>
      </div>
    );
  }

  if (policyBlocked) {
    return (
      <div className="border border-red-400/50 p-3" role="alert">
        <p className="font-mono text-[11px] uppercase tracking-widest text-red-300">Policy blocked</p>
        <p className="mt-1 text-[11px] text-white/50">This effect is blocked by policy. No approval path exists.</p>
      </div>
    );
  }

  if (outcome?.status === 'APPROVED') {
    return (
      <div className="border border-emerald-400/50 p-3">
        <p className="font-mono text-[11px] uppercase tracking-widest text-emerald-300">Approved</p>
        <p className="mt-1 text-[11px] text-white/60">Lease {outcome.lease?.leaseId} issued. Effect eligible to run.</p>
      </div>
    );
  }

  if (outcome?.status === 'DENIED') {
    return (
      <div className="border border-red-400/50 p-3">
        <p className="font-mono text-[11px] uppercase tracking-widest text-red-300">Denied</p>
        <p className="mt-1 text-[11px] text-white/60">No lease was issued.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <EffectManifestDialog
        manifest={manifest}
        disabled={disabled}
        onApprove={(reason) => setPendingDecision('approve')}
        onDeny={(reason) => setPendingDecision('deny')}
      />
      <ApprovalConfirmationDialog
        open={pendingDecision !== null}
        decision={pendingDecision ?? 'approve'}
        onConfirm={() => pendingDecision && runDecision(pendingDecision)}
        onCancel={() => setPendingDecision(null)}
      />
    </div>
  );
}
