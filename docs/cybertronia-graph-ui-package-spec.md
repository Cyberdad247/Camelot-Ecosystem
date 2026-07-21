# cybertronia-graph-ui — Shared Package Spec (Draft 0.1)

> Companion to **[cybertronia-graph-ui-spec.md Draft 0.3](./cybertronia-graph-ui-spec.md)**.
> Where Draft 0.3 (the **upstream contract**) defines *what the data looks
> like*, this Draft 0.1 (the **shared-package spec**) defines *how a
> consumer imports, mounts, and shares state with the package*.
>
> Two consumers race against the same boot timeline:
> 1. **PWA Cockpit lazy cartridge** (Next.js 16 App Router slot)
> 2. **Anya Dashboard graph panel** (modal/sidebar in the cognitive surface)
>
> Both mount in parallel against `GraphSnapshotStub` until Phase 2's compiler
> ships and Phase 4 SSE delivers the first real `GraphSnapshot`.

| Field | Value |
|---|---|
| Status | **Draft 0.1** — package identity chosen, public/transport surface split decided, mount contract defined as `<CybertroniaSurface>`, drift-test ownership transferred from PWA to the package; **Phase 4 SSE wiring deferred** |
| Companion | `cybertronia-graph-ui-spec.md` (Draft 0.3) — the upstream contract; this document never disagrees with Draft 0.3, only references it |
| Producer (data) | `control_plane/cybertronia_audit.py` (Phase 1) → `control_plane/cybertronia_compile.py` (Phase 2, TBD) → `control_plane/cognitive_service.py` (Phase 4 endpoints, TBD) |
| Consumer A | `phase-verify-wt/02_FORGE/packages/cybertronia-graph-ui/...` — the package itself |
| Consumer B usage | `phase-verify-wt/02_FORGE/PORTAL_CORE/web/components/cockpit/CybertroniaCartridge.tsx` (Cockpit slot, TBD) |
| Consumer C usage | `CAMELOT_OS/dashboards/anya/graph-panel/` (Anya panel, TBD) |

---

## 0. Glossary

| Term | Definition |
|---|---|
| `package` | The `cybertronia-graph-ui` shared module declared in this document |
| `consumer` | A Next.js / React surface that imports and mounts the package — PWA Cockpit cartridge and Anya Dashboard panel |
| `mount` | The act of rendering `<CybertroniaSurface payload={...}>` at a consumer slot |
| `parallel mount` | Two consumer instances live simultaneously on the same browser page; their `SelectionState` converges via `sessionStorage` per Draft 0.3 §3 anchor point |
| `phase gate` | The transition point at which the package accepts a real `GraphSnapshot` from Phase 4 instead of the consumer-built `GraphSnapshotStub` |
| `transport` | Internal package code that moves payloads (delta stream, atomic swap, SSE) — deliberately *not* part of the package's public exports |

---

## 1. Package Identity & Integration

### 1.1 Naming + workspace placement

> ⚠️ **PRE-HOIST NOTE (Draft 0.1.1 addendum).** Until the workspace hoist
> refactor (the four steps below) lands, the `cybertronia-graph-ui`
> package **does NOT exist as an enforced boundary**. The v2 code is
> still co-located in
> `phase-verify-wt/02_FORGE/PORTAL_CORE/web/components/scene/CybertroniaR3FMap.*`
> and is reachable as named exports. **None of §1.3's export-boundary
> promises are enforceable yet.** Pre-hoist, a consumer can still
> `import { CybertroniaBackingStore, tryAtomicSwap, Vector25 } from
> '@/components/scene/CybertroniaR3FMap.backingStore'` — the package
> name claims existence but the package directory does not. The §1.3
> promises become enforceable on the day the four hoist steps complete
> AND the §6.3 migration window opens (see Draft 0.3.1 §6.3).

- **Package name**: `cybertronia-graph-ui`
- **Reserved by**: Draft 0.3 §header ("The package name `cybertronia-graph-ui` is reserved; do NOT claim the name until Phase 3 ships" — this Draft 0.1 *is* the Phase 3 claim).
- **Workspace directory**: `phase-verify-wt/02_FORGE/packages/cybertronia-graph-ui/`
  - Currently the v2 implementation lives at `phase-verify-wt/02_FORGE/PORTAL_CORE/web/components/scene/CybertroniaR3FMap.*`. The Hoist refactor is the first action item after Draft 0.1 sign-off:
    1. `git mv` the seven `CybertroniaR3FMap.*` files into `packages/cybertronia-graph-ui/src/`.
    2. Replace intra-PORTAL_CORE imports with `import { ... } from 'cybertronia-graph-ui'`.
    3. Add `packages/cybertronia-graph-ui/package.json` (private workspace, name `cybertronia-graph-ui`, no publish).
    4. Add `packages/cybertronia-graph-ui/tsconfig.json` (extends `../../tsconfig.json` with `composite: true` for project references).

### 1.2 Semantic versioning policy

- **Pre-1.0**: `0.1.x` until Phase 4 SSE lands. Breaking changes bump `0.x` minor.
- **Phase 4 ship**: bump to `0.2.0` (SSE consumer enters the public surface as `useCybertroniaSSE`).
- **1.0.0 gate**: bumps when both (a) the package is consumed by the
  Goose-side mirror (Draft 0.3 §6.1 lockbox), AND (b) Phase 2 + Phase 4
  have produced a stable digest for ≥7 days.
- **Cross-shape revisions**: `cybertronia.snapshot/v2` is *not* an automatic
  bump. It is an authoritative schema change gated by Draft 0.3 §1's
  `schema_version` literal type. The consumer *must* maintain two-way
  shims for any `v*` value shipped by the producer — see §6.4.

### 1.3 Public export surface — consumer types only

> ⚠️ **PRE-HOIST NOTE (Draft 0.1.1 addendum).** The list below is a
> **forward-looking contract**. Pre-hoist, every name in §1.3 is also
> reachable directly from the v2 source files in PORTAL_CORE, AND every
> name in the §1.3 *internal* list (e.g. `CybertroniaBackingStore`,
> `tryAtomicSwap`, `Vector25`, `calcFlyToCamera`, all stride constants)
> is similarly reachable — there is no `src/index.ts` gate today. The
> day the §1.1 hoist completes, this list becomes the **only safe import
> surface**: the package's `src/index.ts` MUST literal-export every
> name below and MUST NOT export anything from the internal list. Any
> consumer that imported an internal name pre-hoist MUST rename to the
> equivalent public name or migrate to one of the listed hooks.
> Pre-hoist, the consumer MUST NOT use ANY of these names in new code —
> use the v2 file path equivalents until the hoist lands.

The package's `src/index.ts` exports *only the consumer-facing surface*.
Transport shapes the consumer cannot use directly stay internal:

| Public export | Source file | Consumer use |
|---|---|---|
| `GraphPayload` (type)           | `CybertroniaR3FMap.types.ts`  | The full payload union — what the consumer feeds into `<CybertroniaSurface>` and what the consumer reads back from `useSelectionState()`. |
| `GraphSnapshot` (type)          | `CybertroniaR3FMap.types.ts`  | Narrow guard before rendering 3D (e.g. `if (isGraphSnapshot(payload)) { ... }`). |
| `GraphSnapshotStub` (type)      | `CybertroniaR3FMap.types.ts`  | Pre-SSE fallback signal — consumer constructs this from the Phase 1 audit cursor. |
| `SelectionState` (type)         | `CybertroniaR3FMap.selection.ts` | Read from `useSelectionState()` when the consumer wants to mirror selection into its own UI (e.g. an Anya "currently selected" badge). |
| `SelectionEvent` (type)         | `CybertroniaR3FMap.types.ts` | Consumer-built events fed back via `dispatchSelection(event)` for keyboard shortcuts. |
| `PerfProfile` (type)            | `CybertroniaR3FMap.types.ts` | Initial `SnapshotMeta.perf_profile` decoded by the consumer-built payload. |
| `NodeId` (type)                 | `CybertroniaR3FMap.types.ts` | All `id` fields and selection arrays use this opaque string. |
| `<CybertroniaSurface>` (component) | `CybertroniaR3FMap.v2.tsx`  | The mount point (see §2). The consumer DOES NOT need any other runtime import. |
| `useSelectionState` (hook)      | `CybertroniaR3FMap.selection.ts` | React-side read of the package's backing-store selection (no-op until `dispatchSelection` is called). |
| `dispatchSelection` (function)  | `CybertroniaR3FMap.selection.ts` | Imperative consumer-side selection action (forwarded to `applySelection(prev, event)`). |
| `decideBranch` (pure function)  | `CybertroniaR3FMap.tsx`       | `payload.snapshot === null ? '2d' : '3d'` — exported so consumers can pre-branch for layout (e.g. reserving canvas area). |
| `isGraphSnapshot` (type guard)  | `CybertroniaR3FMap.types.ts`  | Discriminated-union guard for the snapshot half of `GraphPayload`. |

**Internal — NOT exported** (the package owns these; consumer never names them):

- `CybertroniaBackingStore`, `getCybertroniaStore`, `tryAtomicSwap`, `applyDelta`, `applyDeltaOp`, `compareHlt`
- `DeltaOp`, `GraphDelta`, `SyncStatusResponse`, `UseCybertroniaSSEReturn`, `Vector25`, `Vector25Index`
- `calcFlyToCamera`, `calcFlyToTimeline`, `calcBob` — internal easing only
- `CybertroniaNode3D`, `CybertroniaEdge3D`, `V2Node`, `FlyToController`, `StubBanner`, `SceneInner` — internal JSX
- All typed-array stride constants (`NODE_STRIDE_FLOATS=10`, `EDGE_STRIDE_FLOATS=8`, …)

Rationale (Q4 from design review): keeping the buffer/swap/delta machinery
internal so a future v2-shaped refactor (e.g. switching from
InstancedMesh to a single Points render path) never ripples to consumers.
The drift test (see §6) is the only place these internals are pinned.

### 1.4 Peer dependency policy

The package declares React 18.x + R3F 8.x + drei 9.x + three 0.16x as **peer
dependencies**. They are NOT bundled — the workspace host (PWA
`next@^16`, Anya side via `vite`/`rollup`) owns its own resolution. This
keeps the package from picking lock-step versions that would otherwise
fight the host's React upgrade cycle.

---

## 2. Component Mount Surface & Routing

The package exposes ONE public component:
`<CybertroniaSurface payload={...} onSelectionChange={...} />`. All
consumer surfaces (PWA Cockpit, Anya Dashboard) compose their slot as:

```tsx
import { CybertroniaSurface, type GraphPayload } from 'cybertronia-graph-ui';

export default function CockpitCybertroniaCartridge() {
  const [payload, setPayload] = useState<GraphPayload>(stubFromAuditCursor());
  return (
    <div className="cockpit-cartridge cybertronia">
      <CybertroniaSurface
        payload={payload}
        onSelectionChange={(s) => /* log or mirror into Anya panel */ console.log(s)}
      />
    </div>
  );
}
```

### 2.1 Self-branching — `decideBranch` is the only fork

`<CybertroniaSurface>` calls the package's internal `decideBranch(payload)`
to decide between the 2D fallback sub-tree and the 3D scene tree. **The
consumer never branches externally.** This is intentional: when the
package's `PerfProfile` step-down logic (see §5.2) decides to demote to
2D, the surface swaps sub-trees atomically — the consumer doesn't need
any "did it switch?" handshake.

```typescript
// Internal — pure, exported only because consumers want layout reserves
export function decideBranch(payload: GraphPayload | null): '2d' | '3d' {
  return payload === null ? '2d'
    : payload.snapshot === null ? '2d'
    : '3d';
}
```

### 2.2 Layout reservation contract

If the consumer needs to reserve canvas area before the first commit
(SSR, layout-shift prevention), call `decideBranch(stub)` on the stub
the consumer will eventually pass in. The pure function returns the
exact branch the package will mount.

### 2.3 What the consumer MUST NOT do

- **Do not import** any `CybertroniaR3FMap.*` file directly. Use the
  package entrypoint. (When the workspace hoists the v2 files into the
  package, internal imports `@/components/scene/CybertroniaR3FMap.foo`
  become package-internal.)
- **Do not construct** `CybertroniaBackingStore` directly. The package
  owns the singleton. Consumers can subscribe via `useSelectionState`.
- **Do not branch on `payload.snapshot === null`** for layout decisions
  other than reserving space. The package's `decideBranch` already
  handles both branches atomically — overriding it risks a flash
  between stub banner and 3D scene.
- **Do not pass `Vector25`-shaped objects** as input. The package reads
  `payload.vectors` (a `Record<NodeId, Vector25>`) for rendering; passing
  raw vectors is internal.

---

## 3. Pre-SSE Bootstrap (Phase 2 deferred)

Until Phase 2 compiler + Phase 4 SSE ship, the producer side delivers no
`GraphSnapshot` over the wire. The consumer is responsible for
constructing a `GraphSnapshotStub` and feeding it to the package — this
is the only path that keeps the renderer mounted and the 2D fallback
banner visible without network reads.

```typescript
// Consumer-side helper — NOT shipped by the package (different read paths)
import { type GraphSnapshotStub } from 'cybertronia-graph-ui';
import { readAuditCursor, readScanMeta } from '@/lib/audit';

export async function stubFromAuditCursor(root: string): Promise<GraphSnapshotStub> {
  const cursor = await readAuditCursor();
  const meta   = await readScanMeta();
  return {
    snapshot: null,
    fallback_2d: true,
    source: 'audit-cursor',
    scan_id: cursor?.scan_id ?? null,
    cursor_last_path: cursor?.last_path ?? null,
    completed_at: meta?.completed_at ?? null,
    nodes_total: cursor?.files_seen ?? 0,
    fallback_reason: 'audit_cursor_only',
  };
}
```

The package **does not** read Phase 1 audit data on its own — that's
explicit so the same package can mount in tests, in CI, in admin
panels, and in offline previews without coupling to a specific filesystem
location.

When `useCybertroniaSSE` lands (Phase 4), the consumer's `stubFromAuditCursor`
call is replaced by a hook that returns either a stub (Phase 1 only) or a
live `GraphSnapshot` (Phase 1 + Phase 2 + Phase 4 wired). The package's
`<CybertroniaSurface>` accepts whichever the consumer hands it.

---

## 4. State Management & Parallel Consumers

### 4.1 Single backing store inside the package

Per Draft 0.3 §4.3 step 1, the backing-store commit (`commitAtomic`) is
the *only* mutation root. The package owns one singleton
`CybertroniaBackingStore` per browser context (mounted via
`window.__cybertroniaSnapshot` for cross-tab continuity, mirroring Draft
0.3 §4.3 step 1 anchor paragraph).

`<CybertroniaSurface>` is a `useSyncExternalStore` reader of this
singleton. Consumers NEVER name the store; they only consume the
selection state via `useSelectionState()` (a thin hook that delegates
back into the same `useSyncExternalStore`).

### 4.2 Parallel-mount convergence via sessionStorage

When both the PWA Cockpit cartridge AND the Anya Dashboard panel are
mounted on the same browser tab, a node selected in PWA's surface must
show as selected in Anya. The convergence is **NOT** by sharing one
React subtree (which would force one mount); it is by sharing
`SelectionState` via `sessionStorage`:

1. When `dispatchSelection(event)` is called, the reducer updates the
   selection AND mirrors the new `SelectionState` to
   `sessionStorage[__CYBERTRONIA_SELECTION_KEY]`.
2. On mount, `<CybertroniaSurface>` reads `sessionStorage` for a prior
   selection and seeds its local view.
3. When another tab's `selectionchange` (or local `storage` window event
   for cross-tab convergence) fires, the package re-applies the
   `SelectionState` from storage with a flag `external: true` to avoid
   re-mirroring (no `storage-echo` loop).

Keys and namespace are constants exported alongside `decideBranch`:

```typescript
// Internal but exported for key stability — see §6 drift test
export const CYBERTRONIA_SELECTION_KEY = 'cybertronia:selection:v1';
export const CYBERTRONIA_PAYLOAD_KEY   = 'cybertronia:payload:v1';
```

(Yes, the payload *also* caches to sessionStorage. This means a single
Phase 4 mirror tab with the packge mounted can populate the graph for
the other tab via sessionStorage — *only if* the consumer calls the
package's `mirrorPayloadToSession()` explicitly. Off by default.)

### 4.3 SelectionState cross-surface — semantics

Each guard in Draft 0.3 §3 (focus, multi, filter, edge highlight, camera
target) round-trips through the singleton store. The selection reducer
(see `CybertroniaR3FMap.selection.ts:applySelection`) already enforces:

- `MAX_SELECTION = 25` cap on cmd_click multi-add
- `FLY_TO_DURATION_MS = 800` for camera-target transitions
- `hover/unhover` does NOT disturb `camera_target`
- `escape` resets to `defaultSelection()`

The package spec inherits all of these from Draft 0.3 §3 verbatim. No new
selection semantics are introduced by the package — Draft 0.3 is the
canonical anchor.

### 4.4 Same-tick parallel-mount ordering + baseUrl-hashed window namespace

When the PWA Cockpit lazy cartridge AND the Anya Dashboard panel both
mount in the same browser tab during the same React commit tick (a real
case: the Anya panel opens a modal over the cockpit without unmounting
it — both `<CybertroniaSurface>` instances come alive on the same
`useEffect` cycle), the order they mount determines:

1. Which surface owns the singleton backing store on first commit.
2. Which `sessionStorage[__CYBERTRONIA_SELECTION_KEY]` value is chosen
   as the seed for both mounts (§4.2 step 2 — the last writer wins).
3. Which `window.__cybertroniaSnapshot` global is canonical.

Without a pinned ordering rule, React's commit ordering is undefined
across sibling subtrees, so three different booting profiles can produce
three different selections on first paint. The package defines the
ordering rule as **canonical, not advisory**:

> **Ordering rule (4.4.1).** PWA Cockpit mounts FIRST and acts as the
> *anchor surface* during the same commit tick. Anya panel mounts
> SECOND and reads selection from `sessionStorage` seeded by PWA's
> mount. The rule is enforced by ordering: in BOTH surfaces, the
> `<CybertroniaSurface>` component MUST be the first sibling of the
> surface root, and the consumer MUST publish a `data-mount-order`
> attribute (`"anchor"` for PWA, `"follower"` for Anya) so the package's
> internal mount handler can verify the order at boot. If Anya mounts
> first, the package logs `[cybertronia] mount-order violated: Anya
> before PWA — selection will be undefined on first frame` and treats
> it as a `WARN` in dev tools but does not abort. If PWA mounts first,
> silent.

Why PWA is the anchor:

- PWA is the lockbox owner per Draft 0.3 §6.1 / Draft 0.3.1 §6.3 — it
  carries the canonical `EXPECTED_*` constants into a mount cycle.
- Anya is the cognitive surface; if it ever owns selection on first
  paint, the cockpit user sees a stale selection drift without an
  opportunity to correct it.
- Cognitively, the cockpit is "where you go to look at the graph", so
  its selection is the user's intent; the Anya panel is "where you go
  to discuss the graph", so its selection is downstream.

> **Window namespace rule (4.4.2).** The `window.__cybertroniaSnapshot`
> global mentioned in Draft 0.3 §4.3 step 1 is namespaced per-`baseUrl`
> when the package mounts against multiple Phase 4 SSE endpoints
> concurrently (e.g. `https://cockpit.local` and `https://anya.local`
> in the same browser tab — the same-origin policy does NOT isolate
> `window` between these because they are the same origin). The key
> shape is:

```typescript
// Internal — exported only because the §6.3 drift test pins it.
export function cybertroniaWindowKey(baseUrl: string): string {
  // sha256(baseUrl).slice(0, 8) — fixed length, opaque, baseUrl-stable
  const h = sha256Hex(baseUrl).slice(0, 8);
  return `cybertronia:snapshot:${h}`;
}

export function cybertroniaSessionKey(baseUrl: string): string {
  // sessionStorage key (separate key namespace from window global).
  // Same hash so a consumer searching for "which keys does this
  // surface own" gets a single greppable pattern.
  const h = sha256Hex(baseUrl).slice(0, 8);
  return `cybertronia:payload:${h}`;
}
```

The §1.3-listed `CYBERTRONIA_SELECTION_KEY` constant stays GLOBAL
(`'cybertronia:selection:v1'` — selection is a per-tab concept, not
per-endpoint), and is the ONLY key not scoped by `baseUrl`. Both
`cybertroniaWindowKey` and `cybertroniaSessionKey` are explicitly
INTERNAL exports even though §6 names them — they appear in the lockbox
test for byte-stability but never in the public surface.

During Phase 1 (single `baseUrl` consumer), the namespace degrades
gracefully: `cybertroniaWindowKey('https://cockpit.local')` and the
literal `'__cybertroniaSnapshot'` resolve to the SAME global because
`sha256('https://cockpit.local').slice(0,8)` is the v0.1.x default.
Phase 4 introduces a second consumer-side `baseUrl`, and at that point
the explicit key function replaces the literal.

---

## 5. Internal Renderer Policy (Blackboxed)

### 5.1 InstancedMesh stride layout — INTERNAL

The byte strides from Draft 0.3 §4.2 stay un-exported:

| Stride constant         | Value | Bytes per element |
|---|---|---|
| `NODE_STRIDE_FLOATS`    | `10`  | `40`              |
| `EDGE_STRIDE_FLOATS`    | `8`   | `32`              |
| `NODE_CAP_INITIAL`      | `1500`| —                 |
| `EDGE_CAP_INITIAL`      | `3000`| —                 |
| `STRIDE_SENTINEL`       | `NaN` | `4`               |

The package's internal drift test (see §6.3) re-exports these as named
constants so they appear in the test file but consumers cannot name
them. Future refactors (e.g. moving to a Points-based render path) may
delete some of them; the spec only constrains that **the package's
lockbox test reflects Draft 0.3 §4.2 verbatim**.

### 5.2 PerformanceMonitor — internal, single owner

Draft 0.3 §4.1's `PerformanceMonitor` runs inside `<CybertroniaSurface>`.
It is the single owner of the `PerfProfile` step-down/step-up ladder:

- `high → mid → low → "2d"` (then auto-engages the 2D fallback tree)
- Step-up is permitted only after `30 consecutive frames ≥ expected_fps_band + 5`
- `hidden` is one-way: never stepped away from when set by
  `document.hidden` / Page Visibility

The consumer influences `PerfProfile` ONLY through `SnapshotMeta.perf_profile`
(e.g. Phase 2 emits `"low"` because the host's GPU class is mobile).
The package's `PerformanceMonitor` clamps to the lower of
`SnapshotMeta.perf_profile` and the frame-driven verdict.

### 5.3 Component lifecycle — dispose on unmount

Every Geometry / Material / Texture / RenderTarget that
`<CybertroniaSurface>` creates is disposed on unmount. Draft 0.3 §9's
"mount churn" test (100× unmount/remount, expect 0 leaked
`Geometry`/`Material` references) is in the package's lockbox test, not in
the PWA's. The acceptance criterion is **the package code**, never a
property the consumer has to verify.

### 5.4 WebGL context loss recovery — internal

Per Draft 0.3 §4, a `webglcontextlost` listener rebuilds the
InstancedMesh from `base_digest + last_good_delta` after one retry. If
the retry fails, `<CybertroniaSurface>` synchronously swaps to the 2D
subtree (same atomic swap semantics as a stub → snapshot transition).

---

## 6. Cross-Worktree Drift Contract (Package Ownership Transfer)

Draft 0.3 §6 specifies that **PWA side OWNS the lockbox** in
`phase7-wt/02_FORGE/apps/pwa-cockpit/tests/cybertronia-graph-drift.test.ts`.
This Draft 0.1 **transfers ownership** to the package itself: the
canonical drift anchor lives at
`packages/cybertronia-graph-ui/tests/cybertronia-graph-drift.test.ts`.
Both consumers import the package's anchor; neither owns a copy.

Why the transfer:
- The Goose-side mirror in Draft 0.3 §6.1 reads the PWA-side file at
  test time. With the package in charge, the Goose-side mirror reads
  the **package** test file, which is single-source-of-truth across all
  consumers.
- The package's lockbox test pins both: (a) Draft 0.3 invariants as
  `EXPECTED_*` constants, AND (b) Python-producer invariants read from
  `CAMELOT_OS/control_plane/cybertronia_compile.py:VECTOR25_FIELD_NAMES`.

### 6.1 Lockbox pins owned by the package

```typescript
// packages/cybertronia-graph-ui/tests/cybertronia-graph-drift.test.ts
import { describe, it, expect } from 'vitest';
import type { NodeLayer, NodeKind, RelationKind, PerfProfile } from '../src';

// OWNED BY THIS FILE. Consumers + Goose-side mirror read + assert equality.
const EXPECTED_LAYERS  = ['bin','control_plane','02_FORGE','03_VAULT','runtime']
  as const satisfies readonly NodeLayer[];
const EXPECTED_KINDS   = [
  'file','dir','symlink','volume',
  'runtime_service','process_group','listener_port',
] as const satisfies readonly NodeKind[];
const EXPECTED_RELATIONS = [
  'imports','wires','extends',
  'spawns','exposes','consumes',
  'depends_on','builds_into','reads_from',
] as const satisfies readonly RelationKind[];
const EXPECTED_PERF_PROFILES = ['high','mid','low','2d','hidden']
  as const satisfies readonly PerfProfile[];

// Mirror of Draft 0.3 §1's EXPECTED_VECTOR_FIELD_NAMES. Lockbox-cloned
// here so the Python producer-side VECTOR25_FIELD_NAMES tuple can be
// cross-checked against this list (see §6.3).
const EXPECTED_VECTOR_FIELD_NAMES = [
  'layer','type','path depth','size','file count',
  'recency','churn','cpu cost','memory cost','storage cost',
  'runtime state','health','exposure','in_degree','out_degree',
  'centrality','betweenness','pagerank','community','criticality',
  'sensitivity','mutability','provenance','sync state','resource pressure',
] as const;

const EXPECTED_VECTOR_LEN          = 25 as const;
const EXPECTED_NODE_STRIDE_FLOATS  = 10 as const;
const EXPECTED_NODE_STRIDE_BYTES   = 40 as const;
const EXPECTED_EDGE_STRIDE_FLOATS  = 8  as const;   // Draft 0.3 — weight inlined
const EXPECTED_EDGE_STRIDE_BYTES   = 32 as const;
```

### 6.2 Drift vs Draft 0.3 lockbox

The package's drift test asserts:

| Property              | Reference side | Verification side |
|---|---|---|
| `EXPECTED_VECTOR_FIELD_NAMES` (25 strings) | `CybertroniaR3FMap.types.ts:Vector25Index` docstring | verbatim-byte match against Draft 0.3 §1 |
| `EXPECTED_*` constants (layers, kinds, relations, perf-profiles) | `CybertroniaR3FMap.types.ts` closed unions | structural equality via `satisfies` |
| Stride constants | `CybertroniaR3FMap.v2.tsx` typed-array allocation | pinned numeric match |

### 6.3 Drift vs `cybertronia_compile.py` producer

The test file reads `control_plane/cybertronia_compile.py` and pulls out
the `VECTOR25_FIELD_NAMES` tuple order (substring match against
`VECTOR25_FIELD_NAMES = (` block + word-token-extracted sequence +
`,' pack`). It then asserts:

```typescript
const PRODUCER_VECTOR_NAMES = /* extracted from cybertronia_compile.py */;
expect([...EXPECTED_VECTOR_FIELD_NAMES]).toEqual([...PRODUCER_VECTOR_NAMES]);
```

A failure here means **the producer and the consumer drifted**. Both
must move together.

### 6.4 Schema version coexistence

The package's `validateSnapshot(payload: unknown): payload is GraphSnapshot`
guard rejects any payload whose `schema_version` is not in the
`SUPPORTED_SCHEMA_VERSIONS` set:

```typescript
export const SUPPORTED_SCHEMA_VERSIONS = ['cybertronia.snapshot/v1'] as const;
```

When the producer cuts `cybertronia.snapshot/v2`, this constant is
extended (two-versions-supported at peak; old one removed when all
backups archive). The drift test extends the expected list at the same
time.

---

## 7. Phase 4 Deferred Integration Blueprint

Phase 4 SSE wiring is **deferred** in this Draft 0.1. The blueprint is
documented so Phase 4 lands without surprises:

| Step | Status | Action |
|---|---|---|
| 7.1 | **NOW** | Consumer builds `GraphSnapshotStub` from Phase 1 audit cursor (see §3). |
| 7.2 | **Phase 4 LANDS** | Consumer replaces `stubFromAuditCursor()` with `useCybertroniaSSE({ baseUrl })` from `control_plane/cognitive_service.py`. The package re-exports the same hook under the public surface as `useCybertroniaLivePayload()` (returns `GraphPayload | null` + `isLoading` + `error`). |
| 7.3 | Phase 4 LANDS | The package's `<CybertroniaSurface>` accepts either stub-from-consumer or live-from-hook. `decideBranch` continues to handle both. |
| 7.4 | Phase 4 LANDS | The atomic-swap state machine (`CybertroniaR3FMap.backingStore.tryAtomicSwap`) is **not** exported via the package public surface; consumers always interact through `<CybertroniaSurface>`. |
| 7.5 | Phase 4 LANDS | The package bumps to `0.2.0` (per §1.2 semver policy). Drift test still pins Draft 0.3 invariants unchanged. |
| 7.6 | Phase 4 LANDS (or pre-`0.2.0` consumer migration) | `<CybertroniaR3FMapV2>` rename → `<CybertroniaSurface>`. See §7.6.1 below.

#### §7.6.1 — Component-rename migration note (binary, fail-loud)

The public component is `<CybertroniaSurface>`, NOT `<CybertroniaR3FMapV2>`.
This is a **silent breaking change** for any consumer that imported the
v2 default export by its prior name. To make the migration binary
(not gradual), the package MUST fail loud on a dual-import:

```typescript
// Inside the package's src/index.ts — runs once at module load.
// Throws at module-evaluation time if both names are requested from
// the SAME consumer's compiled bundle (catches partial migrations).
if (typeof globalThis !== 'undefined') {
  const cybertroniaDualImportSentinel =
    '__cybertronia_dual_import_v2_to_surface_v0__';
  // The sentinel is set by the package's internal alias if a consumer
  // imports both names. Detection happens via TypeScript path mapping
  // during the package build (see package.json "exports" map below).
  Object.defineProperty(globalThis, cybertroniaDualImportSentinel, {
    value: (Symbol.for(cybertroniaDualImportSentinel) as unknown) ?? true,
    writable: false,
    enumerable: false,
    configurable: false,
  });
}
```

**The pre-`0.2.0` migration rule:**

1. Consumer imports `<CybertroniaSurface>` from `'cybertronia-graph-ui'`.
   The package's `package.json` `exports` map forbids
   `'cybertronia-graph-ui/CybertroniaR3FMapV2'` as a subpath — `next`
   and `vite` both refuse the import at build time, throwing a
   `Package subpath './CybertroniaR3FMapV2' is not defined by 'exports'`
   error before any module-load runs.
2. Consumer author MUST migrate all `import CybertroniaR3FMapV2 from
   'cybertronia-graph-ui'` callsites to
   `import { CybertroniaSurface } from 'cybertronia-graph-ui'`.
   The new name is the only allowed import.
3. Pre-hoist, packages do not exist; the `<CybertroniaR3FMapV2>` name
   stays importable from the v2 source files in PORTAL_CORE until the
   hoist lands. The rename becomes a hard error the day package.json's
   `exports` map is published with the package directory.
4. Phase 4 SSE bump to `0.2.0` is the consistent point at which the
   rename surfaces as a hard migration: any consumer still on `0.1.x`
   and importing `<CybertroniaR3FMapV2>` receives the `exports` map
   rejection from step 1 on next `pnpm install`.

**The fail-loud property:**

- Soft deprecation (just a JSDoc tag) does not work: GraphQL, ESBuild,
  and React's HMR all happily keep dual-importing until production
  build, where the collision surfaces as a runtime error or worse, a
  silent selection-state divergence.
- Fail-loud at module-load means that a single `pnpm dev` reveals the
  migration gap in seconds, not after a release cuts.
- The symbol-sentinel fails the dual-import check at TypeScript's
  `tsc --noEmit` time (via the package's `index.ts` re-export check)
  AND at runtime (via the module-load symbol).

The pre-`0.2.0` warning pattern is rejected in favor of a hard
TypeScript / runtime error to make the migration binary and visible.

Critical: the package's public surface in `0.1.x` is **designed to
behave identically whether or not Phase 4 SSE is wired**. The
mount contract (§2) and pre-SSE bootstrap (§3) cover the Phase-1-only
world; Phase 4 SSE re-routes the same `<CybertroniaSurface>` to consume
live payloads via the same prop.

---

## 8. Acceptance Checklist (Package-Local)

| Test | Method | Pass criterion |
|---|---|---|
| Mount churn     | unmount + remount `<CybertroniaSurface>` 100× | reported `dispose` count ≥ 100; zero leaked `Geometry`/`Material` references in Chrome DevTools |
| Drift symmetry (Goose mirror) | both consumer test anchors + Goose mirror | all three vitest blocks green; `EXPECTED_*` tables identical byte-for-byte |
| Drift vs producer | `tests/cybertronia-graph-drift.test.ts` reads python producer + asserts | `EXPECTED_VECTOR_FIELD_NAMES` byte-matches `cybertronia_compile.py:VECTOR25_FIELD_NAMES` |
| Pre-SSE bootstrap | mount before SSE handler is ready; consumer passes stub | 2D fallback renders; banner present; no flash |
| WebGL context recovery | simulate loss + restore | re-built subtrees within 500 ms after `webglcontextrestored` (1 retry) |
| Parallel mount | mount in PWA Cockpit AND Anya panel; select node in PWA | Anya panel re-renders with `selected_ids` matching (within 1 frame) |
| Step-down | throttle FPS to 25 | `high → mid → low → "2d"` ladder observed in 30-frame windows |
| Stride drift | sum buffers at runtime | node stride 40 B / 10 floats; edge stride 32 B / 8 floats (incl. inlined weight) |
| Scheme mismatch | feed an unknown `schema_version` (e.g. `v2`) | `validateSnapshot` returns false; package renders `StubBanner` with `fallback_reason: "sse_not_yet_built"` |
| SessionStorage echo | mount in two tabs; select in tab A | tab B reflects selection; no infinite `storage-event` echo loop on `__CYBERTRONIA_SELECTION_KEY` |
| Browser console | DevTools inspect | zero warnings after full unmount cycle on both PWA and Anya mounts |
| **GPU ceiling**           | load `GraphSnapshot` at 1500 nodes + 3000 edges; measure `renderer.info.memory` (geometry + texture + matrix budgets, not just typed-array bytes) | rendered GPU buffer footprint remains **strictly < 50 MB** at 1500 nodes / 3000 edges; reported via `SnapshotMeta.gpu_buffer_bytes` round-tripped through SSE; package's `gpu_buffer_bytes` MUST stay under cap for 100 consecutive frames during the §5.3 mount-churn run |
| **a11y non-color dash-pattern** | tab through 10 random nodes from the rendered scene; for each node the caption verifier reads BOTH the `CaptionMap.layers[layer].shape` AND the `CaptionMap.sensitivity[sensitivity].pattern` (solid / dashed / dotted); play every match to audible feedback (aria-label + shape name + dash-pattern name) | every selection is **audibly distinguished** — same-layer same-sensitivity MUST produce distinct shape+pattern combinations via the CaptionMap; no two tab stops may emit the same `(layer, sensitivity, aria)` triple; colors are not consulted; the test gates at the data layer (caption table) AND at the runtime layer (Tab + screen-reader picks up distinct shape names) |
| **Package build / tsc** | run `pnpm -F cybertronia-graph-ui build` AND `pnpm -F cybertronia-graph-ui exec tsc --noEmit` AND `pnpm exec tsc --noEmit --project phase-verify-wt/02_FORGE/tsconfig.json` (workspace root) | tsc reference graph is green; package's `exports` map compiles; **zero `any` introduced by the package** in `dist/`; the 3 tsc entrypoints: (1) `tsc --noEmit` against the package's own tsconfig (with `composite: true` for cross-package references), (2) `tsc --noEmit` against the workspace root tsconfig (Phase 18 pattern), (3) `tsc --noEmit` against each consumer's tsconfig (PWA `next@^16` + Anya `vite@^5`) |

---

## 9. Open Questions

1. **Hoist refactor scope.** §1.1 lists four concrete hoisting steps.
   Should the `git mv` happen as a single PR or split (move files first,
   then add package.json, then update imports)? Risk: a partial hoist
   leaves the workspace in a non-runnable state for the duration.
2. **`useCybertroniaLivePayload` naming conflict.** Phase 4 SSE hook
   inside the package (Q7 §7.2). If Goose-side mirror imports the same
   name for its own SSE consumer, the package's hook wins — Goose mirror
   must rename. Worth pre-registering.
3. **Cross-tab `storage` event debouncing.** Draft 0.3 §4.3 step 1
   allows `window.__cybertroniaSnapshot` global. If two tabs on the same
   host populate the singleton differently (different `baseUrl`), the
   last-write-wins on `__cybertroniaSnapshot` clobbers. Should the
   package namespace the global by `baseUrl` host hash?
4. **SnapshotMeta defaults when fields are missing.** Phase 1 stub
   `audit-cursor` reader produces a partial `SnapshotMeta`. Draft 0.3
   §1 declares `gpu_buffer_bytes?: number` optional; other fields are
   required. The package must accept consumer-injected defaults — to
   what extent should the package itself fill them?
5. **Spec vs implementation drift detection timing.** Adding a CI check
   that runs the package drift test and the Goose mirror drift test
   together, against the upstream `cybertronia-graph-ui-spec.md` and
   the `cybertronia_compile.py`, is unstated in Draft 0.3 §6. Should
   the package's `package.json` declare an `"extras": { "drift":
   ... }` field that codifies what the test reads?

---

## 10. Sign-off

| Phase | Status | Owner | Date |
|---|---|---|---|
| Phase 1 (audit) | shipped | code-reviewer-minimax-m3 approved | 2026-07-14 |
| Phase 2 (compiler) | TBD | — | — |
| Phase 3 (this package spec) | **Draft 0.1.1** — Draft 0.1 preserved; §1.1 + §1.3 pre-hoist banners added; §4.4 same-tick ordering rule (PWA = anchor, Anya = follower) + baseUrl-hashed window/session namespace added; §7.6 binary component-rename migration rule + dual-import symbol sentinel added; §8 fills the 3 missing acceptance gates (GPU ceiling, a11y dash-pattern, package-build/tsc); cross-refs Draft 0.3.1 §6.3 ownership transfer | awaiting package hoist + Goose mirror rename | 2026-07-14 |
| Phase 4 (SSE wiring) | deferred | per §7 | — |
