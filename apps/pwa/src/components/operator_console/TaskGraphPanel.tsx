// SPDX-License-Identifier: MIT

'use client';

interface DagNode {
  nodeId: string;
  name?: string;
  status?: string;
  worker?: string;
  updatedAt?: string;
}

const STATUS_DOT: Record<string, string> = {
  done: 'bg-emerald-400',
  running: 'bg-amber-300',
  blocked: 'bg-red-400',
  cancelled: 'bg-white/30',
};

export function TaskGraphPanel({ nodes }: { nodes: Array<Record<string, unknown>> }) {
  if (!nodes.length) {
    return <p className="text-xs italic text-white/40">No task graph nodes yet.</p>;
  }
  const dag = nodes as unknown as DagNode[];
  return (
    <ul className="space-y-2">
      {dag.map((n) => {
        const status = n.status ?? 'unknown';
        return (
          <li key={n.nodeId} className="flex items-center justify-between gap-2 text-xs text-white/80">
            <span className="flex items-center gap-2">
              <span aria-hidden="true" className={`h-1.5 w-1.5 rounded-full ${STATUS_DOT[status] ?? 'bg-white/40'}`} />
              <span>{n.name ?? n.nodeId}</span>
            </span>
            <span className="font-mono text-[10px] uppercase tracking-wider text-white/40">
              {status}{n.worker ? ` · ${n.worker}` : ''}
            </span>
          </li>
        );
      })}
    </ul>
  );
}
