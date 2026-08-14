// SPDX-License-Identifier: MIT

'use client';

import type { DiffEvidence } from '../../lib/operator_console/schemas';

export function DiffStreamPanel({ diffs }: { diffs: DiffEvidence[] }) {
  return (
    <ul className="space-y-2 text-xs text-white/70">
      {diffs.map((d) => (
        <li key={d.diffSha256} className="break-all">
          <span className="text-gold-light">{d.diffSha256.slice(0, 20)}…</span> · {d.addedLines}+ / {d.removedLines}- · gideon {d.gideonVerdict}
        </li>
      ))}
    </ul>
  );
}
