// src/cartridges/registry-check.ts
//
// Phase 8: typed runtime sanity check for the V1 cartridge manifest
// catalog. Used by the /api/health (nodejs) endpoint to surface
// registry issues as a structured check result, complementing the
// count-based probe that the route already does via getCartridgeIds().
//
// What this checks (manifest-side validation only):
//   - At least one manifest is registered
//   - No duplicate cartridge ids
//   - Each manifest has the required fields: id, label, shortLabel,
//     and at least one capability
//   - Each manifest's accent is one of the four valid values
//
// What this does NOT check:
//   - Loader ↔ manifest correspondence (TypeScript's `satisfies`
//     clause in registry.tsx enforces this at compile time)
//   - Signature verification (that lives in the V2 platform, which
//     uses @noble/ed25519 in nodejs-only code)
//
// Edge-runtime compatible: pure data, no React, no Node primitives.

import { cartridgeManifests } from "./manifests";
import type { CartridgeId } from "./types";

export type RegistryCheckResult = {
  ok: boolean;
  count: number;
  issues: string[];
};

const VALID_ACCENTS: ReadonlySet<string> = new Set([
  "teal",
  "amber",
  "blue",
  "coral",
]);

export function checkCartridgeRegistry(): RegistryCheckResult {
  const issues: string[] = [];

  if (cartridgeManifests.length === 0) {
    issues.push("cartridgeManifests is empty");
    return { ok: false, count: 0, issues };
  }

  // 1. No duplicate ids.
  const seen = new Set<CartridgeId>();
  for (const m of cartridgeManifests) {
    if (!m.id) {
      issues.push("manifest missing id");
      continue;
    }
    if (seen.has(m.id)) {
      issues.push(`duplicate cartridge id: ${m.id}`);
    }
    seen.add(m.id);
  }

  // 2. Required fields and valid accent per manifest.
  for (const m of cartridgeManifests) {
    const idLabel = m.id ?? "?";
    if (!m.label) issues.push(`manifest ${idLabel} missing label`);
    if (!m.shortLabel) issues.push(`manifest ${idLabel} missing shortLabel`);
    if (!Array.isArray(m.capabilities) || m.capabilities.length === 0) {
      issues.push(`manifest ${idLabel} has no capabilities`);
    }
    if (!VALID_ACCENTS.has(m.accent)) {
      issues.push(`manifest ${idLabel} has invalid accent: ${String(m.accent)}`);
    }
  }

  return {
    ok: issues.length === 0,
    count: cartridgeManifests.length,
    issues,
  };
}
