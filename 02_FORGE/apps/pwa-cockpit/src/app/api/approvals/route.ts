import { NextRequest, NextResponse } from "next/server";
import { listApprovals } from "@/lib/control-plane";
import { isAuthorized } from "@/lib/cockpit-auth";

export function GET(request: NextRequest) {
  if (!isAuthorized(request)) return NextResponse.json({ message: "Operator pairing required." }, { status: 401 });
  return NextResponse.json(listApprovals(), {
    headers: { "Cache-Control": "no-store" },
  });
}
