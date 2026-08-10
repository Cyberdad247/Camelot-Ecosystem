// tests/version.test.ts
//
// Phase 8: asserts the shared VERSION constant is exported and that
// both health routes import it from @/lib/version (so they cannot
// drift apart again like they did in Phase 2/3 where the Node route
// reported "1.0.0-phase2" and the Edge route reported "1.0.0-phase3").
//
// Runs under `node --import tsx --test tests/*.test.ts`.

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { VERSION } from "../src/lib/version";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");

test("VERSION is a non-empty semver-like string", () => {
  assert.ok(typeof VERSION === "string" && VERSION.length > 0);
  assert.match(VERSION, /^\d+\.\d+\.\d+/);
});

test("VERSION ends with -phaseN for traceability", () => {
  assert.match(VERSION, /-phase\d+$/);
});

test("both health routes import VERSION from @/lib/version", () => {
  const nodeRoute = readFileSync(
    join(root, "src/app/api/health/route.ts"),
    "utf8",
  );
  const edgeRoute = readFileSync(
    join(root, "src/app/api/health/edge/route.ts"),
    "utf8",
  );
  assert.match(nodeRoute, /from\s+["']@\/lib\/version["']/);
  assert.match(edgeRoute, /from\s+["']@\/lib\/version["']/);
});

test("neither health route declares VERSION inline", () => {
  // Guards against a future regression where someone re-inlines
  // `const VERSION = "..."` in one of the routes.
  const nodeRoute = readFileSync(
    join(root, "src/app/api/health/route.ts"),
    "utf8",
  );
  const edgeRoute = readFileSync(
    join(root, "src/app/api/health/edge/route.ts"),
    "utf8",
  );
  assert.doesNotMatch(nodeRoute, /^const\s+VERSION\s*=\s*"/m);
  assert.doesNotMatch(edgeRoute, /^const\s+VERSION\s*=\s*"/m);
});
