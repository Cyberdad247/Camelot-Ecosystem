// src/app/api/health/edge/route.ts
//
// Edge-runtime health variant. No React imports, no Node primitives.
// Returns a minimal status that the full /api/health (nodejs) endpoint
// augments with deeper checks (V1 registry, V2 platform, Ed25519, etc.).
//
// Used by Vercel/Cloudflare edge monitoring and CI smoke tests that
// need a sub-100ms response without the cold-start cost of the nodejs
// handler. Both endpoints report the same VERSION so operators can
// correlate them.

import { NextResponse } from "next/server";
import { getRecentEvents } from "@/lib/telemetry";
import { VERSION } from "@/lib/version";

export const runtime = "edge";
export const dynamic = "force-dynamic";

type EdgeHealthStatus = {
  status: "ok";
  uptime_s: number;
  version: string;
  edge: true;
  checks: {
    telemetry: { ok: boolean; detail?: string };
  };
};

const START_TS = Date.now();

export function GET(): NextResponse<EdgeHealthStatus> {
  let telemetryOk = true;
  let detail: string | undefined;
  try {
    const events = getRecentEvents(5);
    detail = `buffered: ${events.length}`;
  } catch (e) {
    telemetryOk = false;
    detail = e instanceof Error ? e.message : String(e);
  }
  return NextResponse.json<EdgeHealthStatus>(
    {
      status: "ok",
      uptime_s: Math.floor((Date.now() - START_TS) / 1000),
      version: VERSION,
      edge: true,
      checks: {
        telemetry: { ok: telemetryOk, detail },
      },
    },
    { status: 200 },
  );
}
