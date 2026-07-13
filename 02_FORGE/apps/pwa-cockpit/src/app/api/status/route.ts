import { NextRequest, NextResponse } from "next/server";
import { getStatus } from "@/lib/control-plane";
import { isAuthorized } from "@/lib/cockpit-auth";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  if (!isAuthorized(request)) return NextResponse.json({ message: "Operator pairing required." }, { status: 401 });
  return NextResponse.json(await getStatus(), {
    headers: { "Cache-Control": "no-store" },
  });
}
