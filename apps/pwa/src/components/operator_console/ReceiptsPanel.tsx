// SPDX-License-Identifier: MIT

'use client';

import type { ReceiptSummary } from '../../lib/operator_console/schemas';
import { ageLabel } from '../../lib/operator_console/formatters';

export function ReceiptsPanel({ receipts, taskId }: { receipts: ReceiptSummary[]; taskId: string }) {
  const verified = receipts.filter((r) => r.integrity === 'verified');
  const unanchored = receipts.filter((r) => r.integrity === 'pending_anchor');
  const failed = receipts.filter((r) => r.integrity === 'integrity_failed');

  if (!receipts.length) {
    return <p className="text-xs italic text-white/40">No verified records yet.</p>;
  }

  return (
    <div className="space-y-3">
      {failed.length > 0 && (
        <div className="border border-red-400/60 p-2" role="alert">
          <p className="font-mono text-[10px] uppercase tracking-widest text-red-300">
            Integrity failure — {failed.length} record(s) cannot satisfy any promotion gate.
          </p>
        </div>
      )}
      <p className="font-mono text-[10px] text-white/40">
        Latest 50 verified records for task {taskId} · newest first
      </p>
      <ul className="max-h-72 space-y-1.5 overflow-auto">
        {verified.slice(0, 50).map((r) => (
          <li key={r.receiptId} className="flex items-center justify-between gap-2 text-[11px] text-white/70">
            <span className="uppercase">{r.kind}</span>
            <span className="text-white/40">{ageLabel(r.timestamp)}</span>
          </li>
        ))}
      </ul>
      {unanchored.length > 0 && (
        <p className="font-mono text-[10px] text-amber-200/80">
          {unanchored.length} record(s) pending durable anchor — not promotion-eligible.
        </p>
      )}
    </div>
  );
}
