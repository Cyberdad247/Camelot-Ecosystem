import { NextRequest, NextResponse } from "next/server";
import { isAuthorized } from "@/lib/cockpit-auth";
import { listForgeCartridges } from "@/lib/forge-law";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  if (!isAuthorized(req)) return NextResponse.json({ message: "Operator pairing required." }, { status: 401 });
  return NextResponse.json(listForgeCartridges(), {
    headers: { "Cache-Control": "no-store, max-age=0" },
  });
}

