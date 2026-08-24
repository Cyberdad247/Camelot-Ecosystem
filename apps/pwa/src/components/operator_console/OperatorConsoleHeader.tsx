// SPDX-License-Identifier: MIT

'use client';

import type { EvidenceIntegrity } from '../../lib/operator_console/schemas';
import { EvidenceIntegrityBadge } from './EvidenceIntegrityBadge';

export function OperatorConsoleHeader({
  taskId,
  integrity,
}: {
  taskId: string;
  integrity: EvidenceIntegrity;
}) {
  return (
    <header className="flex flex-wrap items-center justify-between gap-4 border-b border-gold/20 pb-4">
      <div>
        <h1 className="font-display text-2xl tracking-minted text-gold-light">OPERATOR CONSOLE</h1>
        <p className="font-mono text-[11px] text-white/40">
          task {taskId} · read-rich, write-on-approval
        </p>
      </div>
      <EvidenceIntegrityBadge integrity={integrity} taskId={taskId} />
    </header>
  );
}
