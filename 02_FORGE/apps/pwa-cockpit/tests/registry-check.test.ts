// tests/registry-check.test.ts
//
// Phase 8: tests for checkCartridgeRegistry() in
// src/cartridges/registry-check.ts. Validates the result shape and
// confirms the shipped catalog passes all checks.
//
// Runs under `node --import tsx --test tests/*.test.ts`.

import assert from "node:assert/strict";
import test from "node:test";
import { checkCartridgeRegistry } from "../src/cartridges/registry-check";

test("checkCartridgeRegistry returns ok=true for the shipped catalog", () => {
  const result = checkCartridgeRegistry();
  assert.equal(result.ok, true);
  assert.ok(
    result.count > 0,
    "shipped catalog should have at least one manifest",
  );
  assert.equal(result.issues.length, 0);
});

test("checkCartridgeRegistry result has the expected shape", () => {
  const result = checkCartridgeRegistry();
  assert.equal(typeof result.ok, "boolean");
  assert.equal(typeof result.count, "number");
  assert.ok(Array.isArray(result.issues));
});

test("checkCartridgeRegistry reports 7 shipped manifests", () => {
  // The shipped catalog has exactly 7 cartridges: command, factory,
  // forge-law, intelligence, interphase, device-hall, mesh.
  // If this number changes, update both the count and the comment.
  const result = checkCartridgeRegistry();
  assert.equal(result.count, 7);
});
