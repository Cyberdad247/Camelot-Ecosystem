# Website Builder Cartridge — Camelot-OS

> Omni-Eye Dashboard · `02_FORGE/apps/omni-eye-dashboard`

A five-stage inference-to-deploy pipeline that converts plain-language intent into a live website. Inference runs entirely on-device via the **Ouroboros 1.58-bit SSM** — no cloud model calls, no KV-cache growth.

---

## Architecture

```
User Intent
    │
    ▼
A. Inference ──── Rust AVX2 SSM (ouroboros binary, stdin/stdout JSON)
    │
    ▼
B. Parse & Theme ─ Zod v4 schema validation + WCAG contrast engine
    │
    ▼
C. CRDT Store ──── DAG-gated immutable snapshots, undo/redo
    │
    ▼
D. DAG Validation ─ Kahn's O(V+E) topological sort, cycle detection
    │
    ▼
E. Deploy ─────── Static HTML scaffold → Vercel CLI → live URL
```

### Pipeline Files

| Stage | File | Responsibility |
|---|---|---|
| A | `src/app/api/infer/route.ts` | Route Handler — spawns `ouroboros.exe` via `child_process` |
| A | `src/lib/infer.ts` | Client wrapper — `POST /api/infer`, enforces 101ms latency ceiling |
| B | `src/lib/parse-ast.ts` | JSON extraction, `ASTSchema` validation, `deriveTheme()` WCAG tokens |
| C | `src/lib/crdt.ts` | `AstStore` — immutable snapshots, undo/redo, `useSyncExternalStore` hook |
| D | `src/lib/dag.ts` | Full Kahn's `validateDAG()` + incremental `validateDelta()` |
| E | `src/lib/deploy.ts` | HTML code-gen, temp dir scaffold, Vercel CLI spawn |
| E | `src/app/api/deploy/route.ts` | Route Handler — `POST /api/deploy` |
| E | `src/lib/dispatch-deploy.ts` | Client wrapper — `dispatchDeploy()` |

---

## Agents

| Knight | Role | Owns |
|---|---|---|
| **Sir Hydron** 🛠️ | The Hand | Code & UI generation |
| **Sir Visage** 🎨 | The Eye | Visual analysis, mockup generation |
| **Sir Syntax** | The Code Architect | TypeScript quality, Zod schemas, App Router |
| **Sir Stitch** | The Interface Architect | Accessibility, responsive composition |
| **Sir ForgeMaster** ⚒️ | The Agentic Smith | Workflow DAGs, pipeline orchestration |
| **Sir Alchemist** ✨ | The Optimization Smith | Bundle perf, AVX2 hot paths |
| **Baron Vaelen** | The Iron Industrialist | Infra, CI/CD, Vercel deploy |

---

## Ouroboros Engine

The inference engine is a **1.58-bit State Space Model** in `excalibur-dev/crates/ouroboros`.

- **Weights**: simulated ternary `{-1, 0, +1}` — no floating-point weight matrix
- **State**: fixed `Vec<f32>` of `state_dim` (default 256) — zero KV-cache growth across all turns
- **AVX2 hot path**: 8-lane `_mm256_fmadd_ps` when `target-feature=+avx2,+fma`; scalar fallback otherwise
- **Tokenizer**: FNV-1a hash per word → `u32` token id
- **Component vocab**: keyword match first, SSM logit fallback — resolves intent to one of 10 tags

### Component Tags

`hero` · `nav` · `features` · `testimonial` · `pricing` · `gallery` · `cta` · `contact` · `footer` · `card`

### Wire Protocol

```json
// stdin  → ouroboros binary
{ "intent": "add a hero section", "state_dim": 256 }

// stdout ← ouroboros binary
{ "ast_json": "{\"id\":\"…\",\"pid\":null,\"tag\":\"hero\",\"props\":{…}}", "latency_ms": 0.8 }
```

---

## Build

### 1. Compile Ouroboros

```powershell
# From excalibur-dev/
cargo build --release -p excalibur-ouroboros
# Binary → target/release/ouroboros.exe
```

AVX2 is enabled by `.cargo/config.toml`:
```toml
[target.x86_64-pc-windows-msvc]
rustflags = ["-C", "target-feature=+avx2,+fma"]
```

### 2. Install JS Dependencies

```powershell
cd 02_FORGE/apps/omni-eye-dashboard
pnpm install
```

### 3. Run Dev Server

```powershell
pnpm dev
# Turbopack · http://localhost:3000
```

### 4. Production Build

```powershell
pnpm build
```

---

## API Reference

### `POST /api/infer`

Spawns the ouroboros binary and returns an AST node for a given intent string.

**Request**
```json
{ "intent": "add a pricing section", "state_dim": 256 }
```

**Response**
```json
{ "ast_json": "…", "latency_ms": 0.9 }
```

Latency ceiling: **101ms**. Exceeding it returns HTTP 504.

Binary path resolves as:
1. `OUROBOROS_BIN` env var
2. `../../excalibur-dev/target/release/ouroboros.exe`

---

### `POST /api/deploy`

Generates a themed static HTML site from the current AST snapshot and deploys to Vercel.

**Request**
```json
{
  "nodes": [ /* ASTNode[] from astStore */ ],
  "bg": "#0f172a",
  "siteName": "my-camelot-site"
}
```

**Response**
```json
{ "url": "https://my-camelot-site.vercel.app", "latency_ms": 42310 }
```

**Error codes**

| Status | Meaning |
|---|---|
| 400 | Zod validation failed (bad node shape or missing fields) |
| 422 | HTML generation failed (empty node list) |
| 502 | Vercel CLI exited non-zero |
| 500 | Unexpected server error |

**Environment variables**

| Var | Default | Purpose |
|---|---|---|
| `VERCEL_TOKEN` | *(none)* | Passed to `vercel --token`. Not required if already logged in via `vercel login` |
| `VERCEL_BIN` | `vercel.cmd` (Win) / `vercel` | Override CLI binary path |
| `OUROBOROS_BIN` | Auto-resolved from repo | Override ouroboros binary path |

---

## Data Flow Detail

### ASTNode Schema (Zod v4)

```typescript
const ASTSchema = z.object({
  id:    z.uuid(),           // v4 UUID — node identity
  pid:   z.uuid().nullable(),// parent node id (null = root)
  tag:   z.string().min(1),  // component tag
  props: z.record(z.string(), z.unknown()), // arbitrary props + ThemeTokens
});
```

### ThemeTokens (WCAG AA/AAA)

Derived from a single background hex by `deriveTheme(bgHex)`:

```typescript
interface ThemeTokens {
  bg:            string;  // background
  fg:            string;  // foreground (#FFF or #000, WCAG contrast ≥ 7:1)
  surface:       string;  // slightly lifted surface
  surfaceFg:     string;  // foreground on surface
  border:        string;  // 20% blend toward fg
  focusRing:     string;  // #60A5FA (dark) or #1D4ED8 (light)
  contrastRatio: number;  // computed ratio
}
```

### AstStore Mutation Lifecycle

```
insert/update/remove
    │
    ├── validateDelta  (O(depth) incremental — fast pre-check)
    │       ↓ fail → throw MutationError
    ├── copy snapshot
    ├── apply op
    ├── validateDAG    (O(V+E) full Kahn's — catches multi-node cycles)
    │       ↓ fail → discard snapshot, throw MutationError
    └── commit → push to undo stack, notify listeners
```

---

## Latency Budget

| Stage | Ceiling | Notes |
|---|---|---|
| Inference (A) | 101ms | SSM step + JSON round-trip to binary |
| Parse + Theme (B) | < 1ms | Pure CPU, no I/O |
| CRDT commit (C+D) | < 5ms | O(V+E) on typical page (< 20 nodes) |
| Deploy (E) | ~1–3 min | Vercel CLI upload + build |

---

## Project Status

| Component | Status |
|---|---|
| Ouroboros SSM + AVX2 | ✅ Done |
| Ouroboros binary (stdin/stdout) | ✅ Done |
| `/api/infer` Route Handler | ✅ Done |
| `infer.ts` client wrapper | ✅ Done |
| `parse-ast.ts` + WCAG theme engine | ✅ Done |
| `crdt.ts` AstStore + React hook | ✅ Done |
| `dag.ts` Kahn's full + incremental | ✅ Done |
| `deploy.ts` HTML codegen + Vercel CLI | ✅ Done |
| `/api/deploy` Route Handler | ✅ Done |
| `dispatch-deploy.ts` client wrapper | ✅ Done |
| Dashboard UI (cockpit) | 🔧 In progress |
