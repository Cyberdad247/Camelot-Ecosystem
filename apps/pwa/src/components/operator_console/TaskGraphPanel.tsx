// SPDX-License-Identifier: MIT

'use client';

export function TaskGraphPanel({ nodes }: { nodes: Array<Record<string, unknown>> }) {
  return (
    <ul className="space-y-2 text-xs text-white/70">
      {nodes.map((n) => (
        <li key={String(n.nodeId)} className="flex items-center gap-2">
          <span className={`h-1.5 w-1.5 rounded-full ${n.status === 'done' ? 'bg-emerald-400' : 'bg-amber-300'}`} />
          <span>{String(n.name)}</span>
          <span className="text-white/40 uppercase">{String(n.status)}</span>
        </li>
      ))}
    </ul>
  );
}
