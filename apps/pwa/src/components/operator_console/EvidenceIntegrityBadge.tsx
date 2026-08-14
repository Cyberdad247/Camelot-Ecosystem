// SPDX-License-Identifier: MIT

'use client';

import type { EvidenceIntegrity } from '../../lib/operator_console/schemas';

const LABELS: Record<EvidenceIntegrity, { text: string; className: string }> = {
  verified: { text: 'VERIFIED', className: 'text-emerald-400 border-emerald-400/40' },
  pending_anchor: { text: 'PENDING DURABLE ANCHOR', className: 'text-amber-300 border-amber-300/40' },
  unavailable: { text: 'UNAVAILABLE', className: 'text-slate-400 border-slate-400/40' },
  integrity_failed: { text: 'INTEGRITY FAILED', className: 'text-red-400 border-red-400/60' },
};

export function EvidenceIntegrityBadge({ integrity, taskId }: {
  integrity: EvidenceIntegrity;
  taskId: string;
}) {
  const meta = LABELS[integrity];
  const role = integrity === 'integrity_failed' ? 'alert' : 'status';
  return (
    <span
      role={role}
      aria-label={`Evidence integrity ${meta.text} for task ${taskId}`}
      className={`inline-flex items-center gap-2 border px-2 py-0.5 font-mono text-[10px] uppercase tracking-widest ${meta.className}`}
    >
      <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-current" />
      {meta.text}
    </span>
  );
}
