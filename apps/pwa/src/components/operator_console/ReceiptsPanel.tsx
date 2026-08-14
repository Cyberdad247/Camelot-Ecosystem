// SPDX-License-Identifier: MIT

'use client';

import type { ReceiptSummary } from '../../lib/operator_console/schemas';

export function ReceiptsPanel({ receipts }: { receipts: ReceiptSummary[]; taskId: string }) {
  return (
    <ul className="space-y-2 text-xs text-white/70">
      {receipts.slice(0, 50).map((r) => (
        <li key={r.receiptId} className="flex items-center gap-2">
          <span className="uppercase text-white/40">{r.kind}</span>
          <span>{r.timestamp}</span>
        </li>
      ))}
      {receipts.length === 0 && <li className="text-white/40">No receipts yet</li>}
    </ul>
  );
}
