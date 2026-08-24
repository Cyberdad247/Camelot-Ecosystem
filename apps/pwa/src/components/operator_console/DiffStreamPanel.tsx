// SPDX-License-Identifier: MIT

'use client';

import type { DiffEvidence } from '../../lib/operator_console/schemas';

const VERDICT_STYLE: Record<string, string> = {
  pass: 'text-emerald-400',
  fail: 'text-red-400',
  pending: 'text-amber-300',
  unavailable: 'text-slate-400',
};

export function DiffStreamPanel({ diffs }: { diffs: DiffEvidence[] }) {
  if (!diffs.length) {
    return <p className="text-xs italic text-white/40">No diff evidence yet.</p>;
  }
  return (
    <ul className="space-y-3">
      {diffs.map((d) => (
        <li key={d.diffSha256} className="border border-white/10 p-3">
          <div className="flex items-center justify-between gap-2">
            <span className="break-all font-mono text-[10px] text-gold-light">{d.diffSha256}</span>
            <span
              className={`font-mono text-[10px] uppercase ${VERDICT_STYLE[d.gideonVerdict] ?? ''}`}
            >
              gideon: {d.gideonVerdict}
            </span>
          </div>
          <p className="mt-1 text-[11px] text-white/50">
            {d.addedLines} added · {d.removedLines} removed · {d.changedPaths.length} paths
          </p>
          {d.changedPaths.slice(0, 4).map((p) => (
            <p key={p} className="mt-0.5 break-all font-mono text-[10px] text-white/40">
              + {p}
            </p>
          ))}
        </li>
      ))}
    </ul>
  );
}
