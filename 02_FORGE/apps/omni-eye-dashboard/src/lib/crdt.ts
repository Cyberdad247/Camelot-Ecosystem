import { useSyncExternalStore } from 'react';
import type { ASTNode } from './parse-ast';
import { validateDelta, validateDAG, formatDagError } from './dag';
import type { DeltaOp } from './dag';

// ---------------------------------------------------------------------------
// AstStore — append-only action log, DAG-gated commits, undo/redo
//
// Mutation lifecycle:
//   1. validateDelta  — O(depth) incremental check before touching state
//   2. Apply snapshot — copy current Map, apply the change
//   3. validateDAG    — full O(V+E) check on the new snapshot
//   4. Commit         — push snapshot + action onto history stack
//      OR Rollback    — discard snapshot, throw MutationError
// ---------------------------------------------------------------------------

export class MutationError extends Error {
  constructor(
    public readonly reason: 'orphan' | 'cycle' | 'not_found',
    public readonly detail: string,
  ) {
    super(`[CRDT:${reason.toUpperCase()}] ${detail}`);
  }
}

export interface Snapshot {
  nodes:     ReadonlyMap<string, ASTNode>;
  timestamp: number;
}

type Listener = () => void;

export class AstStore {
  // Immutable snapshot — never mutate in place.
  private current: Map<string, ASTNode> = new Map();

  // History stack for undo; future stack for redo.
  private past:   Map<string, ASTNode>[] = [];
  private future: Map<string, ASTNode>[] = [];

  private listeners = new Set<Listener>();

  // ---------------------------------------------------------------------------
  // External store interface (React useSyncExternalStore)
  // ---------------------------------------------------------------------------

  subscribe = (listener: Listener): (() => void) => {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  };

  getSnapshot = (): Snapshot => ({
    nodes:     this.current,
    timestamp: Date.now(),
  });

  private notify() {
    for (const l of this.listeners) l();
  }

  // ---------------------------------------------------------------------------
  // Read
  // ---------------------------------------------------------------------------

  get(id: string): ASTNode | undefined {
    return this.current.get(id);
  }

  has(id: string): boolean {
    return this.current.has(id);
  }

  size(): number {
    return this.current.size;
  }

  nodes(): ReadonlyMap<string, ASTNode> {
    return this.current;
  }

  // ---------------------------------------------------------------------------
  // Write — each method validates, commits, or throws MutationError
  // ---------------------------------------------------------------------------

  insert(node: ASTNode): void {
    this.commit({ type: 'add', node });
  }

  update(node: ASTNode): void {
    if (!this.current.has(node.id)) {
      throw new MutationError('not_found', `Node ${node.id} does not exist`);
    }
    this.commit({ type: 'update', node });
  }

  remove(id: string): void {
    if (!this.current.has(id)) {
      throw new MutationError('not_found', `Node ${id} does not exist`);
    }
    this.commit({ type: 'remove', id });
  }

  // ---------------------------------------------------------------------------
  // Undo / Redo
  // ---------------------------------------------------------------------------

  canUndo(): boolean { return this.past.length > 0; }
  canRedo(): boolean { return this.future.length > 0; }

  undo(): void {
    const prev = this.past.pop();
    if (!prev) return;
    this.future.push(new Map(this.current));
    this.current = prev;
    this.notify();
  }

  redo(): void {
    const next = this.future.pop();
    if (!next) return;
    this.past.push(new Map(this.current));
    this.current = next;
    this.notify();
  }

  // ---------------------------------------------------------------------------
  // Reset — wipe everything
  // ---------------------------------------------------------------------------

  reset(): void {
    this.current = new Map();
    this.past    = [];
    this.future  = [];
    this.notify();
  }

  // ---------------------------------------------------------------------------
  // Private: validated commit
  // ---------------------------------------------------------------------------

  private commit(op: DeltaOp): void {
    // 1. Incremental pre-check (cheap).
    const pre = validateDelta(this.current, op);
    if (!pre.ok) {
      throw new MutationError(pre.reason, formatDagError(pre));
    }

    // 2. Build next snapshot.
    const next = new Map(this.current);
    applyOp(next, op);

    // 3. Full DAG validation on the candidate snapshot (catches multi-node cycles).
    const full = validateDAG(next);
    if (!full.ok) {
      throw new MutationError(full.reason, formatDagError(full));
    }

    // 4. Commit — push current onto undo stack, clear redo stack.
    this.past.push(this.current);
    this.future  = [];
    this.current = next;
    this.notify();
  }
}

// ---------------------------------------------------------------------------
// Apply a DeltaOp to a mutable Map snapshot (no validation — called after checks)
// ---------------------------------------------------------------------------

function applyOp(nodes: Map<string, ASTNode>, op: DeltaOp): void {
  switch (op.type) {
    case 'add':
    case 'update':
      nodes.set(op.node.id, op.node);
      break;
    case 'remove':
      nodes.delete(op.id);
      break;
  }
}

// ---------------------------------------------------------------------------
// Singleton store for the website builder cartridge
// ---------------------------------------------------------------------------

export const astStore = new AstStore();

// ---------------------------------------------------------------------------
// React hook — re-renders on every commit, undo, or redo
// ---------------------------------------------------------------------------

export function useAstStore(): {
  nodes:    ReadonlyMap<string, ASTNode>;
  insert:   (node: ASTNode) => void;
  update:   (node: ASTNode) => void;
  remove:   (id: string)    => void;
  undo:     () => void;
  redo:     () => void;
  canUndo:  boolean;
  canRedo:  boolean;
  reset:    () => void;
} {
  const snapshot = useSyncExternalStore(
    astStore.subscribe,
    astStore.getSnapshot,
    astStore.getSnapshot,  // server snapshot (SSR — empty)
  );

  return {
    nodes:   snapshot.nodes,
    insert:  (n) => astStore.insert(n),
    update:  (n) => astStore.update(n),
    remove:  (id) => astStore.remove(id),
    undo:    () => astStore.undo(),
    redo:    () => astStore.redo(),
    canUndo: astStore.canUndo(),
    canRedo: astStore.canRedo(),
    reset:   () => astStore.reset(),
  };
}
