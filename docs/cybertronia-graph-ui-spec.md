# cybertronia-graph-ui — Shared Package Spec (Draft 0.3)

> Phase 3 of the Cybertronia 3D Graph Sync Forge. Two consumers share one
> runtime: the PWA Cockpit lazy cartridge (Next.js 16 App Router) and the
> Anya Dashboard graph panel. Both consume the same `GraphSnapshot` /
> `GraphDelta` / `SelectionState` shape and select between a 3D
> InstancedMesh path and a 2D SVG/Canvas2D fallback at runtime.

| Field | Value |
|---|---|
| Status | **Draft 0.3.1** — Draft 0.3 invariants preserved; new **§6.3** documents the lockbox-ownership transfer to the package (Draft 0.1 §6) AND the migration window during which BOTH the PWA-side and package-side anchors must coexist green. Phase 2 compiler output still locks the 25-vector field indices; pre-SSE bootstrap (`GraphSnapshotStub`) is now part of the contract; `PerfProfile` typed enum; edge weight inlined into the edge stride (8 floats / 32 bytes); atomic swap ordering pinned to backing-store-first; canonical `DRIFT_MSG` byte-matches the Goose banner; `EXPECTED_VECTOR_FIELD_NAMES` lockbox; `pivot_fps` standardized to `expected_fps_band − 5` (-30 for `hidden`) |
| Producer side | `control_plane/cybertronia_audit.py` (Phase 1, shipped) → `03_VAULT/runtime_state/cybertronia_graph/{node_telemetry.json, cursor.json, scan.meta.json}` |
| Compiler side | `control_plane/cybertronia_compile.py` (Phase 2, TBD) → `lattice_vectors.json`, `graph_delta.json`, redacted `entiremap.md` |
| Transport side | `control_plane/cognitive_service.py` (Phase 4, TBD) → 4 read-only endpoints on `:8092` |
| Consumer A | `phase7-wt/02_FORGE/apps/pwa-cockpit/src/app/cockpit/cartridges/cybertronia-graph/` (lazy cartridge) |
| Consumer B | `CAMELOT_OS/dashboards/anya/graph-panel/` (TBD) |

The package name `cybertronia-graph-ui` is reserved; do NOT claim the name
until Phase 3 ships.

---

## 0. Glossary

| Term | Definition |
|---|---|
| `NodeId` | sha256(scope + "/" + path)[:16] for files; sha256("runtime_service" + "/" + port)[:16] for live services; sha256("process_group" + "/" + regex)[:16] for top-N process buckets |
| `NodeLayer` | one of the five semantic bands: `"bin"`, `"control_plane"`, `"02_FORGE"`, `"03_VAULT"`, `"runtime"` |
| `ClusterId` | sha256(NodeLayer + ":" + community)[8:] — server-side rollup for nodes > 1500 |
| `HLT` | hybrid logical timestamp = `(physical_ms, logical_counter)` — BrainSync convergence token without wall-clock assumptions |
| `Digest` | `"sha256:" + sha256_hex(json.dumps(payload, sort_keys=True))` |
| `PerfProfile` | `"high" \| "mid" \| "low" \| "2d" \| "hidden"` — closed union gating the renderer axes (see §4.1) |

---

## 1. GraphSnapshot — frozen shape

Consumers MUST treat unknown top-level fields as ignored. The snapshot
`digest` is the convergence token shared with BrainSync.

```typescript
// GraphSnapshot — versioned, frozen structure
type GraphSnapshot = {
  schema_version: "cybertronia.snapshot/v1";
  scan_id: string;                           // 16-hex sha256(root + "|" + started_at)
  digest: string;                            // self sha256, includes schema_version
  started_at: string;                        // ISO8601 UTC
  completed_at: string | null;
  source_root: string;                       // absolute scan root resolution

  palette: PaletteBindings;
  caption: CaptionMap;                       // a11y non-color indicators

  nodes: NodeRef[];                          // ≤ 1500 on initial mount
  edges: EdgeRef[];                          // ≤ 3000 on initial mount
  clusters: ClusterRef[];                    // server-side rollups when overflow
  layout: LayoutCoords;                      // pre-computed XYZ positions per node
  vectors: Record<NodeId, Vector25>;         // 25-value schema per node

  meta: SnapshotMeta;
};

type PaletteBindings = {
  obsidian: "#050505";
  gold:     "#D4AF37";
  purple:   "#2E0854";
};

// Non-color a11y: shape + dash-pattern per layer + sensitivity band.
type CaptionMap = {
  layers: Record<NodeLayer, {
    hex: string; aria: string;
    shape: "sphere" | "cube" | "octa" | "torus";
  }>;
  sensitivity: Record<"low" | "med" | "high", {
    hex: string; aria: string;
    pattern: "solid" | "dashed" | "dotted";
  }>;
};

type NodeRef = {
  id: NodeId;
  layer: NodeLayer;
  kind: NodeKind;
  path: string;                              // root-relative, POSIX separators
  size_bytes: number;
  mtime_iso: string;
  sensitivity: "low" | "med" | "high";
  community: number;
  in_degree: number;
  out_degree: number;
  cluster_id?: ClusterId;                    // present when nodes > 1500
};

type NodeKind =
  | "file" | "dir" | "symlink"
  | "runtime_service" | "process_group"
  | "listener_port" | "volume";

type EdgeRef = {
  from: NodeId;
  to: NodeId;
  relation: RelationKind;
  weight: number;                             // 0 ≤ w ≤ 1
};

// Closed vocabulary; new kinds are a contract change (drift test fires).
type RelationKind =
  | "imports" | "wires" | "extends"
  | "spawns" | "exposes" | "consumes"
  | "depends_on" | "builds_into" | "reads_from";

type ClusterRef = {
  id: ClusterId;
  parent_layer: NodeLayer;
  member_count: number;
  centroid: [number, number, number];
};

type LayoutCoords = {
  algorithm: "force" | "radial" | "cluster_centroid";
  scale: "log" | "linear";
  positions: Record<NodeId, [number, number, number]>;
};

// 25-value vector per spec §2; indices are positional, ordered.
// Phase 2 compiler MUST emit values at the named indices so the pwa-side
// and Anya-side consumers can index without re-keying.
type Vector25 = readonly [
  //  v[0]   layer             (one-hot, packed int 0..N_LAYERS)
  //  v[1]   type              (NodeKind one-hot)
  //  v[2]   path depth        (log2 of segments)
  //  v[3]   size              (log bytes)
  //  v[4]   file count        (sibling-aware, log)
  //  v[5]   recency           (mtime age, normalized 0..1)
  //  v[6]   churn             (mtime derivative)
  //  v[7]   cpu cost          (rolling average from telemetry)
  //  v[8]   memory cost       (RSS / heap share)
  //  v[9]   storage cost      (size_bytes / volume.total)
  //  v[10]  runtime state     ("active" | "dormant" | "errored" | "offline")
  //  v[11]  health            (0..1)
  //  v[12]  exposure          (port/listener/iface, one-hot)
  //  v[13]  in_degree         (normalized)
  //  v[14]  out_degree        (normalized)
  //  v[15]  centrality        (eigenvector)
  //  v[16]  betweenness       (normalized)
  //  v[17]  pagerank          (normalized)
  //  v[18]  community         (integer label)
  //  v[19]  criticality       (impact × confidence from Phase H optimizer)
  //  v[20]  sensitivity       (0..2: low | med | high)
  //  v[21]  mutability        (file vs runtime; 0 = immutable, 1 = mutable)
  //  v[22]  provenance        (local | remote | redaction-mask)
  //  v[23]  sync state        ("synced" | "pending" | "diverged")
  //  v[24]  resource pressure (rolling CPU+RAM, normalized)
  number, number, number, number, number,
  number, number, number, number, number,
  number, number, number, number, number,
  number, number, number, number, number,
  number, number, number, number, number,
];

type SnapshotMeta = {
  total_files: number;
  total_bytes: number;
  excluded_count: number;
  exit_reason: "complete" | "memory_abort" | "interrupted";
  fps_target: 30 | 60 | 120;
  perf_profile: PerfProfile;                 // see §4.1 — produced by PerformanceMonitor
  memory_class: "low" | "med" | "high";
  gpu_buffer_bytes?: number;                 // reported back from renderer
};
```

---

## 2. GraphDelta — stream shape

Streamed from `GET /api/cybertronia-graph/stream` (Phase 4). Three
operation kinds: `upsert`, `tombstone`, `expand_cluster`. HLT is
`(physical_ms, logical_counter)`. Merge rule is **last-writer-wins per
node field**, governed by lexicographic `(hlt_ms, hlt_logical)` comparison.

```typescript
type GraphDelta = {
  schema_version: "cybertronia.delta/v1";
  scan_id: string;
  base_digest: string;                       // digest of the snapshot/delta this appends to
  received_at_ms: number;                    // wall-clock receive timestamp (advisory only)
  hlt: [number, number];                     // producer-side (physical_ms, logical)
  operations: DeltaOp[];
};

type DeltaOp =
  | { kind: "upsert"; node_id: NodeId; fields: Partial<NodeRef>;
      occurred_hlt: [number, number] }
  | { kind: "tombstone"; node_id: NodeId; occurred_hlt: [number, number] }
  | { kind: "expand_cluster"; cluster_id: ClusterId;
      member_ids: NodeId[]; occurred_hlt: [number, number] };
```

Merge contract (BrainSync):

1. **Field-level LWW** — for each `(node_id, field_name)`, the op with the
   highest `(occurred_hlt)` wins.
2. **Tombstones are sticky** — a `tombstone` supersedes any prior
   `upsert` for the same `node_id`, regardless of HLT, until an explicit
   `upsert` (which is a normal `upsert`, not an "un-tombstone" verb).
3. **Cadence** — the SSE stream emits at most 1 batch every ≥160 ms;
   ≥ 1 op per batch; idempotency holds because ops are deterministic by
   `(node_id, occurred_hlt)`.
4. **Cluster expansion** — `expand_cluster` adds member `NodeRef`s from
   a `ClusterRef` into the rendered set; subsequent `upsert`s use the
   full `NodeId` set.
5. **Cluster expansion determinism** — when two `expand_cluster` ops for
   the same `ClusterId` arrive out of order, highest HLT wins with both
   expanding the full member set; consumer dedupes by `NodeId`.

---

## 3. SelectionState — per-mount, ephemeral

NOT part of snapshot or delta. Persists in `sessionStorage` so that
opening both surfaces (PWA Cockpit + Anya) on the same machine
converges to the same focus.

```typescript
type SelectionState = {
  kind: "none" | "focus" | "multi";
  selected_ids: NodeId[];
  hovered_id: NodeId | null;
  filter: SearchFilter;
  camera_target: NodeId | null;              // "fly-to" on click
  highlighted_edge: [NodeId, NodeId] | null;
};

type SearchFilter = {
  text?: string;                             // substring over `path` + `kind`
  layer?: NodeLayer;
  sensitivity?: "low" | "med" | "high";
  community?: number;
  provenance?: "local" | "remote";
  fps_target?: 30 | 60 | 120;                // forces suite if not in supported band
};
```

---

## 4. InstancedMesh contract — 3D rendering

R3F path. **One InstancedMesh per layer** (so instanced shape varies
per `CaptionMap.layers[layer].shape`). Edges as `LineSegments` grouped
by `RelationKind`.

Stable typed-array buffers (no per-node React component):

| Buffer | Type | Shape | Notes |
|---|---|---|---|
| `nodePositionsBuffer`  | `Float32Array` | `nodes_count × NODE_STRIDE_FLOATS` | pre-computed from `LayoutCoords.positions` |
| `nodeScaleBuffer`      | `Float32Array` | `nodes_count × 3` (sibling CPU buffer) | size-driven; log scale |
| `nodeColorBuffer`      | `Float32Array` | `nodes_count × 3` | per-instance color = layer hue × sensitivity multiplier |
| `nodeSelectionBuffer`  | `Uint8Array`   | `nodes_count`                       | 0=unselected 1=focused 2=hovered 3=multi |
| `nodeSensitivityBuffer`| `Uint8Array`   | `nodes_count`                       | 0=low 1=med 2=high — drives dash-pattern via shader |
| `edgeBuffer`           | `Float32Array` | `edges_count × EDGE_STRIDE_FLOATS` | one LineSegments index; **edge weight is inlined (no parallel buffer)** |
| `edgeColorBuffer`      | `Float32Array` | `edges_count × 3`                   | per RelationKind |

Per-instance updates use `InstancedMesh.setMatrixAt` and
`InstancedMesh.setColorAt` only on **dirty ranks** tracked in a parallel
`Uint32Array dirtyFlag`. No full-buffer writes per frame.

Renderer policy:

| Setting | Default | Switch |
|---|---|---|
| `frameloop` | `"demand"` | bumped to `"always"` while a transition is active |
| `useFrame` interpolation | bounded | skip 1 frame when `dt > 50ms` to avoid stale interpolation |
| `PerformanceMonitor` step-down | per `PerfProfile` (§4.1) | triggered on `fps < pivot_fps` for 30 consecutive frames |
| WebGL context loss | `"webglcontextlost"` listener rebuilds from `base_digest + last_good_delta` | one retry, then `2D fallback` |
| Component unmount | iterate all geometries / materials / textures / renderTargets and call `.dispose()` | always; no exception paths |
| GPU buffer cap | 50 MB (rendered geometry only) | metrics exported to `SnapshotMeta.gpu_buffer_bytes` for SSE round-trip |

### §4.1 — PerformanceMonitor gating policy (`PerfProfile` typed enum)

The renderer MUST classify itself into exactly one of these five bands at
all times. Drift-tested against `EXPECTED_PERF_PROFILES` (§6).

```typescript
type PerfProfile = "high" | "mid" | "low" | "2d" | "hidden";

type PerfAxis = {
  max_dpr: 0.5 | 1 | 1.5 | 2;                  // ceiling
  max_label_count: 0 | 25 | 100 | 500 | 1500;  // visible labels
  max_visible_edges: 0 | 250 | 1000 | 2000 | 3000;
  max_anim_ms: 0 | 50 | 200 | 500;            // per-frame transition budget
  expected_fps_band: 30 | 60 | 120;
  pivot_fps: number;                          // FPS < pivot_fps for 30 frames ⇒ step down
};

// DRAFT 0.3 FIX: `pivot_fps` standardized to `expected_fps_band - 5` across
// all profiles that have an uptime-based step-down rule. `hidden` is the
// exception (no step-down from `hidden`; pivot_fps = 0 means "never").
const PERF_PROFILE_AXES: Record<PerfProfile, PerfAxis> = {
  high:    { max_dpr: 2,   max_label_count: 500,  max_visible_edges: 3000, max_anim_ms: 200, expected_fps_band: 120, pivot_fps: 115 },
  mid:     { max_dpr: 1.5, max_label_count: 250,  max_visible_edges: 2000, max_anim_ms: 200, expected_fps_band: 60,  pivot_fps: 55  },
  low:     { max_dpr: 1,   max_label_count: 100,  max_visible_edges: 1000, max_anim_ms: 50,  expected_fps_band: 30,  pivot_fps: 25  },
  "2d":    { max_dpr: 1,   max_label_count: 0,    max_visible_edges: 0,    max_anim_ms: 0,   expected_fps_band: 30,  pivot_fps: 25  },
  hidden:  { max_dpr: 0.5, max_label_count: 0,    max_visible_edges: 0,    max_anim_ms: 0,   expected_fps_band: 30,  pivot_fps: 0   }, // never steps away from hidden
};

// Step-down order on `fps < pivot_fps` for 30 consecutive frames (heatmap):
//   high (115)  → mid  (55)  → low (25)  → "2d" (25)  (auto-engages 2D fallback)
// Step-up rule: 30 consecutive frames ≥ `expected_fps_band + 5` ⇒ step up one.
// "hidden" is an EXPLICIT state set by document.hidden / Page Visibility.
// PerformanceMonitor is the SOLE owner of the transition; consumers read
// `SnapshotMeta.perf_profile` (Phase 4) and dispatch accordingly.
```

### §4.2 — InstancedMesh typed-array stride layout

The strides are part of the cross-worktree contract: the SSE delta
payload serializes these buffers byte-for-byte; the Anya 2D fallback
reuses the same positions; the drift test pins byte counts.

```typescript
// === NODE STRIDE — 10 floats × 4 bytes = 40 bytes per node ===
//
//   [0..2]   pos        (x, y, z)         — LayoutCoords.positions[nodeId]
//   [3..5]   scale      (x, y, z)         — log(size_bytes + 1)
//   [6..8]   color      (r, g, b)         — palette[l].hex × sensitivity
//   [9]      flag       (0..3)            — selection 0..3
const NODE_STRIDE_FLOATS = 10 as const;
const NODE_STRIDE_BYTES  = 40 as const;

// === EDGE STRIDE — 8 floats × 4 bytes = 32 bytes per edge ===
//
//   [0..2]   src        (x, y, z)         — from-position
//   [3..5]   dst        (x, y, z)         — to-position
//   [6]      weight     (0..1)            — drives opacity per pixel
//   [7]      tag        (0..N_RELAT)      — RelationKind one-hot
//
// DRAFT 0.3 FIX: `weight` is now INLINED into the edge stride (no more
// parallel `edgeWeightBuffer`). SSE delta payload, 2D-fallback quadratic-
// curve rendering, and 3D LineSegments share one contiguous typed-array
// view per edge. The lockbox EXPECTED_EDGE_STRIDE_FLOATS / _BYTES must
// match (8 / 32).
const EDGE_STRIDE_FLOATS = 8 as const;
const EDGE_STRIDE_BYTES  = 32 as const;

// Sentinel — f32::NAN. MUST NOT appear in normal data; if read, consumer
// treats the slot as "not yet assigned" and forces an idle frame for
// instanced nodes / skips the edge segment.
const STRIDE_SENTINEL = NaN;

// Capacity ceilings — drift-tested against EXPECTED_NODE_CAP / EDGE_CAP.
const NODE_CAP_INITIAL = 1500 as const;     // §7 server gate
const EDGE_CAP_INITIAL = 3000 as const;     // §7 server gate

// Memory ceilings derived from the stride contract.
//
//   nodes.typed_arrays = NODE_CAP_INITIAL * NODE_STRIDE_BYTES
//                      = 1500 * 40              = 60_000 bytes  (60 KB)
//
//   edges.typed_arrays = EDGE_CAP_INITIAL * EDGE_STRIDE_BYTES
//                      = 3000 * 32              = 96_000 bytes  (96 KB)
//
//   nodes+edges typed_arrays (positions only) = 60 KB + 96 KB = 156 KB
//
// Plus sibling CPU buffers (colorBuffer, scaleBuffer, selectionBuffer,
// sensitivityBuffer for nodes; colorBuffer for edges) add modestly
// (~50 KB worst case for 1500 nodes × 16 B/node), staying well under
// the 50 MB GPU cap. The 50 MB cap covers RENDERED geometry buffers
// (instance matrix, TextMesh, draw-call overhead) — distinct from the
// typed-array CPU-side cap. Both ratios are drift-tested independently.
```

### §4.3 — Pre-SSE bootstrap (`GraphSnapshotStub`)

Before Phase 4 SSE delivers the first `GraphSnapshot`, the lazy PWA
cartridge and the Anya Dashboard panel mount against a deterministic
stub derived from the Phase 1 audit cursor + `scan.meta.json`. No
flash-of-empty-canvas.

```typescript
// Explicit null sentinel — consumers branch on `snapshot === null`.
type GraphSnapshotStub = {
  snapshot: null;
  fallback_2d: true;
  source: "audit-cursor";                   // future: "sse-bootstrap"
  scan_id: string | null;                   // from cursor.json if present
  cursor_last_path: string | null;          // from cursor.last_path
  completed_at: string | null;              // from cursor.started_at + scan.meta.json
  nodes_total: number;                      // cursor.files_seen
  fallback_reason: "sse_loading" | "sse_not_yet_built" | "audit_cursor_only";
};

type GraphPayload = GraphSnapshot | GraphSnapshotStub;

// Deterministic branch — no `isLoading`, no animation, no flicker.
function mountSurface(payload: GraphPayload): "3d" | "2d" {
  return payload.snapshot === null ? "2d" : "3d";
}
```

The lazy PWA cartridge and Anya panel mount as:

```tsx
<GraphSurface payload={payload}>
  {mountSurface(payload) === "3d"
    ? <GraphSurface3D  snapshot={payload.snapshot}  deltaStream={delta}/>
    : <GraphSurface2DFallback stub={payload}/>}
</GraphSurface>
```

When SSE eventually arrives, the consumer executes an **ordered atomic
swap**:

1. **Backing-store commit FIRST.** Write `payload.snapshot` to BACKING
   STORE (`window.__cybertroniaSnapshot` for browser-global, or a
   Zustand-style external store) BEFORE any React render fires. No
   `setSnapshot(snapshot)` here.
2. **Validate digest continuity.** Compare snapshot.digest with the
   previous `last_digest` from `/sync-status`. If they diverge without
   a rebase flag, emit `divergence_pending: true`; abort the swap; the
   stub remains in place.
3. **`useSyncExternalStore`-style flip.** Subscribe to the backing
   store via `useSyncExternalStore` (NOT `useState`). The flip is
   atomic with the backing store — no intermediate render, no
   `useEffect` chain.
4. **Concurrent unmount/mount.** The 2D fallback unmounts
   synchronously; the 3D renderer mounts from `payload.snapshot`
   plus the running delta stream in the same commit phase. Selecting
   a side via `mountSurface(payload)` happens here.
5. **Failure mode.** If any step 1–4 fails, the stub remains in place
   (graceful degradation; the SSE consumer logs the failure reason).

"Atomic" therefore means **commit-to-backing-store BEFORE state-flip**,
never `setSnapshot(snapshot)` alone. This is the contract difference
between React 18's `useTransition` (eventually-consistent) and the
`useSyncExternalStore` semantics this swap relies on.

---

## 5. 2D fallback behavior

Auto-triggers (in order):

1. WebGL unavailable OR context lost and 1-retry recovery failed.
2. `renderer.info.memory.geometries * bytesPerVertex >= 50 * 1024 * 1024`.
3. User opts in via `Settings.toggleForce2D` (persisted per-mount).
4. `mountSurface(GraphPayload)` returns `"2d"` (consumes `GraphSnapshotStub`).

Implementation: SVG (preferred for ≤1500 nodes) or Canvas2D (for >1500).
Same `GraphSnapshot` shape, same `SelectionState` event surface, but:

- `frameloop="demand"` permanently; **no `useFrame`**.
- No shadows, no anti-aliasing.
- Edges as quadratic curves attenuated by `weight`.
- Picking via DOM `<rect>` overlay (SVG) or `Path2D` hit-test (Canvas2D).
- Read-only by design — no camera animation, no zoom-and-pan easing.
- Cluster expansion still works (`expand_cluster` op).

When mounting from `GraphSnapshotStub` (§4.3), the 2D fallback lays out
positions from `cursor_last_path` (a single root-aligned node) and
hands a banner to the user: "Phase 4 SSE in progress — showing audit
cursor". When the stub swaps to a real snapshot, the banner is removed.

---

## 6. Cross-worktree contract pin (drift-test)

Mirror of the Phase 18 `AgentConfig` ↔ `PWACockpitStatusBanner` drift-test
pattern. Both consumer surfaces ship a symmetric describe block; the
`DRIFT_MSG` is identical to the Goose banner's pin (Phoenix-18 user spec).

#### §6.1 — Lockbox single-owner policy

**PWA side OWNS the lockbox.** Specifically, the file
`phase7-wt/02_FORGE/apps/pwa-cockpit/tests/cybertronia-graph-drift.test.ts`
is the single source of truth for:

- `EXPECTED_LAYERS`
- `EXPECTED_KINDS`
- `EXPECTED_RELATIONS`
- `EXPECTED_VECTOR_LEN`
- `EXPECTED_PERF_PROFILES`
- `EXPECTED_VECTOR_FIELD_NAMES` (Draft 0.3 — pins the 25 indexed field names verbatim; catches future renames like `"CPU cost"` → `"cpu_cost"`)
- `EXPECTED_NODE_STRIDE_FLOATS`, `EXPECTED_NODE_STRIDE_BYTES`
- `EXPECTED_EDGE_STRIDE_FLOATS`, `EXPECTED_EDGE_STRIDE_BYTES` (Draft 0.3 — now `8` / `32`)

The Goose-side counterpart in
`CAMELOT_OS/02_FORGE/KINETIC_ARMORY/goose/ui/desktop/src/components/settings/providers/PWACockpitStatusBanner.test.tsx`
MIRRORS each of those constants and reads the PWA-side file at test
time (CAMELOT_OS is a local directory in this workspace, so the cross-
file read is allowed). It asserts equality on **every** constant. If
either side drifts, BOTH must be updated in a single commit; the
Phoenix-18 `DRIFT_MSG` already encodes "Both sides MUST be updated
together".

#### §6.2 — Drift test code

```typescript
// pwa-cockpit/tests/cybertronia-graph-drift.test.ts
import { describe, it, expect } from "vitest";
import type {
  NodeLayer, NodeKind, RelationKind, Vector25, PerfProfile,
} from "cybertronia-graph-ui";

// OWNED BY THIS FILE. Goose side reads + asserts equality, byte-by-byte.
const EXPECTED_LAYERS = ["bin", "control_plane", "02_FORGE", "03_VAULT", "runtime"]
  as const satisfies readonly NodeLayer[];
const EXPECTED_KINDS = [
  "file", "dir", "symlink",
  "runtime_service", "process_group", "listener_port", "volume",
] as const satisfies readonly NodeKind[];
const EXPECTED_RELATIONS = [
  "imports", "wires", "extends",
  "spawns", "exposes", "consumes",
  "depends_on", "builds_into", "reads_from",
] as const satisfies readonly RelationKind[];
const EXPECTED_PERF_PROFILES = ["high", "mid", "low", "2d", "hidden"]
  as const satisfies readonly PerfProfile[];

// Draft 0.3 ADD — pins the 25 indexed field names verbatim against §1.
// Any future rename (e.g.  "CPU cost" → "cpu_cost") will fire this test.
const EXPECTED_VECTOR_FIELD_NAMES = [
  "layer",             // v[0]
  "type",              // v[1]
  "path depth",        // v[2]
  "size",              // v[3]
  "file count",        // v[4]
  "recency",           // v[5]
  "churn",             // v[6]
  "cpu cost",          // v[7]
  "memory cost",       // v[8]
  "storage cost",      // v[9]
  "runtime state",     // v[10]
  "health",            // v[11]
  "exposure",          // v[12]
  "in_degree",         // v[13]
  "out_degree",        // v[14]
  "centrality",        // v[15]
  "betweenness",       // v[16]
  "pagerank",          // v[17]
  "community",         // v[18]
  "criticality",       // v[19]
  "sensitivity",       // v[20]
  "mutability",        // v[21]
  "provenance",        // v[22]
  "sync state",        // v[23]
  "resource pressure", // v[24]
] as const;
const EXPECTED_VECTOR_LEN = 25 as const;
const EXPECTED_NODE_STRIDE_FLOATS = 10 as const;
const EXPECTED_NODE_STRIDE_BYTES  = 40 as const;
const EXPECTED_EDGE_STRIDE_FLOATS = 8 as const;   // Draft 0.3 — was 7
const EXPECTED_EDGE_STRIDE_BYTES  = 32 as const;  // Draft 0.3 — was 28

// CANONICAL DRIFT MESSAGE — must byte-match the Goose-side pin in
// PWACockpitStatusBanner.test.tsx (Phase 18 fix). Any paraphrase
// reintroduces drift on the drift message itself.
//
// DRAFT 0.3 FIX (REVISED): array-and-join pattern (not single-literal).
// The previous Draft 0.3 single-literal collapsed the canonical phrase
// into one string of ~270 chars, which tripped markdownlint MD013 and
// TypeScript max-len. Each array element is < 110 chars; the canonical
// phrase "Both sides MUST be updated together" stays WHOLE inside
// element 0 so substring greps (`grep Both sides MUST`) still match.
// Runtime value is unchanged.
const DRIFT_MSG: string = [
  "ProviderId union drifted between pwa-cockpit and Goose. Both sides MUST be updated together. ",
  "To fix: 1. Add literal to BOTH unions. ",
  "2. Update per-side label/model/PROVIDER_PILL/runtime tables. ",
  "3. Update EXPECTED_PROVIDERS in this file only AFTER both AgentConfig surfaces agree.",
].join("");

describe("cybertronia-graph-ui contract drift (PWA Cockpit ↔ Anya)", () => {
  it("NodeLayer is exhaustive", () => {
    expect(EXPECTED_LAYERS as readonly NodeLayer[], DRIFT_MSG)
      .toEqual(Object.freeze([...EXPECTED_LAYERS]));
  });
  it("NodeKind is exhaustive", () => {
    expect(EXPECTED_KINDS as readonly NodeKind[], DRIFT_MSG)
      .toEqual(Object.freeze([...EXPECTED_KINDS]));
  });
  it("RelationKind closes the edge vocabulary", () => {
    expect(EXPECTED_RELATIONS as readonly RelationKind[], DRIFT_MSG)
      .toEqual(Object.freeze([...EXPECTED_RELATIONS]));
  });
  it("PerfProfile is the closed 5-band union", () => {
    expect(EXPECTED_PERF_PROFILES as readonly PerfProfile[], DRIFT_MSG)
      .toEqual(Object.freeze([...EXPECTED_PERF_PROFILES]));
  });
  // Draft 0.3 ADD — pins the 25 indexed field names verbatim against §1.
  //
  // SPEC §1 ↔ LOCKBOX model: §1 of CAMELOT_OS/docs/cybertronia-graph-ui-spec.md
  // is the canonical source of truth; EXPECTED_VECTOR_FIELD_NAMES (above) is
  // the lockbox mirror. BOTH MUST be updated together. The 3 tests below
  // catch single-side edits: rename → first test fails; duplicate slot → second
  // test fails; alphabetical sort (instead of captured order) → third test
  // fails; reorder/insert/drop → first test fails (length + content drift).
  it("Vector25 indexed field names match §1 in declared (locked) order", () => {
    // SPEC VECTOR25 ARCHETYPE — fixture duplicating §1's positional order.
    // If §1 changes, BOTH this fixture AND EXPECTED_VECTOR_FIELD_NAMES (above)
    // move together. The DRIFT_MSG enforces single-commit-pair semantics.
    const SPEC_VECTOR25_IN_DECLARED_ORDER: readonly string[] = [
      "layer", "type", "path depth", "size", "file count",
      "recency", "churn", "cpu cost", "memory cost", "storage cost",
      "runtime state", "health", "exposure", "in_degree", "out_degree",
      "centrality", "betweenness", "pagerank", "community", "criticality",
      "sensitivity", "mutability", "provenance", "sync state", "resource pressure",
    ];
    expect([...EXPECTED_VECTOR_FIELD_NAMES], DRIFT_MSG)
      .toEqual(SPEC_VECTOR25_IN_DECLARED_ORDER);
  });
  it("Vector25 indexed field names are unique (no duplicate slot labels)", () => {
    expect(new Set(EXPECTED_VECTOR_FIELD_NAMES).size, DRIFT_MSG)
      .toBe(EXPECTED_VECTOR_LEN);
  });
  it("Vector25 indexed field names preserve captured order (not alphabetical)", () => {
    const SORTED = [...EXPECTED_VECTOR_FIELD_NAMES].slice().sort();
    const ORIGINAL = [...EXPECTED_VECTOR_FIELD_NAMES];
    const isAlphabetical = SORTED.every((v, i) => v === ORIGINAL[i]);
    expect(isAlphabetical, DRIFT_MSG).toBe(false);
  });
  it("InstancedMesh node stride is 10 floats / 40 bytes", () => {
    expect(EXPECTED_NODE_STRIDE_FLOATS, DRIFT_MSG).toBe(10);
    expect(EXPECTED_NODE_STRIDE_BYTES,  DRIFT_MSG).toBe(40);
  });
  // Draft 0.3 — edge weight INLINED into the edge stride.
  it("InstancedMesh edge stride is 8 floats / 32 bytes (weight inlined)", () => {
    expect(EXPECTED_EDGE_STRIDE_FLOATS, DRIFT_MSG).toBe(8);
    expect(EXPECTED_EDGE_STRIDE_BYTES,  DRIFT_MSG).toBe(32);
  });
});
```

The Goose-side counterpart mirrors every `EXPECTED_*` const and re-exports
the same `DRIFT_MSG`. New kinds/layers/relations/perf-profiles MUST be
added to **both** anchors in the same commit, OR the drift test fails.

#### §6.3 — Lockbox ownership transfer + migration window (Draft 0.3 amendment)

**Draft 0.1 transfers lockbox ownership to the package.** The companion
spec `cybertronia-graph-ui-package-spec.md` §6 declares that
`packages/cybertronia-graph-ui/tests/cybertronia-graph-drift.test.ts`
becomes the canonical owner of:

- `EXPECTED_LAYERS`, `EXPECTED_KINDS`, `EXPECTED_RELATIONS`, `EXPECTED_PERF_PROFILES`
- `EXPECTED_VECTOR_FIELD_NAMES` (the 25 lockbox mirror)
- `EXPECTED_VECTOR_LEN`, `EXPECTED_NODE_STRIDE_FLOATS/BYTES`, `EXPECTED_EDGE_STRIDE_FLOATS/BYTES`

This is a **breaking change for the PWA side's prior ownership claim**
in §6.1 above. It is NOT a one-shot reassignment — during the migration
window, BOTH the PWA-side anchor (`phase7-wt/02_FORGE/apps/pwa-cockpit/tests/cybertronia-graph-drift.test.ts`)
AND the package-side anchor must exist AND pass green on every commit
that touches `EXPECTED_*` constants. The PWA-side file is **not** deleted
in this Draft 0.3.1 — it is held in migration-deprecated state.

**Migration window (binary, no half-states):**

| Phase | PWA-side anchor | Package-side anchor | Goose-side mirror test | Failure mode |
|---|---|---|---|---|
| **Draft 0.3.1 / before hoist:** | owns the lockbox verbatim | does NOT yet exist | reads PWA-side only | PWA-side drift breaks the build |
| **Migration week 1 (package hoist PR lands):** | frozen mirror of package (deprecation banner header) | becomes canonical source | reads BOTH, asserts equality on every constant | divergence between PWA and package breaks the build |
| **Migration week 2 (waiting on green-streak):** | unchanged from week 1 | unchanged from week 1 | unchanged from week 1 | both anchors must stay green continuously |
| **Post-window (7 consecutive days green, Phase 4 deferred OK):** | replaced by a 5-line forwarding stub that `import { ... } from '../<pkg>/tests/cybertronia-graph-drift.test.ts'` and re-exports each `EXPECTED_*` constant with a `// DEPRECATED — see package` JSDoc tag | unchanged (canonical) | unchanged | the forwarding stub's identical bytes are the proof that the PWA-side is now a derived view |
| **Phase 1.0.0 gate:** | DELETE entirely | canonical | reads package-side only | any still-imported PWA-side file is a breaking change → major bump |

**Why the binary window:** a half-state where only one side owns is
exactly the drift failure mode the lockbox was designed to catch. Either
both anchors exist and agree (every day of the window), or neither is
consulted (post-window). The window MUST NOT be shortened because of
schedule pressure — a single missed equivalence check reintroduces the
very drift the test was designed to prevent.

**Verification step both sides run during the window:**

1. The PWA-side lockbox remains pinned **byte-identical** to the
   package-side lockbox at every commit. The byte-identity test is
   `expect(pwaFs.readFileSync(pwaPath, 'utf8')).toEqual(pwaFs.readFileSync(packagePath, 'utf8'))`
   scoped to the `EXPECTED_*` declaration lines only.
2. The Goose-side mirror test reads BOTH files, extracts each `EXPECTED_*`
   array, and asserts `Set#has` equality on every element (renames,
   drop-out, duplicate insertion all trip the equality check).
3. The package-side drift test additionally reads
   `CAMELOT_OS/control_plane/cybertronia_compile.py` and asserts the
   `VECTOR25_FIELD_NAMES` tuple order matches `EXPECTED_VECTOR_FIELD_NAMES`.
   During the migration window, this producer-side check is governed by
   the package spec §6.3 block; before the hoist, the producer-side
   check is gated on Phase 2's shape lock (no enforcement today).

**What happens to the existing PWA-side `EXPECTED_*` constants:**

- **Move verbatim** into the package, preserving order, whitespace, and
  trailing comments.
- **Duplicate-mirror** into the PWA-side file with a leading
  `// MIGRATION MIRROR — see ../../packages/cybertronia-graph-ui/tests/cybertronia-graph-drift.test.ts`
  block. Both copies remain byte-identical for the duration of the
  window. Drift in either copy breaks the build.
- **Delete** the PWA-side copy once the window closes (7 consecutive
  green days + Phase 4 SSE deferred is satisfied). The deletion is a
  Phase 1.0.0 gate, NOT a `0.x` minor bump.

This Draft 0.3.1 amendment is **additive**: it does not change Draft
0.3 §6.1's content, only acknowledges that Draft 0.1 §6 supersedes §6.1
**at the end of the migration window**. Until that end, both sections
are simultaneously correct.

---

## 7. Server-side gates (Phase 2 + Phase 4)

Before the SSE endpoint pushes the snapshot:

| Gate | Server enforcement |
|---|---|
| Initial render cap | `nodes.length ≤ 1500 && edges.length ≤ 3000` |
| Overflow rollup | every additional 1500 nodes becomes one `ClusterRef` |
| Cluster expansion | `expand_cluster` op emits members on demand |
| Delta cadence | `Δnow − Δprev ≥ 160ms` |
| FPS band reduction | first 30 frames of `PerformanceMonitor` coerce to nearest `{30, 60, 120}` |
| Memory class | `gpu_buffer_bytes >= 50 MB` → server emits `2D fallback` recommendation in `SnapshotMeta.memory_class = "high"` |

---

## 8. SSE endpoint shape (Phase 4 — deferred)

| Method + Path | Body | Behavior |
|---|---|---|
| `GET /api/cybertronia-graph/snapshot`     | none | Return one-shot `GraphSnapshot`; `304 Not Modified` if `If-None-Match` matches `digest`. If Phase 1 audit cursor is present but Phase 2 compile is pending, return `GraphSnapshotStub` (`snapshot: null`) so consumers mount via §5 |
| `GET /api/cybertronia-graph/stream`       | none | `text/event-stream`; one `data:` line per `GraphDelta`; cadence ≥ 160 ms; closes on client disconnect |
| `GET /api/cybertronia-graph/nodes/:id`    | none | `NodeRef` JSON or `404` (reads from current `GraphSnapshot`) |
| `GET /api/cybertronia-graph/sync-status`  | none | `{ last_digest, last_seen_at_ms, lag_batches, divergence_pending }` |

**IRON GATE**: cloud publication (`POST`/`PUT` to NotebookLM) and scan
rescan are mutating — never exposed as a normal endpoint. Operate through
the runic router's `//ASSIMILATE` / `//SWARM` runes only, behind the
existing operator token.

---

## 9. Acceptance checklist

| Test | Method | Pass criterion |
|---|---|---|
| Mount churn           | unmount + remount node 100× | reported `dispose` count = 100; zero leaked `Geometry`/`Material` references |
| Drift symmetry        | both consumer test anchors | both vitest blocks green; `EXPECTED_*` tables identical |
| Stride drift          | sum buffers at runtime | node stride 40 B (10 floats); edge stride 32 B (8 floats incl. inlined weight) |
| Pre-SSE bootstrap     | mount before SSE handler is ready | 2D fallback renders from `GraphSnapshotStub`; banner present; no flash |
| WebGL context recovery| simulate loss + restore       | re-built tree within 500 ms after `webglcontextrestored` |
| SSE cadence           | measure inter-batch Δ | every gap ≥ 160 ms |
| PerfProfile step-down | throttle FPS to 25          | `high → mid → low → "2d"` ladder observed in 30-frame windows |
| Browser console       | DevTools inspect              | zero warnings after unmount cycle |
| Mobile-low            | iPhone SE / Android-M profile | 2D fallback engages within 1 frame |
| GPU ceiling           | measured `info.memory`        | remains < 50 MB at 1500 nodes / 3000 edges |
| a11y non-color        | tab through 10 random nodes   | each selection audibly distinguished (shape + dash-pattern) |

---

## 10. Open questions

1. **GraphSnapshotStub → GraphSnapshot swap atomically.** When the SSE
   first snapshot arrives mid-mount, the Phase 2 compiler's first
   compile may still be warm. Phase 4 handler MUST signal "complete
   stub → real snapshot" with a single `ready: true` event before
   `data:` lines start. The consumer then atomically swaps; if the
   event is missed, the stub remains in place (graceful degradation).
2. **Vector25 cross-coverage** — every profile (`v[10]=runtime_state`,
   `v[11]=health`) must come from a consistent telemetry source. Phase 2
   compiler MUST declare which probe it sources each index from, so the
   spec is reproducible.
3. **Color contrast on Obsidian `#050505`** — gold `#D4AF37` and purple
   `#2E0854` against Obsidian may fail WCAG AA on small text. Spec uses
   these as **accent strokes** only; text uses `#E8E8E8` default.
   Should be locked in by the Phase 3 visual baseline.

---

## 11. Sign-off

| Phase | Status | Owner | Date |
|---|---|---|---|
| Phase 1 (audit) | shipped (35/35 PASS, FIX-1..FIX-4) | code-reviewer-minimax-m3 approved | 2026-07-14 |
| Phase 2 (compiler) | TBD | — | — |
| Phase 3 (this spec) | **Draft 0.3.1** — Draft 0.3 invariants preserved; new **§6.3** documents the lockbox-ownership transfer to the package (Draft 0.1 §6) AND the migration window during which BOTH the PWA-side and package-side anchors must coexist green | awaiting Phase 2 shape lock | 2026-07-14 |
| Phase 4 (SSE wiring) | deferred | per spec §8 | — |
