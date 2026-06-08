import type { ASTNode } from './parse-ast';

// ---------------------------------------------------------------------------
// Result types
// ---------------------------------------------------------------------------

export type DagOk  = { ok: true;  order: string[] };
export type DagErr = { ok: false; reason: 'orphan' | 'cycle'; culprits: string[] };
export type DagResult = DagOk | DagErr;

// ---------------------------------------------------------------------------
// Full validation — Kahn's topological sort, O(V + E)
//
// Each ASTNode has at most one parent (pid), so E = V − roots, and the graph
// is a forest.  Kahn's is the right tool: it detects cycles by checking
// whether every node was processed.  When it hasn't been, the unprocessed
// nodes are exactly the members of all cycles.
// ---------------------------------------------------------------------------

export function validateDAG(nodes: Map<string, ASTNode>): DagResult {
  // 1. Orphan check — a non-null pid that points to a node not in the map.
  for (const [id, n] of nodes) {
    if (n.pid !== null && !nodes.has(n.pid)) {
      return { ok: false, reason: 'orphan', culprits: [id] };
    }
  }

  // 2. Build adjacency (parent → children) and in-degree tables.
  const inDeg = new Map<string, number>();
  const adj   = new Map<string, string[]>();

  for (const id of nodes.keys()) {
    inDeg.set(id, 0);
    adj.set(id, []);
  }

  for (const [id, n] of nodes) {
    if (n.pid !== null) {
      adj.get(n.pid)!.push(id);
      inDeg.set(id, inDeg.get(id)! + 1);
    }
  }

  // 3. Kahn's BFS from all roots (inDeg === 0).
  //    Use a stack (push/pop) instead of queue (push/shift) — O(1) vs O(n).
  const stack: string[] = [];
  for (const [id, deg] of inDeg) {
    if (deg === 0) stack.push(id);
  }

  const order: string[] = [];

  while (stack.length > 0) {
    const curr = stack.pop()!;
    order.push(curr);

    for (const child of adj.get(curr)!) {
      const next = inDeg.get(child)! - 1;
      inDeg.set(child, next);
      if (next === 0) stack.push(child);
    }
  }

  // 4. Any node still with inDeg > 0 is part of a cycle.
  if (order.length !== nodes.size) {
    const culprits = [...inDeg]
      .filter(([, d]) => d > 0)
      .map(([id]) => id);
    return { ok: false, reason: 'cycle', culprits };
  }

  return { ok: true, order };
}

// ---------------------------------------------------------------------------
// Incremental delta validator
//
// Re-running full Kahn's on every CRDT mutation is O(V+E) each time.
// Because each node has at most one parent, we can short-circuit:
//
//   ADD    — a brand-new UUID cannot already appear in any ancestor chain,
//             so only an orphan check is needed.
//
//   UPDATE — the node's pid changed.  Walk the ancestor chain of the NEW pid;
//             if we reach the updated node's own id, that's a cycle.
//
//   REMOVE — can never introduce a cycle.  Orphan check on surviving children.
// ---------------------------------------------------------------------------

export type DeltaOp =
  | { type: 'add';    node: ASTNode }
  | { type: 'update'; node: ASTNode }
  | { type: 'remove'; id:   string  };

export function validateDelta(
  nodes: Map<string, ASTNode>,
  op:    DeltaOp,
): DagResult {
  switch (op.type) {
    case 'add': {
      if (op.node.pid !== null && !nodes.has(op.node.pid)) {
        return { ok: false, reason: 'orphan', culprits: [op.node.id] };
      }
      // New UUID — cannot already appear in any existing chain.
      return { ok: true, order: [] };
    }

    case 'update': {
      const { id, pid } = op.node;

      if (pid === null) return { ok: true, order: [] };

      if (!nodes.has(pid)) {
        return { ok: false, reason: 'orphan', culprits: [id] };
      }

      // Walk the ancestor chain of `pid` looking for `id`.
      let cursor: string | null = pid;
      const visited = new Set<string>();

      while (cursor !== null) {
        if (cursor === id) {
          return { ok: false, reason: 'cycle', culprits: [id, pid] };
        }
        if (visited.has(cursor)) break; // Existing cycle — caught by full validate.
        visited.add(cursor);
        cursor = nodes.get(cursor)?.pid ?? null;
      }

      return { ok: true, order: [] };
    }

    case 'remove': {
      // Check surviving children don't become orphans.
      const orphans: string[] = [];
      for (const [nid, n] of nodes) {
        if (nid !== op.id && n.pid === op.id) orphans.push(nid);
      }
      if (orphans.length > 0) {
        return { ok: false, reason: 'orphan', culprits: orphans };
      }
      return { ok: true, order: [] };
    }
  }
}

// ---------------------------------------------------------------------------
// Error formatter — human-readable message for UI / logs
// ---------------------------------------------------------------------------

export function formatDagError(err: DagErr): string {
  return err.reason === 'cycle'
    ? `Cycle detected — nodes involved: ${err.culprits.join(', ')}`
    : `Orphan node(s) — missing parent: ${err.culprits.join(', ')}`;
}
