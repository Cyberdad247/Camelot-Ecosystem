// Health check endpoint — Camelot PWA Cockpit
// Node-runtime compatible (the V1 cartridge registry transitively imports
// React components, which cannot run in the edge runtime). Used by
// Vercel/Cloudflare monitoring, CI smoke tests, and the operator's
// watchdog scripts.
//
// Returns 200 with a JSON body describing liveness, readiness, and the
// last-known manifest version. The endpoint is intentionally cheap so
// it can be polled frequently without affecting the page handler.

import { NextResponse } from "next/server";
import { getRecentEvents } from "@/lib/telemetry";
import { VERSION } from "@/lib/version";
import { checkCartridgeRegistry } from "@/cartridges/registry-check";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type HealthStatus = {
  status: "ok" | "degraded" | "down";
  uptime_s: number;
  version: string;
  edge: boolean;
  cartridges_loaded: number;
  voice_pipeline: "ready" | "unavailable";
  v2_platform: "ready" | "unavailable";
  checks: Record<string, { ok: boolean; detail?: string }>;
  recent_events?: readonly unknown[];
};

const START_TS = Date.now();

export async function GET(): Promise<NextResponse<HealthStatus>> {
  const checks: HealthStatus["checks"] = {};

  // Check 1: V2 cartridge platform module loadable.
  // Dynamic import avoids hard failure if the module is missing in
  // older builds; the check reports the failure rather than 500ing.
  try {
    const v2 = await import("@/lib/v2/cartridge-platform");
    checks.v2_platform = { ok: typeof v2.hydrateV2Cartridge === "function" };
  } catch (e) {
    checks.v2_platform = { ok: false, detail: (e as Error).message };
  }

  // Check 2: ZIP reader loadable (Phase 2 archive format).
  try {
    const zip = await import("@/lib/v2/cartridge-zip");
    checks.zip_reader = { ok: typeof zip.readZip === "function" };
  } catch (e) {
    checks.zip_reader = { ok: false, detail: (e as Error).message };
  }

  // Check 3: V1 cartridge registry (cartridges registered in trustedLoaders).
  // Count via getCartridgeIds() so a new cartridge added to
  // trustedLoaders automatically extends the list — no more silently
  // underreporting when a cartridge id is missing from a hardcoded
  // probe list. Phase 8: also runs checkCartridgeRegistry() (static
  // import — the check is edge-safe) to surface manifest-side issues
  // (duplicates, missing required fields, invalid accent) on the same
  // line.
  try {
    const reg = await import("@/cartridges/registry");
    const ids = reg.getCartridgeIds();
    const result = checkCartridgeRegistry();
    checks.v1_registry = {
      ok: ids.length > 0 && result.ok,
      detail: `cartridges: ${ids.length}${
        result.issues.length > 0 ? `, issues: ${result.issues.join("; ")}` : ""
      }`,
    };
  } catch (e) {
    checks.v1_registry = { ok: false, detail: (e as Error).message };
  }

  // Check 4: Ed25519 verification wired (Phase 2 production).
  try {
    const ed = await import("@noble/ed25519");
    checks.ed25519 = { ok: typeof ed.verify === "function" };
  } catch (e) {
    checks.ed25519 = { ok: false, detail: (e as Error).message };
  }

  // Check 5: Telemetry buffer readable.
  try {
    const events = getRecentEvents(5);
    checks.telemetry = { ok: Array.isArray(events), detail: `buffered: ${events.length}` };
  } catch (e) {
    checks.telemetry = { ok: false, detail: (e as Error).message };
  }
  // Note: getRecentEvents() is intentionally NOT exposed in the public
  // health response because it leaks internal telemetry (cartridge loads,
  // voice states, V2 verify results) to anyone who hits /api/health.
  // A future /api/agent/telemetry endpoint can expose it behind the
  // /api/agent/* auth gate (see middleware.ts).

  const allOk = Object.values(checks).every((c) => c.ok);
  const status: HealthStatus["status"] = allOk ? "ok" : "degraded";
  const cartridges_loaded = Number(checks.v1_registry.detail?.match(/\d+/)?.[0] ?? 0);

  return NextResponse.json<HealthStatus>(
    {
      status,
      uptime_s: Math.floor((Date.now() - START_TS) / 1000),
      version: VERSION,
      edge: false, // nodejs runtime; edge version is a Phase 3 follow-up
      cartridges_loaded,
      voice_pipeline: "unavailable", // Phase 5 wired in cockpit-shell; not yet exposed here
      v2_platform: checks.v2_platform.ok ? "ready" : "unavailable",
      checks,
      // recent_events intentionally omitted from the public response to
      // avoid leaking internal telemetry; expose via /api/agent/telemetry
      // behind the /api/agent/* auth gate (see middleware.ts).
    },
    { status: allOk ? 200 : 503 },
  );
}
