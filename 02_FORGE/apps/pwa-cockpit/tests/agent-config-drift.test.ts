// tests/agent-config-drift.test.ts
//
// Contract drift detection for the AgentConfig interface shared
// between TWO physically-separate worktrees:
//
//   ┌─── this worktree (phase7-wt, feat/phase-7-deploy) ───┐
//   │   src/app/api/agent/config/route.ts                  │
//   │     type ProviderId = "stub" | "gemini" | ...        │
//   │     interface AgentConfig { active_provider: ...  }   │
//   └──────────────────────────────────────────────────────┘
//
//   ┌─── separate worktree (CAMELOT_OS, master) ───────────┐
//   │   02_FORGE/.../PWACockpitStatusBanner.tsx            │
//   │     interface AgentConfig {                          │
//   │       active_provider: "stub" | "gemini" | ...       │
//   │     }                                                │
//   └──────────────────────────────────────────────────────┘
//
// The interfaces MUST stay in sync. Goose uses INLINE string
// literals (no canonical type alias), so adding a provider on
// only one side would silently break runtime safety in the banner.
// This test catches that drift at CI time.
//
// Strategy: 3-source pin (test EXPECTED + pwa route.ts + Goose
// banner). If any pair disagrees, the test fails.
//
// To add a new provider:
//   1. Add the literal to BOTH `active_provider` unions.
//   2. Update per-side label/model/PROVIDER_PILL/runtime tables.
//   3. (Optional) update tests/agent-config.test.ts deepEqual cases.
//   4. Update EXPECTED_PROVIDERS in this file ONLY AFTER both
//      AgentConfig surfaces agree (so we don't hide drift).
//
// Why a runtime text extractor instead of cross-worktree TS type
// import: pwa-cockpit's tsconfig has a strict rootDir; importing
// types from CAMELOT_OS via absolute path is fragile. Reading the
// source as text works regardless of tsconfig boundaries.

import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

// Compile-time anchor: importing the local AgentConfig type
// forces tsc to evaluate the type. If anyone changes
// active_provider to a non-string-union shape, the `satisfies`
// clause below on EXPECTED_PROVIDERS fails fast during
// `npx tsc --noEmit` before this test even runs.
import type { AgentConfig } from "../src/app/api/agent/config/route";

// ─── Paths ──────────────────────────────────────────────────────

// Resolved via `import.meta.url → fileURLToPath` so this test is
// runnable from any cwd (e.g. `npx tsx --test tests/foo.test.ts`
// from a subdirectory, or via `npm test` from the project root).
// `HERE` is this test file's directory (`tests/`); `PWA_ROUTE` walks
// one level up to the project root and into `src/`. The Goose
// banner lives in a SEPARATE worktree (CAMELOT_OS, master branch)
// and is read by absolute path; if the Goose source moves, update
// GOOSE_BANNER — this is the only place the cross-worktree
// coupling is expressed.
const HERE = path.dirname(fileURLToPath(import.meta.url));

const PWA_ROUTE = path.resolve(
  HERE,
  "../src/app/api/agent/config/route.ts"
);

const GOOSE_BANNER = path.resolve(
  "C:/Users/vizio/CAMELOT_OS/02_FORGE/KINETIC_ARMORY/goose/ui/desktop/src/components/settings/providers/PWACockpitStatusBanner.tsx"
);

// ─── Canonical contract (single source of truth for this test) ───

// `satisfies` binds each literal to the local ProviderId union at
// compile time. If the local union shrinks or changes shape, TS
// fails here BEFORE npm test even runs.
const EXPECTED_PROVIDERS = [
  "stub",
  "gemini",
  "openai",
  "anthropic",
  "agents_a1",
] as const satisfies ReadonlyArray<AgentConfig["active_provider"]>;

// Symmetric to EXPECTED_PROVIDERS: `satisfies` binds each literal to
// `keyof AgentConfig` so tsc fails fast if anyone drops or renames a
// field on the local interface, before this test even runs.
const EXPECTED_FIELDS = [
  "active_provider",
  "provider_label",
  "model",
  "config",
  "read_only",
] as const satisfies ReadonlyArray<keyof AgentConfig>;

// ─── Extractors (text-based, work cross-worktree) ───────────────

/**
 * Pulls the ProviderId union literals out of an AgentConfig-shaped
 * file. Supports two patterns:
 *
 *   A. `type ProviderId = "stub" | "gemini" | ...;`
 *      (pwa-cockpit route.ts uses a type alias)
 *
 *   B. `active_provider:\n    | "stub"\n    | "gemini"` …
 *      (Goose banner uses an INLINE multi-line union)
 *
 * PRIORITY: Pattern A wins over Pattern B. The two `match()` calls
 * below are ordered \u2014 if a file declares BOTH forms (a `type
 * ProviderId = \u2026` AND an inline `active_provider: | \u2026`), only
 * the type alias's literals are returned. Both real surfaces we
 * cover today declare exactly ONE form, so this is a principled
 * tie-break documented for future maintainers rather than a
 * behavior we depend on today.
 *
 * Returns the literals in source order. Sort before comparison.
 */
function extractActiveProviderIds(src: string): string[] {
  // Pattern A — type alias.
  const aliased = src.match(/type\s+ProviderId\s*=\s*([\s\S]+?);/);
  if (aliased) {
    return Array.from(aliased[1].matchAll(/"([a-z_0-9]+)"/g), (m) => m[1]);
  }
  // Pattern B — inline union under `active_provider:`.
  const inline = src.match(/active_provider:\s*([\s\S]+?);/);
  if (inline) {
    return Array.from(inline[1].matchAll(/"([a-z_0-9]+)"/g), (m) => m[1]);
  }
  return [];
}

/**
 * Pulls the top-level field names out of an
 * `interface AgentConfig { ... }` block.
 *
 * Skips:
 *   - empty / blank lines
 *   - JSDoc and // comments
 *   - union continuation lines (start with `|` after a multi-line
 *     field like the Goose banner's
 *     `active_provider: | "stub" | "gemini" ...;`)
 *
 * Closing brace is matched at column 0 (preceded by `\n`).
 */
function extractAgentConfigFields(src: string): string[] {
  const m = src.match(/interface\s+AgentConfig\s*\{([\s\S]*?\n\})/);
  if (!m) return [];
  const fields: string[] = [];
  for (const rawLine of m[1].split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line) continue;
    if (
      line.startsWith("*") ||
      line.startsWith("//") ||
      line.startsWith("/*")
    ) {
      continue;
    }
    if (line.startsWith("|")) continue; // union continuation
    const fieldMatch = line.match(/^([a-zA-Z_$][\w$]*)\s*[:?]/);
    if (fieldMatch) fields.push(fieldMatch[1]);
  }
  return fields;
}

// ─── Tests ──────────────────────────────────────────────────────

test("cross-worktree fixtures are reachable", () => {
  if (!fs.existsSync(GOOSE_BANNER)) {
    assert.fail(
      `Goose banner file not found at:\n  ${GOOSE_BANNER}\n\n` +
        `If you moved the file (or no longer have a CAMELOT_OS ` +
        `checkout alongside phase7-wt), update GOOSE_BANNER at the ` +
        `top of this test. This drift test expects a parallel ` +
        `cross-worktree sibling-checkout.`,
    );
  }
  assert.ok(
    fs.existsSync(PWA_ROUTE),
    `local PWA route missing at ${PWA_ROUTE}`,
  );
});

test("active_provider union stays in sync across pwa-cockpit and Goose", () => {
  const pwaText = fs.readFileSync(PWA_ROUTE, "utf8");
  const gooseText = fs.readFileSync(GOOSE_BANNER, "utf8");

  const pwaIds = extractActiveProviderIds(pwaText).sort();
  const gooseIds = extractActiveProviderIds(gooseText).sort();
  const expected = [...EXPECTED_PROVIDERS].sort();

  assert.deepEqual(
    pwaIds,
    gooseIds,
    `ProviderId union drifted between pwa-cockpit and Goose.\n\n` +
      `  pwa-cockpit (${PWA_ROUTE}):\n    [${pwaIds.join(", ")}]\n` +
      `  Goose banner (${GOOSE_BANNER}):\n    [${gooseIds.join(", ")}]\n\n` +
      `Both sides MUST be updated together. To fix:\n` +
      `  1. Add the new literal to BOTH active_provider unions.\n` +
      `  2. Update per-side label/model/PROVIDER_PILL/runtime tables.\n` +
      `  3. Update EXPECTED_PROVIDERS in this file ONLY AFTER both ` +
      `AgentConfig surfaces agree.`,
  );

  assert.deepEqual(
    pwaIds,
    expected,
    `ProviderId union drifted from this test's canonical pin.\n` +
      `  actual:   [${pwaIds.join(", ")}]\n` +
      `  expected: [${expected.join(", ")}]\n\n` +
      `Update EXPECTED_PROVIDERS in this file once both AgentConfig ` +
      `surfaces agree — that is the LAST step, never the first.`,
  );
});

test("AgentConfig field shape stays in sync across pwa-cockpit and Goose", () => {
  const pwaText = fs.readFileSync(PWA_ROUTE, "utf8");
  const gooseText = fs.readFileSync(GOOSE_BANNER, "utf8");

  const pwaFields = extractAgentConfigFields(pwaText).sort();
  const gooseFields = extractAgentConfigFields(gooseText).sort();
  const expected = [...EXPECTED_FIELDS].sort();

  assert.deepEqual(
    pwaFields,
    gooseFields,
    `AgentConfig field shape drifted between the two surfaces.\n\n` +
      `  pwa-cockpit: [${pwaFields.join(", ")}]\n` +
      `  Goose:      [${gooseFields.join(", ")}]\n\n` +
      `Both AgentConfig interfaces must declare identical top-level ` +
      `field names. Do NOT add fields to one side only — every ` +
      `consumer (Goose banner, future operator console, monitoring ` +
      `dashboard) will break.`,
  );

  assert.deepEqual(
    pwaFields,
    expected,
    `AgentConfig field shape drifted from this test's canonical pin.\n` +
      `  actual:   [${pwaFields.join(", ")}]\n` +
      `  expected: [${expected.join(", ")}]\n\n` +
      `Update EXPECTED_FIELDS in this file once both AgentConfig ` +
      `surfaces agree — that is the LAST step, never the first.`,
  );
});
